# RBAC_AUDIT_REPORT.md
Date: 2026-06-21
Scope: FastAPI backend authorization architecture review ONLY (no code changes).

## Summary of Findings
- Authorization model is **mixed**: some routes use `deps.require_permission`, some use `deps.require_admin`, and many use direct `current_user.role.name` checks.
- Canonical role naming is inconsistent: both `"SuperAdmin"` and `"Super Admin"` appear.
- Permission model is duplicated conceptually: `Role.permissions` JSONB + join table `role_permissions` are both used.
- Tenant scoping is partially enforced at query level in some routers, but this must be audited for every sensitive query.
- Permission caching is not implemented (permission guard does DB queries per request).

## Evidence Table (file-level; includes line references by approximate location)

### 1) Authorization dependency layer (`backend/app/api/deps.py`)

#### Issue: Mixed role-name guards and permission guards
- **File:** `backend/app/api/deps.py`
- **Locations:** `require_admin()`, `require_manager_or_admin()`, `require_admin_or_super_admin()`, `has_any_role()`, `require_permission()`
- **Severity:** CRITICAL
- **Issue:**
  - Permission-based authorization exists via `require_permission(permission_name)`.
  - Role-name checks exist via `require_admin*` and `has_any_role`.
  - `require_admin()` explicitly allows `Admin`, `Manager`, and `SuperAdmin` (plus legacy `Super Admin`). This collapses separation of duties.
- **Recommended fix:**
  - Deprecate `require_admin*` for all non-bootstrap endpoints.
  - Replace router-level role-name checks with `require_permission()` everywhere.
  - Enforce a single authorization standard: permission IDs only.

#### Issue: Duplicate permission sources
- **File:** `backend/app/api/deps.py`
- **Location:** `require_permission()`
- **Severity:** HIGH
- **Issue:** `require_permission()` checks:
  1) `current_user.role.permissions` JSONB list membership
  2) `Permission` + `RolePermission` join table mapping
- **Recommended fix:**
  - Choose one canonical permission source.
  - Prefer join table (`role_permissions`) for relational integrity.
  - If keeping JSONB for compatibility, define migration and disable JSONB source after window.

#### Issue: No permission caching
- **File:** `backend/app/api/deps.py`
- **Location:** `require_permission()`
- **Severity:** HIGH
- **Issue:** Permission resolution performs DB queries every request.
- **Recommended fix:**
  - Add request-scoped caching: compute effective permissions set once per request.
  - Add Redis caching keyed by `(org_id,user_id,role_version)` or `(user_id, permission_version)`.
  - Add invalidation on role/permission changes.

#### Issue: Tenant scoping not enforced inside guard
- **File:** `backend/app/api/deps.py`
- **Location:** `get_current_user()`, `require_permission()`
- **Severity:** CRITICAL
- **Issue:** `require_permission` does not accept/validate resource `org_id` scoping. It only checks if the user has the permission globally.
- **Recommended fix:**
  - Extend permission check to validate org/resource scope where relevant.
  - Alternatively, create a second guard `require_permission_scoped(permission_name, resource_org_id_resolver)`.


### 2) Admin governance router (`backend/app/routers/admin.py`)

#### Issue: role-name check bypasses permission taxonomy
- **File:** `backend/app/routers/admin.py`
- **Locations:**
  - `get_blockchain_status` uses `current_user.role.name != "SuperAdmin"`
  - `toggle_blockchain_status` uses `current_user.role.name != "SuperAdmin"`
- **Severity:** HIGH
- **Issue:** Direct `role.name` comparisons ignore permission guard. Also the legacy name `"Super Admin"` is not accepted here.
- **Recommended fix:**
  - Replace with `Depends(require_permission("platform.settings.manage"))` (or existing equivalent permission).
  - Canonicalize super admin spelling.


### 3) Organization router (`backend/app/routers/org.py`)

#### Issue: mixed auth responsibilities via require_admin_or_super_admin
- **File:** `backend/app/routers/org.py`
- **Locations:** `create_organization()` uses `deps.require_admin_or_super_admin`
- **Severity:** MEDIUM/HIGH
- **Issue:** `require_admin_or_super_admin` accepts both `admin` and `superadmin` by role name normalization.
- **Recommended fix:**
  - Organization lifecycle should be SuperAdmin-only.
  - Replace with permission-based guard (`platform.organizations.manage`).


### 4) Payroll router (`backend/app/routers/payroll.py`)

#### Issue: role-name checks bypass permission taxonomy
- **File:** `backend/app/routers/payroll.py`
- **Locations:** `is_admin_or_manager()` and checks in `read_payrolls`, `generate_payroll`, `update_payroll_status`
- **Severity:** HIGH
- **Issue:** Payroll access uses `is_admin_or_manager(current_user)` which checks normalized role name strings. This bypasses permission checks.
- **Recommended fix:**
  - Replace with `require_permission("payroll.view.*")` and `require_permission("payroll.run")` semantics.

#### Issue: org scoping seems present in queries but must be verified per endpoint
- **File:** `backend/app/routers/payroll.py`
- **Locations:** queries filter `User.org_id == current_user.org_id`, `Payroll.org_id == current_user.org_id`.
- **Severity:** MEDIUM
- **Recommended fix:**
  - Confirm every payroll-related query includes `org_id` filters.
  - Add automated tenant-scoping tests for each route.


### 5) Users router (`backend/app/routers/users.py`)

#### Issue: mixed role-name guard; not permission-based
- **File:** `backend/app/routers/users.py`
- **Locations:**
  - `read_users`, `create_user`, `read_user_by_id`, `enroll_user_face` use `deps.has_any_role(... "Admin", "Manager", "SuperAdmin", "Super Admin")`
- **Severity:** CRITICAL
- **Issue:** User management and face enrollment administration are authorized by role-name strings instead of permission IDs.
- **Recommended fix:**
  - Replace with permission-based guards for:
    - users.view.org
    - users.manage.org
    - face.manage.org (admin)
    - face.request.self (employee)
    - manager-specific approval endpoints (if applicable)

#### Issue: role separation drift
- **File:** `backend/app/routers/users.py`
- **Locations:** allows `Manager` on `read_users`, `create_user`, and `enroll-face`.
- **Severity:** CRITICAL
- **Issue:** Manager should not have admin-level privileges by default (per canonical separation of duties).
- **Recommended fix:**
  - Remove Manager from user management endpoints; enforce permission taxonomy.


### 6) Other routers/services
- **Not fully audited line-by-line in this pass** due to tool limitations (ripgrep unavailable). Recommended next step: enumerate all `backend/app/routers/*.py` and manually check for:
  - `role.name` comparisons
  - `has_any_role`
  - `require_admin*`
  - direct string checks for `SuperAdmin` and `Super Admin`
  - any endpoints without permission guard.


