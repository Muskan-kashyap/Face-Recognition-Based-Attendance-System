from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session

from app.crud.crud_reimbursement import reimbursement as crud_reimbursement
from app.api import deps
from app.schema.reimbursement import ReimbursementResponse, ReimbursementCreate, ReimbursementUpdate
from app.db.models.all_models import User, Reimbursement
from app.db.session import get_db
from app.services.blockchain import background_blockchain_anchor

router = APIRouter()


@router.get("/", response_model=List[ReimbursementResponse])
def read_claims(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = Query(None),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    query = db.query(Reimbursement).filter(Reimbursement.org_id == current_user.org_id)
    user_role = current_user.role.name.lower()
    if user_role == "employee":
        query = query.filter(Reimbursement.user_id == current_user.id)
    if status:
        query = query.filter(Reimbursement.status == status)
    return query.order_by(Reimbursement.submitted_at.desc()).offset(skip).limit(limit).all()


@router.post("/", response_model=ReimbursementResponse)
async def create_claim(
    *,
    db: Session = Depends(get_db),
    claim_in: ReimbursementCreate,
    current_user: User = Depends(deps.get_current_active_user),
    background_tasks: BackgroundTasks
) -> Any:
    claim = crud_reimbursement.create(db, obj_in=claim_in, user_id=current_user.id, org_id=current_user.org_id)
    payload = {"id": claim.id, "user": current_user.username, "amount": float(claim.amount)}
    background_tasks.add_task(background_blockchain_anchor, claim.id, payload, "reimbursement")
    return claim


@router.patch("/{claim_id}/approve", response_model=ReimbursementResponse)
def approve_claim(
    *,
    db: Session = Depends(get_db),
    claim_id: int,
    claim_in: ReimbursementUpdate,
    current_user: User = Depends(deps.require_role(["manager"])),
    background_tasks: BackgroundTasks
) -> Any:

    # SECURE: Filter by org_id
    claim_obj = db.query(Reimbursement).filter(Reimbursement.id == claim_id, Reimbursement.org_id == current_user.org_id).first()
    if not claim_obj:
        raise HTTPException(status_code=404, detail="Claim not found")

    updated = crud_reimbursement.update(db, db_obj=claim_obj, obj_in=claim_in, approver_id=current_user.id)
    payload = {"id": updated.id, "status": updated.status, "by": current_user.username}
    background_tasks.add_task(background_blockchain_anchor, updated.id, payload, "reimbursement")
    return updated
