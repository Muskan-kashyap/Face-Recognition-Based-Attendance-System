from __future__ import annotations

import base64
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple

from sqlalchemy.orm import Session, joinedload

from app.db.models.all_models import AttendanceLog, User
from app.schema.attendance import AttendanceLogResponse, CheckInRequest
from app.crud.crud_attendance import attendance as crud_attendance

from app.services.analytics import analytics_service  # noqa: F401 (kept for future hooks)
from app.services.blockchain import background_blockchain_anchor

from app.repositories.attendance_repo import attendance_repo
from app.repositories.user_repo import user_repo

from app.services.attendance_pipeline.pipeline import FaceAttendancePipeline



logger = logging.getLogger(__name__)


@dataclass
class FacePipelineResult:
    user_id: int
    emotion: Optional[str]
    is_live: int


class AttendanceController:
    """Orchestrates the face/liveness/attendance logic.


    This is the Phase-4 extraction: keep existing API routes stable,
    but move in-route biometric orchestration into a testable controller.
    """

    def extract_image_bytes(self, image_base64: Optional[str]) -> Optional[bytes]:
        if not image_base64:
            return None
        try:
            return base64.b64decode(image_base64)
        except Exception:
            return None

    def run_face_pipeline(
        self,
        db: Session,
        *,
        image_bytes: bytes,
        existing_user_id: Optional[int],
    ) -> FacePipelineResult:
        """Detection → Liveness → Embedding → Vector search → Thresholding.

        Phase 4 extraction: delegate to FaceAttendancePipeline.
        """

        pipeline = FaceAttendancePipeline(attendance_repo=attendance_repo, user_repo=user_repo)
        out = pipeline.run(db, image_bytes=image_bytes, existing_user_id=existing_user_id)
        return FacePipelineResult(user_id=out.user_id, emotion=out.emotion, is_live=out.is_live)


    def compute_shift_status(self, db: Session, *, user_id: int, req_ts: datetime) -> str:
        status_str = "on_time"
        user = db.query(User).options(joinedload(User.shift)).filter(User.id == user_id).first()
        if user and user.shift:
            dt_start = datetime.combine(datetime.today(), user.shift.start_time)
            dt_check = datetime.combine(datetime.today(), req_ts.time())
            diff = (dt_check - dt_start).total_seconds() / 60
            if diff > user.shift.grace_period_mins:
                status_str = "late"
            elif diff < -user.shift.buffer_mins:
                status_str = "early"
        return status_str

    def log_check_in(self, db: Session, *, req: CheckInRequest, status: str) -> AttendanceLog:
        return crud_attendance.log_check_in(db, obj_in=req, status=status)

    def handle_check_in(
        self,
        db: Session,
        *,
        req: CheckInRequest,
        current_user: User,
        background_tasks,
    ) -> AttendanceLog:
        image_bytes = self.extract_image_bytes(req.image_base64)

        # SECURITY FIX (P0): Never let client-supplied user_id bypass biometrics.
        # This prevents spoofing by passing user_id without a face.
        req.user_id = None

        # Recognition requires an image. If no image is provided, reject.
        if not image_bytes:
            raise ValueError("Image required for recognition")

        try:
            pipeline_result = self.run_face_pipeline(
                db,
                image_bytes=image_bytes,
                existing_user_id=None,
            )
        except ValueError as e:
            raise e
        except LookupError as e:
            raise e

        req.user_id = pipeline_result.user_id
        req.is_live = pipeline_result.is_live
        req.emotion = pipeline_result.emotion

        if not req.user_id:
            raise LookupError("Identity not found")


        # Prevent check-in spoofing — users can only check in for themselves
        if current_user.role.name not in ["Admin", "Manager"] and req.user_id != current_user.id:
            raise PermissionError("You can only check in for yourself")


        status_str = self.compute_shift_status(db, user_id=req.user_id, req_ts=req.timestamp)

        log = self.log_check_in(db, req=req, status=status_str)

        # Background blockchain anchoring (existing behavior)
        payload = {
            "log_id": log.id,
            "user_id": log.user_id,
            "status": log.status,
            "timestamp": log.check_in.isoformat(),
        }
        background_tasks.add_task(background_blockchain_anchor, log.id, payload, "attendance")

        return log


attendance_controller = AttendanceController()

