import hashlib
import json
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlmodel import Session

from backend.api.dependencies import get_current_user, require_admin
from backend.db.session import get_session
from backend.repositories.indicators import repo
from backend.schemas.indicators import (
    IndicatorCreate,
    IndicatorPage,
    IndicatorRead,
    IndicatorType,
    IndicatorUpdate,
    Severity,
)
from backend.services.indicator_exports import indicators_to_csv


router = APIRouter(prefix="/indicators", tags=["indicators"])


@router.get("", response_model=List[IndicatorRead])
def read_indicators(
    skip: int = Query(default=0, ge=0, le=1_000_000),
    limit: int = Query(default=100, ge=1, le=100),
    indicator_type: IndicatorType | None = None,
    severity: Severity | None = None,
    is_active: bool | None = None,
    session: Session = Depends(get_session),
):
    return repo.get_all(session, skip, limit, indicator_type, severity, is_active)


@router.get("/page", response_model=IndicatorPage, tags=["contracts"])
def read_indicator_page(
    request: Request,
    page: int = Query(default=1, ge=1, le=1_000_000),
    page_size: int = Query(default=20, ge=1, le=100),
    indicator_type: IndicatorType | None = None,
    severity: Severity | None = None,
    is_active: bool | None = None,
    session: Session = Depends(get_session),
):
    items = repo.get_all(session, (page - 1) * page_size, page_size, indicator_type, severity, is_active)
    payload = IndicatorPage(
        page=page,
        page_size=page_size,
        total=repo.count(session, indicator_type, severity, is_active),
        items=items,
    )
    encoded = jsonable_encoder(payload)
    digest = hashlib.sha256(json.dumps(encoded, sort_keys=True).encode()).hexdigest()
    etag = f'W/"{digest}"'
    headers = {"ETag": etag, "X-Total-Count": str(payload.total)}
    if request.headers.get("if-none-match") == etag:
        return Response(status_code=304, headers=headers)
    return JSONResponse(content=encoded, headers=headers)


@router.get("/export.csv", tags=["contracts"])
def export_indicators_csv(
    indicator_type: IndicatorType | None = None,
    severity: Severity | None = None,
    is_active: bool | None = None,
    session: Session = Depends(get_session),
):
    indicators = repo.get_all(
        session, limit=10_000, indicator_type=indicator_type, severity=severity, is_active=is_active
    )
    return Response(
        content=indicators_to_csv(indicators),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="cygnal_indicators.csv"'},
    )


@router.get("/{indicator_id}", response_model=IndicatorRead, responses={404: {"description": "Indicator not found"}})
def get_indicator(indicator_id: int, session: Session = Depends(get_session)):
    indicator = repo.get_by_id(session, indicator_id)
    if not indicator:
        raise HTTPException(status_code=404, detail="Indicator not found")
    return indicator


@router.post("", response_model=IndicatorRead, status_code=201)
def create_indicator(indicator: IndicatorCreate, session: Session = Depends(get_session)):
    return repo.create(session, indicator)


@router.put("/{indicator_id}", response_model=IndicatorRead, responses={404: {"description": "Indicator not found"}})
def update_indicator(indicator_id: int, update: IndicatorUpdate, session: Session = Depends(get_session)):
    updated = repo.update(session, indicator_id, update)
    if not updated:
        raise HTTPException(status_code=404, detail="Indicator not found")
    return updated


@router.delete(
    "/{indicator_id}",
    dependencies=[Depends(get_current_user)],
    responses={401: {"description": "Missing or invalid JWT"}, 404: {"description": "Indicator not found"}},
)
def delete_indicator(indicator_id: int, session: Session = Depends(get_session)):
    if not repo.delete(session, indicator_id):
        raise HTTPException(status_code=404, detail="Indicator not found")
    return {"ok": True, "message": f"Indicator {indicator_id} deleted."}


@router.post(
    "/{indicator_id}/deactivate",
    dependencies=[Depends(require_admin)],
    tags=["admin"],
    responses={
        401: {"description": "Missing or invalid JWT"},
        403: {"description": "Admin role required"},
        404: {"description": "Indicator not found"},
    },
)
def deactivate_indicator(indicator_id: int, session: Session = Depends(get_session)):
    updated = repo.update(session, indicator_id, IndicatorUpdate(is_active=False))
    if not updated:
        raise HTTPException(status_code=404, detail="Indicator not found")
    return {"ok": True, "message": f"Indicator {indicator_id} deactivated."}
