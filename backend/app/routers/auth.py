"""
auth.py — Public authentication endpoints.
"""
from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from sqlalchemy.orm import Session

from app.api import deps
from app.core import security
from app.core.config import settings
from app.core.rate_limit import rate_limit_dependency
from app.crud.crud_user import user as crud_user
from app.schema.token import Token
from app.schema.user import UserSignup, UserResponse
from app.db.models.all_models import User
from app.db.database import SessionLocal

router = APIRouter()


@router.post("/login", response_model=Token)
def login_access_token(
    request: Request,
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
    _: bool = Depends(rate_limit_dependency(max_requests=5, window_seconds=60))
) -> Any:
    """
    Accepts username (email) + password, returns a JWT access token.
    Compatible with OAuth2PasswordBearer on the frontend.
    Rate limited: 5 attempts per IP per minute.
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
        raise HTTPException(status_code=400, detail="Account is suspended")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    return {
        "access_token": security.create_access_token(
            user_obj.id, expires_delta=access_token_expires
        ),
        "refresh_token": security.create_refresh_token(
            user_obj.id, expires_delta=refresh_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    refresh_token: str,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Refresh an access token using a valid refresh token.
    """
    if await security.is_token_blacklisted(refresh_token):
        raise HTTPException(status_code=401, detail="Refresh token has been revoked")

    if not security.verify_token_type(refresh_token, "refresh"):
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[security.ALGORITHM])
        user_id = int(payload.get("sub"))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_obj = db.query(User).filter(User.id == user_id, User.is_deleted == 0).first()
    if not user_obj or not user_obj.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(user_obj.id, expires_delta=access_token_expires),
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/logout")
async def logout(
    token: str = Depends(deps.oauth2_scheme),
) -> Any:
    """
    Logout the current user by blacklisting the token.
    """
    await security.blacklist_token(token)
    return {"detail": "Successfully logged out"}


@router.post("/register", response_model=UserResponse)
def register_user(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserSignup,
    _: bool = Depends(rate_limit_dependency(max_requests=3, window_seconds=300))
) -> Any:
    """
    Self-service registration. Creates a new org or joins an existing one.
    Rate limited: 3 registrations per IP per 5 minutes.
    """
    # Password strength validation
    is_valid, error_msg = security.validate_password_strength(user_in.password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    existing = crud_user.get_by_email(db, email=user_in.email)
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already registered."
        )
    new_user = crud_user.create(db, obj_in=user_in.model_dump())
    return new_user

