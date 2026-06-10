from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from backend.api.dependencies import get_current_user
from backend.core.config import settings
from backend.core.security import create_access_token
from backend.schemas.auth import Token, User
from backend.services.authentication import authenticate_user


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form.username, form.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=User, responses={401: {"description": "Missing or invalid JWT"}})
def me(current_user: User = Depends(get_current_user)):
    return current_user
