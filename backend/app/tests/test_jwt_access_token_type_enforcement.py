import pytest
from fastapi import HTTPException

from app.api import deps


def test_get_current_user_rejects_refresh_token(monkeypatch):
    # Monkeypatch JWT decode to return a payload with type=refresh
    monkeypatch.setattr(
        deps.jwt,
        "decode",
        lambda token, secret, algorithms: {"sub": "1", "type": "refresh"},
    )

    # Monkeypatch blacklist check to always be false
    async def _blacklisted(_token: str) -> bool:
        return False

    monkeypatch.setattr(deps.security, "is_token_blacklisted", _blacklisted)

    # Minimal DB stub: should never be queried due to token type rejection.
    class DummyDB:
        # Keep typing/lint quiet: deps.get_current_user expects a SQLAlchemy Session,
        # but we intentionally use a stub to ensure DB is never called.
        def query(self, *args, **kwargs):
            raise AssertionError("DB should not be queried")

    async def _run():
        return await deps.get_current_user(db=DummyDB(), token="dummy")

    with pytest.raises(HTTPException) as excinfo:
        # Avoid pytest async plugins; run the coroutine directly.
        import asyncio

        asyncio.run(_run())

    assert excinfo.value.status_code == 401
    assert "Invalid token type" in str(excinfo.value.detail)

