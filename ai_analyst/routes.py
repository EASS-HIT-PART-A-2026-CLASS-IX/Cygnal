import httpx
from fastapi import APIRouter, HTTPException

from ai_analyst.schemas import AnalyzeRequest, AnalyzeResponse, ReportResponse
from ai_analyst.service import ask_claude, build_analysis_prompt, build_report_prompt, get_indicator, get_indicators


router = APIRouter()


@router.get("/health", tags=["diagnostics"])
def health():
    return {"status": "ok", "app": "Cygnal AI Analyst"}


@router.post("/analyze", response_model=AnalyzeResponse, tags=["ai"])
def analyze_indicator(request: AnalyzeRequest):
    try:
        indicator = get_indicator(request.indicator_id)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Indicator not found") from exc
        raise
    return AnalyzeResponse(
        indicator_id=indicator["id"],
        value=indicator["value"],
        analysis=ask_claude(build_analysis_prompt(indicator)),
    )


@router.post("/report", response_model=ReportResponse, tags=["ai"])
def generate_report():
    active = [item for item in get_indicators() if item.get("is_active")]
    if not active:
        return ReportResponse(total_indicators=0, report="No active indicators found.")
    return ReportResponse(total_indicators=len(active), report=ask_claude(build_report_prompt(active)))
