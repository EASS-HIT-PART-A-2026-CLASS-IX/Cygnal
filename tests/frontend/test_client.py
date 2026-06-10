from unittest.mock import patch, MagicMock
from frontend.api.client import (
    create_indicator,
    deactivate_indicator,
    delete_indicator,
    get_current_user,
    list_indicators,
    login,
)
from frontend.services.indicators import filter_indicators


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

    with patch("frontend.api.client._client") as mock_client:
        mock_client.return_value.get.return_value = mock_response
        result = list_indicators()
        assert isinstance(result, list)
        assert result[0]["value"] == "1.1.1.1"


def test_list_indicators_sends_filters():
    mock_response = MagicMock()
    mock_response.json.return_value = []

    with patch("frontend.api.client._client") as mock_client:
        mock_client.return_value.get.return_value = mock_response

        list_indicators(indicator_type="IP", severity="high")

        mock_client.return_value.get.assert_called_once_with(
            "/indicators",
            params={"indicator_type": "IP", "severity": "high"},
        )


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

    with patch("frontend.api.client._client") as mock_client:
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

    with patch("frontend.api.client._client") as mock_client:
        mock_client.return_value.delete.return_value = mock_response
        delete_indicator(1, "test-token")
        mock_client.return_value.delete.assert_called_once_with(
            "/indicators/1",
            headers={"Authorization": "Bearer test-token"},
        )


def test_login_returns_access_token():
    mock_response = MagicMock()
    mock_response.json.return_value = {"access_token": "test-token", "token_type": "bearer"}

    with patch("frontend.api.client._client") as mock_client:
        mock_client.return_value.post.return_value = mock_response

        token = login("analyst", "analyst123")

        assert token == "test-token"
        mock_client.return_value.post.assert_called_once_with(
            "/auth/login",
            data={"username": "analyst", "password": "analyst123"},
        )
        mock_response.raise_for_status.assert_called_once()


def test_get_current_user_sends_token():
    mock_response = MagicMock()
    mock_response.json.return_value = {"username": "analyst", "role": "analyst"}

    with patch("frontend.api.client._client") as mock_client:
        mock_client.return_value.get.return_value = mock_response

        user = get_current_user("test-token")

        assert user["role"] == "analyst"
        mock_client.return_value.get.assert_called_once_with(
            "/auth/me",
            headers={"Authorization": "Bearer test-token"},
        )


def test_deactivate_indicator_sends_admin_token():
    mock_response = MagicMock()

    with patch("frontend.api.client._client") as mock_client:
        mock_client.return_value.post.return_value = mock_response

        deactivate_indicator(7, "admin-token")

        mock_client.return_value.post.assert_called_once_with(
            "/indicators/7/deactivate",
            headers={"Authorization": "Bearer admin-token"},
        )
        mock_response.raise_for_status.assert_called_once()


def test_filter_indicators_searches_tags_and_status():
    indicators = [
        {
            "indicator_type": "IP",
            "severity": "high",
            "value": "192.0.2.1",
            "source": "unit-test",
            "threat_actor": None,
            "tags": ["ransomware"],
            "is_active": True,
        },
        {
            "indicator_type": "Domain",
            "severity": "low",
            "value": "inactive.example",
            "source": "unit-test",
            "threat_actor": None,
            "tags": [],
            "is_active": False,
        },
    ]

    result = filter_indicators(indicators, severity="high", query="RANSOM", active_only=True)

    assert result == [indicators[0]]
