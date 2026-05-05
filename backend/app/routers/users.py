"""
users.py — RBAC-protected user management router.
All queries are scoped to current_user.org_id for strict multi-tenancy.
"""
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.crud.crud_user import user as crud_user
from app.api import deps
from app.schema.user import UserResponse, UserCreate, UserUpdate, FaceEnroll
from app.db.models.all_models import User
from app.db.session import get_db

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.require_role(["manager"])),
) -> Any:
    """STRICT MULTI-TENANCY: Admins only see users in their own org."""
    return db.query(User).filter(
        User.org_id == current_user.org_id,
        User.is_deleted == 0
    ).offset(skip).limit(limit).all()


@router.post("/", response_model=UserResponse)
def create_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
    current_user: User = Depends(deps.require_role(["manager"])),
) -> Any:

    # Enforce org_id from the calling admin's session — prevents org spoofing
    user_in.org_id = current_user.org_id
    user_in.organization = current_user.organization.name if current_user.organization else "default"

    existing = crud_user.get_by_email(db, email=user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Identity already registered.")

    user_count = db.query(func.count(User.id)).filter(
        User.org_id == current_user.org_id,
        User.is_deleted == 0
    ).scalar()
    if user_count >= 10:
        raise HTTPException(status_code=402, detail="Tier limit reached. Upgrade to Pro.")

    return crud_user.create(db, obj_in=user_in.model_dump())


@router.get("/me", response_model=UserResponse)
def read_user_me(current_user: User = Depends(deps.get_current_active_user)) -> Any:
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
def read_user_by_id(
    user_id: int,
    current_user: User = Depends(deps.get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    # SECURE: filter by org prevents cross-tenant ID enumeration
    user = db.query(User).filter(
        User.id == user_id,
        User.org_id == current_user.org_id
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="Identity not found")
    user_role = current_user.role.name.lower()
    if current_user.id != user_id and user_role == "employee":
        raise HTTPException(status_code=403, detail="Forbidden")
    return user


@router.post("/{user_id}/enroll")
def enroll_user_face(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    enroll_in: FaceEnroll,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    # SECURE: multi-tenant + role check
    user = db.query(User).filter(
        User.id == user_id,
        User.org_id == current_user.org_id
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="Identity not found")
    user_role = current_user.role.name.lower()
    if user_role == "employee" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    crud_user.enroll_face(db, user_id=user_id, embedding=enroll_in.face_embedding)
    return {"status": "success", "message": "Neural identity registered."}
