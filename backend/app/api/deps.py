"""
deps.py — FastAPI dependency injection with JWT RBAC claims.
- get_current_user: Decodes JWT → role/permissions + fetches full User
- require_role(roles): Centralized RBAC with hierarchy
"""
from typing import Generator, List
from fastapi import Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core import security
from app.db.session import get_db
from app.db.models.all_models import User
from app.schema.token import TokenPayload

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    """
    🔥 FIXED: Extract role/permissions from JWT claims (fast)
    Still fetch full User for org_id etc.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError) as e:
        print(f"DEBUG: JWT Validation Error: {e}") 
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    # token_data.sub is a string (JWT claim), User.id is integer
    try:
        user_id = int(token_data.sub)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token subject",
        )
    user = db.query(User).filter(User.id == user_id, User.is_deleted == 0).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 🔥 OBSERVABILITY: Log user + role for tracing
    import logging
    logger = logging.getLogger("app.api.deps")
    logger.info(f"Authenticated user {user.id} ({user.role.name})")
    
    return user



async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Account is inactive")
    return current_user


# 🔥 NEW: Role hierarchy
ROLE_HIERARCHY = {
    "superadmin": 4,
    "admin": 3,
    "manager": 2,
    "employee": 1
}


def has_higher_role(user_role: str, required_role: str) -> bool:
    """SuperAdmin > Admin > Manager > Employee"""
    return ROLE_HIERARCHY.get(user_role, 0) > ROLE_HIERARCHY.get(required_role, 0)


# 🔥 NEW: Centralized RBAC dependency
def require_role(required_roles: List[str]):
    """
    Factory that returns a dependency for role-based access control.
    Usage: Depends(require_role(["admin", "manager"]))
    """
    async def role_dependency(
        current_user: User = Depends(get_current_user)
    ) -> User:
        user_role = current_user.role.name.lower()
        
        # Direct match or higher role
        if (user_role in required_roles or 
            any(has_higher_role(user_role, req_role) for req_role in required_roles)):
            return current_user
        
        # 🔥 OBSERVABILITY: Log denied attempt
        import logging
        logger = logging.getLogger("app.api.deps")
        logger.warning(f"ACCESS DENIED: User {current_user.id} ({user_role}) tried to access {required_roles}")

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role &#39;{user_role}&#39; lacks permission (requires: {required_roles})"
        )
    return role_dependency




# Legacy (IMPROVED)
async def require_admin(
    current_user: User = Depends(get_current_active_user),
) -> User:
    # Use the factory internally
    dep = require_role(["admin", "superadmin"])
    return await dep(current_user=current_user)


async def require_manager_or_admin(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Deprecated: use require_role(["manager", "admin", "superadmin"])"""
    dep = require_role(["manager", "admin", "superadmin"])
    return await dep(current_user=current_user)
