from typing import Any, List
import logging

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    BackgroundTasks,
    status,
)
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.crud.crud_payroll import payroll as crud_payroll
from app.api import deps
from app.schema.payroll import (
    PayrollResponse,
    PayrollCreate,
    PayrollUpdate,
)
from app.db.models.all_models import (
    User,
    Payroll,
    Reimbursement,
    AttendanceLog,
    BlockchainAuditLog,
)
from app.db.database import (
    get_db,
    SessionLocal,
)
from app.services.blockchain import blockchain_service

router = APIRouter()

logger = logging.getLogger(__name__)

DEFAULT_BASE_SALARY = 50000.0
LATE_DEDUCTION_AMOUNT = 10.0


def is_admin_or_manager(user: User) -> bool:
    if user.role is None:
        return False

    role = user.role.name.strip().lower()

    return role in {
        "admin",
        "manager",
        "superadmin",
        "super admin",
    }


async def background_blockchain_anchor(
    ref_id: int,
    payload: dict,
    ref_type: str,
):
    """
    Background blockchain anchoring.
    """

    db = SessionLocal()

    try:
        tx_hash = blockchain_service.anchor_record(
            ref_id,
            ref_type,
            payload,
        )

        audit = BlockchainAuditLog(
            ref_id=ref_id,
            ref_type=ref_type,
            record_hash=blockchain_service.generate_record_hash(
                payload
            ),
            tx_hash=tx_hash,
        )

        db.add(audit)
        db.commit()

    except Exception:
        db.rollback()

        logger.exception(
            "Blockchain anchoring failed for %s:%s",
            ref_type,
            ref_id,
        )

    finally:
        db.close()


@router.get("/", response_model=List[PayrollResponse])
def read_payrolls(
    db: Session = Depends(get_db),
    month: int | None = None,
    year: int | None = None,
    current_user: User = Depends(
        deps.get_current_active_user
    ),
) -> Any:

    if not is_admin_or_manager(current_user):
        return (
            db.query(Payroll)
            .filter(
                Payroll.user_id == current_user.id
            )
            .all()
        )

    return crud_payroll.get_multi_by_org(
        db,
        org_id=current_user.org_id,
        month=month,
        year=year,
    )


