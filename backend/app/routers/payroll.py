from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.crud.crud_payroll import payroll as crud_payroll
from app.api import deps
from app.schema.payroll import PayrollResponse, PayrollCreate, PayrollUpdate
from app.db.models.all_models import User, Payroll, Reimbursement, AttendanceLog, BlockchainAuditLog
from app.db.database import get_db
from app.services.blockchain import blockchain_service

router = APIRouter()

async def background_blockchain_anchor(db: Session, ref_id: int, payload: dict, ref_type: str):
    try:
        tx_hash = blockchain_service.anchor_record(ref_id, ref_type, payload)
        audit = BlockchainAuditLog(
            ref_id=ref_id,
            ref_type=ref_type,
            record_hash=blockchain_service.generate_record_hash(payload),
            tx_hash=tx_hash
        )
        db.add(audit)
        db.commit()
    except Exception:
        pass # Log in production

@router.get("/", response_model=List[PayrollResponse])
def read_payrolls(
    db: Session = Depends(get_db),
    month: int = None,
    year: int = None,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    if current_user.role.name not in ["Admin", "Manager"]:
        return db.query(Payroll).filter(Payroll.user_id == current_user.id).all()
    return crud_payroll.get_multi_by_org(db, org_id=current_user.org_id, month=month, year=year)

@router.post("/generate", response_model=List[PayrollResponse])
async def generate_payroll(
    *,
    db: Session = Depends(get_db),
    month: int,
    year: int,
    current_user: User = Depends(deps.get_current_active_user),
    background_tasks: BackgroundTasks
) -> Any:
    """
    OPTIMIZED: Single query approach to avoid N+1 bottlenecks.
    """
    if current_user.role.name not in ["Admin", "Manager"]:
        raise HTTPException(status_code=403, detail="Forbidden")
        
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
            db.add(existing); payroll_obj = existing
        else:
            payroll_obj = crud_payroll.create(db, obj_in=PayrollCreate(
                user_id=u.id, month=month, year=year, base_salary=base_salary,
                deductions=deductions, reimbursements_total=reimb_total, total_salary=total_salary
            ), org_id=u.org_id)
        
        results.append(payroll_obj)
        payload = {"id": payroll_obj.id, "user": u.username, "total": total_salary}
        background_tasks.add_task(background_blockchain_anchor, db, payroll_obj.id, payload, "payroll")

    db.commit()
    return results

@router.patch("/{payroll_id}", response_model=PayrollResponse)
def update_payroll_status(
    *,
    db: Session = Depends(get_db),
    payroll_id: int,
    status_in: PayrollUpdate,
    current_user: User = Depends(deps.get_current_active_user),
    background_tasks: BackgroundTasks
) -> Any:
    if current_user.role.name not in ["Admin", "Manager"]:
        raise HTTPException(status_code=403, detail="Forbidden")
        
    # SECURE: Filter by org_id
    payroll_obj = db.query(Payroll).filter(
        Payroll.id == payroll_id,
        Payroll.org_id == current_user.org_id
    ).first()
    
    if not payroll_obj:
        raise HTTPException(status_code=404, detail="Payroll not found")
        
    updated = crud_payroll.update(db, db_obj=payroll_obj, obj_in=status_in)
    payload = {"id": updated.id, "status": updated.status, "by": current_user.username}
    background_tasks.add_task(background_blockchain_anchor, db, updated.id, payload, "payroll")
    db.commit()
    
    return updated
