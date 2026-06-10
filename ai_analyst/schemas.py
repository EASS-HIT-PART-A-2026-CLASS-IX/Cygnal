from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
    indicator_id: int


class AnalyzeResponse(BaseModel):
    indicator_id: int
    value: str
    analysis: str


class ReportResponse(BaseModel):
    total_indicators: int
    report: str
