import httpx
from fastapi import APIRouter, HTTPException

from ai_analyst.config import settings
from ai_analyst.schemas import AnalyzeRequest, AnalyzeResponse, ReportResponse
from ai_analyst.service import (
    add_optional_ollama_explanation,
    build_deterministic_analysis,
    build_report,
    get_indicator,
    get_indicators,
)


router = APIRouter()


@router.get("/health", tags=["diagnostics"])
def health():
    return {
        "status": "ok",
        "app": "Cygnal Enrichment Analyst",
        "default_mode": "deterministic",
        "ollama_configured": bool(settings.ollama_base_url),
    }


@router.post("/analyze", response_model=AnalyzeResponse, tags=["enrichment"])
def analyze_indicator(request: AnalyzeRequest):
    try:
        indicator = get_indicator(request.indicator_id)
        indicators = get_indicators()
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Indicator not found") from exc
        raise HTTPException(status_code=502, detail="Backend service unavailable") from exc
    analysis = build_deterministic_analysis(indicator, indicators)
    return AnalyzeResponse(**add_optional_ollama_explanation(analysis))


@router.post("/report", response_model=ReportResponse, tags=["enrichment"])
def generate_report():
    try:
        active = [item for item in get_indicators() if item.get("is_active")]
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="Backend service unavailable") from exc
    return ReportResponse(**build_report(active))
