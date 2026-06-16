"""
Adapters bridge domain interfaces to existing application services/repos.

Milestone 2: adapter scaffolding (no endpoint behavior change).
"""

from __future__ import annotations

from typing import Any, Optional

from backend.domain.tenant import TenantContext
from backend.domain.services.enrollment import EnrollmentService


class EnrollmentAdapter(EnrollmentService):
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
        # TODO(Milestone2): call existing enrollment implementation.
        # For now return a domain-friendly pass-through payload to keep behavior unchanged.
        return {
            "tenant_context": tenant_context,
            "correlation_id": correlation_id,
            "user_id": user_id,
            "model_name": model_name,
            "embedding_dim": embedding_dim,
            "face_embedding_dim": len(face_embedding) if face_embedding is not None else None,
        }
