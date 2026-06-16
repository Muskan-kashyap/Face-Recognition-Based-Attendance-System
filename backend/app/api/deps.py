"""
deps.py — FastAPI dependency injection.
Provides the current authenticated user to all protected routes.
"""
from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session, selectinload

from app.core.config import settings
from app.core import security
from app.db.database import SessionLocal
from app.db.models.all_models import User, Permission, RolePermission, UserRole
from app.schema.token import TokenPayload

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    try:
        if await security.is_token_blacklisted(token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
            )

        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        # Token type enforcement.
        # Keep backward compatibility: if `type` is missing, accept.
        # If `type` is present and not access => reject.
        token_type = payload.get("type")
        if token_type is not None and token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )

        token_data = TokenPayload(**payload)






        if token_data.sub is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )

        user_id = int(str(token_data.sub))
    except (JWTError, ValidationError, ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


    user = (
        db.query(User)
        .options(selectinload(User.role))
        .filter(User.id == user_id, User.is_deleted == 0)
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Account is inactive")
    return current_user


async def require_admin(
    current_user: User = Depends(get_current_active_user),
) -> User:
    if current_user.role.name not in ["Admin", "Manager", "SuperAdmin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin, Manager, or SuperAdmin privileges required"
        )
    return current_user







async def require_manager_or_admin(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Reusable dependency for routes restricted to Admin or Manager roles."""
    if current_user.role.name not in ["Admin", "Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden"
        )
    return current_user


def require_permission(permission_name: str):
    """Return a dependency that requires the current user to have `permission_name`.

    Checks, in order:
    - Explicit permission listed in the role `permissions` JSON array
    - Mapping in the `role_permissions` join table for any role the user has
    """

    async def _dependency(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db),
    ) -> User:
        # 1) Check role-level JSON permissions
        role_perms = current_user.role.permissions or []
        if isinstance(role_perms, (list, tuple)) and permission_name in role_perms:
            return current_user

        # 2) Aggregate role ids (primary + any user_roles)
        role_ids = [current_user.role_id]
        extra_roles = db.query(UserRole).filter(UserRole.user_id == current_user.id).all()
        for ur in extra_roles:
            if ur.role_id not in role_ids:
                role_ids.append(ur.role_id)

        # 3) Lookup permission entry and role_permissions mapping
        perm = db.query(Permission).filter(Permission.name == permission_name, Permission.is_active == True).first()
        if perm:
            rp = db.query(RolePermission).filter(
                RolePermission.permission_id == perm.id,
                RolePermission.role_id.in_(role_ids),
            ).first()
            if rp:
                return current_user

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")

    return _dependency

