from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.crud.crud_payroll import payroll as crud_payroll
from app.api import deps
from app.schema.payroll import PayrollResponse, PayrollCreate, PayrollUpdate
from app.db.models.all_models import User, Payroll, Reimbursement, AttendanceLog
from app.db.session import get_db
from app.services.blockchain import background_blockchain_anchor

router = APIRouter()


@router.get("/", response_model=List[PayrollResponse])
def read_payrolls(
    db: Session = Depends(get_db),
    month: Optional[int] = None,
    year: Optional[int] = None,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    # Employees see only their own, Managers/Admins see org-wide
    user_role = current_user.role.name.lower()
    if user_role in ["employee"]:
        return db.query(Payroll).filter(Payroll.user_id == current_user.id).all()
    return crud_payroll.get_multi_by_org(db, org_id=current_user.org_id, month=month, year=year)


@router.post("/generate", response_model=List[PayrollResponse])
async def generate_payroll(
    *,
    db: Session = Depends(get_db),
    payload: PayrollCreate,
    current_user: User = Depends(deps.require_role(["manager"])), # Hierarchy: manager, admin, superadmin
    background_tasks: BackgroundTasks
) -> Any:
    """
    OPTIMIZED: Single query approach to avoid N+1 bottlenecks.
    Accepts JSON body with month and year.
    """

    month = payload.month
    year = payload.year

    # 1. Bulk fetch deductions
    late_counts = db.query(
        AttendanceLog.user_id,
        func.count(AttendanceLog.id).label('count')
    ).join(User).filter(
        User.org_id == current_user.org_id,
        AttendanceLog.status == "late",
        func.extract('month', AttendanceLog.check_in) == month,
        func.extract('year', AttendanceLog.check_in) == year
    ).group_by(AttendanceLog.user_id).all()
    late_map = {row.user_id: row.count for row in late_counts}

    # 2. Bulk fetch reimbursements
    reimb_sums = db.query(
        Reimbursement.user_id,
        func.sum(Reimbursement.amount).label('total')
    ).filter(
        Reimbursement.org_id == current_user.org_id,
        Reimbursement.status == "approved",
        func.extract('month', Reimbursement.submitted_at) == month,
        func.extract('year', Reimbursement.submitted_at) == year
    ).group_by(Reimbursement.user_id).all()
    reimb_map = {row.user_id: float(row.total) for row in reimb_sums}

    users = db.query(User).filter(User.org_id == current_user.org_id, User.is_deleted == 0).all()
    results = []

    for u in users:
        base_salary = 50000.0
        deductions = float(late_map.get(u.id, 0) * 10.0)
        reimb_total = reimb_map.get(u.id, 0.0)
        total_salary = base_salary - deductions + reimb_total

        existing = crud_payroll.get_by_user(db, user_id=u.id, month=month, year=year)
        if existing:
            existing.base_salary, existing.deductions = base_salary, deductions
            existing.reimbursements_total, existing.total_salary = reimb_total, total_salary
            db.add(existing)
            payroll_obj = existing
        else:
            payroll_obj = crud_payroll.create(db, obj_in=PayrollCreate(
                user_id=u.id, month=month, year=year, base_salary=base_salary,
                deductions=deductions, reimbursements_total=reimb_total, total_salary=total_salary
            ), org_id=u.org_id)

        results.append(payroll_obj)
        payload = {"id": payroll_obj.id, "user": u.username, "total": total_salary}
        background_tasks.add_task(background_blockchain_anchor, payroll_obj.id, payload, "payroll")

    db.commit()
    return results


@router.patch("/{payroll_id}", response_model=PayrollResponse)
def update_payroll_status(
    *,
    db: Session = Depends(get_db),
    payroll_id: int,
    status_in: PayrollUpdate,
    current_user: User = Depends(deps.require_role(["manager"])),
    background_tasks: BackgroundTasks
) -> Any:

    # SECURE: Filter by org_id
    payroll_obj = db.query(Payroll).filter(
        Payroll.id == payroll_id,
        Payroll.org_id == current_user.org_id
    ).first()

    if not payroll_obj:
        raise HTTPException(status_code=404, detail="Payroll not found")

    updated = crud_payroll.update(db, db_obj=payroll_obj, obj_in=status_in)
    payload = {"id": updated.id, "status": updated.status, "by": current_user.username}
    background_tasks.add_task(background_blockchain_anchor, updated.id, payload, "payroll")

    return updated
