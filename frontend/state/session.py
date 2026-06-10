from __future__ import annotations

import streamlit as st

from frontend.api.client import get_current_user, login


def initialize_session() -> None:
    """Initialize authentication and display preferences for this session."""
    st.session_state.setdefault("access_token", None)
    st.session_state.setdefault("current_user", None)


def authenticate(username: str, password: str) -> None:
    """Authenticate and persist the validated user identity for this session."""
    token = login(username.strip(), password)
    user = get_current_user(token)
    st.session_state.access_token = token
    st.session_state.current_user = user


def logout() -> None:
    """Clear authentication state and return to the dedicated login screen."""
    st.session_state.access_token = None
    st.session_state.current_user = None
    st.rerun()
