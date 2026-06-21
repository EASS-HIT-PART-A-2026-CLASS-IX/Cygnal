from __future__ import annotations

import streamlit as st

from frontend.api.client import analyze_indicator_ai
from frontend.components.layout import page_header
from frontend.services.indicators import load_indicators


def render() -> None:
    page_header(
        "IOC Enrichment",
        "Generate a free, structured risk assessment with evidence and recommended analyst actions.",
        "Deterministic analysis",
    )
    indicators = load_indicators()
    if not indicators:
        st.info("No indicators are available for enrichment.")
        return

    options = {f"#{item['id']}  [{item['indicator_type']}]  {item['value']}": item for item in indicators}
    selected = st.selectbox("Indicator to enrich", list(options))
    item = options[selected]

    left, right = st.columns([1, 1.6], gap="large")
    with left:
        with st.container(border=True):
            st.caption("Selected intelligence record")
            st.markdown(f"### `{item['value']}`")
            st.write(f"**Type:** {item['indicator_type']}")
            st.write(f"**Severity:** {item['severity'].title()}")
            st.write(f"**Source confidence:** {item['confidence']}%")
            st.write(f"**Source:** {item['source']}")
            st.write(f"**Tags:** {', '.join(item.get('tags') or []) or 'None'}")
            st.write(f"**Threat actor:** {item.get('threat_actor') or 'Unknown'}")

    with right:
        st.subheader("Analyst assessment")
        st.caption("The default engine is deterministic and works offline. Ollama is optional.")
        if st.button("Enrich indicator", type="primary", icon=":material/troubleshoot:", width="stretch"):
            with st.spinner("Calculating evidence-based risk..."):
                try:
                    st.session_state.enrichment_result = analyze_indicator_ai(item["id"])
                except Exception as exc:
                    st.error(f"Enrichment failed: {exc}")

    result = st.session_state.get("enrichment_result")
    if not result or result.get("indicator_id") != item["id"]:
        st.info("Run enrichment to calculate risk, context, and response actions.")
        return

    st.divider()
    score, level, confidence, mode = st.columns(4)
    score.metric("Risk score", f"{result['risk_score']}/100")
    level.metric("Risk level", result["risk_level"].title())
    confidence.metric("Analysis confidence", f"{result['confidence']}%")
    mode.metric("Analysis mode", result["analysis_mode"])

    st.markdown(f"### {result['summary']}")
    context, history = st.columns(2, gap="large")
    with context:
        st.subheader("Context")
        st.write(result["type_analysis"])
        st.write(result["source_context"])
        if result.get("local_model_explanation"):
            st.info(result["local_model_explanation"])
    with history:
        historical = result["historical_context"]
        st.subheader("Historical context")
        st.write(f"**First seen:** {historical['first_seen']}")
        st.write(f"**Age:** {historical['age_days']} day(s)")
        st.write(f"**Matching records:** {historical['matching_records']}")
        st.write(f"**Current status:** {'Active' if historical['is_active'] else 'Inactive'}")

    reasoning, actions = st.columns(2, gap="large")
    with reasoning:
        st.subheader("Why this score")
        for reason in result["reasoning"]:
            st.markdown(f"- {reason}")
    with actions:
        st.subheader("Recommended actions")
        for action in result["recommended_actions"]:
            st.markdown(f"- {action}")
