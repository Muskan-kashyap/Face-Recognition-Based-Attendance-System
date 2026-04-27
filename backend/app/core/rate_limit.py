"""
Simple in-memory rate limiter for auth endpoints.
Production: Replace with Redis-backed limiter (e.g., Slowapi + Redis).
"""
import logging
from fastapi import HTTPException, Request
from app.core.config import settings
import redis.asyncio as redis_async

logger = logging.getLogger(__name__)

# Redis Client
redis_client = redis_async.from_url(settings.REDIS_URL, decode_responses=True)

def rate_limit_dependency(max_requests: int = 5, window_seconds: int = 60):
    """
    FastAPI dependency for rate limiting by client IP using Redis.
    Usage: Depends(rate_limit_dependency(max_requests=5, window_seconds=60))
    """
    async def _check(request: Request):
        client_ip = request.client.host if request.client else "unknown"
        key = f"rate_limit:{request.url.path}:{client_ip}"
        
        # Redis pipeline for atomic transaction
        async with redis_client.pipeline(transaction=True) as pipe:
            try:
                # Increment the counter
                pipe.incr(key)
                # Set expiry if it's the first request
                pipe.expire(key, window_seconds, nx=True)
                # Execute pipeline
                results = await pipe.execute()
                
                current_requests = results[0]
                
                if current_requests > max_requests:
                    logger.warning("Rate limit exceeded for %s on %s", client_ip, request.url.path)
                    raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")
                
            except redis_async.RedisError as e:
                logger.error(f"Redis rate limiter error: {e}")
                # Fail open to not block legitimate requests if Redis goes down, or fail closed
                # Here we will fail open but log the error
                pass
                
        return True
    return _check

