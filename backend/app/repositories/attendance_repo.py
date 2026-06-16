from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from sqlalchemy.orm import Session

from app.crud.crud_attendance import attendance as crud_attendance
from app.db.models.all_models import AttendanceLog
from app.schema.attendance import CheckInRequest


@dataclass(frozen=True)
class FaceMatchResult:
    user_id: Optional[int]


class AttendanceRepository:
    def find_user_by_face(
        self,
        db: Session,
        *,
        embedding: list[float],
        threshold: float,
    ) -> FaceMatchResult:
        user_id = crud_attendance.find_user_by_face(db, embedding=embedding, threshold=threshold)
        return FaceMatchResult(user_id=user_id)

    def log_check_in(self, db: Session, *, req: CheckInRequest, status: str) -> AttendanceLog:
        return crud_attendance.log_check_in(db, obj_in=req, status=status)


attendance_repo = AttendanceRepository()

