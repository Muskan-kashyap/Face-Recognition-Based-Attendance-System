import os
import sys
import secrets

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.db.database import SessionLocal
from app.db.models.all_models import Permission, Role, RolePermission, User, UserRole, Organization
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

    # 1.1 Create default permission registry for RBAC
    default_permissions = [
        ("attendance.view", "Attendance"),
        ("attendance.checkin", "Attendance"),
        ("attendance.override", "Attendance"),
        ("attendance.export", "Attendance"),
        ("user.manage", "User Management"),
        ("org.manage", "Organization"),
        ("report.generate", "Reporting"),
        ("report.view", "Reporting"),
        ("device.register", "Device"),
    ]
    permissions_by_name = {}
    for perm_name, category in default_permissions:
        permission = db.query(Permission).filter(Permission.name == perm_name).first()
        if not permission:
            permission = Permission(name=perm_name, category=category)
            db.add(permission)
            db.flush()
        permissions_by_name[perm_name] = permission
    db.commit()

    admin_role = db.query(Role).filter(Role.name == "Admin").first()
    manager_role = db.query(Role).filter(Role.name == "Manager").first()
    employee_role = db.query(Role).filter(Role.name == "Employee").first()
    device_role = db.query(Role).filter(Role.name == "Device").first()

    # 1.2 Assign permissions to default roles
    role_permission_map = {
        "Admin": [perm_name for perm_name, _ in default_permissions],
        "Manager": ["attendance.view", "attendance.export", "report.view"],
        "Employee": ["attendance.view", "attendance.checkin"],
        "Device": ["attendance.checkin", "device.register"],
    }
    for role_name, perm_names in role_permission_map.items():
        role = db.query(Role).filter(Role.name == role_name).first()
        for perm_name in perm_names:
            perm = permissions_by_name[perm_name]
            rp = db.query(RolePermission).filter(
                RolePermission.role_id == role.id,
                RolePermission.permission_id == perm.id,
            ).first()
            if not rp:
                db.add(RolePermission(role_id=role.id, permission_id=perm.id))
    db.commit()

    admin_role = admin_role or db.query(Role).filter(Role.name == "Admin").first()

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
        # bcrypt has a 72-byte input limit — truncate generated passwords to be safe
        if len(seed_password) > 72:
            seed_password = seed_password[:72]
        admin = User(
            org_id=org.id,
            role_id=admin_role.id,
            full_name="System Administrator",
            username="admin",
            email="admin@example.com",
            employee_id="ADM-001",
            hashed_password=get_password_hash(seed_password),
            is_active=1,
            is_deleted=0,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        logger.info(f"Created admin user with auto-generated password: {seed_password}")

    # 3.1 Ensure admin user is assigned to the Admin role via user_roles join table
    existing_user_role = db.query(UserRole).filter(
        UserRole.user_id == admin.id,
        UserRole.role_id == admin_role.id,
    ).first()
    if not existing_user_role:
        db.add(UserRole(user_id=admin.id, role_id=admin_role.id))
        db.commit()

    logger.info("Database seeding completed.")
    db.close()

if __name__ == "__main__":
    seed_db()
