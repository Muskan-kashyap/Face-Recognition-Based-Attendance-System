"""
Domain service interface: OverrideService.
"""

from __future__ import annotations

from typing import Any

from backend.domain.tenant import TenantContext


class OverrideService:
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
        """
        Apply a manual attendance override in a tenant-safe manner.

        Implementations must:
        - enforce RBAC (admin/manager)
        - ensure target log belongs to tenant org
        - ensure audit logging + append-only blockchain audit
        """
        raise NotImplementedError
