import sys
import os
import types
import pytest

# Make backend package importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.api import deps
from fastapi import HTTPException

# Importing real app.api.deps here; tests use monkeypatch to isolate side effects.



class DummyRole:
    def __init__(self, name, permissions=None, id=1):
        self.name = name
        self.permissions = permissions or []
        self.id = id


class DummyUser:
    def __init__(self, user_id=1, role=None, role_id=1, is_active=True):
        self.id = user_id
        self.role = role or DummyRole("Employee", permissions=[])
        self.role_id = role_id
        self.is_active = is_active


class DummyQuery:
    def __init__(self, result=None):
        self._result = result

    def filter(self, *args, **kwargs):
        return self

    def filter_by(self, **kwargs):
        return self

    def first(self):
        return self._result

    def all(self):
        return self._result or []


class DummyDB:
    def __init__(self, permission_exists=False):
        self.permission_exists = permission_exists

    def query(self, model):
        # deps.require_permission expects Permission, RolePermission, UserRole.
        name = getattr(model, '__name__', '')
        if name == 'Permission':
            if self.permission_exists:
                perm = types.SimpleNamespace(id=123, is_active=True)
                return DummyQuery(perm)
            return DummyQuery(None)
        if name == 'RolePermission':
            # Return a mapping row if permission_exists is True.
            return DummyQuery(types.SimpleNamespace(id=1) if self.permission_exists else None)
        if name == 'UserRole':
            # No extra roles.
            return DummyQuery([])
        return DummyQuery(None)


@pytest.fixture(autouse=True)
def scoped_stubs(monkeypatch):
    """Scope imports for require_permission so tests don't hit the real DB.

    We patch only what deps.py uses at import/runtime.
    """
    # Stub fastapi.security module (duck-typed)
    fastapi_security_mod = types.ModuleType("fastapi.security")

    class OAuth2PasswordBearer:  # pragma: no cover
        def __init__(self, tokenUrl):
            self.tokenUrl = tokenUrl

    monkeypatch.setattr(fastapi_security_mod, "OAuth2PasswordBearer", OAuth2PasswordBearer, raising=False)
    monkeypatch.setitem(sys.modules, "fastapi.security", fastapi_security_mod)

    # Stub jose
    jose_mod = types.ModuleType("jose")

    class JWTError(Exception):
        pass

    monkeypatch.setattr(jose_mod, "JWTError", JWTError, raising=False)
    jwt_stub = types.SimpleNamespace(decode=lambda *a, **k: {})
    monkeypatch.setitem(sys.modules, "jose", jose_mod)
    monkeypatch.setitem(sys.modules, "jose.jwt", jwt_stub)

    # Stub pydantic ValidationError
    pydantic_mod = types.ModuleType("pydantic")

    class ValidationError(Exception):
        pass

    monkeypatch.setattr(pydantic_mod, "ValidationError", ValidationError, raising=False)
    monkeypatch.setitem(sys.modules, "pydantic", pydantic_mod)

    # Minimal app.core.config
    app_core_config = types.ModuleType("app.core.config")
    settings = types.SimpleNamespace(API_V1_STR="/api/v1", SECRET_KEY="x" * 32, ALGORITHM="HS256")
    monkeypatch.setattr(app_core_config, "settings", settings, raising=False)
    monkeypatch.setitem(sys.modules, "app.core.config", app_core_config)

    # Minimal app.core.security
    app_core_security = types.ModuleType("app.core.security")

    async def is_token_blacklisted(token):
        return False

    monkeypatch.setattr(app_core_security, "is_token_blacklisted", is_token_blacklisted, raising=False)
    monkeypatch.setitem(sys.modules, "app.core.security", app_core_security)

    # Minimal app.db.database
    app_db_database = types.ModuleType("app.db.database")
    monkeypatch.setattr(app_db_database, "SessionLocal", lambda: None, raising=False)
    monkeypatch.setitem(sys.modules, "app.db.database", app_db_database)

    # Minimal models
    app_db_models = types.ModuleType("app.db.models.all_models")

    class User:  # pragma: no cover
        pass

    class Permission:  # pragma: no cover
        name = None
        is_active = True

    class RolePermission:  # pragma: no cover
        class _Inable:
            def in_(self, vals):
                return self

        permission_id = None
        role_id = _Inable()

    class UserRole:  # pragma: no cover
        user_id = None
        role_id = None

    class Role:  # pragma: no cover
        pass

    monkeypatch.setattr(app_db_models, "User", User, raising=False)
    monkeypatch.setattr(app_db_models, "Permission", Permission, raising=False)
    monkeypatch.setattr(app_db_models, "RolePermission", RolePermission, raising=False)
    monkeypatch.setattr(app_db_models, "UserRole", UserRole, raising=False)
    monkeypatch.setattr(app_db_models, "Role", Role, raising=False)
    monkeypatch.setitem(sys.modules, "app.db.models.all_models", app_db_models)

    # Minimal TokenPayload schema
    app_schema_token = types.ModuleType("app.schema.token")

    class TokenPayload:  # pragma: no cover
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    monkeypatch.setattr(app_schema_token, "TokenPayload", TokenPayload, raising=False)
    monkeypatch.setitem(sys.modules, "app.schema.token", app_schema_token)



def asyncio_run(coro):
    """Run async coroutine safely on Py3.12+ (no current event loop)."""
    import asyncio

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        raise RuntimeError("asyncio_run cannot be used while an event loop is running")

    return asyncio.run(coro)



def test_permission_allowed_via_role_json_permissions():
    user = DummyUser(role=DummyRole('Employee', permissions=['users.view']))
    dep = deps.require_permission('users.view')

    db = DummyDB(permission_exists=False)
    result = asyncio_run(dep(current_user=user, db=db))
    assert result is user


def test_permission_denied_when_not_in_role_json_and_mapping_absent():
    user = DummyUser(role=DummyRole('Employee', permissions=[]), role_id=2)
    dep = deps.require_permission('users.delete')

    db = DummyDB(permission_exists=False)

    with pytest.raises(HTTPException):
        asyncio_run(dep(current_user=user, db=db))


def test_permission_allowed_via_role_permission_mapping():
    user = DummyUser(role=DummyRole('Employee', permissions=[]), role_id=2)
    dep = deps.require_permission('attendance.view')

    db = DummyDB(permission_exists=True)
    result = asyncio_run(dep(current_user=user, db=db))
    assert result is user

