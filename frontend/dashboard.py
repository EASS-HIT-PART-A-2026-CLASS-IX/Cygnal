from __future__ import annotations

import streamlit as st

from frontend.components.layout import render_sidebar_brand, render_user_card
from frontend.state import initialize_session, logout
from frontend.styles import apply_global_styles
from frontend.views import (
    add_indicator,
    administration,
    ai_analyst,
    dashboard,
    indicators,
    login,
    reports,
    search,
    settings,
)


st.set_page_config(
    page_title="Cygnal",
    page_icon=":material/security:",
    layout="wide",
    initial_sidebar_state="expanded",
)

initialize_session()
apply_global_styles()

if not st.session_state.access_token:
    login.render()
    st.stop()

render_sidebar_brand()

pages = {
    "Workspace": [
        st.Page(dashboard.render, title="Threat Feed", icon=":material/dashboard:", url_path="dashboard", default=True),
        st.Page(
            add_indicator.render,
            title="Add Indicator",
            icon=":material/add_circle:",
            url_path="add-indicator",
        ),
        st.Page(indicators.render, title="Manage Indicators", icon=":material/list_alt:", url_path="indicators"),
        st.Page(search.render, title="Search & Export", icon=":material/manage_search:", url_path="search"),
    ],
    "Intelligence": [
        st.Page(ai_analyst.render, title="IOC Enrichment", icon=":material/troubleshoot:", url_path="enrichment"),
        st.Page(reports.render, title="Reports", icon=":material/assessment:", url_path="reports"),
    ],
    "System": [
        st.Page(
            administration.render,
            title="Administration",
            icon=":material/admin_panel_settings:",
            url_path="administration",
        ),
        st.Page(settings.render, title="Settings", icon=":material/settings:", url_path="settings"),
    ],
}

navigation = st.navigation(pages, position="sidebar", expanded=True)

with st.sidebar:
    st.divider()
    render_user_card()
    if st.button("Sign out", icon=":material/logout:", width="stretch"):
        logout()

navigation.run()
