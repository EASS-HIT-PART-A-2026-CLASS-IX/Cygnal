from __future__ import annotations

import pandas as pd
import streamlit as st

from frontend.api.client import generate_report
from frontend.components.layout import page_header
from frontend.services.indicators import load_indicators


def render() -> None:
    page_header(
        "Reports",
        "Create a deterministic threat summary and export the current intelligence dataset.",
        "Intelligence reporting",
    )
    indicators = load_indicators()
    active = [item for item in indicators if item["is_active"]]

    summary, export = st.columns(2, gap="large")
    with summary:
        st.subheader("Threat intelligence summary")
        st.caption(f"Generate an offline report from {len(active)} active indicators.")
        if st.button("Generate report", type="primary", icon=":material/assessment:", width="stretch"):
            with st.spinner("Calculating threat report..."):
                try:
                    st.session_state.generated_report = generate_report()
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

    result = st.session_state.get("generated_report")
    if result:
        st.divider()
        total, high_risk, average = st.columns(3)
        total.metric("Analyzed", result["total_indicators"])
        high_risk.metric("High risk", result["high_risk_indicators"])
        average.metric("Average risk", f"{result['average_risk_score']}/100")
        st.markdown(result["report"])
