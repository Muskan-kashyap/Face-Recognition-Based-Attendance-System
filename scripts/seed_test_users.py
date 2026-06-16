import sys
import os

# Add backend directory to sys.path so we can import from app
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.db.database import SessionLocal
from app.db.models.all_models import Role, User, Organization
from app.core.security import get_password_hash

def seed_users():
    db = SessionLocal()
    try:
        # Ensure we have a default organization
        org = db.query(Organization).first()
        if not org:
            org = Organization(name="Test Org", legal_id="123456789")
            db.add(org)
            db.commit()
            db.refresh(org)
            
        roles_to_create = ["SuperAdmin", "Admin", "Manager", "Employee"]
        
        print("\n--- TEST CREDENTIALS ---")
        
        for role_name in roles_to_create:
            # Check if role exists
            role = db.query(Role).filter(Role.name == role_name).first()
            if not role:
                role = Role(name=role_name)
                db.add(role)
                db.commit()
                db.refresh(role)
            
            # Check if user exists for this role
            email = f"{role_name.lower()}@test.com"
            user = db.query(User).filter(User.email == email).first()
            
            password = "TestPassword123!"
            
            if not user:
                user = User(
                    org_id=org.id,
                    role_id=role.id,
                    full_name=f"Test {role_name}",
                    username=f"test{role_name.lower()}",
                    email=email,
                    employee_id=f"EMP-{role_name[:3].upper()}-01",
                    hashed_password=get_password_hash(password),
                    is_active=1,
                    is_deleted=0
                )
                db.add(user)
                db.commit()
            
            print(f"\nRole: {role_name}")
            print(f"Email / Username: {email}")
            print(f"Password: {password}")
            
        print("\n------------------------")
            
    except Exception as e:
        print(f"Error seeding users: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_users()
