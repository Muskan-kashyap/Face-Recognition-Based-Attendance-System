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
    import logging

    logger = logging.getLogger(__name__)

    if not image_bytes:
        logger.warning("extract_liveness: empty image_bytes")
    else:
        logger.info("extract_liveness: bytes=%s", len(image_bytes))

    is_live_bool, score = liveness_service.detect_liveness(image_bytes)
    logger.info("extract_liveness: is_live_bool=%s score=%s", is_live_bool, score)
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
    # attendance_repo currently returns user_id only.
    # For Phase 3 end-to-end, we keep distance None until we extend the repo.
    res = attendance_repo.find_user_by_face(db, embedding=embedding, threshold=threshold)
    matched_user_id = getattr(res, "user_id", None)
    import logging
    logger = logging.getLogger(__name__)
    if matched_user_id is None:
        logger.warning("match_by_vector: no user matched (threshold=%s)", threshold)
    return MatchStageResult(matched_user_id=matched_user_id)




def extract_emotion(image_bytes: bytes) -> EmotionStageResult:
    # emotion analysis is best-effort; fallback handled in face_engine
    emotion = face_engine.get_emotion(image_bytes)
    return EmotionStageResult(emotion=emotion)

