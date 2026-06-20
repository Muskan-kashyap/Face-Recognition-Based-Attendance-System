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


import logging

logger = logging.getLogger(__name__)


async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User:
    """
    Validate access token and return the authenticated user.

    Flow:
    1. Check blacklist
    2. Decode JWT
    3. Verify token type
    4. Validate payload
    5. Load user from database
    """

    try:
        # ---------------------------------------------------------------------
        # Check whether token has been revoked
        # ---------------------------------------------------------------------
        if await security.is_token_blacklisted(token):
            logger.warning("Blacklisted token used")

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
            )

        # ---------------------------------------------------------------------
        # Decode JWT
        # ---------------------------------------------------------------------
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        logger.info("JWT decoded successfully")
        logger.debug("JWT payload: %s", payload)

        # ---------------------------------------------------------------------
        # Ensure access token is used
        # ---------------------------------------------------------------------
        token_type = payload.get("type")

        if token_type and token_type != "access":
            logger.warning(
                "Invalid token type received: %s",
                token_type,
            )

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )

        # ---------------------------------------------------------------------
        # Validate token payload
        # ---------------------------------------------------------------------
        token_data = TokenPayload(**payload)

        logger.debug("TokenPayload: %s", token_data)

        if token_data.sub is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing subject in token",
            )

        try:
            user_id = int(token_data.sub)
        except ValueError:
            logger.error(
                "Invalid user id in token: %s",
                token_data.sub,
            )

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user identifier",
            )

    except JWTError as e:
        logger.exception("JWT validation failed")

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"JWT validation failed: {str(e)}",
        )

    except ValidationError as e:
        logger.exception("Token payload validation failed")

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token payload validation failed: {str(e)}",
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.exception("Unexpected authentication error")

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication error: {str(e)}",
        )

    # -------------------------------------------------------------------------
    # Fetch user
    # -------------------------------------------------------------------------
    user = (
        db.query(User)
        .options(selectinload(User.role))
        .filter(
            User.id == user_id,
            User.is_deleted == 0,
        )
        .first()
    )

    if not user:
        logger.warning(
            "Authenticated user not found: user_id=%s",
            user_id,
        )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    logger.info(
        "Authenticated user: id=%s email=%s",
        user.id,
        user.email,
    )

    return user

# async def get_current_user(
#     db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
# ) -> User:
#     try:
#         if await security.is_token_blacklisted(token):
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Token has been revoked",
#             )

#         payload = jwt.decode(
#             token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
#         )

#         # Token type enforcement.
#         # Keep backward compatibility: if `type` is missing, accept.
#         # If `type` is present and not access => reject.
#         token_type = payload.get("type")
#         if token_type is not None and token_type != "access":
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Invalid token type",
#             )

#         token_data = TokenPayload(**payload)






#         if token_data.sub is None:
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Invalid token payload",
#             )

#         user_id = int(str(token_data.sub))
#     except (JWTError, ValidationError, ValueError, TypeError):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Could not validate credentials",
#         )


#     user = (
#         db.query(User)
#         .options(selectinload(User.role))
#         .filter(User.id == user_id, User.is_deleted == 0)
#         .first()
#     )
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )

    if current_user.role is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No role assigned to this user.",
        )

    return current_user


# async def require_admin(
#     current_user: User = Depends(get_current_active_user),
# ) -> User:
#     if current_user.role.name not in ["Admin", "Manager", "SuperAdmin"]:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Admin, Manager, or SuperAdmin privileges required"
#         )
#     return current_user

def has_any_role(user: User, *roles: str) -> bool:
    """
    Check whether a user has one of the allowed roles.
    Handles legacy naming inconsistencies.
    """

    if user.role is None:
        return False

    user_role = user.role.name.strip().lower()

    normalized_roles = {
        role.strip().lower()
        for role in roles
    }

    return user_role in normalized_roles

# async def require_admin(
#     current_user: User = Depends(get_current_active_user),
# ) -> User:
#     """
#     Allows Admin, Manager, and Super Admin users.
#     Handles legacy role naming inconsistencies safely.
#     """

    # if current_user.role is None:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="No role assigned to this user."
    #     )

    # role_name = current_user.role.name.strip().lower()

    # allowed_roles = {
    #     "admin",
    #     "manager",
    #     "superadmin",
    #     "super admin",
    # }

    # if role_name not in allowed_roles:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail=(
    #             "Admin, Manager, or Super Admin privileges required."
    #         ),
    #     )

    # return current_user


async def require_admin(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Allow:
    - Admin
    - Manager
    - SuperAdmin
    - Super Admin
    """

    if not has_any_role(
        current_user,
        "Admin",
        "Manager",
        "SuperAdmin",
        "Super Admin",
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin, Manager, or Super Admin privileges required.",
        )

    return current_user




async def require_manager_or_admin(
    current_user: User = Depends(get_current_active_user),
) -> User:
    if not has_any_role(
        current_user,
        "Admin",
        "Manager",
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or Manager privileges required.",
        )

    return current_user

async def require_admin_or_super_admin(
    current_user: User = Depends(get_current_active_user),
) -> User:
    if current_user.role is None:
        raise HTTPException(
            status_code=403,
            detail="No role assigned.",
        )

    role = current_user.role.name.strip().lower()

    if role not in {
        "admin",
        "superadmin",
        "super admin",
    }:
        raise HTTPException(
            status_code=403,
            detail="Admin privileges required.",
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
        role_perms = (
            current_user.role.permissions
            if current_user.role and current_user.role.permissions
            else []
        )
        if isinstance(role_perms, (list, tuple)) and permission_name in role_perms:
            return current_user

        # 2) Aggregate role ids (primary + any user_roles)
        # role_ids = [current_user.role_id]
        role_ids = []
        if current_user.role_id:
            role_ids.append(current_user.role_id)
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

