# # =============================================================================
# #  core/config.py
# # =============================================================================
# from __future__ import annotations
# import secrets
# import logging
# from functools import lru_cache
# from typing import List, Literal
# from pydantic import Field, field_validator
# from pydantic_settings import BaseSettings, SettingsConfigDict
# from urllib.parse import quote_plus
# import os

# logger = logging.getLogger(__name__)


# class Settings(BaseSettings):
#     model_config = SettingsConfigDict(
#         env_file=".env", env_file_encoding="utf-8",
#         case_sensitive=False, extra="ignore",
#     )

#     # App
#     APP_NAME: str = "Face Detection Attendance System"
#     APP_VERSION: str = "1.0.0"
#     ENVIRONMENT: Literal["development", "staging", "production"] = "development"
#     DEBUG: bool = False
#     API_V1_STR: str = "/api/v1"

#     # Security
#     SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(48), min_length=32)

#     @field_validator("SECRET_KEY", mode="after")
#     @classmethod
#     def validate_secret_key(cls, v: str, info) -> str:
#         # Access other fields during validation
#         environment = info.data.get("ENVIRONMENT", "development")
#         if environment == "production" and len(v) < 32:
#             raise ValueError("SECRET_KEY must be ≥32 chars in production. Set in .env.")
#         if len(v) < 32:
#             logger.warning("Generated dev SECRET_KEY. Set strong key in .env for prod.")
#         return v


    
#     @property
#     def DATABASE_URL(self) -> str:
#         # Encode the password here!
#         password = quote_plus(self.POSTGRES_PASSWORD)
#         return (f"postgresql://{self.POSTGRES_USER}:{password}"
#                 f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}")

#     @property
#     def ASYNC_DATABASE_URL(self) -> str:
#         # Encode the password here too!
#         password = quote_plus(self.POSTGRES_PASSWORD)
#         return (f"postgresql+asyncpg://{self.POSTGRES_USER}:{password}"
#                 f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}")
#     # CORS
#     ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

#     # Face recognition
#     FACE_MODEL_NAME: str = "Facenet"
#     FACE_DISTANCE_THRESHOLD: float = 0.40
#     LIVENESS_CHECK_ENABLED: bool = True
#     EMBEDDING_DIMENSIONS: int = 128

#     # ZKP
#     ZKP_DEFAULT_THRESHOLD: float = 0.98

#     # Blockchain
#     BLOCKCHAIN_URL: str = "http://127.0.0.1:8545"
#     BLOCKCHAIN_ENABLED: bool = False

#     # Geofencing
#     GEOFENCE_ENABLED: bool = False
#     GEOFENCE_RADIUS_METERS: int = 50

#     # Attendance
#     CHECKIN_COOLDOWN_MINUTES: int = 5

#     # Email
#     SMTP_HOST: str = "smtp.gmail.com"
#     SMTP_PORT: int = 587
#     SMTP_USER: str = ""
#     SMTP_PASSWORD: str = ""
#     EMAIL_FROM: str = "noreply@attendance.local"

# # JWT & Auth
#     ALGORITHM: str = "HS256"
#     ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
#     REFRESH_TOKEN_EXPIRE_DAYS: int = 7
#     LOGIN_LOCKOUT_MINUTES: int = 15
#     MAX_LOGIN_ATTEMPTS: int = 5
    
#     # Frontend URL for password reset links
#     FRONTEND_URL: str = "http://localhost:3000"

#     # Cache & Rate Limiting
#     CACHE_DIR: str = "/tmp/visioncore_cache"
#     REDIS_URL: str = "redis://localhost:6379/0"


# @lru_cache
# def get_settings() -> Settings:
#     return Settings()


# settings: Settings = get_settings()

# =============================================================================
#  core/config.py
# =============================================================================
from __future__ import annotations
import secrets
import logging
from functools import lru_cache
from typing import List, Literal
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from urllib.parse import quote_plus
import os

logger = logging.getLogger(__name__)


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
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(48), min_length=32)

    # FIX ADDED HERE (JWT Algorithm)
    ALGORITHM: Literal["HS256"] = "HS256"

    # PostgreSQL Configuration
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "Hrhk@9090"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "attendance_db"

    @field_validator("SECRET_KEY", mode="after")
    @classmethod
    def validate_secret_key(cls, v: str, info) -> str:
        environment = info.data.get("ENVIRONMENT", "development")
        if environment == "production" and len(v) < 32:
            raise ValueError("SECRET_KEY must be ≥32 chars in production. Set in .env.")
        if len(v) < 32:
            logger.warning("Generated dev SECRET_KEY. Set strong key in .env for prod.")
        return v

    

    # Database
    @property
    def DATABASE_URL(self) -> str:
        password = quote_plus(self.POSTGRES_PASSWORD)
        return (f"postgresql://{self.POSTGRES_USER}:{password}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}")

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        password = quote_plus(self.POSTGRES_PASSWORD)
        return (f"postgresql+asyncpg://{self.POSTGRES_USER}:{password}"
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
    BLOCKCHAIN_URL: str = "http://127.0.0.1:8545"
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

    # JWT & Auth
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    LOGIN_LOCKOUT_MINUTES: int = 15
    MAX_LOGIN_ATTEMPTS: int = 5

    # Frontend URL
    FRONTEND_URL: str = "http://localhost:3000"

    # Cache & Rate Limiting
    CACHE_DIR: str = "/tmp/visioncore_cache"
    REDIS_URL: str = "redis://localhost:6379/0"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings: Settings = get_settings()
