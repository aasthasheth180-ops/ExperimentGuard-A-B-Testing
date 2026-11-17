
import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import SessionLocal
from .models import UserRecord

password_hasher = PasswordHash.recommended()
bearer = HTTPBearer(auto_error=False)
ALGORITHM = "HS256"


def validate_auth_configuration() -> None:
    secret = os.getenv("JWT_SECRET_KEY")

    if not secret:
        raise RuntimeError(
            "JWT_SECRET_KEY is missing. Configure it in your environment."
        )

    if len(secret) < 32:
        raise RuntimeError(
            "JWT_SECRET_KEY must contain at least 32 characters."
        )



def get_auth_db():
    with SessionLocal() as db:
        yield db


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return password_hasher.verify(password, hashed)


def create_access_token(user_id: int) -> str:
    secret = os.environ["JWT_SECRET_KEY"]
    now = datetime.now(timezone.utc)

    return jwt.encode(
        {
            "sub": str(user_id),
            "iat": now,
            "exp": now + timedelta(minutes=60),
        },
        secret,
        algorithm=ALGORITHM,
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_auth_db),
) -> UserRecord:
    error = HTTPException(
        status_code=401,
        detail="Invalid or expired authentication.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise error

    try:
        payload = jwt.decode(
            credentials.credentials,
            os.environ["JWT_SECRET_KEY"],
            algorithms=[ALGORITHM],
        )
        user_id = int(payload["sub"])
    except (InvalidTokenError, KeyError, ValueError, TypeError):
        raise error from None

    user = db.get(UserRecord, user_id)

    if user is None or not user.is_active:
        raise error

    return user
