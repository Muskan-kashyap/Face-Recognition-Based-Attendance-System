from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud.crud_org import organization as crud_org
from app.schema.org import OrganizationResponse, OrganizationCreate
from app.db.session import get_db
from app.api import deps
from app.db.models.all_models import User

router = APIRouter()

@router.post("/", response_model=OrganizationResponse)
def create_organization(
    *,
    db: Session = Depends(get_db),
    org_in: OrganizationCreate,
    current_user: User = Depends(deps.require_role(["admin"])),
):
         
    org = crud_org.get_by_legal_id(db, legal_id=org_in.legal_id)
    if org:
        raise HTTPException(
            status_code=400,
            detail="The organization with this legal ID already exists.",
        )
    org = crud_org.create(db, obj_in=org_in)
    return org
