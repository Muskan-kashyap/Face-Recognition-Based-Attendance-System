from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from sqlalchemy.orm import Session

from app.repositories.attendance_repo import AttendanceRepository
from app.repositories.user_repo import UserRepository
from app.core.config import settings
from app.services.face_engine import face_engine
from app.services.liveness import liveness_service


@dataclass(frozen=True)
class LivenessStageResult:
    is_live: int


@dataclass(frozen=True)
class EmbeddingStageResult:
    embedding: list[float]


@dataclass(frozen=True)
class MatchStageResult:
    matched_user_id: Optional[int]


@dataclass(frozen=True)
class EmotionStageResult:
    emotion: Optional[str]


def extract_liveness(image_bytes: bytes) -> LivenessStageResult:
    is_live_bool, _ = liveness_service.detect_liveness(image_bytes)
    return LivenessStageResult(is_live=1 if is_live_bool else 0)


def extract_embedding(image_bytes: bytes) -> EmbeddingStageResult:
    embedding = face_engine.get_embedding(image_bytes)
    if not embedding:
        raise ValueError("No face detected / could not extract embedding")
    return EmbeddingStageResult(embedding=embedding)


def match_by_vector(
    db: Session,
    *,
    embedding: list[float],
    threshold: float,
    attendance_repo: AttendanceRepository,
) -> MatchStageResult:
    res = attendance_repo.find_user_by_face(db, embedding=embedding, threshold=threshold)
    return MatchStageResult(matched_user_id=res.user_id)


def extract_emotion(image_bytes: bytes) -> EmotionStageResult:
    # emotion analysis is best-effort; fallback handled in face_engine
    emotion = face_engine.get_emotion(image_bytes)
    return EmotionStageResult(emotion=emotion)

