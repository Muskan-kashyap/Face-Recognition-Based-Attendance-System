from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.db.models.all_models import AttendanceLog
from app.schema.attendance import CheckInRequest
from pydantic import BaseModel

class CheckInUpdate(BaseModel):
    pass

class CRUDAttendance(CRUDBase[AttendanceLog, CheckInRequest, CheckInUpdate]):
    def log_check_in(self, db: Session, *, obj_in: CheckInRequest, status: str) -> AttendanceLog:
        db_obj = AttendanceLog(
            user_id=obj_in.user_id,
            # Always use server-side UTC timestamp — never trust client-supplied time.
            # BUG-10 fix: client previously controlled check_in via obj_in.timestamp.
            check_in=datetime.now(timezone.utc),
            status=status,
            emotion=obj_in.emotion,
            emotion_score=obj_in.emotion_score,
            is_live=obj_in.is_live,
            source=obj_in.source,
            geofence_pass=obj_in.geofence_pass,
            gps_lat=obj_in.gps_lat,
            gps_lng=obj_in.gps_lng,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def find_user_by_face(self, db: Session, *, embedding: list[float], threshold: float = 0.5) -> Optional[int]:
        from app.db.models.all_models import FaceEmbedding
        from sqlalchemy import select, func
        
        # Find the closest embedding using pgvector L2 distance
        stmt = (
            select(FaceEmbedding, FaceEmbedding.embedding.l2_distance(embedding).label("distance"))
            .where(FaceEmbedding.is_active == 1)
            .order_by(FaceEmbedding.embedding.l2_distance(embedding))
            .limit(1)
        )
        row = db.execute(stmt).first()
        
        # CRITICAL: Only return a match if the distance is within the allowed threshold.
        # Without this check, ANY face would match the closest person in the DB.
        if row and row.distance <= threshold:
            return row.FaceEmbedding.user_id
        return None

attendance = CRUDAttendance(AttendanceLog)
