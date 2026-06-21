from __future__ import annotations

import streamlit as st

from backend.services.ioc_validation import validate_ioc_value
from frontend.api.client import create_indicator
from frontend.components.layout import page_header
from frontend.services.indicators import refresh_indicators


TYPES = ["IP", "Domain", "URL", "Hash", "Email"]
SEVERITIES = ["low", "medium", "high", "critical"]
EXAMPLES = {
    "IP": "203.0.113.42",
    "Domain": "malicious.example",
    "URL": "https://malicious.example/login",
    "Hash": "d41d8cd98f00b204e9800998ecf8427e",
    "Email": "sender@example.com",
}


def render() -> None:
    page_header(
        "Add Threat Indicator",
        "Create a validated intelligence record for investigation, enrichment, and reporting.",
        "IOC intake",
    )
    indicator_type = st.selectbox("Indicator type", TYPES, help="The selected type controls value validation.")

    with st.form("create_indicator_form"):
        left, right = st.columns(2, gap="large")
        with left:
            value = st.text_input("Indicator value", placeholder=EXAMPLES[indicator_type])
            severity = st.selectbox("Severity", SEVERITIES, index=1)
            source = st.text_input("Source", placeholder="e.g. AbuseIPDB, internal SOC")
        with right:
            confidence = st.slider("Source confidence", 0, 100, 50)
            tags_input = st.text_input("Tags", placeholder="ransomware, c2, phishing")
            threat_actor = st.text_input("Threat actor", placeholder="Optional attribution")
            is_active = st.checkbox("Active indicator", value=True)
        st.caption("Values are validated by IOC type before they are sent to the API.")
        submitted = st.form_submit_button("Create indicator", type="primary", width="stretch")

    if not submitted:
        return
    if not source.strip():
        st.error("Source is required.")
        return
    try:
        normalized_value = validate_ioc_value(indicator_type, value)
    except ValueError as exc:
        st.error(f"Invalid {indicator_type} indicator: {exc}")
        return

    try:
        created = create_indicator(
            indicator_type=indicator_type,
            value=normalized_value,
            severity=severity,
            source=source.strip(),
            confidence=confidence,
            tags=[tag.strip() for tag in tags_input.split(",") if tag.strip()],
            threat_actor=threat_actor.strip() or None,
            is_active=is_active,
        )
        refresh_indicators()
        st.success(f"Created [{created['indicator_type']}] {created['value']}")
    except Exception as exc:
        st.error(f"Create failed: {exc}")
