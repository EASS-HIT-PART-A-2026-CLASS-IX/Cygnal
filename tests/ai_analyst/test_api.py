from unittest.mock import MagicMock, patch

import httpx
from fastapi.testclient import TestClient

from ai_analyst.config import settings
from ai_analyst.main import app


client = TestClient(app)


INDICATOR = {
    "id": 1,
    "indicator_type": "IP",
    "value": "192.0.2.1",
    "severity": "high",
    "source": "unit-test",
    "confidence": 90,
    "tags": ["ransomware", "scanning"],
    "threat_actor": None,
    "is_active": True,
    "created_at": "2026-01-01T00:00:00Z",
}


def _response(payload, status_code=200):
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = payload
    response.raise_for_status.return_value = None
    return response


def _backend_client(*responses):
    backend = MagicMock()
    backend.__enter__.return_value = backend
    backend.__exit__.return_value = False
    backend.get.side_effect = list(responses)
    return backend


def test_health_describes_free_default_mode():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["default_mode"] == "deterministic"


def test_analyze_indicator_returns_structured_deterministic_analysis(monkeypatch):
    monkeypatch.setattr(settings, "ollama_base_url", "")
    backend = _backend_client(_response(INDICATOR), _response([INDICATOR]))

    with patch("ai_analyst.service.httpx.Client", return_value=backend):
        response = client.post("/analyze", json={"indicator_id": 1})

    assert response.status_code == 200
    payload = response.json()
    assert payload["indicator_type"] == "IP"
    assert 0 <= payload["risk_score"] <= 100
    assert payload["risk_level"] in {"low", "medium", "high", "critical"}
    assert payload["reasoning"]
    assert payload["recommended_actions"]
    assert payload["type_analysis"]
    assert payload["source_context"]
    assert payload["historical_context"]["matching_records"] == 1
    assert payload["analysis_mode"] == "deterministic"


def test_analyze_indicator_uses_optional_ollama(monkeypatch):
    monkeypatch.setattr(settings, "ollama_base_url", "http://ollama.test")
    backend = _backend_client(_response(INDICATOR), _response([INDICATOR]))
    ollama_response = _response({"response": "Local model explanation."})

    with (
        patch("ai_analyst.service.httpx.Client", return_value=backend),
        patch("ai_analyst.service.httpx.post", return_value=ollama_response),
    ):
        response = client.post("/analyze", json={"indicator_id": 1})

    assert response.status_code == 200
    assert response.json()["analysis_mode"] == "deterministic+ollama"
    assert response.json()["local_model_explanation"] == "Local model explanation."


def test_local_ai_unavailable_falls_back_to_deterministic(monkeypatch):
    monkeypatch.setattr(settings, "ollama_base_url", "http://127.0.0.1:11434")
    backend = _backend_client(_response(INDICATOR), _response([INDICATOR]))
    request = httpx.Request("POST", "http://127.0.0.1:11434/api/generate")

    with (
        patch("ai_analyst.service.httpx.Client", return_value=backend),
        patch(
            "ai_analyst.service.httpx.post",
            side_effect=httpx.ConnectError("offline", request=request),
        ),
    ):
        response = client.post("/analyze", json={"indicator_id": 1})

    assert response.status_code == 200
    assert response.json()["analysis_mode"] == "deterministic"
    assert response.json()["local_model_explanation"] is None


def test_analyze_rejects_invalid_indicator_id():
    response = client.post("/analyze", json={"indicator_id": 0})

    assert response.status_code == 422


def test_analyze_returns_not_found():
    response = httpx.Response(
        404,
        request=httpx.Request("GET", "http://backend/indicators/999"),
    )
    backend = MagicMock()
    backend.__enter__.return_value = backend
    backend.__exit__.return_value = False
    backend.get.side_effect = httpx.HTTPStatusError(
        "not found",
        request=response.request,
        response=response,
    )

    with patch("ai_analyst.service.httpx.Client", return_value=backend):
        result = client.post("/analyze", json={"indicator_id": 999})

    assert result.status_code == 404


def test_backend_failure_returns_502():
    response = httpx.Response(
        500,
        request=httpx.Request("GET", "http://backend/indicators/1"),
    )
    backend = MagicMock()
    backend.__enter__.return_value = backend
    backend.__exit__.return_value = False
    backend.get.side_effect = httpx.HTTPStatusError(
        "backend failed",
        request=response.request,
        response=response,
    )

    with patch("ai_analyst.service.httpx.Client", return_value=backend):
        result = client.post("/analyze", json={"indicator_id": 1})

    assert result.status_code == 502


def test_generate_report_returns_meaningful_metrics(monkeypatch):
    monkeypatch.setattr(settings, "ollama_base_url", "")
    inactive = {**INDICATOR, "id": 2, "value": "192.0.2.2", "is_active": False}
    backend = _backend_client(_response([INDICATOR, inactive]))

    with patch("ai_analyst.service.httpx.Client", return_value=backend):
        response = client.post("/report")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_indicators"] == 1
    assert payload["high_risk_indicators"] == 1
    assert payload["average_risk_score"] > 0
    assert "Highest-priority indicators" in payload["report"]
