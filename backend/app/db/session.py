"""
Single source of truth for sync SQLAlchemy engine/session.
Production-grade connection pooling + extensions setup.
"""
import logging
from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from app.core.config import settings
from app.db.models.base import Base

logger = logging.getLogger(__name__)

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,    # Detect stale connections
    pool_size=10,          # Concurrent requests
    max_overflow=20,
)

SessionLocal = sessionmaker(
    bind=engine, 
    autocommit=False, 
    autoflush=False,
    expire_on_commit=False,
)

def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency generator."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_extensions_and_indexes():
    """Enable PostgreSQL extensions + HNSW index for pgvector."""
    try:
        with engine.begin() as conn:
            for stmt in [
                'CREATE EXTENSION IF NOT EXISTS "vector";',
                'CREATE EXTENSION IF NOT EXISTS "uuid-ossp";',
                'CREATE EXTENSION IF NOT EXISTS "pgcrypto";',
            ]:
                conn.execute(text(stmt))
            
            # HNSW index for cosine similarity on face embeddings
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_face_embed_hnsw
                ON face_embeddings USING hnsw (embedding vector_cosine_ops)
                WITH (m = 16, ef_construction = 64);
            """))
            conn.commit()
        logger.info("PostgreSQL extensions and HNSW index verified.")
    except Exception as e:
        logger.warning(f"Extensions/index setup warning (manual enable?): {e}")

# For Alembic/CLI usage
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
