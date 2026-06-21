# RBAC_IMPLEMENTATION_CHECKLIST.md
Date: 2026-06-21
Scope: Phase 4.1 RBAC cleanup & hardening checklist (no code; execution plan only).

## PHASE 4.1 OBJECTIVE
Eliminate authorization inconsistencies by standardizing on permission-based enforcement, canonicalizing role names, removing duplicate permission sources (or isolating them), designing permission caching, and auditing tenant scoping.

## Task 0 — Inventory & Endpoint Classification
- [ ] Enumerate all FastAPI router endpoints in `backend/app/routers/*.py`.
- [ ] For each endpoint, classify:
  - endpoint type: read/mutation
  - tenant-scoped resource: yes/no
  - current auth mechanism: role-name guard, require_admin, require_permission, or none
- [ ] Produce an endpoint list to be updated by router remediation.

## Task 1 — Canonical Role Strategy
- [ ] Create canonical role catalog and confirm it maps to existing roles.
- [ ] Decide canonical naming and remove/merge variants (`Super Admin`).
- [ ] Define bootstrap policy during migration (temporary compatibility) if needed.

## Task 2 — Router Authorization Standardization
- [ ] Replace all `current_user.role.name == ...` checks.
- [ ] Replace all `has_any_role(...)` checks.
- [ ] Replace all `is_admin_or_manager(...)` checks.
- [ ] Replace all usage of `require_admin*` for protected business endpoints.
- [ ] Ensure each endpoint declares exactly one permission dependency.

## Task 3 — Permission Cache Design + Enablement Plan
- [ ] Implement cache key scheme.
- [ ] Decide invalidation/versioning.
- [ ] Define fallback behavior when Redis is down (DB fallback).

## Task 4 — Tenant Scoping Verification
- [ ] Verify every endpoint that returns/updates tenant resources filters by `org_id`.
- [ ] Add tests that attempt cross-tenant resource access.

## Task 5 — Regression & Security Tests
- [ ] Route-level RBAC tests:
  - verify allow/deny per permission matrix
  - verify role name variants don’t bypass constraints
- [ ] Tenant isolation tests:
  - 403/404 for cross-org access
- [ ] Permission resolution tests:
  - verify effective permissions from joins not JSONB drift

## Exit Criteria
- [ ] No router remains using role-name checks for business endpoints.
- [ ] All endpoints that should be protected have explicit permission guards.
- [ ] Tenant scoping is enforced for all resources.
- [ ] RBAC behavior documented and tested.

## Estimated Risk
- **High**: authorization changes affect every request; regressions likely without comprehensive tests.


