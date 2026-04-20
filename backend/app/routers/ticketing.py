from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.crud.crud_ticket import ticket as crud_ticket
from app.api import deps
from app.schema.ticket import TicketResponse, TicketCreate, TicketUpdate
from app.db.models.all_models import User, Ticket, BlockchainAuditLog
from app.db.database import get_db
from app.services.blockchain import blockchain_service

router = APIRouter()

async def background_blockchain_anchor(db: Session, ref_id: int, payload: dict, ref_type: str):
    try:
        tx_hash = blockchain_service.anchor_record(ref_id, ref_type, payload)
        audit = BlockchainAuditLog(
            ref_id=ref_id, ref_type=ref_type,
            record_hash=blockchain_service.generate_record_hash(payload),
            tx_hash=tx_hash
        )
        db.add(audit)
        db.commit()
    except Exception: pass

async def escalate_tickets_job(db: Session):
    threshold = datetime.utcnow() - timedelta(hours=48)
    tickets = db.query(Ticket).filter(Ticket.status == "open", Ticket.created_at < threshold).all()
    for t in tickets:
        t.status, t.priority = "escalated", "critical"
        payload = {"ticket_id": t.id, "reason": "auto_escalation_48h"}
        await background_blockchain_anchor(db, t.id, payload, "ticket")
    db.commit()

@router.get("/", response_model=List[TicketResponse])
def read_tickets(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    if current_user.role.name in ["Admin", "Manager"]:
        return crud_ticket.get_multi_by_org(db, org_id=current_user.org_id, skip=skip, limit=limit)
    return crud_ticket.get_multi_by_user(db, user_id=current_user.id, skip=skip, limit=limit)

@router.post("/", response_model=TicketResponse)
async def create_ticket(
    *,
    db: Session = Depends(get_db),
    ticket_in: TicketCreate,
    current_user: User = Depends(deps.get_current_active_user),
    background_tasks: BackgroundTasks
) -> Any:
    ticket = crud_ticket.create(db, obj_in=ticket_in, user_id=current_user.id, org_id=current_user.org_id)
    payload = {"id": ticket.id, "user": current_user.username, "title": ticket.title}
    background_tasks.add_task(background_blockchain_anchor, db, ticket.id, payload, "ticket")
    background_tasks.add_task(escalate_tickets_job, db)
    return ticket

@router.patch("/{ticket_id}", response_model=TicketResponse)
def update_ticket(
    *,
    db: Session = Depends(get_db),
    ticket_id: int,
    ticket_in: TicketUpdate,
    current_user: User = Depends(deps.get_current_active_user),
    background_tasks: BackgroundTasks
) -> Any:
    # SECURE: Filter by org_id
    ticket_obj = db.query(Ticket).filter(Ticket.id == ticket_id, Ticket.org_id == current_user.org_id).first()
    if not ticket_obj:
        raise HTTPException(status_code=404, detail="Ticket not found")
        
    if current_user.role.name not in ["Admin", "Manager"] and ticket_obj.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
        
    updated = crud_ticket.update(db, db_obj=ticket_obj, obj_in=ticket_in)
    payload = {"id": updated.id, "status": updated.status, "by": current_user.username}
    background_tasks.add_task(background_blockchain_anchor, db, updated.id, payload, "ticket")
    return updated
