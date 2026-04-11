from fastapi import FastAPI, HTTPException, status, Depends
from typing import Annotated
# שימוש ב-Imports יחסיים נשאר תקין כל עוד אנחנו בתוך תיקיית ה-app
from .models import ThreatIndicator
from .repository import repo, ThreatRepository
from .config import settings

app = FastAPI(
    title=settings.app_name, 
    description="A centralized platform to manage and share cyber threat indicators.",
    version="1.0.0"
)

# פונקציה להזרקת התלות של ה-Repository
def get_repo():
    return repo

# יצירת Annotated type לשימוש חוזר נוח
RepoDep = Annotated[ThreatRepository, Depends(get_repo)]

@app.get("/health", tags=["diagnostics"])
def health():
    return {"status": "ok", "app": settings.app_name}

@app.get("/indicators", response_model=list[ThreatIndicator], tags=["threat-intelligence"])
def list_indicators(repository: RepoDep):
    return repository.list()

@app.post("/indicators", status_code=status.HTTP_201_CREATED, tags=["threat-intelligence"])
def create_indicator(payload: ThreatIndicator, repository: RepoDep):
    return repository.create(payload)

@app.get("/indicators/{indicator_id}", tags=["threat-intelligence"])
def get_indicator(indicator_id: int, repository: RepoDep):
    indicator = repository.get(indicator_id)
    if not indicator:
        raise HTTPException(status_code=404, detail="Indicator not found")
    return indicator

@app.delete("/indicators/{indicator_id}", tags=["threat-intelligence"])
def delete_indicator(indicator_id: int, repository: RepoDep):
    success = repository.delete(indicator_id)
    if not success:
        raise HTTPException(status_code=404, detail="Indicator not found")
    return {"detail": "Indicator deleted"}