"""
AI Analyst microservice – analyzes IOCs and generates threat reports using Claude API.
Run with: uv run uvicorn ai_analyst.main:app --port 8001
"""

import os
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

app = FastAPI(title="Cygnal AI Analyst", version="1.0.0")


class AnalyzeRequest(BaseModel):
    indicator_id: int


class AnalyzeResponse(BaseModel):
    indicator_id: int
    value: str
    analysis: str


class ReportResponse(BaseModel):
    total_indicators: int
    report: str


def ask_claude(prompt: str) -> str:
    """שלח prompt ל-Claude API וקבל תשובה."""
    if not ANTHROPIC_API_KEY:
        return "⚠️ No ANTHROPIC_API_KEY set – mock analysis returned."

    response = httpx.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 1000,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=30.0,
    )
    response.raise_for_status()
    return response.json()["content"][0]["text"]


@app.get("/health", tags=["diagnostics"])
def health():
    return {"status": "ok", "app": "Cygnal AI Analyst"}


@app.post("/analyze", response_model=AnalyzeResponse, tags=["ai"])
def analyze_indicator(request: AnalyzeRequest):
    """נתח IOC בודד עם Claude."""
    with httpx.Client() as client:
        resp = client.get(f"{BACKEND_URL}/indicators/{request.indicator_id}")
        if resp.status_code == 404:
            raise HTTPException(status_code=404, detail="Indicator not found")
        resp.raise_for_status()
        indicator = resp.json()

    prompt = f"""You are a cybersecurity analyst. Analyze the following threat indicator and provide a brief assessment.

Indicator:
- Type: {indicator['indicator_type']}
- Value: {indicator['value']}
- Severity: {indicator['severity']}
- Source: {indicator['source']}
- Confidence: {indicator['confidence']}%
- Tags: {', '.join(indicator.get('tags', []))}
- Threat Actor: {indicator.get('threat_actor') or 'Unknown'}

Provide:
1. What this indicator likely represents
2. Potential risk level and impact
3. Recommended action (block / monitor / investigate)

Keep the response concise (3-5 sentences)."""

    analysis = ask_claude(prompt)

    return AnalyzeResponse(
        indicator_id=indicator["id"],
        value=indicator["value"],
        analysis=analysis,
    )


@app.get("/report", response_model=ReportResponse, tags=["ai"])
def generate_report():
    """צור דוח סיכום של כל ה-IOCs הפעילים."""
    with httpx.Client() as client:
        resp = client.get(f"{BACKEND_URL}/indicators")
        resp.raise_for_status()
        indicators = resp.json()

    active = [i for i in indicators if i.get("is_active")]

    if not active:
        return ReportResponse(total_indicators=0, report="No active indicators found.")

    summary_lines = []
    for i in active:
        tags = ", ".join(i.get("tags", [])) or "none"
        summary_lines.append(
            f"- [{i['indicator_type']}] {i['value']} | severity={i['severity']} | confidence={i['confidence']}% | tags={tags}"
        )

    summary = "\n".join(summary_lines)

    prompt = f"""You are a cybersecurity analyst. Generate a concise threat intelligence report based on the following active IOCs:

{summary}

The report should include:
1. Executive summary (2-3 sentences)
2. Key threat patterns observed
3. Top 3 most critical indicators
4. Recommended immediate actions

Keep the report professional and actionable."""

    report = ask_claude(prompt)

    return ReportResponse(total_indicators=len(active), report=report)