from unittest.mock import patch, MagicMock
from frontend.client import list_indicators, create_indicator, delete_indicator


def test_list_indicators_returns_list():
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "id": 1,
            "indicator_type": "IP",
            "value": "1.1.1.1",
            "severity": "high",
            "source": "test",
            "confidence": 80,
            "tags": ["ransomware"],
            "threat_actor": None,
            "is_active": True,
            "created_at": "2026-01-01T00:00:00"
        }
    ]
    mock_response.raise_for_status = MagicMock()

    with patch("frontend.client._client") as mock_client:
        mock_client.return_value.get.return_value = mock_response
        result = list_indicators()
        assert isinstance(result, list)
        assert result[0]["value"] == "1.1.1.1"


def test_create_indicator_returns_dict():
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "id": 2,
        "indicator_type": "Domain",
        "value": "evil.com",
        "severity": "critical",
        "source": "test",
        "confidence": 95,
        "tags": ["c2"],
        "threat_actor": "APT29",
        "is_active": True,
        "created_at": "2026-01-01T00:00:00"
    }
    mock_response.raise_for_status = MagicMock()

    with patch("frontend.client._client") as mock_client:
        mock_client.return_value.post.return_value = mock_response
        result = create_indicator(
            indicator_type="Domain",
            value="evil.com",
            severity="critical",
            source="test",
            confidence=95,
            tags=["c2"],
            threat_actor="APT29",
            is_active=True,
        )
        assert result["value"] == "evil.com"
        assert result["id"] == 2


def test_delete_indicator_calls_api():
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()

    with patch("frontend.client._client") as mock_client:
        mock_client.return_value.delete.return_value = mock_response
        delete_indicator(1)
        mock_client.return_value.delete.assert_called_once_with("/indicators/1")