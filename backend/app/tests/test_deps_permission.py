import sys
import types
import os
import pytest
from unittest.mock import MagicMock

# Ensure the backend package root is on sys.path so 'app' is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# NOTE:
# This test file previously mutated sys.modules at import-time, which polluted the
# global interpreter state and broke other tests (including SQLAlchemy mapper
# configuration due to stubbing sqlalchemy.orm).
#
# Production code must not be modified; therefore, we scope all stubs using
# pytest's monkeypatch fixture.

from app.api import deps
from fastapi import HTTPException



@pytest.fixture(autouse=True)
def scoped_stubs(monkeypatch):
    # Inject minimal stub modules so importing app.api.deps doesn't require the whole backend stack.
    # Everything is scoped to this test via monkeypatch so it automatically restores.

    fastapi_security_mod = types.ModuleType("fastapi.security")

    class OAuth2PasswordBearer:
        def __init__(self, tokenUrl):
            self.tokenUrl = tokenUrl

    fastapi_security_mod.OAuth2PasswordBearer = OAuth2PasswordBearer
    monkeypatch.setitem(sys.modules, 'fastapi.security', fastapi_security_mod)

    jose_mod = types.ModuleType('jose')

    class JWTError(Exception):
        pass

    jose_mod.JWTError = JWTError
    jwt_stub = types.SimpleNamespace(decode=lambda *a, **k: {})
    monkeypatch.setitem(sys.modules, 'jose', jose_mod)
    monkeypatch.setitem(sys.modules, 'jose.jwt', jwt_stub)

    pydantic_mod = types.ModuleType('pydantic')

    class ValidationError(Exception):
        pass

    # Only stub what this test needs.
    pydantic_mod.ValidationError = ValidationError
    monkeypatch.setitem(sys.modules, 'pydantic', pydantic_mod)

    # SQLAlchemy stubs: ONLY add missing attributes required by deps import.
    # Do NOT replace sqlalchemy.orm completely to avoid breaking mapper configuration.
    import sqlalchemy.orm as real_orm

    def foreign(*args, **kwargs):
        return None

    monkeypatch.setattr(real_orm, 'foreign', foreign, raising=False)

    # Minimal app core stubs
    app_core_config = types.ModuleType('app.core.config')
    settings = types.SimpleNamespace(API_V1_STR='/api/v1', SECRET_KEY='x' * 32, ALGORITHM='HS256')
    app_core_config.settings = settings
    monkeypatch.setitem(sys.modules, 'app.core.config', app_core_config)

    app_core_security = types.ModuleType('app.core.security')

    async def is_token_blacklisted(token):
        return False

    app_core_security.is_token_blacklisted = is_token_blacklisted
    monkeypatch.setitem(sys.modules, 'app.core.security', app_core_security)

    # Minimal DB and model stubs
    app_db_database = types.ModuleType('app.db.database')
    app_db_database.SessionLocal = lambda: None
    monkeypatch.setitem(sys.modules, 'app.db.database', app_db_database)

    app_db_models = types.ModuleType('app.db.models.all_models')

    class User:
        pass

    class Permission:
        name = None
        is_active = True

    class RolePermission:
        permission_id = None

        class _Inable:
            def in_(self, vals):
                return self

        role_id = _Inable()

    class UserRole:
        user_id = None
        role_id = None

    class Role:
        pass

    class Organization:
        pass

    class OrgApiKey:
        pass

    class Department:
        pass

    class Shift:
        pass

    class FaceEmbedding:
        pass

    class AttendanceLog:
        pass

    class ManualOverride:
        pass

    class BlockchainAuditLog:
        pass

    class MonthlyGrowthSummary:
        pass

    class OfflineSyncQueue:
        pass

    app_db_models.User = User
    app_db_models.Permission = Permission
    app_db_models.RolePermission = RolePermission
    app_db_models.UserRole = UserRole
    app_db_models.Role = Role
    app_db_models.Organization = Organization
    app_db_models.OrgApiKey = OrgApiKey
    app_db_models.Department = Department
    app_db_models.Shift = Shift
    app_db_models.FaceEmbedding = FaceEmbedding
    app_db_models.AttendanceLog = AttendanceLog
    app_db_models.ManualOverride = ManualOverride
    app_db_models.BlockchainAuditLog = BlockchainAuditLog
    app_db_models.MonthlyGrowthSummary = MonthlyGrowthSummary
    app_db_models.OfflineSyncQueue = OfflineSyncQueue
    monkeypatch.setitem(sys.modules, 'app.db.models.all_models', app_db_models)

    app_schema_token = types.ModuleType('app.schema.token')

    class TokenPayload:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    app_schema_token.TokenPayload = TokenPayload
    monkeypatch.setitem(sys.modules, 'app.schema.token', app_schema_token)



class DummyRole:
    def __init__(self, name, permissions=None, id=1):
        self.name = name
        self.permissions = permissions or []
        self.id = id


class DummyUser:
    def __init__(self, id=1, role=None, role_id=1):
        self.id = id
        self.role = role or DummyRole("Employee", permissions=[])
        self.role_id = role_id


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


class DummyDB(MagicMock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def query(self, model):
        # Return a dummy query; tests will set _result appropriately
        return DummyQuery(getattr(self, "_query_result", None))


def test_permission_allowed_via_role_permissions_list():
    user = DummyUser(role=DummyRole("Employee", permissions=["attendance.view"]))
    dep = deps.require_permission("attendance.view")

    # call the inner dependency with a DB placeholder
    db = DummyDB()
    coro = dep(current_user=user, db=db)
    # dep returns coroutine because it's async; run it
    result = asyncio_run(coro)
    assert result is user


def test_permission_allowed_via_role_permission_mapping(monkeypatch):
    user = DummyUser(role=DummyRole("Employee", permissions=[]), role_id=2)
    dep = deps.require_permission("attendance.export")

    # Prepare DB mock to return a Permission and RolePermission mapping
    db = DummyDB()
    perm = MagicMock()
    perm.id = 123
    db._query_result = None

    # Monkeypatch db.query to return specific results depending on model
    def query_side_effect(model):
        if model.__name__ == "Permission":
            return DummyQuery(perm)
        if model.__name__ == "RolePermission":
            return DummyQuery(MagicMock())
        if model.__name__ == "UserRole":
            return DummyQuery([])
        return DummyQuery(None)

    db.query = query_side_effect

    result = asyncio_run(dep(current_user=user, db=db))
    assert result is user


def test_permission_denied_when_missing(monkeypatch):
    user = DummyUser(role=DummyRole("Employee", permissions=[]), role_id=3)
    dep = deps.require_permission("non.existent")
    db = DummyDB()
    db.query = lambda model: DummyQuery(None)

    with pytest.raises(HTTPException):
        asyncio_run(dep(current_user=user, db=db))


# Small helper to run async coroutines in pytest without adding pytest-asyncio
import asyncio


def asyncio_run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)
