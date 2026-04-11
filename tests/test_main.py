import pytest
from fastapi.testclient import TestClient
from cygnal.app.main import app

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
        "source": "unit-test"
    }
    response = client.post("/indicators", json=payload)
    assert response.status_code == 201
    assert response.json()["value"] == "1.1.1.1"

def test_list_indicators():
    response = client.get("/indicators")
    assert response.status_code == 200
    assert isinstance(response.json(), list)