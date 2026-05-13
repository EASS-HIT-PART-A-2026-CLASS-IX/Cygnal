import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_create_indicator():
    payload = {
        "indicator_type": "IP",
        "value": "1.1.1.1",
        "severity": "high",
        "source": "unit-test",
        "confidence": 90,
        "tags": ["test"],
        "is_active": True
    }
    response = client.post("/indicators", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["value"] == "1.1.1.1"
    assert data["id"] is not None

def test_list_indicators():
    response = client.get("/indicators")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_non_existent_indicator():
    response = client.get("/indicators/99999")
    assert response.status_code == 404