@router.post(
    "/generate",
    response_model=List[PayrollResponse],
)
async def generate_payroll(
    *,
    db: Session = Depends(get_db),
    month: int,
    year: int,
    current_user: User = Depends(
        deps.get_current_active_user
    ),
    background_tasks: BackgroundTasks,
) -> Any:

    if not is_admin_or_manager(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or Manager privileges required.",
        )

    if month < 1 or month > 12:
        raise HTTPException(
            status_code=400,
            detail="Month must be between 1 and 12.",
        )

    try:

        late_counts = (
            db.query(
                AttendanceLog.user_id,
                func.count(
                    AttendanceLog.id
                ).label("count"),
            )
            .join(User)
            .filter(
                User.org_id == current_user.org_id,
                AttendanceLog.status == "late",
                func.extract(
                    "month",
                    AttendanceLog.check_in,
                )
                == month,
                func.extract(
                    "year",
                    AttendanceLog.check_in,
                )
                == year,
            )
            .group_by(
                AttendanceLog.user_id
            )
            .all()
        )

        late_map = {
            row.user_id: row.count
            for row in late_counts
        }

        reimb_sums = (
            db.query(
                Reimbursement.user_id,
                func.sum(
                    Reimbursement.amount
                ).label("total"),
            )
            .filter(
                Reimbursement.org_id
                == current_user.org_id,
                Reimbursement.status
                == "approved",
                func.extract(
                    "month",
                    Reimbursement.submitted_at,
                )
                == month,
                func.extract(
                    "year",
                    Reimbursement.submitted_at,
                )
                == year,
            )
            .group_by(
                Reimbursement.user_id
            )
            .all()
        )

        reimb_map = {
            row.user_id: float(
                row.total or 0
            )
            for row in reimb_sums
        }

        users = (
            db.query(User)
            .filter(
                User.org_id
                == current_user.org_id,
                User.is_deleted == 0,
            )
            .all()
        )

        existing_count = (
            db.query(Payroll)
            .filter(
                Payroll.org_id
                == current_user.org_id,
                Payroll.month == month,
                Payroll.year == year,
            )
            .count()
        )

        if existing_count > 0:
            logger.warning(
                "Regenerating payroll for %s/%s",
                month,
                year,
            )

        existing_payrolls = {
            p.user_id: p
            for p in (
                db.query(Payroll)
                .filter(
                    Payroll.org_id
                    == current_user.org_id,
                    Payroll.month == month,
                    Payroll.year == year,
                )
                .all()
            )
        }

        results = []
        blockchain_jobs = []

        for u in users:

            base_salary = DEFAULT_BASE_SALARY

            deductions = (
                float(
                    late_map.get(u.id, 0)
                )
                * LATE_DEDUCTION_AMOUNT
            )

            reimb_total = reimb_map.get(
                u.id,
                0.0,
            )

            total_salary = (
                base_salary
                - deductions
                + reimb_total
            )

            existing = existing_payrolls.get(
                u.id
            )

            if existing:

                existing.base_salary = (
                    base_salary
                )

                existing.deductions = (
                    deductions
                )

                existing.reimbursements_total = (
                    reimb_total
                )

                existing.total_salary = (
                    total_salary
                )

                payroll_obj = existing

            else:

                payroll_obj = crud_payroll.create(
                    db,
                    obj_in=PayrollCreate(
                        user_id=u.id,
                        month=month,
                        year=year,
                        base_salary=base_salary,
                        deductions=deductions,
                        reimbursements_total=reimb_total,
                        total_salary=total_salary,
                    ),
                    org_id=u.org_id,
                )

            db.flush()

            results.append(
                payroll_obj
            )

            blockchain_jobs.append(
                (
                    payroll_obj.id,
                    {
                        "id": payroll_obj.id,
                        "user": getattr(
                            u,
                            "username",
                            str(u.id),
                        ),
                        "total": total_salary,
                    },
                )
            )

        db.commit()

        for payroll_id, payload in blockchain_jobs:

            background_tasks.add_task(
                background_blockchain_anchor,
                payroll_id,
                payload,
                "payroll",
            )

        return results

    except Exception as exc:

        db.rollback()

        logger.exception(
            "Payroll generation failed: %s",
            str(exc),
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Payroll generation failed.",
        )


@router.patch(
    "/{payroll_id}",
    response_model=PayrollResponse,
)
def update_payroll_status(
    *,
    db: Session = Depends(get_db),
    payroll_id: int,
    status_in: PayrollUpdate,
    current_user: User = Depends(
        deps.get_current_active_user
    ),
    background_tasks: BackgroundTasks,
) -> Any:

    if not is_admin_or_manager(
        current_user
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or Manager privileges required.",
        )

    try:

        payroll_obj = (
            db.query(Payroll)
            .filter(
                Payroll.id == payroll_id,
                Payroll.org_id
                == current_user.org_id,
            )
            .first()
        )

        if not payroll_obj:
            raise HTTPException(
                status_code=404,
                detail="Payroll not found",
            )

        updated = crud_payroll.update(
            db=db,
            db_obj=payroll_obj,
            obj_in=status_in,
        )

        db.commit()

        payload = {
            "id": updated.id,
            "status": updated.status,
            "by": getattr(
                current_user,
                "username",
                str(current_user.id),
            ),
        }

        background_tasks.add_task(
            background_blockchain_anchor,
            updated.id,
            payload,
            "payroll",
        )

        return updated

    except HTTPException:
        raise

    except Exception as exc:

        db.rollback()

        logger.exception(
            "Payroll update failed: %s",
            str(exc),
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update payroll.",
        )