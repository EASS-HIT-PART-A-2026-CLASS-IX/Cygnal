from typing import Optional

from backend.core.security import hash_password, verify_password
from backend.schemas.auth import User


USERS_DB = {
    "analyst": {"username": "analyst", "hashed_password": hash_password("analyst123"), "role": "analyst"},
    "admin": {"username": "admin", "hashed_password": hash_password("admin123"), "role": "admin"},
}


def authenticate_user(username: str, password: str) -> Optional[User]:
    user = USERS_DB.get(username)
    if not user or not verify_password(password, user["hashed_password"]):
        return None
    return User(username=user["username"], role=user["role"])
