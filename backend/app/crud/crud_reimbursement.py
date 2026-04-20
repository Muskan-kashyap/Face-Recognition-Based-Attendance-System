from sqlalchemy.orm import Session
from app.db.models.all_models import Reimbursement
from app.schema.reimbursement import ReimbursementCreate, ReimbursementUpdate
from datetime import datetime

class CRUDReimbursement:
    def create(self, db: Session, *, obj_in: ReimbursementCreate, user_id: int, org_id: str) -> Reimbursement:
        db_obj = Reimbursement(
            user_id=user_id,
            org_id=org_id,
            amount=obj_in.amount,
            reason=obj_in.reason,
            receipt_url=obj_in.receipt_url
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_org(self, db: Session, *, org_id: str, skip: int = 0, limit: int = 100):
        return db.query(Reimbursement).filter(Reimbursement.org_id == org_id).offset(skip).limit(limit).all()

    def get_multi_by_user(self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100):
        return db.query(Reimbursement).filter(Reimbursement.user_id == user_id).offset(skip).limit(limit).all()

    def update(self, db: Session, *, db_obj: Reimbursement, obj_in: ReimbursementUpdate, approver_id: int = None) -> Reimbursement:
        if obj_in.status:
            db_obj.status = obj_in.status
            if obj_in.status in ["approved", "rejected"]:
                db_obj.processed_at = datetime.utcnow()
                db_obj.approved_by = approver_id
        db.commit()
        db.refresh(db_obj)
        return db_obj

reimbursement = CRUDReimbursement()
