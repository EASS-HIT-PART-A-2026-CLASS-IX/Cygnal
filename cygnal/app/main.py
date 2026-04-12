import logging
from fastapi import FastAPI, HTTPException, status, Depends
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


def get_repo():
    return repo


RepoDep = Annotated[ThreatRepository, Depends(get_repo)]


@app.get("/health", tags=["diagnostics"])
def health():
    return {"status": "ok", "app": settings.app_name}


@app.get("/indicators", response_model=list[ThreatIndicator], tags=["threat-intelligence"])
def list_indicators(repository: RepoDep):
    return repository.list()


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