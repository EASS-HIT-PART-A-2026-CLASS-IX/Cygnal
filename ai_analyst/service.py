from __future__ import annotations

from datetime import datetime, timezone
import json

import httpx

from ai_analyst.config import settings


SEVERITY_BASE = {"low": 20, "medium": 45, "high": 68, "critical": 85}
RISKY_TAG_WEIGHTS = {
    "ransomware": 8,
    "c2": 8,
    "command-and-control": 8,
    "credential-theft": 7,
    "phishing": 6,
    "malware": 6,
    "botnet": 6,
    "tor-exit-node": 4,
    "scanning": 3,
}
TYPE_ANALYSIS = {
    "IP": "Network address IOC. Validate ownership, hosting, geolocation, and recent connection telemetry.",
    "Domain": "Domain IOC. Review DNS history, registration age, certificate data, and related subdomains.",
    "URL": "URL IOC. Preserve the full path, inspect redirects safely, and search proxy or web telemetry.",
    "Hash": "File-hash IOC. Identify the hash algorithm and search endpoint, sandbox, and malware telemetry.",
    "Email": "Email IOC. Review sender authentication, message headers, recipients, and related campaign artifacts.",
}


def get_indicator(indicator_id: int) -> dict:
    with httpx.Client() as client:
        response = client.get(f"{settings.backend_url}/indicators/{indicator_id}")
        response.raise_for_status()
        return response.json()


def get_indicators() -> list[dict]:
    with httpx.Client() as client:
        response = client.get(f"{settings.backend_url}/indicators", params={"limit": 100})
        response.raise_for_status()
        return response.json()


def _parse_timestamp(value: str | datetime) -> datetime:
    if isinstance(value, datetime):
        parsed = value
    else:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _risk_level(score: int) -> str:
    if score >= 85:
        return "critical"
    if score >= 65:
        return "high"
    if score >= 40:
        return "medium"
    return "low"


def _recommended_actions(indicator: dict, risk_level: str) -> list[str]:
    value = indicator["value"]
    actions = [
        f"Search SIEM and endpoint telemetry for occurrences of {value}.",
        "Validate the indicator against at least one independent source before broad blocking.",
    ]
    if risk_level in {"critical", "high"}:
        actions.insert(0, "Prioritize triage and contain confirmed affected assets.")
    if indicator["indicator_type"] == "IP":
        actions.append("Review firewall, DNS, proxy, and authentication logs for traffic to or from this IP.")
    elif indicator["indicator_type"] == "Domain":
        actions.append("Review passive DNS, registration, certificate, and resolver telemetry for this domain.")
    elif indicator["indicator_type"] == "URL":
        actions.append("Inspect the URL only in an isolated analysis environment and review proxy logs.")
    elif indicator["indicator_type"] == "Hash":
        actions.append("Hunt for the hash across endpoint and malware-analysis telemetry.")
    elif indicator["indicator_type"] == "Email":
        actions.append("Review mail headers, sender authentication, recipients, and campaign similarity.")
    return actions


