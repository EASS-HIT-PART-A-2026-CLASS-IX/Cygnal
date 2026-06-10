from typing import Any

import pandas as pd
import streamlit as st


def indicator_dataframe(indicators: list[dict[str, Any]]) -> pd.DataFrame:
    if not indicators:
        return pd.DataFrame()
    frame = pd.DataFrame(indicators).copy()
    frame["tags"] = frame["tags"].map(lambda tags: ", ".join(tags) if tags else "-")
    frame["threat_actor"] = frame["threat_actor"].fillna("-")
    frame["status"] = frame["is_active"].map({True: "Active", False: "Inactive"})
    frame["severity"] = frame["severity"].str.title()
    frame = frame[["id", "indicator_type", "value", "severity", "source", "confidence", "tags", "threat_actor", "status"]]
    frame.columns = ["ID", "Type", "Value", "Severity", "Source", "Confidence", "Tags", "Threat Actor", "Status"]
    return frame


def render_indicator_table(indicators: list[dict[str, Any]], empty_message: str = "No indicators found.") -> None:
    frame = indicator_dataframe(indicators)
    if frame.empty:
        st.info(empty_message)
        return
    st.dataframe(
        frame,
        hide_index=True,
        width="stretch",
        height=min(560, 42 + len(frame) * 36),
        column_config={
            "Confidence": st.column_config.ProgressColumn("Confidence", min_value=0, max_value=100, format="%d%%"),
            "Status": st.column_config.TextColumn("Status"),
        },
    )
