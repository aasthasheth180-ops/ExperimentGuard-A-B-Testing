
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .auth import (
    create_access_token,
    get_auth_db,
    get_current_user,
    hash_password,
    verify_password,
)
from .models import UserRecord

router = APIRouter(prefix="/auth", tags=["Authentication"])


class RegisterRequest(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=12, max_length=128)


class LoginRequest(BaseModel):
    email: str
    password: str


def normalize_email(email: str) -> str:
    return email.strip().lower()


@router.post("/register", status_code=201)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_auth_db),
):
    email = normalize_email(request.email)

    if "@" not in email or "." not in email.split("@")[-1]:
        raise HTTPException(422, "Invalid email address.")

    existing = db.scalar(
        select(UserRecord).where(UserRecord.email == email)
    )

    if existing is not None:
        raise HTTPException(409, "Account already exists.")

    user = UserRecord(
        email=email,
        password_hash=hash_password(request.password),
    )

    db.add(user)

    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Account already exists.") from None

    return {"id": user.id, "email": user.email}


@router.post("/login")
def login(
    request: LoginRequest,
    db: Session = Depends(get_auth_db),
):
    user = db.scalar(
        select(UserRecord).where(
            UserRecord.email == normalize_email(request.email)
        )
    )

    if (
        user is None
        or not user.is_active
        or not verify_password(request.password, user.password_hash)
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )

    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
    }


@router.get("/me")
def me(
    user: Annotated[UserRecord, Depends(get_current_user)],
):
    return {"id": user.id, "email": user.email}
