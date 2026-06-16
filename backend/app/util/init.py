from sqlalchemy import text
from app.db.database import engine
from app.db.models import Base
import app.db.models # Ensure all are loaded

def create_tables():
    # Extensions must be committed before tables that use uuid_generate_v4(),
    # gen_random_bytes(), and vector columns are created.
    try:
        with engine.begin() as conn:
            conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'))
            conn.execute(text('CREATE EXTENSION IF NOT EXISTS "pgcrypto";'))
            conn.execute(text('CREATE EXTENSION IF NOT EXISTS "vector";'))
            print("PostgreSQL extensions enabled.")
    except Exception as e:
        print(f"Warning: Could not enable extensions automatically (probably permissions). Ensure they are enabled manually. {e}")

    Base.metadata.create_all(bind=engine)

    try:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_face_embeddings_hnsw 
                ON face_embeddings 
                USING hnsw (embedding vector_cosine_ops)
                WITH (m = 16, ef_construction = 64);
            """))
            print("HNSW index enabled.")
    except Exception as e:
        print(f"Warning: Could not create HNSW index automatically. Ensure it is enabled manually. {e}")
