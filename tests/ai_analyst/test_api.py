from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from ai_analyst.main import app


client = TestClient(app)


def _mock_backend_response(payload, status_code=200):
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = payload
    return response


def test_analyze_indicator_uses_backend_and_returns_analysis():
    indicator = {
        "id": 1,
        "indicator_type": "IP",
        "value": "192.0.2.1",
        "severity": "high",
        "source": "unit-test",
        "confidence": 90,
        "tags": ["demo"],
        "threat_actor": None,
    }
    backend_client = MagicMock()
    backend_client.__enter__.return_value = backend_client
    backend_client.__exit__.return_value = False
    backend_client.get.return_value = _mock_backend_response(indicator)

    with patch("ai_analyst.service.httpx.Client", return_value=backend_client):
        response = client.post("/analyze", json={"indicator_id": 1})

    assert response.status_code == 200
    assert response.json()["value"] == "192.0.2.1"
    assert "mock analysis" in response.json()["analysis"]


def test_generate_report_counts_only_active_indicators():
    indicators = [
        {
            "id": 1,
            "indicator_type": "IP",
            "value": "192.0.2.1",
            "severity": "high",
            "source": "unit-test",
            "confidence": 90,
            "tags": [],
            "threat_actor": None,
            "is_active": True,
        },
        {
            "id": 2,
            "indicator_type": "Domain",
            "value": "inactive.example",
            "severity": "low",
            "source": "unit-test",
            "confidence": 30,
            "tags": [],
            "threat_actor": None,
            "is_active": False,
        },
    ]
    backend_client = MagicMock()
    backend_client.__enter__.return_value = backend_client
    backend_client.__exit__.return_value = False
    backend_client.get.return_value = _mock_backend_response(indicators)

    with patch("ai_analyst.service.httpx.Client", return_value=backend_client):
        response = client.post("/report")

    assert response.status_code == 200
    assert response.json()["total_indicators"] == 1
