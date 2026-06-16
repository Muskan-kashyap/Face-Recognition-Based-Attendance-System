"""Biometrics service — face enrollment & verification endpoints."""
import base64
import logging
from typing import Optional

import cv2
import numpy as np
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from pgvector.sqlalchemy import Vector
from sqlalchemy import bindparam, text
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user_claims, TenantGuard
from app.db.database import get_db
from app.services.face_engine import face_engine
from app.services.liveness import liveness_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/biometrics", tags=["Biometrics"])

# Cosine similarity acceptance threshold for ArcFace / face_recognition
SIMILARITY_THRESHOLD = 0.45

# ─── Request / Response Schemas ───────────────────────────────────────────────

class EnrollRequest(BaseModel):
    user_id: int
    image_base64: str          # Raw JPEG/PNG encoded as base64


class VerifyRequest(BaseModel):
    image_base64: str
    org_id: str                # Must match org of users being searched


class EnrollResponse(BaseModel):
    status: str
    user_id: int
    model_name: str
    liveness_score: float


class VerifyResponse(BaseModel):
    status: str
    user_id: Optional[int]
    full_name: Optional[str]
    distance: Optional[float]
    is_live: bool
    liveness_score: float
    dominant_emotion: str
    emotion_confidence: float


class ImageRequest(BaseModel):
    image_base64: str


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _decode_image_bytes(image_base64: str) -> bytes:
    """Decode a base64 image payload, raising 400 on invalid input."""
    try:
        return base64.b64decode(image_base64)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 image payload")


def _bytes_to_bgr(image_bytes: bytes) -> np.ndarray:
    """Convert raw bytes to an OpenCV BGR ndarray."""
    arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(status_code=400, detail="Cannot decode image — unsupported format")
    return img


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/enroll", response_model=EnrollResponse, status_code=status.HTTP_201_CREATED)
def enroll_face(
    req: EnrollRequest,
    db: Session = Depends(get_db),
    claims: dict = Depends(get_current_user_claims),
):
    """
    Register a user's face embedding.

    Flow:
    1. Decode image → liveness check
    2. Extract 128-d embedding via FaceEngine
    3. Deactivate any previous embeddings for the user
    4. Persist new embedding in face_embeddings table
    """
    image_bytes = _decode_image_bytes(req.image_base64)
    img_bgr = _bytes_to_bgr(image_bytes)

    # ── 1. Liveness validation ──────────────────────────────────────────────
    # liveness_service from backend takes bytes, not BGR
    is_live, liveness_score = liveness_service.detect_liveness(image_bytes)
    if not is_live:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Enrollment rejected — liveness check failed (score: {liveness_score:.3f}). "
                   "Please use a live camera feed.",
        )

    # ── 2. Embedding extraction ─────────────────────────────────────────────
    embedding = face_engine.get_embedding(image_bytes)
    if embedding is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No face detected in the provided image. "
                   "Ensure the face is clearly visible and well-lit.",
        )

    # ── 3. Deactivate previous embeddings ───────────────────────────────────
    db.execute(
        text("UPDATE face_embeddings SET is_active = 0 WHERE user_id = :uid"),
        {"uid": req.user_id},
    )

    # ── 4. Persist new embedding ────────────────────────────────────────────
    db.execute(
        text(
            "INSERT INTO face_embeddings "
            "(user_id, embedding, model_name, is_active) "
            "VALUES (:uid, :emb, 'ArcFace', 1)"
        ).bindparams(bindparam("emb", type_=Vector(128))),
        {"uid": req.user_id, "emb": embedding},
    )
    db.commit()

    logger.info("Face enrolled for user_id=%s (liveness=%.3f)", req.user_id, liveness_score)
    return EnrollResponse(
        status="enrolled",
        user_id=req.user_id,
        model_name="ArcFace",
        liveness_score=liveness_score,
    )


