import uuid
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlmodel import Session

from backend.database import get_session, create_db_and_tables
from backend.models import Indicator, IndicatorCreate, IndicatorUpdate
from backend.repository import repo


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting up and initializing database...")
    create_db_and_tables()
    yield
    print("💤 Shutting down...")


app = FastAPI(title="Cygnal API", lifespan=lifespan)


@app.middleware("http")
async def add_trace_id_and_error_envelope(request: Request, call_next):
    trace_id = request.headers.get("x-trace-id", str(uuid.uuid4()))
    request.state.trace_id = trace_id
    try:
        response = await call_next(request)
        response.headers["x-trace-id"] = trace_id
        return response
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": "Internal Server Error", "detail": str(e), "trace_id": trace_id},
            headers={"x-trace-id": trace_id},
        )


# --- Endpoints ---

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/indicators", response_model=List[Indicator])
def read_indicators(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
):
    return repo.get_all(session, skip=skip, limit=limit)


@app.get("/indicators/{indicator_id}", response_model=Indicator)
def get_indicator(indicator_id: int, session: Session = Depends(get_session)):
    indicator = repo.get_by_id(session, indicator_id)
    if not indicator:
        raise HTTPException(status_code=404, detail="Indicator not found")
    return indicator


@app.post("/indicators", response_model=Indicator, status_code=201)
def create_indicator(indicator: IndicatorCreate, session: Session = Depends(get_session)):
    return repo.create(session, indicator)


@app.put("/indicators/{indicator_id}", response_model=Indicator)
def update_indicator(
    indicator_id: int,
    update: IndicatorUpdate,
    session: Session = Depends(get_session),
):
    updated = repo.update(session, indicator_id, update)
    if not updated:
        raise HTTPException(status_code=404, detail="Indicator not found")
    return updated


@app.delete("/indicators/{indicator_id}")
def delete_indicator(indicator_id: int, session: Session = Depends(get_session)):
    success = repo.delete(session, indicator_id)
    if not success:
        raise HTTPException(status_code=404, detail="Indicator not found")
    return {"ok": True, "message": f"Indicator {indicator_id} deleted."}