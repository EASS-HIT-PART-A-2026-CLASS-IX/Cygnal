import logging
import uuid
from fastapi import FastAPI, HTTPException, status, Depends, Request
from fastapi.responses import JSONResponse
from typing import Annotated

from .models import ThreatIndicator, IndicatorCreate
from .repository import repo, ThreatRepository
from .config import settings

logger = logging.getLogger("cygnal")
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

app = FastAPI(
    title=settings.app_name,
    description="A centralized platform to manage and share cyber threat indicators.",
    version="1.0.0"
)

# 1. Middleware לניהול Trace ID (Session 05)
@app.middleware("http")
async def add_trace_id(request: Request, call_next):
    trace_id = request.headers.get("X-Trace-Id") or f"req-{uuid.uuid4().hex[:8]}"
    request.state.trace_id = trace_id
    response = await call_next(request)
    response.headers["X-Trace-Id"] = trace_id
    return response

# 2. Global Exception Handler לעיצוב שגיאות (Session 02)
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    trace_id = getattr(request.state, "trace_id", "unknown")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": exc.status_code,
            "error": "http_error",
            "detail": exc.detail,
            "trace_id": trace_id
        },
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    trace_id = getattr(request.state, "trace_id", "unknown")
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": 500,
            "error": "internal_server_error",
            "detail": "An unexpected error occurred. Please contact support.",
            "trace_id": trace_id
        },
    )

def get_repo():
    return repo

RepoDep = Annotated[ThreatRepository, Depends(get_repo)]

@app.get("/health", tags=["diagnostics"])
def health():
    return {"status": "ok", "app": settings.app_name}

@app.get("/indicators", response_model=list[ThreatIndicator], tags=["threat-intelligence"])
def list_indicators(
    repository: RepoDep, 
    indicator_type: str | None = None, 
    severity: str | None = None
):
    return repository.list(indicator_type=indicator_type, severity=severity)

@app.post("/indicators", response_model=ThreatIndicator, status_code=status.HTTP_201_CREATED, tags=["threat-intelligence"])
def create_indicator(payload: IndicatorCreate, repository: RepoDep):
    indicator = repository.create(payload)
    logger.info("indicator.created id=%s value=%s", indicator.id, indicator.value)
    return indicator

@app.get("/indicators/{indicator_id}", response_model=ThreatIndicator, tags=["threat-intelligence"])
def get_indicator(indicator_id: int, repository: RepoDep):
    indicator = repository.get(indicator_id)
    if not indicator:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Indicator not found")
    return indicator

@app.delete("/indicators/{indicator_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["threat-intelligence"])
def delete_indicator(indicator_id: int, repository: RepoDep):
    success = repository.delete(indicator_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Indicator not found")