def build_deterministic_analysis(indicator: dict, indicators: list[dict]) -> dict:
    severity = str(indicator["severity"]).lower()
    confidence = int(indicator["confidence"])
    tags = {str(tag).casefold() for tag in indicator.get("tags", [])}

    base_score = SEVERITY_BASE[severity]
    confidence_adjustment = round((confidence - 50) * 0.2)
    active_adjustment = 4 if indicator.get("is_active") else -12
    tag_adjustment = min(sum(RISKY_TAG_WEIGHTS.get(tag, 0) for tag in tags), 15)
    score = max(0, min(100, base_score + confidence_adjustment + active_adjustment + tag_adjustment))
    level = _risk_level(score)

    matches = [
        item
        for item in indicators
        if item.get("indicator_type") == indicator.get("indicator_type")
        and str(item.get("value", "")).casefold() == str(indicator["value"]).casefold()
    ]
    first_seen = min(
        (_parse_timestamp(item["created_at"]) for item in matches if item.get("created_at")),
        default=_parse_timestamp(indicator["created_at"]),
    )
    age_days = max(0, (datetime.now(timezone.utc) - first_seen).days)

    reasoning = [
        f"{severity.title()} severity contributes a baseline score of {base_score}.",
        f"Source confidence is {confidence}%, adjusting the score by {confidence_adjustment:+d}.",
        (
            f"Risk-relevant tags add {tag_adjustment} points: {', '.join(sorted(tags))}."
            if tag_adjustment
            else "No configured high-risk tags increased the score."
        ),
        (
            f"The indicator is active and appears in {len(matches)} matching record(s)."
            if indicator.get("is_active")
            else "The indicator is inactive, reducing immediate operational priority."
        ),
    ]
    source = str(indicator.get("source") or "Unknown")
    source_context = (
        f"Reported by {source} with {confidence}% source confidence. "
        "Cygnal does not treat a single source as independent confirmation."
    )
    summary = (
        f"{level.title()}-risk {indicator['indicator_type']} indicator with a score of {score}/100. "
        f"Prioritize according to asset exposure and corroborating telemetry."
    )
    analysis_confidence = max(0, min(100, round(confidence * 0.8 + (10 if source != "Unknown" else 0))))

    return {
        "indicator_id": indicator["id"],
        "value": indicator["value"],
        "indicator_type": indicator["indicator_type"],
        "risk_score": score,
        "risk_level": level,
        "confidence": analysis_confidence,
        "summary": summary,
        "reasoning": reasoning,
        "recommended_actions": _recommended_actions(indicator, level),
        "type_analysis": TYPE_ANALYSIS[indicator["indicator_type"]],
        "source_context": source_context,
        "historical_context": {
            "first_seen": first_seen,
            "age_days": age_days,
            "is_active": bool(indicator.get("is_active")),
            "matching_records": len(matches),
        },
        "analysis_mode": "deterministic",
        "local_model_explanation": None,
    }


def add_optional_ollama_explanation(analysis: dict) -> dict:
    if not settings.ollama_base_url:
        return analysis
    prompt = (
        "You are a defensive cyber threat intelligence analyst. Explain the following deterministic "
        "assessment in no more than 120 words. Do not invent reputation data or claim external lookups.\n"
        + json.dumps(analysis, default=str)
    )
    try:
        response = httpx.post(
            f"{settings.ollama_base_url.rstrip('/')}/api/generate",
            json={"model": settings.ollama_model, "prompt": prompt, "stream": False},
            timeout=settings.ollama_timeout_seconds,
        )
        response.raise_for_status()
        explanation = str(response.json()["response"]).strip()
    except (httpx.HTTPError, KeyError, TypeError, ValueError):
        return analysis
    if explanation:
        analysis = {**analysis, "analysis_mode": "deterministic+ollama", "local_model_explanation": explanation}
    return analysis


def build_report(indicators: list[dict]) -> dict:
    analyses = [build_deterministic_analysis(indicator, indicators) for indicator in indicators]
    critical = sum(item["risk_level"] == "critical" for item in analyses)
    high_risk = sum(item["risk_level"] in {"critical", "high"} for item in analyses)
    average = round(sum(item["risk_score"] for item in analyses) / len(analyses)) if analyses else 0
    prioritized = sorted(analyses, key=lambda item: item["risk_score"], reverse=True)[:5]
    lines = [
        "# Cygnal Threat Intelligence Summary",
        "",
        f"- Active indicators analyzed: {len(analyses)}",
        f"- Critical assessments: {critical}",
        f"- High-risk or critical assessments: {high_risk}",
        f"- Average deterministic risk score: {average}/100",
        "",
        "## Highest-priority indicators",
    ]
    lines.extend(
        f"- **{item['risk_score']}/100** [{item['indicator_type']}] `{item['value']}` - {item['summary']}"
        for item in prioritized
    )
    return {
        "total_indicators": len(analyses),
        "report": "\n".join(lines),
        "critical_indicators": critical,
        "high_risk_indicators": high_risk,
        "average_risk_score": average,
        "analysis_mode": "deterministic",
    }
