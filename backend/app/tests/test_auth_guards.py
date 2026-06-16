import pytest

from app.api import deps


class DummyRole:
    def __init__(self, name: str):
        self.name = name
        self.permissions = []


class DummyUser:
    def __init__(self, role_name: str, is_active: bool = True):
        self.role = DummyRole(role_name)
        self.is_active = is_active


def test_require_admin_allows_superadmin(monkeypatch):
    # Instead of depending on DB, call require_admin with a dummy user.
    user = DummyUser("SuperAdmin")

    # get_current_active_user dependency isn't invoked here; we test the guard directly.
    # If require_admin depends on get_current_active_user in FastAPI, this unit test stays pure.
    import asyncio

    async def run():
        return await deps.require_admin(user)  # type: ignore[arg-type]

    loop = asyncio.get_event_loop()
    if loop.is_running():
        result = loop.create_task(run())
        loop.run_until_complete(result)
        return result.result()
    result = loop.run_until_complete(run())
    assert result is user



def test_require_admin_rejects_employee(monkeypatch):
    user = DummyUser("Employee")

    import asyncio
    from fastapi import HTTPException

    async def run():
        return await deps.require_admin(user)  # type: ignore[arg-type]

    with pytest.raises(HTTPException) as excinfo:
        asyncio.get_event_loop().run_until_complete(run())



    assert excinfo.value.status_code == 403

