from __future__ import annotations

import pandas as pd
import streamlit as st

from frontend.api.client import generate_report
from frontend.components.layout import page_header
from frontend.services.indicators import load_indicators


def render() -> None:
    page_header(
        "Reports",
        "Create executive threat summaries and export the current intelligence dataset.",
        "Intelligence reporting",
    )
    indicators = load_indicators()
    active = [item for item in indicators if item["is_active"]]

    summary, export = st.columns(2, gap="large")
    with summary:
        st.subheader("AI threat summary")
        st.caption(f"Generate an actionable report from {len(active)} active indicators.")
        if st.button("Generate report", type="primary", icon=":material/assessment:", width="stretch"):
            with st.spinner("Generating threat report..."):
                try:
                    result = generate_report()
                    st.session_state.generated_report = result["report"]
                    st.session_state.report_total = result["total_indicators"]
                except Exception as exc:
                    st.error(f"Report generation failed: {exc}")

    with export:
        st.subheader("Dataset export")
        st.caption("Download the complete IOC dataset for offline investigation or sharing.")
        st.download_button(
            "Download all indicators as CSV",
            data=pd.DataFrame(indicators).to_csv(index=False),
            file_name="cygnal_indicators.csv",
            mime="text/csv",
            icon=":material/download:",
            width="stretch",
            disabled=not indicators,
        )

    if st.session_state.get("generated_report"):
        st.divider()
        st.caption(f"Report based on {st.session_state.report_total} active indicators")
        st.markdown(st.session_state.generated_report)
