# =============================================================================
#  core/config.py
# =============================================================================
from __future__ import annotations
import json
import os
import secrets
import logging
from functools import lru_cache
from typing import List, Literal
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)

# Remove blank complex env vars so .env defaults can be used instead.
if os.environ.get("ALLOWED_ORIGINS", None) == "":
    os.environ.pop("ALLOWED_ORIGINS", None)


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
    SECRET_KEY: str = Field(default="", min_length=0)

    @field_validator("SECRET_KEY", mode="after")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if not v or len(v) < 32:
            # Auto-generate a secure key for development only
            generated = secrets.token_urlsafe(48)
            logger.critical(
                "SECRET_KEY was not provided or too short. A temporary key has been generated. "
                "Set a strong SECRET_KEY in your .env file for production!"
            )
            return generated
        return v

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    BCRYPT_ROUNDS: int = 12

    # PostgreSQL — credentials MUST come from environment variables in production
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = Field(default="", min_length=0)
    POSTGRES_DB: str = "attendance_db"
    DB_ECHO: bool = False

    @property
    def DATABASE_URL(self) -> str:
        # Encode the password here!
        password = quote_plus(self.POSTGRES_PASSWORD)
        return (f"postgresql://{self.POSTGRES_USER}:{password}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}")

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        # Encode the password here too!
        password = quote_plus(self.POSTGRES_PASSWORD)
        return (f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}")
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str):
            raw = v.strip()
            if raw == "":
                return []
            if raw.startswith("[") and raw.endswith("]"):
                try:
                    parsed = json.loads(raw)
                    if isinstance(parsed, list):
                        return [str(origin).strip() for origin in parsed if str(origin).strip()]
                except json.JSONDecodeError:
                    pass
            return [origin.strip() for origin in raw.split(",") if origin.strip()]
        return v

    # Face recognition
    FACE_MODEL_NAME: str = "Facenet"
    FACE_DISTANCE_THRESHOLD: float = 0.40
    LIVENESS_CHECK_ENABLED: bool = True
    EMBEDDING_DIMENSIONS: int = 128

    # ZKP
    ZKP_DEFAULT_THRESHOLD: float = 0.98

    # Blockchain
    BLOCKCHAIN_URL: str = "http://127.0.0.1:8545"
    BLOCKCHAIN_ENABLED: bool = False
    BLOCKCHAIN_PRIVATE_KEY: str = Field(default="", description="Private key for anchoring transactions")
    BLOCKCHAIN_CONTRACT_ADDRESS: str = Field(default="", description="Deployed AttendanceAudit contract address")

    @field_validator("BLOCKCHAIN_PRIVATE_KEY", "BLOCKCHAIN_CONTRACT_ADDRESS", mode="after")
    @classmethod
    def validate_blockchain_credentials(cls, v: str, info) -> str:
        # Pydantic V2 passes ValidationInfo as second argument
        if info.data.get("BLOCKCHAIN_ENABLED") and not v:
            logger.warning(f"{info.field_name} is missing but BLOCKCHAIN_ENABLED is True.")
        return v

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

    # Audit
    AUDIT_ENABLED: bool = True

    # Cache & Rate Limiting
    CACHE_DIR: str = "/tmp/visioncore_cache"
    REDIS_URL: str = "redis://localhost:6379/0"



@lru_cache
def get_settings() -> Settings:
    return Settings()


settings: Settings = get_settings()

