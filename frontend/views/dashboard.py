from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone

import pandas as pd
import plotly.express as px
import streamlit as st

from frontend.api.client import delete_indicator, update_indicator
from frontend.components.indicator_table import render_indicator_table
from frontend.components.layout import page_header
from frontend.services.indicators import filter_indicators, load_indicators, refresh_indicators
from frontend.styles import CHART_COLORS, INDICATOR_TYPES, SEVERITY_LEVELS


SEVERITIES = ["low", "medium", "high", "critical"]


def _is_today(timestamp: str) -> bool:
    parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).date() == datetime.now(timezone.utc).date()


def render() -> None:
    page_header(
        "Threat Intelligence Feed",
        "Search, prioritize, and act on the indicators currently tracked by Cygnal.",
        "Analyst operations",
    )
    indicators = load_indicators()
    active = [item for item in indicators if item["is_active"]]
    critical = sum(item["severity"] == "critical" for item in active)
    high_risk = sum(item["severity"] in {"critical", "high"} for item in active)
    added_today = sum(_is_today(item["created_at"]) for item in indicators)
    average_confidence = round(sum(item["confidence"] for item in indicators) / len(indicators)) if indicators else 0
    source_counts = Counter(item["source"] for item in active)
    most_active_source = source_counts.most_common(1)[0][0] if source_counts else "None"

    columns = st.columns(6)
    columns[0].metric("Total IOCs", len(indicators))
    columns[1].metric("Critical", critical)
    columns[2].metric("High risk", high_risk)
    columns[3].metric("Added today", added_today)
    columns[4].metric("Top source", most_active_source)
    columns[5].metric("Avg. confidence", f"{average_confidence}%")

    if not indicators:
        st.info("No indicators are available yet. Use Add Indicator to create the first record.")
        return

    with st.container(border=True):
        first, second, third = st.columns([1, 1, 2])
        indicator_type = first.selectbox("Indicator type", INDICATOR_TYPES, key="feed_type")
        severity = second.selectbox("Severity", SEVERITY_LEVELS, key="feed_severity")
        query = third.text_input(
            "Search the feed",
            placeholder="IP, domain, URL, hash, email, source, tag, or actor",
            key="feed_query",
        )
        active_only = st.toggle("Active indicators only", value=True, key="feed_active")

    filtered = filter_indicators(indicators, indicator_type, severity, query, active_only)
    st.subheader("Current threat feed")
    st.caption(f"{len(filtered)} of {len(indicators)} indicators shown")
    render_indicator_table(filtered, "No indicators match the current feed filters.")

    if filtered:
        _render_quick_actions(filtered)

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


def _render_quick_actions(indicators: list[dict]) -> None:
    with st.expander("Feed quick actions", icon=":material/edit_square:"):
        options = {f"#{item['id']} [{item['indicator_type']}] {item['value']}": item for item in indicators}
        selected = st.selectbox("Selected indicator", list(options), key="feed_action_indicator")
        item = options[selected]

        with st.form("feed_quick_action_form"):
            first, second, third = st.columns(3)
            severity = first.selectbox(
                "Severity",
                SEVERITIES,
                index=SEVERITIES.index(item["severity"]),
                key="feed_action_severity",
            )
            confidence = second.slider(
                "Confidence",
                0,
                100,
                item["confidence"],
                key="feed_action_confidence",
            )
            is_active = third.checkbox("Active", value=item["is_active"], key="feed_action_active")
            confirm_delete = st.checkbox("Confirm permanent deletion", key="feed_confirm_delete")
            save, delete = st.columns(2)
            save_clicked = save.form_submit_button("Save assessment", type="primary", width="stretch")
            delete_clicked = delete.form_submit_button(
                "Delete indicator",
                width="stretch",
                disabled=not confirm_delete,
            )

        try:
            if save_clicked:
                update_indicator(
                    item["id"],
                    severity=severity,
                    source=item["source"],
                    confidence=confidence,
                    tags=item.get("tags") or [],
                    threat_actor=item.get("threat_actor"),
                    is_active=is_active,
                )
                refresh_indicators()
                st.success("Indicator assessment updated.")
                st.rerun()
            if delete_clicked:
                delete_indicator(item["id"], st.session_state.access_token)
                refresh_indicators()
                st.success("Indicator deleted.")
                st.rerun()
        except Exception as exc:
            st.error(f"Action failed: {exc}")
