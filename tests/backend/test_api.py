import pytest
from datetime import timedelta
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient

from backend.core.security import create_access_token


def _get_token(client: TestClient) -> str:
    response = client.post(
        "/auth/login",
        data={"username": "analyst", "password": "analyst123"},
    )
    return response.json()["access_token"]


def _get_admin_token(client: TestClient) -> str:
    response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "admin123"},
    )
    return response.json()["access_token"]


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.headers["X-RateLimit-Limit"] == "100"
    assert int(response.headers["X-RateLimit-Remaining"]) >= 0


def test_rate_limit_rejection_has_headers(client, monkeypatch):
    monkeypatch.setattr(
        "backend.middleware.trace.check_rate_limit",
        AsyncMock(return_value=(False, 0)),
    )

    response = client.get("/health")

    assert response.status_code == 429
    assert response.headers["X-RateLimit-Remaining"] == "0"
    assert response.headers["Retry-After"] == "60"


def test_create_indicator(client):
    payload = {
        "indicator_type": "IP",
        "value": "1.1.1.1",
        "severity": "high",
        "source": "unit-test",
        "confidence": 85,
        "tags": ["ransomware"],
        "threat_actor": None,
        "is_active": True,
    }
    response = client.post("/indicators", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["value"] == "1.1.1.1"
    assert data["id"] is not None


def test_list_indicators_empty(client):
    response = client.get("/indicators")
    assert response.status_code == 200
    assert response.json() == []


def test_list_indicators_after_create(client):
    client.post(
        "/indicators",
        json={
            "indicator_type": "IP",
            "value": "2.2.2.2",
            "severity": "low",
            "source": "unit-test",
            "confidence": 50,
            "tags": [],
            "threat_actor": None,
            "is_active": True,
        },
    )
    response = client.get("/indicators")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["created_at"].endswith("Z")


def test_list_indicators_rejects_unsafe_pagination(client):
    response = client.get("/indicators", params={"skip": -1, "limit": 101})

    assert response.status_code == 422


def test_list_indicators_applies_filters(client):
    values = {"IP": "192.0.2.10", "Domain": "inactive.example"}
    for indicator_type, severity, is_active in [
        ("IP", "high", True),
        ("Domain", "low", False),
    ]:
        client.post(
            "/indicators",
            json={
                "indicator_type": indicator_type,
                "value": values[indicator_type],
                "severity": severity,
                "source": "unit-test",
                "confidence": 50,
                "tags": [],
                "threat_actor": None,
                "is_active": is_active,
            },
        )

    response = client.get(
        "/indicators",
        params={
            "indicator_type": "Domain",
            "severity": "low",
            "is_active": False,
        },
    )

    assert response.status_code == 200
    assert [indicator["indicator_type"] for indicator in response.json()] == ["Domain"]


def test_paginated_indicators_support_etag(client):
    for index in range(3):
        client.post(
            "/indicators",
            json={
                "indicator_type": "IP",
                "value": f"192.0.2.{index}",
                "severity": "medium",
                "source": "unit-test",
                "confidence": 60,
            },
        )

    response = client.get("/indicators/page", params={"page": 1, "page_size": 2})

    assert response.status_code == 200
    assert response.json()["total"] == 3
    assert len(response.json()["items"]) == 2
    assert response.headers["X-Total-Count"] == "3"
    assert response.headers["ETag"]

    not_modified = client.get(
        "/indicators/page",
        params={"page": 1, "page_size": 2},
        headers={"If-None-Match": response.headers["ETag"]},
    )
    assert not_modified.status_code == 304


def test_paginated_indicators_rejects_unsafe_page(client):
    response = client.get("/indicators/page", params={"page": 1_763_735_598_833_504_512})

    assert response.status_code == 422


def test_export_indicators_csv(client):
    client.post(
        "/indicators",
        json={
            "indicator_type": "Domain",
            "value": "malicious.example",
            "severity": "critical",
            "source": "unit-test",
            "confidence": 99,
            "tags": ["c2", "demo"],
        },
    )

    response = client.get("/indicators/export.csv")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "malicious.example" in response.text
    assert "c2,demo" in response.text


def test_get_indicator_by_id(client):
    create = client.post(
        "/indicators",
        json={
            "indicator_type": "URL",
            "value": "http://evil.com",
            "severity": "high",
            "source": "unit-test",
            "confidence": 90,
            "tags": [],
            "threat_actor": None,
            "is_active": True,
        },
    )
    indicator_id = create.json()["id"]
    response = client.get(f"/indicators/{indicator_id}")
    assert response.status_code == 200
    assert response.json()["value"] == "http://evil.com"


def test_get_indicator_not_found(client):
    response = client.get("/indicators/9999")
    assert response.status_code == 404
    assert response.json()["error"] == "resource_not_found"
    assert response.json()["trace_id"]


def test_update_indicator(client):
    create = client.post(
        "/indicators",
        json={
            "indicator_type": "URL",
            "value": "https://malicious.example",
            "severity": "medium",
            "source": "unit-test",
            "confidence": 70,
        },
    )

    response = client.put(
        f"/indicators/{create.json()['id']}",
        json={"severity": "critical", "confidence": 99},
    )

    assert response.status_code == 200
    assert response.json()["severity"] == "critical"
    assert response.json()["confidence"] == 99


def test_delete_indicator(client):
    token = _get_token(client)
    create = client.post(
        "/indicators",
        json={
            "indicator_type": "Hash",
            "value": "d41d8cd98f00b204e9800998ecf8427e",
            "severity": "medium",
            "source": "unit-test",
            "confidence": 70,
            "tags": [],
            "threat_actor": None,
            "is_active": True,
        },
    )
    indicator_id = create.json()["id"]
    response = client.delete(
        f"/indicators/{indicator_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    get_response = client.get(f"/indicators/{indicator_id}")
    assert get_response.status_code == 404


def test_delete_indicator_not_found(client):
    token = _get_token(client)
    response = client.delete(
        "/indicators/9999",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


def test_delete_indicator_unauthorized(client):
    create = client.post(
        "/indicators",
        json={
            "indicator_type": "IP",
            "value": "9.9.9.9",
            "severity": "low",
            "source": "unit-test",
            "confidence": 50,
            "tags": [],
            "threat_actor": None,
            "is_active": True,
        },
    )
    indicator_id = create.json()["id"]
    response = client.delete(f"/indicators/{indicator_id}")
    assert response.status_code == 401


def test_delete_indicator_expired_token(client):
    """Token that expired 1 second ago must be rejected with 401."""
    expired_token = create_access_token(
        data={"sub": "analyst", "role": "analyst"},
        expires_delta=timedelta(seconds=-1),
    )
    create = client.post(
        "/indicators",
        json={
            "indicator_type": "IP",
            "value": "5.5.5.5",
            "severity": "low",
            "source": "unit-test",
            "confidence": 50,
            "tags": [],
            "threat_actor": None,
            "is_active": True,
        },
    )
    indicator_id = create.json()["id"]
    response = client.delete(
        f"/indicators/{indicator_id}",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert response.status_code == 401


def test_create_indicator_invalid_confidence(client):
    payload = {
        "indicator_type": "IP",
        "value": "3.3.3.3",
        "severity": "low",
        "source": "unit-test",
        "confidence": 150,
        "tags": [],
        "threat_actor": None,
        "is_active": True,
    }
    response = client.post("/indicators", json=payload)
    assert response.status_code == 422


@pytest.mark.parametrize("field", ["created_at", "unexpected"])
def test_create_indicator_rejects_server_owned_or_unknown_fields(client, field):
    payload = {
        "indicator_type": "IP",
        "value": "3.3.3.3",
        "severity": "low",
        "source": "unit-test",
        "confidence": 80,
        field: "not-accepted",
    }

    response = client.post("/indicators", json=payload)

    assert response.status_code == 422


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("indicator_type", "NotARealType"),
        ("severity", "banana"),
        ("value", "   "),
        ("source", ""),
    ],
)
def test_create_indicator_rejects_invalid_values(client, field, value):
    payload = {
        "indicator_type": "IP",
        "value": "3.3.3.3",
        "severity": "low",
        "source": "unit-test",
        "confidence": 80,
    }
    payload[field] = value

    response = client.post("/indicators", json=payload)

    assert response.status_code == 422


def test_update_indicator_rejects_invalid_values(client):
    create = client.post(
        "/indicators",
        json={
            "indicator_type": "IP",
            "value": "4.4.4.4",
            "severity": "low",
            "source": "unit-test",
            "confidence": 50,
        },
    )

    response = client.put(
        f"/indicators/{create.json()['id']}",
        json={"severity": "banana", "source": "   ", "confidence": 101},
    )

    assert response.status_code == 422


def test_analyst_cannot_deactivate_indicator(client):
    token = _get_token(client)
    create = client.post(
        "/indicators",
        json={
            "indicator_type": "IP",
            "value": "6.6.6.6",
            "severity": "high",
            "source": "unit-test",
            "confidence": 90,
        },
    )

    response = client.post(
        f"/indicators/{create.json()['id']}/deactivate",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_admin_can_deactivate_indicator(client):
    token = _get_admin_token(client)
    create = client.post(
        "/indicators",
        json={
            "indicator_type": "IP",
            "value": "7.7.7.7",
            "severity": "high",
            "source": "unit-test",
            "confidence": 90,
        },
    )

    response = client.post(
        f"/indicators/{create.json()['id']}/deactivate",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    indicator = client.get(f"/indicators/{create.json()['id']}").json()
    assert indicator["is_active"] is False


def test_create_indicator_missing_required_fields(client):
    response = client.post("/indicators", json={"value": "1.1.1.1"})
    assert response.status_code == 422


@pytest.mark.parametrize(
    ("indicator_type", "value"),
    [
        ("IP", "999.999.999.999"),
        ("Domain", "not a domain"),
        ("URL", "javascript:alert(1)"),
        ("Hash", "abc123"),
        ("Email", "missing-at.example.com"),
    ],
)
def test_create_indicator_rejects_invalid_ioc_format(client, indicator_type, value):
    response = client.post(
        "/indicators",
        json={
            "indicator_type": indicator_type,
            "value": value,
            "severity": "medium",
            "source": "unit-test",
            "confidence": 60,
        },
    )

    assert response.status_code == 422


@pytest.mark.anyio
async def test_health_check_async(async_client):
    response = await async_client.get("/health")
    assert response.status_code == 200
