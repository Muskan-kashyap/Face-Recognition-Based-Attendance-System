from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.models.all_models import Organization


def seed_organization(db: Session):
    existing = db.execute(select(Organization)).scalar()

    if existing:
        print("⚠️ Organization already exists")
        return

    org = Organization(
        name="Test Company",
        legal_id="TEST123"
    )

    db.add(org)
    db.commit()

    print("✅ Organization seeded")