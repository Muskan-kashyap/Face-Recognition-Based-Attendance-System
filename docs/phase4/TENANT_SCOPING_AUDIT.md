# TENANT_SCOPING_AUDIT.md
Date: 2026-06-21
Scope: Tenant boundary enforcement audit (analysis only) for key entities.

## Legend
- **SAFE**: Evidence indicates consistent org_id scoping in queries and mutations.
- **UNSAFE**: Likely missing scoping or enforcement not verifiable from inspected evidence.
- **REQUIRES_REVIEW**: Not fully audited due to tool limitations; requires manual endpoint-by-endpoint verification.

## Findings (based on limited file reads where possible)

### Organizations / Org API keys
- **Status: REQUIRES_REVIEW**
- Reason: organization router not fully analyzed for reads beyond creation; ensure all list/export endpoints require org governance scope.

### Users
- **Status: SAFE (partial)**
- Evidence: `backend/app/routers/users.py` filters `User.org_id == current_user.org_id` on list, and on `read_user_by_id`.
- Risk: enroll-face route checks `User.id == user_id` and `User.org_id == current_user.org_id`.

### Attendance
- **Status: REQUIRES_REVIEW**
- Reason: attendance routers/services not read line-by-line in this RBAC audit pass.
- Must ensure:
  - `attendance_logs` queries always filter by `user.org_id` through join
  - correction/override queries filter by target user's org_id

### Reports
- **Status: REQUIRES_REVIEW**
- Reason: reporting endpoints not verified in this pass.
- Must ensure export/report generation queries are scoped by `reports.org_id`.

### Payroll
- **Status: SAFE (partial)**
- Evidence: `backend/routers/payroll.py` filters payroll by `Payroll.org_id == current_user.org_id` and joins on `User.org_id == current_user.org_id` for late counts.
- Risk: ensure no endpoints allow user-scoped data across orgs via `payroll_id` parameter without scoping.

### Ticketing
- **Status: REQUIRES_REVIEW**
- Must ensure `tickets` queries filter by org_id.

## Global Risk Note
Even if query filters exist, authorization guards must also ensure the caller’s permission is valid for that tenant. The guard `require_permission` currently does not take `resource_org_id`.


