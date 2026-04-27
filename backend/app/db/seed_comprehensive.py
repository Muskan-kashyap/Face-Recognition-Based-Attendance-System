#!/usr/bin/env python3
"""
Comprehensive database seeding script for QA testing.
Creates realistic users across all roles with edge cases.
"""
import os
import sys
import uuid
from datetime import datetime, timezone
from typing import List

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import text
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models.all_models import (
    Role, Organization, Department, Shift, User
)
from app.core.security import get_password_hash
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_comprehensive():
    """Seed database with realistic test data."""
    db = SessionLocal()
    
    try:
        # 1. Ensure extensions
        db.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'))
        db.execute(text('CREATE EXTENSION IF NOT EXISTS pgcrypto;'))
        db.commit()
        
        # 2. Create Organization
        org = db.query(Organization).filter(Organization.legal_id == "TEST-ORG-001").first()
        if not org:
            org = Organization(
                name="VisionCore Test Organization",
                legal_id="TEST-ORG-001",
                zkp_threshold=0.98
            )
            db.add(org)
            db.commit()
            db.refresh(org)
            logger.info(f"Created organization: {org.id}")
        else:
            logger.info(f"Organization exists: {org.id}")

        # 3. Create Departments
        departments_data = [
            ("Engineering", "Software development and AI teams"),
            ("HR", "Human resources and compliance"),
            ("Operations", "Facility and device management"),
            ("Management", "Executive leadership")
        ]
        dept_ids = {}
        for name, desc in departments_data:
            dept = db.query(Department).filter(Department.name == name, Department.org_id == org.id).first()
            if not dept:
                dept = Department(
                    org_id=org.id,
                    name=name,
                    description=desc
                )
                db.add(dept)
                db.commit()
                db.refresh(dept)
                logger.info(f"Created department: {dept.id} - {name}")
            dept_ids[name] = dept.id

        # 4. Create Shifts
        shifts_data = [
            ("Morning", "09:00", "17:00", 5, 15),
            ("Afternoon", "13:00", "21:00", 10, 15),
            ("Night", "21:00", "05:00", 15, 30)
        ]
        shift_ids = {}
        for name, start, end, grace, buffer in shifts_data:
            shift = db.query(Shift).filter(Shift.shift_name == name, Shift.org_id == org.id).first()
            if not shift:
                shift = Shift(
                    org_id=org.id,
                    shift_name=name,
                    start_time=start,
                    end_time=end,
                    grace_period_mins=grace,
                    buffer_mins=buffer
                )
                db.add(shift)
                db.commit()
                db.refresh(shift)
                logger.info(f"Created shift: {shift.id} - {name}")
            shift_ids[name] = shift.id

        # 5. Create Roles
        roles_data = ["Super Admin", "Admin", "Manager", "Employee"]
        role_ids = {}
        for role_name in roles_data:
            role = db.query(Role).filter(Role.name == role_name).first()
            if not role:
                role = Role(name=role_name, permissions=[])
                db.add(role)
                db.commit()
                db.refresh(role)
                logger.info(f"Created role: {role.id} - {role_name}")
            role_ids[role_name] = role.id

        # 6. Create Users (3 per role + edge cases)
        users_data = {
            "Super Admin": [
                ("Dr. Elena Vasquez", "elena.vasquez@visioncore.com", "SuperE1!2024"),
                ("Marcus Chen", "marcus.chen@visioncore.com", "SuperM2#2024"),
                ("Dr. Sophia Patel", "sophia.patel@visioncore.com", "SuperS3@2024"),
                ("Dheeraj Saroha","btcl220010159010gjust@visioncore.com","Dheeraj@1907")
            ],
            "Admin": [
                ("James Rodriguez", "james.rodriguez@visioncore.com", "AdminJ1!2024"),
                ("Lisa Nguyen", "lisa.nguyen@visioncore.com", "AdminL2#2024"),
                ("David Kim", "david.kim@visioncore.com", "AdminD3@2024")
            ],
            "Manager": [
                ("Sarah Thompson", "sarah.thompson@visioncore.com", "MgrS1!2024"),
                ("Michael Brown", "michael.brown@visioncore.com", "MgrM2#2024"),
                ("Emma Wilson", "emma.wilson@visioncore.com", "MgrE3@2024")
            ],
            "Employee": [
                ("John Davis", "john.davis@visioncore.com", "EmpJ1!2024"),
                ("Maria Garcia", "maria.garcia@visioncore.com", "EmpM2#2024"),
                ("Robert Johnson", "robert.johnson@visioncore.com", "EmpR3@2024")
            ]
        }

        created_users = []
        for role_name, users in users_data.items():
            role_id = role_ids[role_name]
            dept_id = dept_ids.get("Management" if role_name in ["Super Admin", "Admin"] else "Engineering", None)
            shift_id = shift_ids["Morning"]
            
            for full_name, email, password in users:
                username = email.split("@")[0]
                employee_id = f"{role_name[:3].upper()}-{uuid.uuid4().hex[:4].upper()}"
                
                # Check if user exists by email or username
                existing_email = db.query(User).filter(User.email == email).first()
                existing_username = db.query(User).filter(User.username == username).first()
                if existing_email:
                    logger.warning(f"User exists (email): {email}")
                    continue
                if existing_username:
                    logger.warning(f"User exists (username): {username}")
                    continue
                
                user = User(
                    org_id=org.id,
                    role_id=role_id,
                    dept_id=dept_id,
                    shift_id=shift_id,
                    full_name=full_name,
                    username=username,
                    email=email,
                    employee_id=employee_id,
                    hashed_password=get_password_hash(password),
                    is_active=1,
                    is_deleted=0
                )
                db.add(user)
                created_users.append({
                    "email": email,
                    "password": password,
                    "role": role_name,
                    "employee_id": employee_id
                })
        
        # 7. Edge Cases
        # Deactivated user
        existing_inactive = db.query(User).filter(
            (User.email == "inactive.test@visioncore.com") | (User.username == "inactive.test")
        ).first()
        if not existing_inactive:
            deactivated_user = User(
                org_id=org.id,
                role_id=role_ids["Employee"],
                dept_id=dept_ids["Engineering"],
                shift_id=shift_ids["Morning"],
                full_name="Inactive Test User",
                username="inactive.test",
                email="inactive.test@visioncore.com",
                employee_id="EMP-INACT",
                hashed_password=get_password_hash("Inactive1!2024"),
                is_active=0,  # DEACTIVATED
                is_deleted=0
            )
            db.add(deactivated_user)
            created_users.append({
                "email": "inactive.test@visioncore.com",
                "password": "Inactive1!2024",
                "role": "Employee (DEACTIVATED)",
                "employee_id": "EMP-INACT"
            })
        else:
            logger.warning("User exists: inactive.test@visioncore.com")

        # Incomplete profile
        existing_incomplete = db.query(User).filter(
            (User.email == "john.doe.incomplete@visioncore.com") | (User.username == "john.doe.incomplete")
        ).first()
        if not existing_incomplete:
            incomplete_user = User(
                org_id=org.id,
                role_id=role_ids["Employee"],
                full_name="John Doe",  # Incomplete name
                username="john.doe.incomplete",
                email="john.doe.incomplete@visioncore.com",
                employee_id="EMP-INCMP",
                hashed_password=get_password_hash("Incomplete1!2024"),
                is_active=1,
                is_deleted=0
            )
            db.add(incomplete_user)
            created_users.append({
                "email": "john.doe.incomplete@visioncore.com",
                "password": "Incomplete1!2024",
                "role": "Employee (INCOMPLETE)",
                "employee_id": "EMP-INCMP"
            })
        else:
            logger.warning("User exists: john.doe.incomplete@visioncore.com")

        db.commit()
        logger.info("✅ Seeding completed successfully!")
        logger.info("📋 Test Credentials:")
        for user in created_users:
            logger.info(f"  👤 {user['role']:<25} | {user['email']:<30} | PW: {user['password']}")

    except Exception as e:
        logger.error(f"❌ Seeding failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_comprehensive()
