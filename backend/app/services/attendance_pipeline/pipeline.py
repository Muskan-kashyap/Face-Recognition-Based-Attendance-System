from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.repositories.attendance_repo import AttendanceRepository
from app.repositories.user_repo import UserRepository
from app.services.attendance_pipeline.metric import get_face_matching_config
from app.services.attendance_pipeline import stages


@dataclass(frozen=True)
class FacePipelineOutput:
    user_id: int
    emotion: Optional[str]
    is_live: int


class FaceAttendancePipeline:
    """Detection → Liveness → Embedding → Vector search → Thresholding."""

    def __init__(
        self,
        *,
        attendance_repo: AttendanceRepository,
        user_repo: UserRepository,
    ):
        self.attendance_repo = attendance_repo
        self.user_repo = user_repo

    def run(
        self,
        db: Session,
        *,
        image_bytes: bytes,
        existing_user_id: Optional[int] = None,
    ) -> FacePipelineOutput:
        liveness_res = stages.extract_liveness(image_bytes)
        is_live = liveness_res.is_live

        if existing_user_id is not None:
            return FacePipelineOutput(user_id=existing_user_id, emotion=None, is_live=is_live)

        embedding_res = stages.extract_embedding(image_bytes)
        match_cfg = get_face_matching_config()

        match_res = stages.match_by_vector(
            db,
            embedding=embedding_res.embedding,
            threshold=match_cfg.threshold,
            attendance_repo=self.attendance_repo,
        )

        if not match_res.matched_user_id:
            raise LookupError("Identity not found")

        emotion_res = stages.extract_emotion(image_bytes)

        return FacePipelineOutput(
            user_id=match_res.matched_user_id,
            emotion=emotion_res.emotion,
            is_live=is_live,
        )

