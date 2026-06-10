import httpx

from ai_analyst.config import settings


def ask_claude(prompt: str) -> str:
    if not settings.anthropic_api_key:
        return "⚠️ No ANTHROPIC_API_KEY set – mock analysis returned."
    response = httpx.post(
        "https://api.anthropic.com/v1/messages",
        headers={"x-api-key": settings.anthropic_api_key, "anthropic-version": "2023-06-01"},
        json={"model": settings.anthropic_model, "max_tokens": 1000, "messages": [{"role": "user", "content": prompt}]},
        timeout=30.0,
    )
    response.raise_for_status()
    return response.json()["content"][0]["text"]


def get_indicator(indicator_id: int) -> dict:
    with httpx.Client() as client:
        response = client.get(f"{settings.backend_url}/indicators/{indicator_id}")
        response.raise_for_status()
        return response.json()


def get_indicators() -> list[dict]:
    with httpx.Client() as client:
        response = client.get(f"{settings.backend_url}/indicators")
        response.raise_for_status()
        return response.json()


def build_analysis_prompt(indicator: dict) -> str:
    return f"""Analyze this cybersecurity threat indicator and recommend an action:
Type: {indicator['indicator_type']}
Value: {indicator['value']}
Severity: {indicator['severity']}
Source: {indicator['source']}
Confidence: {indicator['confidence']}%
Tags: {', '.join(indicator.get('tags', []))}
Threat Actor: {indicator.get('threat_actor') or 'Unknown'}"""


def build_report_prompt(indicators: list[dict]) -> str:
    summary = "\n".join(
        f"- [{item['indicator_type']}] {item['value']} | severity={item['severity']} | confidence={item['confidence']}%"
        for item in indicators
    )
    return f"Generate a concise professional threat intelligence report from these active IOCs:\n{summary}"
