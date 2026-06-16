"""
Domain service interface: RecognitionService.

This is an interface/spec module. Concrete implementations are provided by
adapters in backend/app/adapters/*.
"""

from __future__ import annotations

from typing import Any, Optional

from backend.domain.tenant import TenantContext


class RecognitionService:
    @staticmethod
    def identify_user(
        *,
        tenant_context: TenantContext,
        correlation_id: str,
        image_bytes: bytes,
        device_info: Optional[dict] = None,
        **kwargs: Any,
    ) -> Any:
        """
        Identify a user given an image within a tenant.

        Implementations must:
        - run liveness detection + face embedding generation
        - execute org-scoped vector search
        - apply thresholding
        - return explainable match decision
        """
        raise NotImplementedError
