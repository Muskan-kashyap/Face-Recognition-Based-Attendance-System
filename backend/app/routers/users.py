"""
users.py — RBAC-protected user management router.
All queries are scoped to current_user.org_id for strict multi-tenancy.
"""
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.crud.crud_user import user as crud_user
from app.api import deps
from app.schema.user import UserResponse, UserCreate, UserUpdate
from app.db.models.all_models import User
from app.db.database import get_db
from app.services.face_engine import face_engine
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """STRICT MULTI-TENANCY: Admins only see users in their own org."""
    if not deps.has_any_role(current_user, "Admin", "Manager", "SuperAdmin", "Super Admin"):
        raise HTTPException(status_code=403, detail="Unauthorized")
    return db.query(User).filter(

        User.org_id == current_user.org_id,
        User.is_deleted == 0
    ).offset(skip).limit(limit).all()


@router.post("/", response_model=UserResponse)
def create_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    if not deps.has_any_role(current_user, "Admin", "Manager", "SuperAdmin", "Super Admin"):
        raise HTTPException(status_code=403, detail="Unauthorized")



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
    if current_user.id != user_id and not deps.has_any_role(current_user, "Admin", "Manager", "SuperAdmin", "Super Admin"):
        raise HTTPException(status_code=403, detail="Forbidden")


    return user


@router.post("/{user_id}/enroll-face")
async def enroll_user_face(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    # SECURE: multi-tenant + role check
    user = db.query(User).filter(
        User.id == user_id,
        User.org_id == current_user.org_id
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="Identity not found")
    if not deps.has_any_role(current_user, "Admin", "Manager", "SuperAdmin", "Super Admin") and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")


    logger.info("Enrollment started for user=%s", user_id)
    image_bytes = await file.read()

    # Phase 3 Module 1: enrollment quality gating + audit event logging.
    # The ai-service face extraction already enforces "single face" for embedding.
    from app.db.models.all_models import EnrollmentEvent, SpoofDetectionLog

    org_id = current_user.org_id
    min_bytes = 1024
    try:
        logger.info(
            "Image validation: bytes=%s min_bytes=%s",
            len(image_bytes) if image_bytes else 0,
            min_bytes,
        )
        if not image_bytes or len(image_bytes) < min_bytes:
            raise ValueError("Image resolution too low")

        logger.info("Embedding generation started")
        embedding = face_engine.get_embedding(image_bytes)
        logger.info(
            "Embedding generated=%s length=%s",
            embedding is not None,
            len(embedding) if embedding else 0,
        )
        if not embedding:
            raise ValueError("No face or multiple faces detected in the image")

        # Basic quality heuristics (no new ML models):
        # - quality_score scales with payload size; capped for stability.
        quality_score = min(9.9, max(0.1, len(image_bytes) / 100000.0))
        # embedding_version = "ai-service-embedding-v1"
        embedding_version = "face_recognition_v1"

        logger.info("Calling crud_user.enroll_face")
        crud_user.enroll_face(db, user_id=user_id, embedding=embedding)
        logger.info("Face embedding stored")

        logger.info("Creating EnrollmentEvent")
        db.add(
            EnrollmentEvent(
                user_id=user_id,
                org_id=org_id,
                status="success",
                quality_score=quality_score,
                embedding_version=embedding_version,
                image_resolution=f"{len(image_bytes)}bytes",
                brightness_score=None,
                blur_score=None,
            )
        )

        logger.info("Creating SpoofDetectionLog")
        # Liveness/spoof attempt on enrollment (best-effort if ai-service provides it).
        # If ai-service does not expose spoof here, we still log attempt_type with is_spoof=0.
        # NOTE: liveness_service is used in the recognition pipeline; for now keep enrollment spoof log minimal.
        db.add(
            SpoofDetectionLog(
                user_id=user_id,
                org_id=org_id,
                attempt_type="enrollment",
                is_spoof=0,
                spoof_score=None,
                model_name=None,
            )
        )

        logger.info("Committing transaction")
        db.commit()
        logger.info("Enrollment completed")
        return {"status": "success", "message": "Neural identity registered."}


    except Exception as e:
        import traceback
        traceback.print_exc()

        logger.exception(
            "Face enrollment failed: %s",
            str(e),
        )

        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )





