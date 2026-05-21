import time
import pytest
from datetime import timedelta
from fastapi.testclient import TestClient

from backend.auth import create_access_token


def _get_token(client: TestClient) -> str:
    response = client.post(
        "/auth/login",
        data={"username": "analyst", "password": "analyst123"},
    )
    return response.json()["access_token"]


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200


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
    client.post("/indicators", json={
        "indicator_type": "IP",
        "value": "2.2.2.2",
        "severity": "low",
        "source": "unit-test",
        "confidence": 50,
        "tags": [],
        "threat_actor": None,
        "is_active": True,
    })
    response = client.get("/indicators")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_indicator_by_id(client):
    create = client.post("/indicators", json={
        "indicator_type": "URL",
        "value": "http://evil.com",
        "severity": "high",
        "source": "unit-test",
        "confidence": 90,
        "tags": [],
        "threat_actor": None,
        "is_active": True,
    })
    indicator_id = create.json()["id"]
    response = client.get(f"/indicators/{indicator_id}")
    assert response.status_code == 200
    assert response.json()["value"] == "http://evil.com"


def test_get_indicator_not_found(client):
    response = client.get("/indicators/9999")
    assert response.status_code == 404


def test_delete_indicator(client):
    token = _get_token(client)
    create = client.post("/indicators", json={
        "indicator_type": "Hash",
        "value": "abc123",
        "severity": "medium",
        "source": "unit-test",
        "confidence": 70,
        "tags": [],
        "threat_actor": None,
        "is_active": True,
    })
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
    create = client.post("/indicators", json={
        "indicator_type": "IP",
        "value": "9.9.9.9",
        "severity": "low",
        "source": "unit-test",
        "confidence": 50,
        "tags": [],
        "threat_actor": None,
        "is_active": True,
    })
    indicator_id = create.json()["id"]
    response = client.delete(f"/indicators/{indicator_id}")
    assert response.status_code == 401


def test_delete_indicator_expired_token(client):
    """Token that expired 1 second ago must be rejected with 401."""
    expired_token = create_access_token(
        data={"sub": "analyst", "role": "analyst"},
        expires_delta=timedelta(seconds=-1),
    )
    create = client.post("/indicators", json={
        "indicator_type": "IP",
        "value": "5.5.5.5",
        "severity": "low",
        "source": "unit-test",
        "confidence": 50,
        "tags": [],
        "threat_actor": None,
        "is_active": True,
    })
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


def test_create_indicator_missing_required_fields(client):
    response = client.post("/indicators", json={"value": "1.1.1.1"})
    assert response.status_code == 422


@pytest.mark.anyio
async def test_health_check_async(async_client):
    response = await async_client.get("/health")
    assert response.status_code == 200