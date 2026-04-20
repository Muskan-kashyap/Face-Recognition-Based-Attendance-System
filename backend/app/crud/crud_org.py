from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.db.models.all_models import Organization
from app.schema.org import OrganizationCreate, OrganizationUpdate
from typing import Optional

class CRUDOrganization(CRUDBase[Organization, OrganizationCreate, OrganizationUpdate]):
    def get_by_legal_id(self, db: Session, *, legal_id: str) -> Optional[Organization]:
        return db.query(Organization).filter(Organization.legal_id == legal_id).first()

organization = CRUDOrganization(Organization)
