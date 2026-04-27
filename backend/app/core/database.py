# =============================================================================
#  core/database.py
# =============================================================================
from __future__ import annotations
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (AsyncConnection, AsyncEngine, AsyncSession,
                                     async_sessionmaker, create_async_engine)
from sqlalchemy.pool import NullPool
from app.core.config import settings

import os
from urllib.parse import quote_plus
from sqlalchemy import create_all, create_engine
logger = logging.getLogger(__name__)
# 1. Get the raw password from environment
raw_password = os.getenv("DB_PASSWORD")

# 2. URL-encode the password to handle the '@' symbol
safe_password = quote_plus(raw_password)

# 3. Construct the URL using the safe password
SQLALCHEMY_DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{safe_password}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

engine: AsyncEngine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    echo=settings.DB_ECHO,
    pool_pre_ping=True,
    poolclass=NullPool,
)

AsyncSessionFactory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine, class_=AsyncSession,
    expire_on_commit=False, autoflush=False, autocommit=False,
)

async def bootstrap_extensions(conn: AsyncConnection) -> None:
    for stmt in [
        "CREATE EXTENSION IF NOT EXISTS vector;",
        'CREATE EXTENSION IF NOT EXISTS "uuid-ossp";',
        "CREATE EXTENSION IF NOT EXISTS pgcrypto;",
    ]:
        await conn.execute(text(stmt))
    await conn.commit()
    logger.info("Extensions verified: vector, uuid-ossp, pgcrypto")

async def create_hnsw_index(conn: AsyncConnection) -> None:
    await conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_face_embed_hnsw
        ON face_embeddings USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64);
    """))
    await conn.commit()

async def init_db() -> None:
    from app.db.models import Base
    async with engine.begin() as conn:
        await bootstrap_extensions(conn)
        await conn.run_sync(Base.metadata.create_all)
        await create_hnsw_index(conn)
    logger.info("Database schema ready")

async def drop_db() -> None:
    from app.db.models import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

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

async def provision_tenant_schema(org_id: str) -> None:
    schema = "org_" + org_id.replace("-", "_")
    async with engine.begin() as conn:
        await conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
    logger.info("Tenant schema provisioned: %s", schema)

@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise