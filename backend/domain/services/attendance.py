"""
Domain service interface: AttendanceService.
"""

from __future__ import annotations

from typing import Any, Optional

from backend.domain.tenant import TenantContext


class AttendanceService:
    @staticmethod
    def check_in(
        *,
        tenant_context: TenantContext,
        correlation_id: str,
        user_id: int,
        timestamp: Any,
        is_live: int,
        recognition_distance: Optional[float] = None,
        emotion: Optional[str] = None,
        **kwargs: Any,
    ) -> Any:
        """
        Persist attendance check-in after domain decisioning.

        Implementations must:
        - enforce tenant scope
        - dedupe according to domain rules
        - write audit logs if required by policy
        """
        raise NotImplementedError
