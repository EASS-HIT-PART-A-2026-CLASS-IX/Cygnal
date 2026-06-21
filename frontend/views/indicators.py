from __future__ import annotations

import streamlit as st

from frontend.api.client import update_indicator
from frontend.components.indicator_table import render_indicator_table
from frontend.components.layout import page_header
from frontend.services.indicators import load_indicators, refresh_indicators


SEVERITIES = ["low", "medium", "high", "critical"]


def render() -> None:
    page_header(
        "Indicator Management",
        "Browse and maintain the intelligence records used across Cygnal.",
        "IOC lifecycle",
    )
    indicators = load_indicators()
    browse_tab, edit_tab = st.tabs(["Browse", "Edit indicator"])

    with browse_tab:
        top_left, top_right = st.columns([4, 1])
        top_left.caption(f"{len(indicators)} indicators currently stored")
        if top_right.button("Refresh", icon=":material/refresh:", width="stretch"):
            refresh_indicators()
            st.rerun()
        render_indicator_table(indicators)

    with edit_tab:
        _render_edit_form(indicators)


def _render_edit_form(indicators: list[dict]) -> None:
    if not indicators:
        st.info("Add an indicator before editing.")
        return
    options = {f"#{item['id']}  [{item['indicator_type']}]  {item['value']}": item for item in indicators}
    selected = st.selectbox("Select indicator", list(options))
    item = options[selected]

    with st.form("edit_indicator_form"):
        left, right = st.columns(2, gap="large")
        with left:
            severity = st.selectbox("Severity", SEVERITIES, index=SEVERITIES.index(item["severity"]))
            source = st.text_input("Source", value=item["source"])
            confidence = st.slider("Confidence", 0, 100, item["confidence"])
        with right:
            tags = st.text_input("Tags", value=", ".join(item.get("tags") or []))
            threat_actor = st.text_input("Threat actor", value=item.get("threat_actor") or "")
            is_active = st.checkbox("Active indicator", value=item["is_active"])
        submitted = st.form_submit_button("Save changes", type="primary", width="stretch")

    if submitted:
        if not source.strip():
            st.error("Source is required.")
            return
        try:
            update_indicator(
                item["id"],
                severity=severity,
                source=source.strip(),
                confidence=confidence,
                tags=[tag.strip() for tag in tags.split(",") if tag.strip()],
                threat_actor=threat_actor.strip() or None,
                is_active=is_active,
            )
            refresh_indicators()
            st.success("Indicator updated.")
        except Exception as exc:
            st.error(f"Update failed: {exc}")
