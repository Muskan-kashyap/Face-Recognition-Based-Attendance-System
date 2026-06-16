from datetime import datetime, timedelta, timezone
from typing import Any, Union
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import settings
import logging
import re

import redis.asyncio as redis_async

logger = logging.getLogger(__name__)

# Exported for any module that needs it directly
ALGORITHM = settings.ALGORITHM

pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")

# Global Token Blacklist via Redis.
# socket_connect_timeout / socket_timeout prevent the asyncio retry wrapper
# from re-raising ConnectionError past our try/except in is_token_blacklisted.
redis_client = redis_async.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    socket_connect_timeout=2,
    socket_timeout=2,
)


async def blacklist_token(token: str, expires_in: int = None) -> None:
    """Add a token to the Redis blacklist. Best-effort — silently skips if Redis is down."""
    if expires_in is None:
        expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    try:
        await redis_client.setex(f"blacklist:{token}", expires_in, "revoked")
    except Exception as exc:
        logger.warning("Redis unavailable — token blacklist write skipped: %s", exc)


async def is_token_blacklisted(token: str) -> bool:
    """Return True if the token has been revoked. Fails open when Redis is down."""
    try:
        return await redis_client.exists(f"blacklist:{token}") > 0
    except Exception as exc:
        # Fail-open: Redis being down must NOT block all authenticated requests.
        # A revoked token may briefly continue to work — acceptable in development.
        # In production, ensure Redis is highly available.
        logger.warning("Redis unavailable for token blacklist check (fail-open): %s", exc)
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
