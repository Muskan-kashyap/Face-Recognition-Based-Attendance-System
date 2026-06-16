"""
Domain-level tenant scoping helpers.

All tenant boundary checks should funnel through here to prevent tenant leakage.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TenantContext:
    org_id: str
    user_id: int


def get_tenant_context_from_user(current_user: Any) -> TenantContext:
    """
    Extract tenant context from a user-like object.

    Expects the calling layer to ensure current_user has org_id and id.
    """
    return TenantContext(org_id=str(current_user.org_id), user_id=int(current_user.id))


def assert_org_scope_match(resource_org_id: str, ctx: TenantContext) -> None:
    """
    Raise ValueError on mismatch. Keep domain exceptions explicit so adapters
    can convert them to appropriate HTTP errors.
    """
    if str(resource_org_id) != str(ctx.org_id):
        raise ValueError("tenant scope mismatch")
