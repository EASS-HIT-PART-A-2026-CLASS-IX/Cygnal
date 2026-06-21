from __future__ import annotations

import streamlit as st

from frontend.api.client import deactivate_indicator, delete_indicator
from frontend.components.layout import page_header
from frontend.services.indicators import load_indicators, refresh_indicators


def render() -> None:
    st.markdown(
        """
        <style>
            .st-key-delete_permanently button {
                background: linear-gradient(135deg, #b91c1c, #dc2626) !important;
                border-color: #ef4444 !important;
            }
            .st-key-delete_permanently button:hover {
                background: linear-gradient(135deg, #991b1b, #b91c1c) !important;
                border-color: #f87171 !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
    page_header(
        "Administration",
        "Perform protected lifecycle actions and review the permissions of the current session.",
        "Protected operations",
    )
    indicators = load_indicators()
    user = st.session_state.current_user or {}

    role_col, access_col = st.columns(2)
    role_col.metric("Authenticated user", user.get("username", "Unknown"))
    access_col.metric("Access role", user.get("role", "unknown").title())

    if not indicators:
        st.info("There are no indicators to administer.")
        return

    options = {f"#{item['id']}  [{item['indicator_type']}]  {item['value']}": item for item in indicators}
    selected = st.selectbox("Select indicator", list(options))
    item = options[selected]

    deactivate_col, delete_col = st.columns(2, gap="large")
    with deactivate_col:
        with st.container(border=True):
            st.subheader("Deactivate indicator")
            st.caption("Admin-only action. The record remains available for audit and reporting.")
            if user.get("role") != "admin":
                st.info("Your session does not have the admin role.")
            if st.button(
                "Deactivate",
                icon=":material/block:",
                width="stretch",
                disabled=user.get("role") != "admin" or not item["is_active"],
            ):
                try:
                    deactivate_indicator(item["id"], st.session_state.access_token)
                    refresh_indicators()
                    st.success("Indicator deactivated.")
                except Exception as exc:
                    st.error(f"Deactivation failed: {exc}")

    with delete_col:
        with st.container(border=True):
            st.subheader("Delete indicator")
            st.caption("Authenticated destructive action. This permanently removes the record.")
            confirm = st.checkbox("I understand this action is permanent", key="confirm_delete")
            if st.button(
                "Delete permanently",
                type="primary",
                icon=":material/delete_forever:",
                width="stretch",
                disabled=not confirm,
                key="delete_permanently",
            ):
                try:
                    delete_indicator(item["id"], st.session_state.access_token)
                    refresh_indicators()
                    st.success("Indicator deleted.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Delete failed: {exc}")
