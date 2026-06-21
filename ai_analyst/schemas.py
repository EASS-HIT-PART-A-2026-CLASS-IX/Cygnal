from datetime import datetime

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    indicator_id: int = Field(gt=0)


class HistoricalContext(BaseModel):
    first_seen: datetime
    age_days: int
    is_active: bool
    matching_records: int


class AnalyzeResponse(BaseModel):
    indicator_id: int
    value: str
    indicator_type: str
    risk_score: int = Field(ge=0, le=100)
    risk_level: str
    confidence: int = Field(ge=0, le=100)
    summary: str
    reasoning: list[str]
    recommended_actions: list[str]
    type_analysis: str
    source_context: str
    historical_context: HistoricalContext
    analysis_mode: str
    local_model_explanation: str | None = None


class ReportResponse(BaseModel):
    total_indicators: int
    report: str
    critical_indicators: int
    high_risk_indicators: int
    average_risk_score: int
    analysis_mode: str
