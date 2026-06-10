from __future__ import annotations

import streamlit as st

from frontend.api.client import analyze_indicator_ai
from frontend.components.layout import page_header
from frontend.services.indicators import load_indicators


def render() -> None:
    page_header(
        "AI Analyst",
        "Generate a concise risk assessment and response recommendation for a selected IOC.",
        "Assisted analysis",
    )
    indicators = load_indicators()
    if not indicators:
        st.info("No indicators are available for analysis.")
        return

    options = {
        f"#{item['id']}  [{item['indicator_type']}]  {item['value']}": item
        for item in indicators
    }
    selected = st.selectbox("Indicator to analyze", list(options))
    item = options[selected]

    left, right = st.columns([1, 1.6], gap="large")
    with left:
        with st.container(border=True):
            st.caption("Selected intelligence record")
            st.markdown(f"### `{item['value']}`")
            st.write(f"**Type:** {item['indicator_type']}")
            st.write(f"**Severity:** {item['severity'].title()}")
            st.write(f"**Confidence:** {item['confidence']}%")
            st.write(f"**Source:** {item['source']}")
            st.write(f"**Tags:** {', '.join(item.get('tags') or []) or 'None'}")

    with right:
        st.subheader("Analyst assessment")
        if st.button("Analyze indicator", type="primary", icon=":material/psychology:", width="stretch"):
            with st.spinner("Generating assessment..."):
                try:
                    result = analyze_indicator_ai(item["id"])
                    st.markdown(result["analysis"])
                except Exception as exc:
                    st.error(f"Analysis failed: {exc}")
        else:
            st.info("Run the analyst to generate risk context and recommended actions.")
