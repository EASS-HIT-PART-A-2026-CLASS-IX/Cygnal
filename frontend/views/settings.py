from __future__ import annotations

import streamlit as st

from frontend.api.config import settings
from frontend.components.layout import page_header
from frontend.services.indicators import refresh_indicators
from frontend.state import logout


def render() -> None:
    page_header(
        "Settings",
        "Review session context, service connectivity, and local dashboard behavior.",
        "Workspace configuration",
    )
    user = st.session_state.current_user or {}

    appearance_tab, session_tab, services_tab = st.tabs(["Appearance", "Session", "Services"])
    with appearance_tab:
        st.info(
            "Use the System, Light, or Dark selector in Streamlit's application menu. "
            "Cygnal follows the selected theme across every page and chart."
        )

    with session_tab:
        left, right = st.columns(2)
        left.metric("Username", user.get("username", "Unknown"))
        right.metric("Role", user.get("role", "unknown").title())
        st.info("The dashboard stores the JWT only in this Streamlit browser session.")
        if st.button("Sign out of Cygnal", icon=":material/logout:"):
            logout()

    with services_tab:
        st.text_input("API base URL", value=settings.api_base_url, disabled=True)
        st.text_input("AI analyst URL", value=settings.ai_analyst_url, disabled=True)
        st.text_input("Trace ID", value=settings.trace_id, disabled=True)
        if st.button("Clear indicator cache", icon=":material/refresh:"):
            refresh_indicators()
            st.success("Indicator cache cleared.")
