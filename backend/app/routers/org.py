# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session

# from app.crud.crud_org import organization as crud_org
# from app.schema.org import OrganizationResponse, OrganizationCreate
# from app.db.database import get_db
# from app.api import deps
# from app.db.models.all_models import User

# router = APIRouter()

# @router.post("/", response_model=OrganizationResponse)
# def create_organization(
#     *,
#     db: Session = Depends(get_db),
#     org_in: OrganizationCreate,
#     current_user: User = Depends(deps.get_current_active_user),
# ):
#     """
#     Create a new organization (Tenant).
#     """
#     if current_user.role.name != "Admin":
#          raise HTTPException(status_code=403, detail="Not enough permissions")
         
#     org = crud_org.get_by_legal_id(db, legal_id=org_in.legal_id)
#     if org:
#         raise HTTPException(
#             status_code=400,
#             detail="The organization with this legal ID already exists.",
#         )
#     org = crud_org.create(db, obj_in=org_in)
#     return org

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.crud.crud_org import organization as crud_org
from app.schema.org import OrganizationResponse, OrganizationCreate
from app.db.database import get_db
from app.api import deps
from app.db.models.all_models import User

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=OrganizationResponse)
def create_organization(
    *,
    db: Session = Depends(get_db),
    org_in: OrganizationCreate,
    current_user: User = Depends(
        deps.require_admin_or_super_admin
    ),
):
    existing_org = crud_org.get_by_legal_id(
        db,
        legal_id=org_in.legal_id,
    )

    if existing_org:
        raise HTTPException(
            status_code=400,
            detail="The organization with this legal ID already exists.",
        )

    return crud_org.create(
        db,
        obj_in=org_in,
    )