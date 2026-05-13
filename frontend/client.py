from __future__ import annotations

from functools import lru_cache
from typing import Any

import httpx
from pydantic_settings import BaseSettings, SettingsConfigDict


class UISettings(BaseSettings):
    api_base_url: str = "http://127.0.0.1:8000"
    trace_id: str = "ui-streamlit"

    model_config = SettingsConfigDict(
        env_prefix="CYGNAL_",
        env_file=".env",
        extra="ignore"
    )


settings = UISettings()


@lru_cache(maxsize=1)
def _client() -> httpx.Client:
    """יצירת קליינט HTTP יחיד לשימוש חוזר (Session 06)."""
    return httpx.Client(
        base_url=settings.api_base_url,
        headers={"X-Trace-Id": settings.trace_id},
        timeout=5.0,
    )


def list_indicators(
    *,
    indicator_type: str | None = None,
    severity: str | None = None,
) -> list[dict[str, Any]]:
    """שליפת רשימת אינדיקטורים עם תמיכה בסינון צד-שרת."""
    params = {}
    if indicator_type and indicator_type != "All":
        params["indicator_type"] = indicator_type
    if severity and severity != "All":
        params["severity"] = severity
        
    try:
        response = _client().get("/indicators", params=params or None)
        response.raise_for_status()
        return response.json()
    except httpx.RequestError as exc:
        # טיפול במקרה שהשרת לא זמין
        raise RuntimeError(f"Could not connect to API at {settings.api_base_url}") from exc


def create_indicator(
    *,
    indicator_type: str,
    value: str,
    severity: str,
    source: str,
    confidence: int,
    tags: list[str],
    threat_actor: str | None,
    is_active: bool,
) -> dict[str, Any]:
    """יצירת אינדיקטור חדש דרך ה-API."""
    payload = {
        "indicator_type": indicator_type,
        "value": value,
        "severity": severity,
        "source": source,
        "confidence": confidence,
        "tags": tags,
        "threat_actor": threat_actor,
        "is_active": is_active,
    }
    response = _client().post("/indicators", json=payload)
    response.raise_for_status()
    return response.json()


def delete_indicator(indicator_id: int) -> None:
    """מחיקת אינדיקטור לפי מזהה."""
    response = _client().delete(f"/indicators/{indicator_id}")
    response.raise_for_status()