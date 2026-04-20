from sqlalchemy.orm import Session
from app.db.models.all_models import Ticket
from app.schema.ticket import TicketCreate, TicketUpdate

class CRUDTicket:
    def create(self, db: Session, *, obj_in: TicketCreate, user_id: int, org_id: str) -> Ticket:
        db_obj = Ticket(
            user_id=user_id,
            org_id=org_id,
            title=obj_in.title,
            description=obj_in.description,
            priority=obj_in.priority
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_org(self, db: Session, *, org_id: str, skip: int = 0, limit: int = 100):
        return db.query(Ticket).filter(Ticket.org_id == org_id).offset(skip).limit(limit).all()

    def get_multi_by_user(self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100):
        return db.query(Ticket).filter(Ticket.user_id == user_id).offset(skip).limit(limit).all()

    def update(self, db: Session, *, db_obj: Ticket, obj_in: TicketUpdate) -> Ticket:
        if obj_in.status:
            db_obj.status = obj_in.status
        if obj_in.priority:
            db_obj.priority = obj_in.priority
        db.commit()
        db.refresh(db_obj)
        return db_obj

ticket = CRUDTicket()
