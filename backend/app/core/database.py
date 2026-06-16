# =============================================================================
#  core/database.py  —  Async SQLAlchemy engine (PostgreSQL + asyncpg)
# =============================================================================
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.core.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Engine — sourced exclusively from Settings (env-var backed)
# ---------------------------------------------------------------------------
engine: AsyncEngine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    echo=settings.DB_ECHO,
    pool_pre_ping=True,
    poolclass=NullPool,
)

AsyncSessionFactory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


# ---------------------------------------------------------------------------
# Bootstrap helpers (called once at startup)
# ---------------------------------------------------------------------------

async def bootstrap_extensions(conn: AsyncConnection) -> None:
    """Create required PostgreSQL extensions if they don't already exist."""
    for stmt in [
        "CREATE EXTENSION IF NOT EXISTS vector;",
        'CREATE EXTENSION IF NOT EXISTS "uuid-ossp";',
        "CREATE EXTENSION IF NOT EXISTS pgcrypto;",
    ]:
        try:
            await conn.execute(text(stmt))
        except Exception as exc:
            logger.warning("Could not create extension (%s): %s", stmt, exc)
    await conn.commit()
    logger.info("Extensions verified: vector, uuid-ossp, pgcrypto")


async def create_hnsw_index(conn: AsyncConnection) -> None:
    """Create HNSW index on face_embeddings if table exists."""
    try:
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_face_embed_hnsw
            ON face_embeddings USING hnsw (embedding vector_cosine_ops)
            WITH (m = 16, ef_construction = 64);
        """))
        await conn.commit()
    except Exception as exc:
        logger.warning("Could not create HNSW index (table may not exist yet): %s", exc)


async def init_db() -> None:
    """Create all tables, extensions, and indexes. Called from lifespan."""
    from app.db.models import Base  # noqa: PLC0415 (lazy import avoids circularity)
    async with engine.begin() as conn:
        await bootstrap_extensions(conn)
        await conn.run_sync(Base.metadata.create_all)
        await create_hnsw_index(conn)
    logger.info("Database schema ready")


async def drop_db() -> None:
    from app.db.models import Base  # noqa: PLC0415
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ---------------------------------------------------------------------------
# Session dependency (used by async routes)
# ---------------------------------------------------------------------------

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ---------------------------------------------------------------------------
# Context-manager version (used by background tasks / scripts)
# ---------------------------------------------------------------------------

@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ---------------------------------------------------------------------------
# Multi-tenancy helper (Removed)
# System relies on logical row-level isolation (org_id filtering)
# ---------------------------------------------------------------------------