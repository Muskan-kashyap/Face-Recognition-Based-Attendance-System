from datetime import datetime, timedelta, timezone
from typing import Any, Union
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import settings
import re

import redis.asyncio as redis_async

# Exported for any module that needs it directly
ALGORITHM = settings.ALGORITHM

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Global Token Blacklist via Redis
redis_client = redis_async.from_url(settings.REDIS_URL, decode_responses=True)

async def blacklist_token(token: str, expires_in: int = None) -> None:
    if expires_in is None:
        expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    await redis_client.setex(f"blacklist:{token}", expires_in, "revoked")

async def is_token_blacklisted(token: str) -> bool:
    try:
        return await redis_client.exists(f"blacklist:{token}") > 0
    except Exception as exc:
        # If Redis is unavailable, treat tokens as not blacklisted to avoid
        # failing all authenticated requests. This makes the blacklist an
        # optional best-effort feature in development environments.
        import logging
        logging.getLogger(__name__).warning(
            f"Redis unavailable for token blacklist check: {exc}")
        return False


def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def verify_token_type(token: str, expected_type: str) -> bool:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("type") == expected_type
    except (JWTError, Exception):
        return False


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validates password strength.
    Returns (is_valid, error_message).
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one digit."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>\-_=+\[\]\\;/`~]", password):
        return False, "Password must contain at least one special character."
    return True, ""
