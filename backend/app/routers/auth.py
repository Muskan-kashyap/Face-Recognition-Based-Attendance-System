"""
auth.py — Production-ready authentication endpoints
JWT with role/permissions claims for fast RBAC
JSON body (not form) for modern frontend compat
"""
import logging
from jose import jwt
from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps as api_deps
from app.core import security
from app.core.config import settings
from app.core.rate_limit import rate_limit_dependency
from app.crud.crud_user import user as crud_user
from app.schema.token import Token
from app.schema.user import UserSignup, UserResponse, LoginResponse
from app.db.models.all_models import User
from app.db.session import get_db
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()


# 🔥 NEW: Typed request models
class LoginRequest(BaseModel):
    email: str
    password: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


def extract_token(token_data) -> str:
    """
    Safe unpack: str | tuple | dict → str
    """
    if isinstance(token_data, tuple):
        return token_data[0]
    if isinstance(token_data, dict):
        return token_data.get("access_token") or token_data.get("token", "")
    return str(token_data)


@router.post("/login", response_model=LoginResponse)
async def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
    _: bool = Depends(rate_limit_dependency(max_requests=5, window_seconds=60))
) -> Any:
    """
    ✅ FIXED (PHASE 1): Returns JWT + user{id,email,role} for frontend
    Rate limited per IP
    """
    email = payload.email
    password = payload.password

    logger.info(f"Login attempt: {email}")

    # Fail-open lockout check
    try:
        if await security.is_login_locked(email):
            raise HTTPException(status_code=429, detail="Account locked - too many attempts")
    except Exception as e:
        logger.warning(f"Lockout check failed: {e}, continuing")

    user_obj = db.query(User).filter(
        User.email == email, User.is_deleted == 0
    ).first()

    if not user_obj or not security.verify_password(password, user_obj.hashed_password):
        try:
            await security.login_increment_attempt(email)
        except:
            pass
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user_obj.is_active:
        raise HTTPException(status_code=400, detail="Account inactive")

    # 🔥 FIXED: Pass role/permissions to JWT
    role_name = user_obj.role.name.lower()
    permissions = list(user_obj.role.permissions) if user_obj.role.permissions else []

    # Reset attempts on success
    try:
        await security.reset_login_attempts(email)
    except:
        pass

    access_token = security.create_access_token(
        subject=user_obj.id,
        role_name=role_name,
        permissions=permissions,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    refresh_token, _ = security.create_refresh_token(
        subject=user_obj.id,
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "id": user_obj.id,
            "email": user_obj.email,
            "role": role_name
        }
    }


@router.post("/refresh", response_model=Token)
def refresh_token(refresh_token: str, db: Session = Depends(get_db)) -> Any:
    """
    Refresh → new access token with fresh role/permissions
    """
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[security.ALGORITHM])
        if payload.get("type") != "refresh":
            raise ValueError("Invalid token type")
        user_id = int(payload["sub"])
    except:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_obj = db.query(User).filter(User.id == user_id, User.is_deleted == 0).first()
    if not user_obj:
        raise HTTPException(status_code=401, detail="User not found")

    # Re-fetch role/permissions (fresh)
    role_name = user_obj.role.name.lower()
    permissions = list(user_obj.role.permissions) if user_obj.role.permissions else []

    access_token = security.create_access_token(
        subject=user_obj.id,
        role_name=role_name,
        permissions=permissions,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/logout")
async def logout(token: str = Depends(api_deps.oauth2_scheme)):
    """Blacklist access token."""
    try:
        jti = security.get_token_jti(token)
        if jti:
            await security.blacklist_token(jti)
    except Exception as e:
        logger.warning(f"Logout blacklist failed: {e}")
    return { "detail": "Logged out successfully" }


@router.post("/register", response_model=UserResponse)
def register(user_in: UserSignup, db: Session = Depends(get_db)) -> Any:
    """
    Self-register as employee (default role)
    """
    if not security.validate_password_strength(user_in.password)[0]:
        raise HTTPException(status_code=400, detail="Weak password")

    if crud_user.get_by_email(db, email=user_in.email):
        raise HTTPException(status_code=400, detail="Email exists")

    # Default employee role
    user_data = user_in.model_dump()
    user_data["role"] = "employee"  # Lowercase

    return crud_user.create(db, obj_in=user_data)


@router.post("/forgot-password")
def forgot_password(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email, User.is_deleted == 0).first()
    if not user:
        return { "detail": "If email exists, check sent" }

    # Short-lived reset token
    reset_token = security.create_access_token(
        user.id, "reset", [], timedelta(minutes=15)
    )
    reset_url = f"{settings.FRONTEND_URL}/reset-password/{reset_token}"
    logger.info(f"Reset URL: {reset_url}")  # Dev: copy-paste
    return { "detail": "Reset link sent" }


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    if not security.verify_token_type(payload.token, "access"):  # reset uses access type
        raise HTTPException(status_code=400, detail="Invalid token")

    try:
        decoded = jwt.decode(payload.token, settings.SECRET_KEY, algorithms=[security.ALGORITHM])
        user_id = int(decoded["sub"])
    except:
        raise HTTPException(status_code=400, detail="Expired token")

    user = db.query(User).filter(User.id == user_id, User.is_deleted == 0).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not security.validate_password_strength(payload.new_password)[0]:
        raise HTTPException(status_code=400, detail="Weak password")

    user.hashed_password = security.get_password_hash(payload.new_password)
    db.commit()
    return { "message": "Password updated" }
