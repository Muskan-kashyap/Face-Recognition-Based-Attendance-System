from app.db.session import SessionLocal

from app.seeds.roles import seed_roles
from app.seeds.organization import seed_organization
from app.seeds.users import seed_users


def run():
    db = SessionLocal()
    try:
        seed_roles(db)
        seed_organization(db)
        seed_users(db)
    finally:
        db.close()


if __name__ == "__main__":
    run()