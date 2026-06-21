from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

import pytest
from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine

from sqlalchemy.types import JSON

from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.services.audit_service import AuditService


TestBase = declarative_base()


class AuditLogTest(TestBase):
    """SQLite-compatible persistence model used only for unit tests."""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    occurred_at = Column(DateTime(timezone=False), nullable=False)

    tenant_org_id = Column(String, nullable=True)
    actor_user_id = Column(Integer, nullable=True)
    actor_role_name = Column(String, nullable=True)

    action = Column(String, nullable=False)
    target_type = Column(String, nullable=False)
    target_id = Column(String, nullable=False)

    before_state = Column(JSON, nullable=True)
    after_state = Column(JSON, nullable=True)



    reason = Column(Text, nullable=True)

    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    correlation_id = Column(String, nullable=True)

    status = Column(String, nullable=False)
    failure_reason = Column(Text, nullable=True)


@dataclass
class MockRole:
    name: str


@dataclass
class MockActor:
    id: int
    org_id: str
    role: MockRole


@pytest.fixture(scope="function")
def db_session() -> Session:
    engine = create_engine("sqlite:///:memory:")
    TestBase.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def _make_service(db_session: Session) -> AuditService:
    service = AuditService(db_session)
    # Inject SQLite test model so AuditService persists into TestBase.
    service.AuditLog = AuditLogTest
    return service


def _enable_audit(monkeypatch: pytest.MonkeyPatch, enabled: bool) -> None:
    # Patch the exact object instance used by AuditService: app.core.config.settings
    from app.core.config import settings

    monkeypatch.setattr(settings, "AUDIT_ENABLED", enabled, raising=False)


def test_audit_event_creation_and_redaction(db_session: Session, monkeypatch: pytest.MonkeyPatch):
    _enable_audit(monkeypatch, True)

    service = _make_service(db_session)
    actor = MockActor(id=1, org_id="org-1", role=MockRole(name="Admin"))

    before: dict[str, Any] = {"hashed_password": "secret", "token": "t1"}
    after: dict[str, Any] = {"password": "p1", "access_token": "a1", "embedding": [0.1, 0.2]}

    audit = service.log_update(

        actor=actor,  # type: ignore[arg-type]
        action="users.update",
        target_type="User",
        target_id=str(actor.id),
        before_state=before,
        after_state=after,
        correlation_id=str(uuid.uuid4()),
        ip_address="127.0.0.1",
        user_agent="pytest",
        tenant_org_id=str(actor.org_id),
        reason=None,
    )

    assert audit is not None
    assert getattr(audit, "status") == "success"

    # AuditService deep-redacts sensitive keys.
    assert audit.before_state["hashed_password"] == "[REDACTED]"
    assert audit.before_state["token"] == "[REDACTED]"
    assert audit.after_state["password"] == "[REDACTED]"
    assert audit.after_state["access_token"] == "[REDACTED]"
    assert audit.after_state["embedding"] == "[REDACTED]"


def test_audit_service_disabled_noop(db_session: Session, monkeypatch: pytest.MonkeyPatch):
    _enable_audit(monkeypatch, False)

    service = _make_service(db_session)
    actor = MockActor(id=1, org_id="org-1", role=MockRole(name="Admin"))

    audit = service.log_failure(
        actor=actor,  # type: ignore[arg-type]
        action="users.update",
        target_type="User",
        target_id=str(actor.id),
        failure_reason="nope",
        correlation_id=str(uuid.uuid4()),
        ip_address="127.0.0.1",
        user_agent="pytest",
        tenant_org_id=str(actor.org_id),
    )

    assert audit is None


def test_correlation_id_roundtrip(db_session: Session, monkeypatch: pytest.MonkeyPatch):
    _enable_audit(monkeypatch, True)

    service = _make_service(db_session)
    actor = MockActor(id=1, org_id="org-1", role=MockRole(name="Admin"))

    cid = str(uuid.uuid4())
    audit = service.log_create(
        actor=actor,  # type: ignore[arg-type]
        action="users.create",
        target_type="User",
        target_id=str(actor.id),
        after_state={"name": "x"},
        correlation_id=cid,
        ip_address=None,
        user_agent=None,
        tenant_org_id=str(actor.org_id),
        reason=None,
    )

    assert audit is not None
    assert audit.correlation_id == cid

