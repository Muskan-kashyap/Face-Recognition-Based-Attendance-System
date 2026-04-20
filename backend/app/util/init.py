from sqlalchemy import text
from app.db.database import engine
from app.db.models import Base
import app.db.models # Ensure all are loaded

def create_tables():
    # Attempt to enable necessary Postgres extensions
    try:
        with engine.begin() as conn:
            conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'))
            conn.execute(text('CREATE EXTENSION IF NOT EXISTS "pgcrypto";'))
            conn.execute(text('CREATE EXTENSION IF NOT EXISTS "vector";'))
            # Create HNSW index for cosine distance on face embeddings
            # Note: 128 is the dimension of the embeddings
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_face_embeddings_hnsw 
                ON face_embeddings 
                USING hnsw (embedding vector_cosine_ops)
                WITH (m = 16, ef_construction = 64);
            """))
            print("PostgreSQL extensions and HNSW index enabled.")
    except Exception as e:
        print(f"Warning: Could not enable extensions automatically (probably permissions). Ensure they are enabled manually. {e}")
        
    Base.metadata.create_all(bind=engine)
