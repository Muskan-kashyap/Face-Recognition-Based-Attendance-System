import os
import sys
import secrets

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.db.database import SessionLocal
from app.db.models.all_models import Role, Organization, User
from app.core.security import get_password_hash
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_db():
    db = SessionLocal()
    
    # Create extensions if not exists
    try:
        db.execute(text('CREATE EXTENSION IF NOT EXISTS vector;'))
        db.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'))
        db.execute(text('CREATE EXTENSION IF NOT EXISTS pgcrypto;'))
        db.commit()
    except Exception as e:
        logger.warning(f"Failed to create extensions (might require superuser): {e}")
        db.rollback()

    # 1. Create Roles
    roles = ["Admin", "Manager", "Employee", "Device"]
    for r_name in roles:
        role = db.query(Role).filter(Role.name == r_name).first()
        if not role:
            role = Role(name=r_name, permissions=[])
            db.add(role)
    db.commit()

    admin_role = db.query(Role).filter(Role.name == "Admin").first()

    # 2. Create Initial Organization
    org = db.query(Organization).filter(Organization.legal_id == "HQ-001").first()
    if not org:
        org = Organization(
            name="HQ Default Org",
            legal_id="HQ-001",
            zkp_threshold=0.98
        )
        db.add(org)
        db.commit()
        db.refresh(org)

    # 3. Create Super Admin User
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        # Generate or use env var for seed password
        seed_password = os.getenv("SEED_ADMIN_PASSWORD", secrets.token_urlsafe(16))
        admin = User(
            org_id=org.id,
            role_id=admin_role.id,
            full_name="System Administrator",
            username="admin",
            email="admin@example.com",
            employee_id="ADM-001",
            hashed_password=get_password_hash(seed_password),
            is_active=True,
            is_deleted=False,
        )
        db.add(admin)
        db.commit()
        logger.info(f"Created admin user with auto-generated password: {seed_password}")

    logger.info("Database seeding completed.")
    db.close()

if __name__ == "__main__":
    seed_db()
