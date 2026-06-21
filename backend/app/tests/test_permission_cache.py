import sys
import os
import time
import types
import pytest

# Ensure backend package is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


# NOTE:
# This project currently does not include a concrete permission-cache implementation.
# The tests below are deliberately lightweight and serve as a contract for the
# cache resolver behavior expected by Phase 4.1.
#
# When the cache module is introduced, these tests should be updated to import
# the real cache service.


def _simulate_cache_key(user_id: int) -> str:
    return f"rbac:user:{user_id}"


class PermissionCacheContract:
    """In-memory contract used for unit-testing cache semantics."""

    def __init__(self, ttl_seconds: int = 900):
        self.ttl_seconds = ttl_seconds
        self._store = {}  # key -> (value, expires_at)

    def get(self, key: str):
        item = self._store.get(key)
        if not item:
            return None
        value, expires_at = item
        if time.time() >= expires_at:
            self._store.pop(key, None)
            return None
        return value

    def set(self, key: str, value):
        self._store[key] = (value, time.time() + self.ttl_seconds)

    def invalidate_user(self, user_id: int):
        self._store.pop(_simulate_cache_key(user_id), None)


def test_cache_set_and_get():
    cache = PermissionCacheContract(ttl_seconds=900)
    key = _simulate_cache_key(7)
    cache.set(key, {"permissions": ["users.view"]})

    assert cache.get(key) == {"permissions": ["users.view"]}


def test_cache_invalidation_on_role_change_contract():
    cache = PermissionCacheContract(ttl_seconds=900)
    key = _simulate_cache_key(7)

    cache.set(key, {"permissions": ["users.view"]})
    assert cache.get(key) is not None

    cache.invalidate_user(7)
    assert cache.get(key) is None


def test_cache_expiry_contract():
    cache = PermissionCacheContract(ttl_seconds=1)
    key = _simulate_cache_key(7)

    cache.set(key, {"permissions": ["users.view"]})
    assert cache.get(key) is not None

    time.sleep(1.1)
    assert cache.get(key) is None

