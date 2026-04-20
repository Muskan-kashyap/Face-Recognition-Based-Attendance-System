"""
database.py — Single source of truth for DB connection.
Credentials MUST be set via the DATABASE_URL environment variable in production.
The hardcoded fallback is for local development ONLY.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from urllib.parse import quote_plus

# SECURITY NOTE: Set DATABASE_URL in your .env file for production.
# Never commit real credentials to version control.
# SQLALCHEMY_DATABASE_URL = os.getenv(
#     "DATABASE_URL",
#     "postgresql+psycopg2://postgres:password@localhost:5432/attendance"
# )
# Get variables with fallbacks
user = os.getenv("DB_USER", "postgres")
password = os.getenv("DB_PASSWORD", "Hrhk@9090")
host = os.getenv("DB_HOST", "localhost")
port = os.getenv("DB_PORT", "5432")
name = os.getenv("DB_NAME", "attendance")

# URL-encode the password to handle the '@' symbol
safe_password = quote_plus(password)

SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{user}:{safe_password}@{host}:{port}/{name}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,   # Detect stale connections
    pool_size=10,         # Connection pool for concurrent requests
    max_overflow=20
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
