from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import logging
from typing import Any, Optional, Mapping

from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models.all_models import User

logger = logging.getLogger(__name__)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


SENSITIVE_KEYS = {
    # auth / session
    "token",
    "access_token",
    "refresh_token",
    # credential / password
    "password",
    "hashed_password",
    "new_password",
    "old_password",
    # biometrics
    "embedding",
    "face_embedding",
}


def _redact_value(key: str, value: Any) -> Any:
    if key in SENSITIVE_KEYS:
        return "[REDACTED]"
    return value


def _deep_redact(obj: Any) -> Any:
    """Redact sensitive fields from nested JSON-like structures."""
    if isinstance(obj, Mapping):
        redacted: dict[str, Any] = {}
        for k, v in obj.items():
            # Normalize keys to match SENSITIVE_KEYS
            ks = str(k)
            redacted[ks] = _deep_redact(_redact_value(ks, v))
        return redacted

    if isinstance(obj, list):
        return [_deep_redact(i) for i in obj]

    return obj


@dataclass(frozen=True)
class AuditLogEvent:
    action: str
    target_type: str
    target_id: str
    tenant_org_id: Optional[str]
    actor_user_id: Optional[int]
    actor_role_name: Optional[str]
    before_state: Optional[dict[str, Any]]
    after_state: Optional[dict[str, Any]]
    reason: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    correlation_id: Optional[str]
    status: str  # success|failure
    failure_reason: Optional[str] = None


class AuditService:
    """Enterprise audit logging service.

    Foundation scope:
    - persistence-only (no blockchain anchoring)
    - sensitive redaction
    - safe no-op when AUDIT_ENABLED is false
    """

    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def enabled() -> bool:
        # Required by Phase 4.2.1 spec
        return bool(getattr(settings, "AUDIT_ENABLED", False))

    def log_event(self, event: AuditLogEvent):
        """Persist an audit event.

        If AUDIT_ENABLED is false, this is a safe no-op.
        """
        if not self.enabled():
            logger.debug("Audit disabled; skipping event action=%s", event.action)
            return None

        # Allow tests to monkeypatch the persistence model by overriding
        # AuditService.AuditLog (used by Phase 4.2 unit tests).
        AuditLog = getattr(self, "AuditLog", None)
        if AuditLog is None:
            from app.db.models.all_models import AuditLog  # local import to avoid circulars


        before_state = event.before_state
        after_state = event.after_state

        # redact
        before_state_redacted = _deep_redact(before_state) if before_state is not None else None
        after_state_redacted = _deep_redact(after_state) if after_state is not None else None

        audit = AuditLog(
            occurred_at=_utc_now(),
            tenant_org_id=event.tenant_org_id,
            actor_user_id=event.actor_user_id,
            actor_role_name=event.actor_role_name,
            action=event.action,
            target_type=event.target_type,
            target_id=event.target_id,
            before_state=before_state_redacted,
            after_state=after_state_redacted,
            reason=event.reason,
            ip_address=event.ip_address,
            user_agent=event.user_agent,
            correlation_id=event.correlation_id,
            status=event.status,
            failure_reason=event.failure_reason,
        )

        self.db.add(audit)
        self.db.commit()
        self.db.refresh(audit)
        return audit

    def log_create(
        self,
        *,
        actor: User,
        action: str,
        target_type: str,
        target_id: str,
        after_state: dict[str, Any],
        correlation_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        tenant_org_id: Optional[str] = None,
        reason: Optional[str] = None,
    ):
        return self.log_event(
            AuditLogEvent(
                action=action,
                target_type=target_type,
                target_id=str(target_id),
                tenant_org_id=tenant_org_id,
                actor_user_id=getattr(actor, "id", None),
                actor_role_name=getattr(getattr(actor, "role", None), "name", None),
                before_state=None,
                after_state=after_state,
                reason=reason,
                ip_address=ip_address,
                user_agent=user_agent,
                correlation_id=correlation_id,
                status="success",
                failure_reason=None,
            )
        )

    def log_update(
        self,
        *,
        actor: User,
        action: str,
        target_type: str,
        target_id: str,
        before_state: dict[str, Any],
        after_state: dict[str, Any],
        correlation_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        tenant_org_id: Optional[str] = None,
        reason: Optional[str] = None,
    ):
        return self.log_event(
            AuditLogEvent(
                action=action,
                target_type=target_type,
                target_id=str(target_id),
                tenant_org_id=tenant_org_id,
                actor_user_id=getattr(actor, "id", None),
                actor_role_name=getattr(getattr(actor, "role", None), "name", None),
                before_state=before_state,
                after_state=after_state,
                reason=reason,
                ip_address=ip_address,
                user_agent=user_agent,
                correlation_id=correlation_id,
                status="success",
                failure_reason=None,
            )
        )

    def log_delete(
        self,
        *,
        actor: User,
        action: str,
        target_type: str,
        target_id: str,
        before_state: dict[str, Any],
        correlation_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        tenant_org_id: Optional[str] = None,
        reason: Optional[str] = None,
    ):
        return self.log_event(
            AuditLogEvent(
                action=action,
                target_type=target_type,
                target_id=str(target_id),
                tenant_org_id=tenant_org_id,
                actor_user_id=getattr(actor, "id", None),
                actor_role_name=getattr(getattr(actor, "role", None), "name", None),
                before_state=before_state,
                after_state=None,
                reason=reason,
                ip_address=ip_address,
                user_agent=user_agent,
                correlation_id=correlation_id,
                status="success",
                failure_reason=None,
            )
        )

    def log_failure(
        self,
        *,
        actor: Optional[User],
        action: str,
        target_type: str,
        target_id: str,
        failure_reason: str,
        correlation_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        tenant_org_id: Optional[str] = None,
        reason: Optional[str] = None,
        before_state: Optional[dict[str, Any]] = None,
        after_state: Optional[dict[str, Any]] = None,
    ):
        return self.log_event(
            AuditLogEvent(
                action=action,
                target_type=target_type,
                target_id=str(target_id),
                tenant_org_id=tenant_org_id,
                actor_user_id=getattr(actor, "id", None) if actor else None,
                actor_role_name=getattr(getattr(actor, "role", None), "name", None) if actor else None,
                before_state=before_state,
                after_state=after_state,
                reason=reason,
                ip_address=ip_address,
                user_agent=user_agent,
                correlation_id=correlation_id,
                status="failure",
                failure_reason=failure_reason,
            )
        )

