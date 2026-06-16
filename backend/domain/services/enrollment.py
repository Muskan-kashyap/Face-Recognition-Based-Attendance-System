"""
Domain service interface: EnrollmentService.

This is an interface/spec module. Concrete implementations are provided by
adapters in backend/app/adapters/*.
"""

from __future__ import annotations

from typing import Any, Optional

from backend.domain.tenant import TenantContext


class EnrollmentService:
    @staticmethod
    def enroll_face(
        *,
        tenant_context: TenantContext,
        correlation_id: str,
        user_id: int,
        face_embedding: list[float],
        model_name: Optional[str] = None,
        embedding_dim: Optional[int] = None,
        **kwargs: Any,
    ) -> Any:
        """
        Enroll face embedding for a user within a tenant.

        Implementations must:
        - enforce tenant scope
        - write audit logs (append-only) if required by the domain policy
        """
        raise NotImplementedError
