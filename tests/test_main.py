import pytest
from fastapi.testclient import TestClient


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_indicator(client):
    payload = {
        "indicator_type": "IP",
        "value": "1.1.1.1",
        "severity": "high",
        "source": "unit-test"
    }
    response = client.post("/indicators", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["value"] == "1.1.1.1"
    assert data["severity"] == "high"
    assert data["confidence"] == 50
    assert data["is_active"] == True
    assert data["id"] == 1


def test_create_indicator_with_all_fields(client):
    payload = {
        "indicator_type": "Domain",
        "value": "evil.com",
        "severity": "critical",
        "source": "unit-test",
        "confidence": 90,
        "tags": ["ransomware", "APT29"],
        "threat_actor": "Lazarus Group",
        "is_active": True
    }
    response = client.post("/indicators", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["tags"] == ["ransomware", "APT29"]
    assert data["threat_actor"] == "Lazarus Group"
    assert data["confidence"] == 90


def test_list_indicators_empty(client):
    response = client.get("/indicators")
    assert response.status_code == 200
    assert response.json() == []


def test_list_indicators_after_create(client):
    client.post("/indicators", json={
        "indicator_type": "IP",
        "value": "2.2.2.2",
        "severity": "low",
        "source": "unit-test"
    })
    response = client.get("/indicators")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_indicator_by_id(client):
    create = client.post("/indicators", json={
        "indicator_type": "URL",
        "value": "http://evil.com/payload",
        "severity": "high",
        "source": "unit-test"
    })
    indicator_id = create.json()["id"]
    response = client.get(f"/indicators/{indicator_id}")
    assert response.status_code == 200
    assert response.json()["value"] == "http://evil.com/payload"


def test_get_indicator_not_found(client):
    response = client.get("/indicators/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Indicator not found"


def test_delete_indicator(client):
    create = client.post("/indicators", json={
        "indicator_type": "Hash",
        "value": "abc123",
        "severity": "medium",
        "source": "unit-test"
    })
    indicator_id = create.json()["id"]
    response = client.delete(f"/indicators/{indicator_id}")
    assert response.status_code == 204
    get_response = client.get(f"/indicators/{indicator_id}")
    assert get_response.status_code == 404


def test_delete_indicator_not_found(client):
    response = client.delete("/indicators/9999")
    assert response.status_code == 404


def test_create_indicator_invalid_confidence(client):
    payload = {
        "indicator_type": "IP",
        "value": "3.3.3.3",
        "severity": "low",
        "source": "unit-test",
        "confidence": 150
    }
    response = client.post("/indicators", json=payload)
    assert response.status_code == 422


def test_create_indicator_missing_required_fields(client):
    response = client.post("/indicators", json={"value": "1.1.1.1"})
    assert response.status_code == 422


def test_ids_increment(client):
    first = client.post("/indicators", json={
        "indicator_type": "IP",
        "value": "1.1.1.1",
        "severity": "low",
        "source": "unit-test"
    }).json()["id"]
    second = client.post("/indicators", json={
        "indicator_type": "IP",
        "value": "2.2.2.2",
        "severity": "low",
        "source": "unit-test"
    }).json()["id"]
    assert second == first + 1