@router.post("/verify", response_model=VerifyResponse)
def verify_face(
    req: VerifyRequest,
    db: Session = Depends(get_db),
):
    """
    Identify a user via their face.

    Flow:
    1. Decode image → liveness check
    2. Extract embedding → HNSW cosine search in pgvector
    3. Emotion analysis on detected face region
    4. Return user identity if distance < threshold
    """
    image_bytes = _decode_image_bytes(req.image_base64)
    img_bgr = _bytes_to_bgr(image_bytes)

    # ── 1. Liveness check ───────────────────────────────────────────────────
    is_live, liveness_score = liveness_service.detect_liveness(image_bytes)
    if not is_live:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Verification rejected — liveness check failed (score: {liveness_score:.3f}).",
        )

    # ── 2. Embedding extraction ─────────────────────────────────────────────
    embedding = face_engine.get_embedding(image_bytes)
    if embedding is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No face detected in the camera frame.",
        )

    # ── 3. pgvector HNSW cosine similarity search ───────────────────────────
    match = db.execute(
        text(
            "SELECT f.user_id, u.full_name, (f.embedding <=> :emb) AS distance "
            "FROM face_embeddings f "
            "JOIN users u ON f.user_id = u.id "
            "WHERE u.org_id = :org_id "
            "  AND f.is_active = 1 "
            "  AND u.is_deleted = 0 "
            "ORDER BY f.embedding <=> :emb "
            "LIMIT 1"
        ).bindparams(bindparam("emb", type_=Vector(128))),
        {"emb": embedding, "org_id": req.org_id},
    ).fetchone()

    # ── 4. Emotion analysis ─────────────────────────────────────────────────
    dominant_emotion = face_engine.get_emotion(image_bytes)
    emotion_confidence = 1.0 # default since DeepFace emotion doesn't return raw score easily

    # ── 5. Threshold gate ───────────────────────────────────────────────────
    if not match or match.distance > SIMILARITY_THRESHOLD:
        if not is_live:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Liveness check failed AND no matching face found.",
            )
        return VerifyResponse(
            status="unknown",
            user_id=None,
            full_name=None,
            distance=float(match.distance) if match else None,
            is_live=is_live,
            liveness_score=liveness_score,
            dominant_emotion=dominant_emotion,
            emotion_confidence=emotion_confidence,
        )

    logger.info(
        "Face verified: user_id=%s distance=%.4f emotion=%s",
        match.user_id, match.distance, dominant_emotion,
    )
    return VerifyResponse(
        status="verified",
        user_id=match.user_id,
        full_name=match.full_name,
        distance=float(match.distance),
        is_live=is_live,
        liveness_score=liveness_score,
        dominant_emotion=dominant_emotion,
        emotion_confidence=emotion_confidence,
    )


@router.get("/status/{user_id}")
def get_enrollment_status(
    user_id: int,
    db: Session = Depends(get_db),
    claims: dict = Depends(get_current_user_claims),
):
    """Check whether a user has an active face embedding registered."""
    row = db.execute(
        text(
            "SELECT id, model_name, enrolled_at FROM face_embeddings "
            "WHERE user_id = :uid AND is_active = 1"
        ),
        {"uid": user_id},
    ).fetchone()

    if not row:
        return {"enrolled": False, "user_id": user_id}

    return {
        "enrolled": True,
        "user_id": user_id,
        "embedding_id": row.id,
        "model_name": row.model_name,
        "enrolled_at": row.enrolled_at.isoformat() if row.enrolled_at else None,
    }


# ─── Granular Endpoints for Pipeline Proxy ────────────────────────────────────

@router.post("/extract")
def extract_embedding_granular(req: ImageRequest):
    image_bytes = _decode_image_bytes(req.image_base64)
    embedding = face_engine.get_embedding(image_bytes)
    return {"embedding": embedding}

@router.post("/liveness")
def extract_liveness_granular(req: ImageRequest):
    image_bytes = _decode_image_bytes(req.image_base64)
    is_live, score = liveness_service.detect_liveness(image_bytes)
    return {"is_live": is_live, "confidence": score}

@router.post("/emotion")
def extract_emotion_granular(req: ImageRequest):
    image_bytes = _decode_image_bytes(req.image_base64)
    emotion = face_engine.get_emotion(image_bytes)
    return {"emotion": emotion}

