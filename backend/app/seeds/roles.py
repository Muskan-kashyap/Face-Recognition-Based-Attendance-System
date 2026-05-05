from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.models.all_models import Role

ROLES = [
    {"name": "superadmin", "permissions": {"all": True}},
    {"name": "admin", "permissions": {"manage_users": True}},
    {"name": "manager", "permissions": {"view_reports": True}},
    {"name": "employee", "permissions": {}},
]

def seed_roles(db: Session):
    for role_data in ROLES:
        existing = db.execute(
            select(Role).where(Role.name == role_data["name"])
        ).scalar()

        if existing:
            continue

        db.add(Role(**role_data))

    db.commit()
    print("✅ Roles seeded")