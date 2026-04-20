from sqlalchemy.orm import Session
from app.db.models.all_models import Payroll
from app.schema.payroll import PayrollCreate, PayrollUpdate

class CRUDPayroll:
    def create(self, db: Session, *, obj_in: PayrollCreate, org_id: str) -> Payroll:
        db_obj = Payroll(
            user_id=obj_in.user_id,
            org_id=org_id,
            month=obj_in.month,
            year=obj_in.year,
            base_salary=obj_in.base_salary,
            deductions=obj_in.deductions,
            reimbursements_total=obj_in.reimbursements_total,
            total_salary=obj_in.total_salary,
            status="draft"
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_org(self, db: Session, *, org_id: str, month: int = None, year: int = None):
        query = db.query(Payroll).filter(Payroll.org_id == org_id)
        if month:
            query = query.filter(Payroll.month == month)
        if year:
            query = query.filter(Payroll.year == year)
        return query.all()

    def get_by_user(self, db: Session, *, user_id: int, month: int, year: int):
        return db.query(Payroll).filter(
            Payroll.user_id == user_id,
            Payroll.month == month,
            Payroll.year == year
        ).first()

    def update(self, db: Session, *, db_obj: Payroll, obj_in: PayrollUpdate) -> Payroll:
        db_obj.status = obj_in.status
        db.commit()
        db.refresh(db_obj)
        return db_obj

payroll = CRUDPayroll()
