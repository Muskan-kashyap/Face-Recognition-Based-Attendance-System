"""
Recognition adapter scaffolding.

This bridges domain RecognitionService to existing application face pipeline
(kept as pass-through for Milestone 2 to avoid changing endpoint behavior).
"""

from __future__ import annotations

from typing import Any, Optional

from backend.domain.tenant import TenantContext
from backend.domain.services.recognition import RecognitionService


class RecognitionAdapter(RecognitionService):
    @staticmethod
    def identify_user(
        *,
        tenant_context: TenantContext,
        correlation_id: str,
        image_bytes: bytes,
        device_info: Optional[dict] = None,
        **kwargs: Any,
    ) -> Any:
        # TODO(Milestone2): call existing liveness/embedding/vector search implementation.
        # Return a domain-friendly decision placeholder.
        return {
            "tenant_context": tenant_context,
            "correlation_id": correlation_id,
            "device_info": device_info,
            "image_byte_length": len(image_bytes) if image_bytes is not None else 0,
            "match": None,
            "distance": None,
            "threshold_met": False,
        }
