from typing import Any

import streamlit as st

from frontend.api.client import list_indicators


@st.cache_data(ttl=30)
def cached_indicators() -> list[dict[str, Any]]:
    return list_indicators()


def load_indicators() -> list[dict[str, Any]]:
    try:
        return cached_indicators()
    except Exception as exc:
        st.error(f"Cannot connect to the Cygnal API: {exc}")
        st.info("Verify that the API service is running and healthy.")
        st.stop()
        raise RuntimeError("Streamlit execution should have stopped") from exc


def refresh_indicators() -> None:
    cached_indicators.clear()


def filter_indicators(
    indicators: list[dict[str, Any]],
    indicator_type: str = "All",
    severity: str = "All",
    query: str = "",
    active_only: bool = False,
) -> list[dict[str, Any]]:
    filtered = indicators
    if indicator_type != "All":
        filtered = [item for item in filtered if item["indicator_type"] == indicator_type]
    if severity != "All":
        filtered = [item for item in filtered if item["severity"] == severity]
    if active_only:
        filtered = [item for item in filtered if item.get("is_active")]
    if query:
        normalized = query.casefold()
        filtered = [
            item
            for item in filtered
            if normalized in item.get("value", "").casefold()
            or normalized in item.get("source", "").casefold()
            or normalized in (item.get("threat_actor") or "").casefold()
            or any(normalized in tag.casefold() for tag in item.get("tags", []))
        ]
    return filtered
