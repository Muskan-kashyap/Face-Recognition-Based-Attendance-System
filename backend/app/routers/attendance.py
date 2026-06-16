from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query, Request

from sqlalchemy.orm import Session
from datetime import datetime
from typing import Any, List
import base64
import logging

from app.schema.attendance import CheckInRequest, AttendanceLogResponse
from app.db.database import get_db
from app.api import deps
from app.db.models.all_models import User, AttendanceLog
from app.services.analytics import analytics_service
from app.services.cache import cache_response
from app.services.attendance_controller import attendance_controller
from app.services.blockchain import background_blockchain_anchor
from app.core.rate_limit import rate_limit_dependency



router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/wellness-heatmap")
@cache_response(expire=300)
async def get_wellness_heatmap(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.require_permission("attendance.view")),
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
    request: Request,
    db: Session = Depends(get_db),
    req: CheckInRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(deps.get_current_active_user),
    _: bool = Depends(rate_limit_dependency(max_requests=10, window_seconds=60)),
) -> Any:

    """
    Refactored check-in with robust error handling and async anchoring.
    SECURE: Requires authenticated user. Users can only check in as themselves
    unless Admin/Manager.
    """
    try:
        log = attendance_controller.handle_check_in(
            db,
            req=req,
            current_user=current_user,
            background_tasks=background_tasks,
        )
        return log
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        # Preserve observability context (request_id is set by main.py middleware)
        request_id = getattr(getattr(request, "state", None), "request_id", None)
        logger.exception(f"Check-in failed [request_id={request_id}]: {e}")

        raise HTTPException(status_code=500, detail="Biometric processing failed")



@router.patch("/logs/{log_id}", response_model=AttendanceLogResponse)
def update_attendance_log(
    *,
    db: Session = Depends(get_db),
    log_id: int,
    status: str,
    current_user: User = Depends(deps.require_permission("attendance.override")),
    background_tasks: BackgroundTasks
) -> Any:

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

