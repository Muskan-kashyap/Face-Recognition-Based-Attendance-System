from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Any, List
import base64
import logging

from app.crud.crud_attendance import attendance as crud_attendance
from app.schema.attendance import CheckInRequest, AttendanceLogResponse
from app.db.database import get_db
from app.api import deps
from app.db.models.all_models import User, AttendanceLog
from app.services.analytics import analytics_service
from app.services.blockchain import background_blockchain_anchor
from app.services.cache import cache_response
from app.services.face_engine import face_engine
from app.services.liveness import liveness_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/wellness-heatmap")
@cache_response(expire=300)
async def get_wellness_heatmap(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    STRICT MULTI-TENANCY: Uses org_id from authenticated user.
    """
    return analytics_service.get_wellness_heatmap(db, current_user.org_id)


@router.get("/productivity-report")
def get_productivity_report(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    return analytics_service.get_productivity_growth(db, current_user.org_id)


@router.get("/logs", response_model=List[AttendanceLogResponse])
def get_logs(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: str = Query(None),
    date_from: datetime = Query(None),
    date_to: datetime = Query(None),
) -> Any:
    """
    Get attendance logs with pagination and optional filtering.
    """
    query = db.query(AttendanceLog).join(User).filter(
        User.org_id == current_user.org_id,
        AttendanceLog.is_deleted == 0
    )
    if status:
        query = query.filter(AttendanceLog.status == status)
    if date_from:
        query = query.filter(AttendanceLog.check_in >= date_from)
    if date_to:
        query = query.filter(AttendanceLog.check_in <= date_to)

    return query.order_by(AttendanceLog.check_in.desc()).offset(skip).limit(limit).all()


@router.post("/check-in", response_model=AttendanceLogResponse)
async def check_in(
    *,
    db: Session = Depends(get_db),
    req: CheckInRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Refactored check-in with robust error handling and async anchoring.
    SECURE: Requires authenticated user. Users can only check in as themselves
    unless Admin/Manager.
    """
    image_bytes = None
    if req.image_base64:
        try:
            image_bytes = base64.b64decode(req.image_base64)
        except Exception:
            raise HTTPException(status_code=400, detail="Malformed base64 image data")

    # 1. Liveness & Face Identification
    if image_bytes:
        try:
            is_live, _ = liveness_service.detect_liveness(image_bytes)
            req.is_live = 1 if is_live else 0

            if not req.user_id:
                embedding = face_engine.get_embedding(image_bytes)
                if not embedding:
                    raise HTTPException(status_code=400, detail="No face detected")

                user_id = crud_attendance.find_user_by_face(db, embedding=embedding)
                if not user_id:
                    raise HTTPException(status_code=404, detail="Identity not found")
                req.user_id = user_id
                req.emotion = face_engine.get_emotion(image_bytes)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"AI Processing Error: {e}")
            raise HTTPException(status_code=500, detail="Biometric processing failed")

    if not req.user_id:
        raise HTTPException(status_code=400, detail="User identification required")

    # SECURE: Prevent check-in spoofing — users can only clock in as themselves
    if current_user.role.name not in ["Admin", "Manager"] and req.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only check in for yourself")

    # 2. Logic Branch: Shift Status
    status_str = "on_time"
    from sqlalchemy.orm import joinedload
    user = db.query(User).options(joinedload(User.shift)).filter(User.id == req.user_id).first()
    if user and user.shift:
        dt_start = datetime.combine(datetime.today(), user.shift.start_time)
        dt_check = datetime.combine(datetime.today(), req.timestamp.time())
        diff = (dt_check - dt_start).total_seconds() / 60
        if diff > user.shift.grace_period_mins:
            status_str = "late"
        elif diff < -user.shift.buffer_mins:
            status_str = "early"

    # 3. Save Record
    log = crud_attendance.log_check_in(db, obj_in=req, status=status_str)

    # 4. Offload Blockchain to Background
    payload = {
        "log_id": log.id,
        "user_id": log.user_id,
        "status": log.status,
        "timestamp": log.check_in.isoformat()
    }
    background_tasks.add_task(background_blockchain_anchor, log.id, payload, "attendance")

    return log


@router.patch("/logs/{log_id}", response_model=AttendanceLogResponse)
def update_attendance_log(
    *,
    db: Session = Depends(get_db),
    log_id: int,
    status: str,
    current_user: User = Depends(deps.get_current_active_user),
    background_tasks: BackgroundTasks
) -> Any:
    if current_user.role.name not in ["Admin", "Manager"]:
        raise HTTPException(status_code=403, detail="Unauthorized")

    # SECURE: Ensure the log belongs to the admin's organization
    log = db.query(AttendanceLog).join(User).filter(
        AttendanceLog.id == log_id,
        User.org_id == current_user.org_id
    ).first()

    if not log:
        raise HTTPException(status_code=404, detail="Log not found in your organization")

    log.status = status
    db.commit()
    db.refresh(log)

    payload = {"log_id": log.id, "new_status": log.status, "by": current_user.username}
    background_tasks.add_task(background_blockchain_anchor, log.id, payload, "manual_override")

    return log
