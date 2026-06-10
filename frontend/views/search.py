from __future__ import annotations

import pandas as pd
import streamlit as st

from frontend.components.indicator_table import render_indicator_table
from frontend.components.layout import page_header
from frontend.services.indicators import filter_indicators, load_indicators
from frontend.styles import INDICATOR_TYPES, SEVERITY_LEVELS


def render() -> None:
    page_header(
        "Search & Filters",
        "Pivot across IOC values, sources, tags, attribution, severity, and activity state.",
        "Investigation workspace",
    )
    indicators = load_indicators()

    with st.container(border=True):
        first, second, third = st.columns([1, 1, 2])
        indicator_type = first.selectbox("Indicator type", INDICATOR_TYPES)
        severity = second.selectbox("Severity", SEVERITY_LEVELS)
        query = third.text_input("Search", placeholder="Value, source, tag, or threat actor")
        active_only = st.toggle("Active indicators only")

    filtered = filter_indicators(indicators, indicator_type, severity, query, active_only)
    metric_left, metric_right = st.columns(2)
    metric_left.metric("Matching indicators", len(filtered))
    metric_right.metric("Search coverage", f"{round((len(filtered) / len(indicators)) * 100) if indicators else 0}%")

    render_indicator_table(filtered, "No indicators match these filters.")
    if filtered:
        st.download_button(
            "Export search results",
            data=pd.DataFrame(filtered).to_csv(index=False),
            file_name="cygnal_search_results.csv",
            mime="text/csv",
            icon=":material/download:",
        )
