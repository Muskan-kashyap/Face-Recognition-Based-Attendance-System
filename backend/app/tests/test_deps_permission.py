import sys
import types
import os

# Ensure the backend package root is on sys.path so 'app' is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Inject minimal stub modules so importing app.api.deps doesn't require the whole backend stack.
fastapi_mod = types.ModuleType("fastapi")
class HTTPException(Exception):
    def __init__(self, *args, **kwargs):
        self.status_code = kwargs.get('status_code')
        self.detail = kwargs.get('detail')
        super().__init__(self.detail)
fastapi_mod.HTTPException = HTTPException
def Depends(x=None):
    return x
fastapi_mod.Depends = Depends
class status:
    HTTP_401_UNAUTHORIZED = 401
    HTTP_403_FORBIDDEN = 403
    HTTP_404_NOT_FOUND = 404
    HTTP_400_BAD_REQUEST = 400
fastapi_mod.status = status
# sys.modules['fastapi'] = fastapi_mod  # disabled: avoid conflicting HTTPException classes during full-suite runs

security_mod = types.ModuleType('fastapi.security')
class OAuth2PasswordBearer:
    def __init__(self, tokenUrl):
        self.tokenUrl = tokenUrl
security_mod.OAuth2PasswordBearer = OAuth2PasswordBearer
sys.modules['fastapi.security'] = security_mod

jose_mod = types.ModuleType('jose')
class JWTError(Exception):
    pass
jose_mod.JWTError = JWTError
jwt_stub = types.SimpleNamespace(decode=lambda *a, **k: {})
# expose both 'jose' and 'jose.jwt' to satisfy imports
sys.modules['jose'] = jose_mod
sys.modules['jose.jwt'] = jwt_stub

pydantic_mod = types.ModuleType('pydantic')
class ValidationError(Exception):
    pass
pydantic_mod.ValidationError = ValidationError
sys.modules['pydantic'] = pydantic_mod

sqlalchemy_orm = types.ModuleType('sqlalchemy.orm')
sqlalchemy_orm.Session = object
def selectinload(x):
    return x
sqlalchemy_orm.selectinload = selectinload
# Provide DeclarativeBase used by app.db.models.base
class DeclarativeBase:
    pass
sqlalchemy_orm.DeclarativeBase = DeclarativeBase
sys.modules['sqlalchemy.orm'] = sqlalchemy_orm

# Minimal app core stubs
app_core_config = types.ModuleType('app.core.config')
settings = types.SimpleNamespace(API_V1_STR='/api/v1', SECRET_KEY='x'*32, ALGORITHM='HS256')
app_core_config.settings = settings
sys.modules['app.core.config'] = app_core_config

app_core_security = types.ModuleType('app.core.security')
async def is_token_blacklisted(token):
    return False
app_core_security.is_token_blacklisted = is_token_blacklisted
sys.modules['app.core.security'] = app_core_security

# Minimal DB and model stubs
app_db_database = types.ModuleType('app.db.database')
app_db_database.SessionLocal = lambda: None
sys.modules['app.db.database'] = app_db_database

app_db_models = types.ModuleType('app.db.models.all_models')
# Minimal model stubs used by deps and backend package import
class User:
    pass
class Permission:
    pass
class RolePermission:
    pass
class UserRole:
    # allow attribute access used in filters
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
# Additional attributes on permission/rolepermission used by deps
class Permission:
    name = None
    is_active = True
class RolePermission:
    permission_id = None
    # provide an `in_`-capable stub used in filter expressions
    class _Inable:
        def in_(self, vals):
            return self
    role_id = _Inable()

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
sys.modules['app.db.models.all_models'] = app_db_models

app_schema_token = types.ModuleType('app.schema.token')
class TokenPayload:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
app_schema_token.TokenPayload = TokenPayload
sys.modules['app.schema.token'] = app_schema_token

import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException

from app.api import deps


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
