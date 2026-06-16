"""
Attendance adapter scaffolding.

Milestone 2: bridge domain AttendanceService to existing attendance logic
without changing endpoint behavior yet.
"""

from __future__ import annotations

from typing import Any, Optional

from backend.domain.tenant import TenantContext
from backend.domain.services.attendance import AttendanceService


class AttendanceAdapter(AttendanceService):
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
        # TODO(Milestone2): call existing attendance_controller/pipeline/repo implementation.
        # Keep placeholder output to avoid changing behavior yet.
        return {
            "tenant_context": tenant_context,
            "correlation_id": correlation_id,
            "user_id": user_id,
            "timestamp": str(timestamp),
            "is_live": is_live,
            "recognition_distance": recognition_distance,
            "emotion": emotion,
            "result": None,
        }
