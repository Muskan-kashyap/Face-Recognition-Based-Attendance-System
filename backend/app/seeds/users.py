from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.models.all_models import User, Role, Organization
from app.core.security import get_password_hash

USERS = [
    ("btcl220010159010gjust@gmail.com", "Dheeraj@2002", "superadmin"),
    ("superadmin@test.com", "Super@123", "superadmin"),
    ("admin@test.com", "Admin@123", "admin"),
    ("manager@test.com", "Manager@123", "manager"),
    ("employee@test.com", "Employee@123", "employee"),
]

def seed_users(db: Session):
    org = db.execute(select(Organization)).scalar()

    if not org:
        print("❌ No organization found. Run organization seed first.")
        return

    for email, password, role_name in USERS:

        role = db.execute(
            select(Role).where(Role.name == role_name)
        ).scalar()

        if not role:
            print(f"❌ Role '{role_name}' not found")
            continue

        existing = db.execute(
            select(User).where(User.email == email)
        ).scalar()

        if existing:
            continue

        user = User(
            email=email,
            username=email.split("@")[0],
            full_name=email.split("@")[0],
            employee_id=f"EMP-{email[:5]}",
            hashed_password=get_password_hash(password),
            role_id=role.id,
            org_id=org.id,
            is_active=1,
            is_deleted=0
        )

        db.add(user)

    db.commit()
    print("✅ Users seeded")