"""
Domain-level authorization and permission policy.

This module is intentionally dependency-light and side-effect free so it can be
unit-tested and used consistently across API dependencies, services, and adapters.

DO NOT import FastAPI, SQLAlchemy, or business-logic modules here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional


@dataclass(frozen=True)
class TenantContext:
    org_id: str
    user_id: int
    role_name: str
    permissions: Optional[Iterable[str]] = None


@dataclass(frozen=True)
class AuthorizationDecision:
    allowed: bool
    reason: str


# Canonical resource/action identifiers used by the domain layer.
class AttendanceActions:
    CHECK_IN = "attendance.check_in"
    OVERRIDE = "attendance.override"
    ENROLL = "attendance.enroll"


def _has_permission(ctx: TenantContext, permission_name: str) -> bool:
    if not ctx.permissions:
        return False
    return permission_name in set(ctx.permissions)


def authorize_attendance_action(
    ctx: TenantContext,
    action: str,
) -> AuthorizationDecision:
    """
    Allow/deny policy for attendance domain operations.

    This policy is the single source of truth.
    """
    # Superusers (tenant-level) are allowed for attendance domain.
    if ctx.role_name in {"SuperAdmin", "Admin", "Manager"}:
        # Managers/Admins can override; Employees can check-in only if permission is present.
        if action in {
            AttendanceActions.CHECK_IN,
            AttendanceActions.OVERRIDE,
            AttendanceActions.ENROLL,
        }:
            return AuthorizationDecision(True, "role allows attendance action")

    # Non-admin roles: enforce permissions
    if action == AttendanceActions.CHECK_IN and _has_permission(ctx, "attendance.checkin"):
        return AuthorizationDecision(True, "permission attendance.checkin")

    if action == AttendanceActions.OVERRIDE and _has_permission(ctx, "attendance.override"):
        return AuthorizationDecision(True, "permission attendance.override")

    if action == AttendanceActions.ENROLL and _has_permission(ctx, "attendance.enroll"):
        return AuthorizationDecision(True, "permission attendance.enroll")

    return AuthorizationDecision(False, "missing required role/permission")
