from unittest.mock import patch

from streamlit.testing.v1 import AppTest


def test_authenticated_navigation_has_unique_pages():
    with (
        patch("frontend.state.session.login", return_value="test-token"),
        patch("frontend.state.session.get_current_user", return_value={"username": "analyst", "role": "analyst"}),
        patch("frontend.services.indicators.list_indicators", return_value=[]),
    ):
        app = AppTest.from_file("frontend/dashboard.py")
        app.run(timeout=30)
        app.text_input[0].set_value("analyst")
        app.text_input[1].set_value("analyst123")
        app.button[0].click()
        app.run(timeout=30)

    assert not app.exception
    assert app.session_state["current_user"]["role"] == "analyst"
