# PHASE4_RBAC_DESIGN.md

## Phase 4 — Enterprise RBAC Design (Analysis Only)
Date: 2026-06-21

### 1. Current RBAC State (Observed)

#### Roles (current)
- `Role` table contains: name, permissions JSONB
- Seeded roles likely include Admin/Manager/Employee, and some Super Admin naming mismatch exists per RBAC audit report.

#### Permissions (current)
- `Permission` table contains name, description, category, is_active

#### Mappings (current)
- `RolePermission` join table links roles ↔ permissions
- `UserRole` join table supports multiple roles per user

#### Authorization Flow (current)
- `get_current_user` loads authenticated user and primary role
- `require_permission(permission_name)` checks:
  1) permission in `current_user.role.permissions` JSONB
  2) permission exists in DB and mapping exists in role_permissions for effective role_ids
- Some endpoints also use `require_admin` or `current_user.role.name` checks.

### 2. Current Weaknesses
- Mixed enforcement strategies (permission guard vs role-name checks).
- Role-name canonicalization issues (SuperAdmin vs Super Admin).
- Duplicate permission sources (JSONB + join table).
- Missing caching strategy for permission sets.
- Tenant scoping not guaranteed for every query.

### 3. Target Enterprise RBAC Architecture

#### Canonical Roles (Phase 4 spec + extended)
- **SuperAdmin** — platform governance
- **Admin** — organization administration
- **Manager** — team supervision + approvals
- **HR** — employee lifecycle and compliance requests (new business mapping)
- **Finance** — payroll & reimbursements approvals (new mapping)
- **Employee** — self-service
- **Auditor** — read-only audit/report export

> Implementation note: If current system supports only SuperAdmin/Admin/Manager/Employee, treat HR/Finance/Auditor as additional roles via same permission catalog and role_permissions mapping.

#### Permission Catalog (namespaced)
Design rule:
- Permissions are stable strings: `module.action.scope` (or `domain:action.scope`)

Example domains per your spec:
- `users.create|update|view|delete` (or namespaced variants)
- `attendance.view`, `attendance.approve`, `attendance.override`
- `payroll.view`, `payroll.run`, `payroll.export`
- `reports.view`
- `audit.view`
- `organizations.create/update`

### 4. Role Matrix (Recommended)

| Role | Key capabilities |
|---|---|
| SuperAdmin | full governance, organization lifecycle, global settings, audit export |
| Admin | org-scoped employee/attendance/admin operations, attendance override manage |
| Manager | team-scoped attendance correction approvals/rejections, team reporting |
| HR | employee lifecycle + correction workflow requests management; audit read |
| Finance | payroll runs/approvals/export, payroll-related analytics |
| Employee | self check-in, own attendance view, correction request submission |
| Auditor | audit logs view/export, reporting read-only |

### 5. Permission Matrix (Recommended)
A full matrix should be generated as part of implementation; below is an enterprise taxonomy excerpt:

#### Platform permissions
- `platform.organizations.manage`
- `platform.settings.manage`
- `platform.security.manage`
- `platform.audit.view`
- `platform.analytics.view`
- `platform.users.manage`

#### Org permissions
- `org.structure.manage`
- `org.employees.manage`
- `org.faces.manage`
- `org.attendance.records.view`
- `org.attendance.override.manage`
- `org.reports.export`

#### Team/approval permissions
- `team.members.view`
- `team.attendance.view`
- `team.attendance.regularization.approve|reject`
- `team.reports.export`

#### Self-service permissions
- `self.attendance.checkin`
- `self.attendance.view`
- `self.attendance.regularization.request`
- `self.reports.export`

### 6. Backend Enforcement Design

#### Rules (non-negotiable)
1. **Every protected router endpoint** must declare a permission requirement.
2. **Tenant scoping** must be applied consistently using `org_id` derived from authenticated user.
3. Authorization decisions must be auditable (store action + target).
4. Remove role-name checks except for bootstrap/initial seeding flows.

#### Enforcement mechanism
- Keep `get_current_active_user` as authentication gate
- Replace router hard-coded checks with:
  - `Depends(require_permission("<perm>"))`
- Add permission resolver:
  - Input: user_id, org_id, permission_name
  - Output: allow/deny + decision metadata

#### Effective role resolution
- Use `users.role_id` plus `user_roles` to compute effective roles
- Map roles → permissions via join table, with fallback compatibility during migration

### 7. Frontend Enforcement Design

- Use a single RBAC config mapping from permissions to UI routes/actions
- ProtectedRoute should check required permission(s), not raw role strings
- Hidden menu items should be permission-aware
- Employee dashboards should be self-scoped

### 8. Caching Strategy

- Request-scoped permission caching:
  - Compute effective permission set once per request
- Shared caching:
  - Redis cache: key `(user_id, role_version)`
- Token/session approach:
  - Include permission/role version in JWT (future recommendation)

---

## Summary
- RBAC schema is a strong base.
- Enterprise-grade enforcement requires eliminating role-name checks and using permission guards consistently.
- HR/Finance/Auditor roles can be enabled without structural changes by seeding roles and permission bundles.

