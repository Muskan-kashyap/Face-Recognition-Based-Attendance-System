"""
Override adapter scaffolding.

Milestone 2: bridge domain OverrideService to existing manual override logic.
No endpoint behavior change at this stage; returns placeholder domain response.
"""

from __future__ import annotations

from typing import Any

from backend.domain.tenant import TenantContext
from backend.domain.services.override import OverrideService


class OverrideAdapter(OverrideService):
    @staticmethod
    def override_attendance(
        *,
        tenant_context: TenantContext,
        correlation_id: str,
        attendance_log_id: int,
        target_user_id: int,
        admin_user_id: int,
        new_status: str,
        reason_category: str,
        override_notes: str | None = None,
        **kwargs: Any,
    ) -> Any:
        # TODO(Milestone2): call existing manual override repo/controller.
        return {
            "tenant_context": tenant_context,
            "correlation_id": correlation_id,
            "attendance_log_id": attendance_log_id,
            "target_user_id": target_user_id,
            "admin_user_id": admin_user_id,
            "new_status": new_status,
            "reason_category": reason_category,
            "override_notes": override_notes,
            "result": None,
        }
