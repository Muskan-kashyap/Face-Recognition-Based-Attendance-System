import functools
import json
from typing import Any, Optional
from diskcache import Cache
from app.core.config import settings

# In a real 2026 prod env, this would be Redis. 
# DiskCache is a high-performance alternative for edge/local deployments.
cache = Cache("/tmp/visioncore_cache")

def cache_response(expire: int = 60):
    """
    Decorator to cache API responses.
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Create a unique key based on function name and arguments
            key = f"{func.__name__}:{args}:{kwargs}"
            result = cache.get(key)
            
            if result is not None:
                return json.loads(result)
            
            # Execute the function
            response = await func(*args, **kwargs)
            
            # Store in cache
            cache.set(key, json.dumps(response), expire=expire)
            return response
        return wrapper
    return decorator

def invalidate_cache(key_prefix: str):
    """
    Clear cache keys starting with a prefix.
    """
    for key in cache.iterkeys():
        if key.startswith(key_prefix):
            cache.delete(key)
