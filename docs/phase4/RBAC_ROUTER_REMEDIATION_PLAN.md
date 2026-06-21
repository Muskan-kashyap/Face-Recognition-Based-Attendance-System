# RBAC_ROUTER_REMEDIATION_PLAN.md
Date: 2026-06-21
Scope: Authorization standardization plan only.

## 1) Standard
Replace all of the following patterns with `Depends(require_permission(<permission_name>))`:
- `if current_user.role.name == ...`
- `deps.has_any_role(current_user, "Admin", ...)`
- custom `is_admin_or_manager(user)` logic
- `require_admin*` dependencies (except possibly temporary bootstrap during migration)

## 2) Router-by-Router Modification Targets (verified by file reads where possible)

### `backend/app/routers/admin.py`
- Replace:
  - `current_user.role.name != "SuperAdmin"` checks
- With:
  - `require_permission("platform.settings.manage")` (or existing closest permission id)

### `backend/app/routers/org.py`
- Replace `deps.require_admin_or_super_admin` on organization creation.
- With:
  - `require_permission("platform.organizations.manage")`.
- Ensure only platform governance endpoints accept SuperAdmin.

### `backend/app/routers/payroll.py`
- Replace `is_admin_or_manager` checks for read/generate/update.
- With:
  - `require_permission("payroll.view")`
  - `require_permission("payroll.run")`
  - `require_permission("payroll.manage")` / approval-related permission.

### `backend/app/routers/users.py`
- Replace `deps.has_any_role` checks.
- With permission taxonomy:
  - users.view.org
  - users.manage.org
  - face.manage.org
  - self.* permissions for employee self-service
- Remove Manager privileges from admin operations unless explicit `team.*` permission is implemented.

## 3) General Rules for All Routers (must be enforced)
1. Every mutation endpoint must declare the exact permission.
2. Every read endpoint must declare a `*.view` permission.
3. No router should rely on role-name strings beyond temporary bootstrap code.
4. For tenant-sensitive resources:
   - permission check + query scoping must both be present.

## 4) Verification Method (tests)
- Create route-level authorization tests per endpoint:
  - For each role, test allowed/denied based on permission matrix.
  - For sensitive tenant resources, verify org leakage is impossible (unauthorized org IDs return 404/403).


