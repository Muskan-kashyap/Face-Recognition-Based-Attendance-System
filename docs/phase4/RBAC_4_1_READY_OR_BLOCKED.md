# PHASE 4.1 READY / BLOCKED
Date: 2026-06-21

## PHASE 4.1 STATUS: BLOCKED

## Why it’s blocked
1. **Tooling limitation prevented full backend audit**: ripgrep (`rg`) binary is missing, so an exhaustive endpoint scan could not be completed. Only a subset of routers was read line-by-line (`admin.py`, `org.py`, `payroll.py`, `users.py`) plus `deps.py`.
2. **Authorization inconsistencies likely remain in other routers** (`attendance.py`, `reimbursement.py`, `ticketing.py`, `auth.py`, etc.) and cannot be confirmed as eliminated.
3. **Tenant scoping verification is incomplete** for attendance/reports/ticketing due to missing endpoint reads.

## Blockers to resolve before implementing Phase 4.1
- Enumerate and review all remaining router endpoints; remove all residual role-name checks and `require_admin*` usage.
- Confirm that every permission guard is applied consistently.
- Perform full tenant-scoping review and add tenant isolation tests.
- Canonicalize super admin role naming across seeds and runtime checks.

