import uuid
import time
import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.routers import api_router

from app.core.config import settings
from sqlalchemy import text
from app.db.session import engine, create_extensions_and_indexes
from app.core.security import redis_client
# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Extensions/indexes handled idempotently on first health check or Alembic
    logger.info("Application startup complete. Use 'alembic upgrade head' for schema.")
    yield
    logger.info("Shutting down application...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
)


# ── Security Headers Middleware ──────────────────────────────────────────────
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        return response


app.add_middleware(SecurityHeadersMiddleware)


# ── CORS ─────────────────────────────────────────────────────────────────────
# Production safety: reject wildcard origins
_cors_origins = settings.ALLOWED_ORIGINS
if settings.ENVIRONMENT == "production" and "*" in _cors_origins:
    logger.critical("CORS wildcard detected in production! Falling back to safe defaults.")
    _cors_origins = []

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# ── Request Logging & Timing Middleware ──────────────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    request.state.request_id = request_id
    start_time = time.time()

    logger.info(f"[{request_id}] {request.method} {request.url.path} - Started")

    try:
        response = await call_next(request)
    except Exception as exc:
        logger.exception(f"[{request_id}] Unhandled exception: {exc}")
        raise

    process_time = (time.time() - start_time) * 1000
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time-Ms"] = str(round(process_time, 2))
    logger.info(
        f"[{request_id}] {request.method} {request.url.path} - {response.status_code} - {process_time:.2f}ms"
    )
    return response


# ── Global Exception Handler ─────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception at {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred. Please try again later."},
    )


# ── Health Check ─────────────────────────────────────────────────────────────
# @app.get("/health", tags=["health"])
# def health_check():
#     """Health check with DB connectivity verification."""
#     db_healthy = False
#     try:
#         with engine.connect() as conn:
#             conn.execute(text("SELECT 1"))
#             db_healthy = True
#     except Exception as e:
#         logger.warning(f"Health check DB connection failed: {e}")

#     status_code = 200 if db_healthy else 503
#     return JSONResponse(
#         status_code=status_code,
#         content={
#             "status": "healthy" if db_healthy else "degraded",
#             "database": "connected" if db_healthy else "disconnected",
#             "version": settings.APP_VERSION,
#             "environment": settings.ENVIRONMENT,
#         },
#     )

@app.get("/health", tags=["health"])
async def health_check():
    db_healthy = False
    redis_healthy = False

    # DB Check
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            db_healthy = True
    except Exception as e:
        print("DB ERROR:", e)

    # Redis Check
    try:
        await redis_client.set("health_check", "ok")
        val = await redis_client.get("health_check")
        if val == "ok":
            redis_healthy = True
    except Exception as e:
        print("REDIS ERROR:", e)

    overall_status = db_healthy and redis_healthy

    return JSONResponse(
        status_code=200 if overall_status else 503,
        content={
            "status": "healthy" if overall_status else "degraded",
            "database": "connected" if db_healthy else "disconnected",
            "redis": "connected" if redis_healthy else "disconnected",
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
        },
    )


@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.APP_NAME} v{settings.APP_VERSION}"}


# ── API Routers ──────────────────────────────────────────────────────────────
app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
