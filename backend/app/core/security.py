from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union, List
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import settings
from app.db.models.all_models import User  # NEW: for type hints
import re
import redis.asyncio as redis_async
import uuid

# Exported for any module that needs it directly
ALGORITHM = settings.ALGORITHM

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

refresh_hash_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Global Token Blacklist via Redis
redis_client = redis_async.from_url(settings.REDIS_URL, decode_responses=True)


def decode_jwt_token(token: str) -> dict:
    """
    Decode JWT token without verification (for extraction only).
    Returns the payload dict or raises ValueError.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise ValueError("Invalid token")


def get_token_jti(token: str) -> Optional[str]:
    """Extract JTI from token."""
    try:
        payload = decode_jwt_token(token)
        return payload.get("jti")
    except ValueError:
        return None


async def blacklist_token(jti: str, expires_in: int = None) -> None:
    if expires_in is None:
        expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    await redis_client.setex(f"blacklist_jti:{jti}", expires_in, "revoked")


async def is_token_blacklisted(jti: str) -> bool:
    return await redis_client.exists(f"blacklist_jti:{jti}") > 0


def hash_refresh_token(token: str) -> str:
    """Hash refresh token for storage."""
    return refresh_hash_context.hash(token)


async def store_refresh_token(user_id: int, jti: str, token_hash: str, ttl: int) -> None:
    """Store hashed refresh token."""
    await redis_client.setex(f"refresh:{user_id}:{jti}", ttl, token_hash)


async def validate_refresh_token(user_id: int, jti: str, token: str) -> bool:
    """Validate refresh token exists and hash matches."""
    stored_hash = await redis_client.get(f"refresh:{user_id}:{jti}")
    if not stored_hash:
        return False
    return refresh_hash_context.verify(token, stored_hash)


async def delete_refresh_token(user_id: int, jti: str) -> None:
    """Delete refresh token."""
    await redis_client.delete(f"refresh:{user_id}:{jti}")


async def login_increment_attempt(identifier: str) -> int:
    """Increment login attempt for user/email."""
    key = f"login_attempts:{identifier}"
    attempts = await redis_client.incr(key)
    if attempts == 1:
        await redis_client.expire(key, settings.LOGIN_LOCKOUT_MINUTES * 60)
    return attempts


async def is_login_locked(identifier: str) -> bool:
    """Check if user is locked."""
    key_lock = f"login_lock:{identifier}"
    return await redis_client.exists(key_lock) > 0


async def lock_user(identifier: str, ttl: int = None) -> None:
    """Lock user after max attempts."""
    if ttl is None:
        ttl = settings.LOGIN_LOCKOUT_MINUTES * 60
    await redis_client.setex(f"login_lock:{identifier}", ttl, "locked")


async def reset_login_attempts(identifier: str) -> None:
    """Reset attempts on success."""
    await redis_client.delete(f"login_attempts:{identifier}")


# 🔥 FIXED: Include role & permissions in JWT (RBAC optimization)
def create_access_token(
    subject: Union[str, Any], 
    role_name: str, 
    permissions: List[str] = [], 
    expires_delta: timedelta = None
) -> str:
    """
    NEW: role_name, permissions from user.role.
    No DB fetch per request!
    """
    jti = str(uuid.uuid4())
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "exp": expire, 
        "sub": str(subject), 
        "type": "access", 
        "jti": jti,
        # 🔥 NEW: RBAC claims
        "role": role_name,
        "permissions": permissions
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


# Refresh also returns access token
def create_refresh_token(subject: Union[str, Any], expires_delta: timedelta = None) -> tuple[str, str]:
    jti = str(uuid.uuid4())
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh", "jti": jti}
    token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return token, jti


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
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-=+\\/~`]", password): 
        return False, "Password must contain at least one special character."
    return True, ""


