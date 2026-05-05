from app.db.session import engine
from app.db.models.base import Base

# 🔥 Import models HERE (not in base)
from app.db.models import all_models  

def init_db():
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created")

if __name__ == "__main__":
    init_db()