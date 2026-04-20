# =============================================================================
#  core/config.py
# =============================================================================
from __future__ import annotations
from functools import lru_cache
from typing import List, Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8",
        case_sensitive=False, extra="ignore",
    )

    # App
    APP_NAME: str = "Face Detection Attendance System"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"


    # Security
    SECRET_KEY: str = Field(default="dev-secret-key-change-in-production-32chars", min_length=32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60   # Matches .env.example; was 15 (conflict)

    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    BCRYPT_ROUNDS: int = 12

    # PostgreSQL
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "admin"
    POSTGRES_PASSWORD: str = "secure_pass"
    POSTGRES_DB: str = "attendance"
    DB_ECHO: bool = False

    @property
    def DATABASE_URL(self) -> str:
        return (f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}")

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        return (f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}")

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Face recognition
    FACE_MODEL_NAME: str = "Facenet"
    FACE_DISTANCE_THRESHOLD: float = 0.40
    LIVENESS_CHECK_ENABLED: bool = True
    EMBEDDING_DIMENSIONS: int = 128

    # ZKP
    ZKP_DEFAULT_THRESHOLD: float = 0.98

    # Blockchain
    BLOCKCHAIN_URL: str = "http://127.0.0.1:8545"  # Canonical key; BLOCKCHAIN_RPC_URL alias removed

    BLOCKCHAIN_ENABLED: bool = False

    # Geofencing
    GEOFENCE_ENABLED: bool = False
    GEOFENCE_RADIUS_METERS: int = 50

    # Attendance
    CHECKIN_COOLDOWN_MINUTES: int = 5

    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@attendance.local"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings: Settings = get_settings()