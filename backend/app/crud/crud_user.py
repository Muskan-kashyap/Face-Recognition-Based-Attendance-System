import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
from app.core.security import get_password_hash
from app.db.models.all_models import User, FaceEmbedding, Organization, Role


class CRUDUser:
    def get(self, db: Session, *, id: int) -> Optional[User]:
        return db.query(User).filter(User.id == id, User.is_deleted == 0).first()

    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(
            User.email == email,
            User.is_deleted == 0
        ).first()

    def create(self, db: Session, *, obj_in: Dict[str, Any]) -> User:
        """
        Creates a user from a dict payload (used by /auth/register and /users/).
        Expects keys: email, password, name/full_name, role, organization.
        """
        # Validate required fields
        required_fields = ["email", "password"]
        for field in required_fields:
            if not obj_in.get(field):
                raise ValueError(f"Missing required field: {field}")

        name = obj_in.get("name") or obj_in.get("full_name", "")
        org_name = obj_in.get("organization", "default")

        # 1. Get or Create Organization
        org = db.query(Organization).filter(Organization.name == org_name).first()
        if not org:
            org = Organization(
                name=org_name,
                legal_id=f"ORG-{org_name.upper()[:4]}-{int(datetime.now(timezone.utc).timestamp())}"
            )
            db.add(org)
            db.commit()
            db.refresh(org)

        # 2. Get or Create Role
        # SECURITY FIX (P0): prevent arbitrary role creation from public inputs.
        role_name = obj_in.get("role", "Employee")
        if role_name != "Employee":
            role_name = "Employee"

        role = db.query(Role).filter(Role.name == role_name).first()
        if not role:
            role = Role(name=role_name, permissions=[])
            db.add(role)
            db.commit()
            db.refresh(role)


        # 3. Create User — use org_id from payload if injected by admin flow
        org_id = obj_in.get("org_id") or org.id

        # BUG-11 fix: derive a unique username by appending a numeric suffix if needed.
        base_username = obj_in["email"].split("@")[0]
        username = base_username
        suffix = 1
        while db.query(User).filter(User.username == username).first():
            username = f"{base_username}{suffix}"
            suffix += 1

        db_obj = User(
            email=obj_in["email"],
            hashed_password=get_password_hash(obj_in["password"]),
            full_name=name,
            username=username,
            org_id=org_id,
            role_id=role.id,
            employee_id=f"EMP-{uuid.uuid4().hex[:6].upper()}",
            is_active=1,   # Integer column: 1=active, 0=suspended
            is_deleted=0,  # Integer column: 0=active, 1=soft-deleted
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def enroll_face(self, db: Session, *, user_id: int, embedding: list) -> FaceEmbedding:
        """
        Stores or replaces the face embedding for a user.
        Marks any previous embedding as inactive.
        """
        # Deactivate previous
        db.query(FaceEmbedding).filter(
            FaceEmbedding.user_id == user_id,
            FaceEmbedding.is_active == True
        ).update({"is_active": False})
        db.commit()

        face_obj = FaceEmbedding(
            user_id=user_id,
            embedding=embedding,
            model_name="face_recognition",
            is_active=True
        )
        db.add(face_obj)
        db.commit()
        db.refresh(face_obj)
        return face_obj


user = CRUDUser()
