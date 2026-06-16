import functools
import hashlib
import json
import logging
from typing import Any, Optional
try:
    from diskcache import Cache
except ModuleNotFoundError:  # dev/env fallback
    Cache = None

from app.core.config import settings

logger = logging.getLogger(__name__)

# In a real 2026 prod env, this would be Redis.
# DiskCache is a high-performance alternative for edge/local deployments.
if Cache is not None:
    cache = Cache(settings.CACHE_DIR if hasattr(settings, "CACHE_DIR") else "/tmp/visioncore_cache")
else:
    # Non-blocking no-op cache when diskcache isn't installed.
    class _NoOpCache:
        def get(self, _key):
            return None

        def set(self, _key, _value, expire=None):
            return None

        def iterkeys(self):
            return iter(())

        def delete(self, _key):
            return None

    cache = _NoOpCache()


def _make_cache_key(func_name: str, args: tuple, kwargs: dict) -> str:
    """Create a deterministic, safe cache key from function call arguments."""
    try:
        key_data = f"{func_name}:{json.dumps(args, sort_keys=True, default=str)}:{json.dumps(kwargs, sort_keys=True, default=str)}"
    except (TypeError, ValueError):
        key_data = f"{func_name}:{id(args)}:{id(kwargs)}"
    return hashlib.sha256(key_data.encode()).hexdigest()


def cache_response(expire: int = 60):
    """
    Decorator to cache API responses.
    Only caches JSON-serializable responses (dicts, lists, primitives).
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            key = _make_cache_key(func.__name__, args, kwargs)
            try:
                result = cache.get(key)
                if result is not None:
                    return json.loads(result)
            except Exception as e:
                logger.warning("Cache read error for key %s: %s", key, e)

            response = await func(*args, **kwargs)

            try:
                serialized = json.dumps(response)
                cache.set(key, serialized, expire=expire)
            except (TypeError, ValueError):
                pass  # Non-serializable response; skip caching

            return response
        return wrapper
    return decorator


def invalidate_cache(key_prefix: str):
    """
    Clear cache keys starting with a prefix.
    """
    try:
        for key in cache.iterkeys():
            if key.startswith(key_prefix):
                cache.delete(key)
    except Exception as e:
        logger.warning("Cache invalidation error for prefix %s: %s", key_prefix, e)

