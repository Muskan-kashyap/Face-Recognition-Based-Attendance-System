"""
auth.py — Public authentication endpoints.
"""
from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api import deps
from app.core import security
from app.core.config import settings
from app.crud.crud_user import user as crud_user
from app.schema.user import Token, UserSignup, UserResponse
from app.db.models.all_models import User

router = APIRouter()


@router.post("/login", response_model=Token)
def login_access_token(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    Accepts username (email) + password, returns a JWT access token.
    Compatible with OAuth2PasswordBearer on the frontend.
    """
    user_obj = db.query(User).filter(
        User.email == form_data.username,
        User.is_deleted == 0
    ).first()

    if not user_obj or not security.verify_password(form_data.password, user_obj.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    if not user_obj.is_active:
        raise HTTPException(status_code=400, detail="Operative account is suspended")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user_obj.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/register", response_model=UserResponse)
def register_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserSignup
) -> Any:
    """
    Self-service registration. Creates a new org or joins an existing one.
    """
    existing = crud_user.get_by_email(db, email=user_in.email)
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already registered."
        )
    new_user = crud_user.create(db, obj_in=user_in.model_dump())
    return new_user
