from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from frontend.components.indicator_table import render_indicator_table
from frontend.components.layout import page_header
from frontend.services.indicators import load_indicators
from frontend.styles import CHART_COLORS


def render() -> None:
    page_header(
        "Intelligence Overview",
        "Monitor the current IOC landscape and focus attention on the highest-risk signals.",
        "Operational dashboard",
    )
    indicators = load_indicators()

    total = len(indicators)
    active = sum(1 for item in indicators if item["is_active"])
    critical = sum(1 for item in indicators if item["severity"] == "critical")
    high = sum(1 for item in indicators if item["severity"] == "high")
    average_confidence = round(sum(item["confidence"] for item in indicators) / total) if total else 0

    columns = st.columns(5)
    columns[0].metric("Total IOCs", total)
    columns[1].metric("Active", active)
    columns[2].metric("Critical", critical)
    columns[3].metric("High", high)
    columns[4].metric("Avg. confidence", f"{average_confidence}%")

    if not indicators:
        st.info("No indicators are available yet.")
        return

    frame = pd.DataFrame(indicators)
    chart_left, chart_right = st.columns(2, gap="large")
    with chart_left:
        st.subheader("Severity distribution")
        severity_counts = frame["severity"].value_counts().rename_axis("severity").reset_index(name="count")
        figure = px.pie(
            severity_counts,
            names="severity",
            values="count",
            color="severity",
            color_discrete_map=CHART_COLORS,
            hole=0.62,
        )
        figure.update_layout(
            margin=dict(t=20, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)",
            legend_title_text="",
        )
        st.plotly_chart(figure, width="stretch")

    with chart_right:
        st.subheader("Indicator types")
        type_counts = frame["indicator_type"].value_counts().rename_axis("type").reset_index(name="count")
        figure = px.bar(
            type_counts,
            x="type",
            y="count",
            color="type",
            color_discrete_map=CHART_COLORS,
            text="count",
        )
        figure.update_layout(
            margin=dict(t=20, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            xaxis_title="",
            yaxis_title="Count",
        )
        st.plotly_chart(figure, width="stretch")

    st.subheader("Priority indicators")
    priority = [
        item for item in indicators
        if item["is_active"] and item["severity"] in {"critical", "high"}
    ][:8]
    render_indicator_table(priority, "No active high-priority indicators.")
