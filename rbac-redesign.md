# Enterprise RBAC Redesign (Super Admin / Admin / Manager / Employee)

Date: 2026-06-15

## 0) Summary of key issues found during Phase 1 audit
1. **Role-string driven frontend gating** (e.g., exact `SuperAdmin` match in Settings) makes Super Admin UX incomplete when backend seeds/returns `Super Admin` vs `SuperAdmin`.
2. **Backend least-privilege gaps**: some attendance endpoints are protected only by authentication (or not protected at all by `require_permission`), so UI hiding is not sufficient.
3. **Co-mingled responsibility**: the current system allows roles to perform cross-discipline work via hard-coded role checks instead of permissions.

This redesign fixes these issues by moving to a consistent permission taxonomy and enforcing it across backend endpoints. Roles become **bundles** of permissions.

---

## 1) Canonical roles and separation of duties

### Super Admin (Platform Governance)
**Business purpose:** Acts as the platform owner/SaaS governance boundary.

**Do:**
- Create/activate/suspend/delete organizations (tenant lifecycle)
- Manage global settings: attendance policies, recognition thresholds, security policy, MFA/session/password policies
- Manage global user governance: view all users, assign/revoke Admin access, reset/disable compromised accounts
- Manage global platform configuration: feature toggles, blockchain anchoring settings, backup/restore/job orchestration, notification templates
- Monitor platform usage/health and export compliance/security/audit reports

**Do not:**
- Perform org-scoped operational work that should be done by Admin (e.g., department CRUD)

---

### Admin (Organization Administration)
**Business purpose:** Administers one tenant (organization) end-to-end.

**Do:**
- Manage org structure: departments, teams, designations, shifts, holidays
- Configure attendance rules (org-scoped)
- Employee administration: create/edit/deactivate employees, import/bulk onboarding, transfers
- Face enrollment administration (org-scoped): approve/re-enroll, delete invalid templates
- Attendance operations (org-scoped): view attendance records, resolve exceptions, apply manual attendance corrections
- Reporting (org-scoped): department attendance summaries/late arrival reports and exports
- Notifications (org-scoped): reminders and announcements

**Do not:**
- Perform global governance actions (subscriptions, tenant lifecycle, system-wide security policy)

---

### Manager (Operational Supervision + Approvals)
**Business purpose:** Supervises a team and manages operational exceptions via approvals.

**Do:**
- View team members and team schedules/attendance summaries
- Review and approve/reject **requests** that require managerial judgment:
  - Attendance regularization/corrections requests
  - Leave requests
  - (Where applicable) enrollment/re-enrollment approvals
- Monitor workforce KPIs: lateness, absence, shift adherence
- Team reporting and exports

**Do not:**
- Create/deactivate employees
- Register/approve face templates directly at a system-admin level (unless your product later adds explicit “manager approval” workflows)
- Override attendance without an approval workflow

---

### Employee (Self-Service)
**Business purpose:** Handles only their own data and requests.

**Do:**
- Personal dashboard (attendance history, work hours, punctuality)
- Self check-in (as self)
- Self-service requests:
  - request attendance correction/regularization
  - apply/cancel leave
  - submit face enrollment request and upload/update enrollment images
- View personal enrollment/approval status
- Receive notifications and decisions

**Do not:**
- View org-wide logs
- Override attendance
- Approve requests

---

## 2) Permission-based RBAC model (enterprise-grade)

### Design rule
- Permissions are **namespaced** by module and scope.
- Backend endpoints must declare `require_permission(<permission>)`.
- Role checks are removed from sensitive endpoints.

### Recommended permission identifiers
Use stable IDs (strings) that never change once seeded.

#### Platform (Super Admin only)
- `platform.organizations.manage`
- `platform.security.manage`
- `platform.settings.manage`
- `platform.audit.view`
- `platform.analytics.view`
- `platform.users.manage`
- `platform.maintenance.manage`

#### Organization (Admin)
- `org.structure.manage`
- `org.attendance.rules.manage`
- `org.employees.manage`
- `org.faces.manage`
- `org.attendance.records.view`
- `org.attendance.override.manage`
- `org.reports.export`
- `org.notifications.manage`

#### Team / Approvals (Manager)
- `team.members.view`
- `team.attendance.view`
- `team.attendance.regularization.approve`
- `team.attendance.regularization.reject`
- `team.leave.approve`
- `team.leave.reject`
- `team.reports.export`

#### Self-service (Employee)
- `self.attendance.checkin`
- `self.attendance.view`
- `self.attendance.regularization.request`
- `self.leave.apply`
- `self.leave.cancel`
- `self.faces.request`
- `self.faces.status.view`

---

## 3) Target permission matrix (Module → Super/Admin/Manager/Employee)

| Module | Super Admin | Admin | Manager | Employee |
|---|---:|---:|---:|---:|
| Tenant lifecycle | Full | No Access | No Access | No Access |
| Global security & policies | Full | No Access | No Access | No Access |
| Blockchain/feature toggles | Full | No Access | No Access | No Access |
| Organization structure (departments/teams) | Read Only/No Access | Full | Read Only (team scope) | No Access |
| Attendance rules (shifts/holidays/thresholds) | Read/Override | Full | No Access | No Access |
| Employee lifecycle | Full | Full | No Access | No Access |
| Face enrollment admin | Full (global monitoring) | Full (org scope) | Approval workflow only | Request self only |
| Attendance records view | Full | Full (org) | Team scope read-only | Personal only |
| Attendance overrides | Audit/Approve (as governance) | Full override | Approval access only | No Access |
| Reports export | Full | Org export | Team export | Personal export |
| Notifications | Templates global + broadcast | Org announcements | Team announcements (if allowed) | Receives only |
| Audit logs export | Full | Read only (org) | No access | No access |

---

## 4) Backend enforcement requirements (non-negotiable)

1. **Replace hard-coded `role.name in [...]` checks** in routers with permission dependencies.
2. Ensure each endpoint declares a permission:
   - Reads that expose sensitive data must require `*.view`.
   - Mutations that change attendance, overrides, or approvals must require `*.manage` or `*.approve`.
3. Enforce **tenant scoping** in every query using org_id from authenticated user.
4. Normalize permission naming and remove inconsistencies:
   - Current domain authorization constants and DB permission names must match exactly.
5. Ensure the authorization layer logs:
   - actor, permission, resource org_id, request path, decision reason.

---

## 5) Target role behavior mapped to current implementation gaps

### Attendance gaps to fix first
- `GET /attendance/logs` and `GET /attendance/productivity-report` must not be callable without permission.
- `POST /attendance/check-in` must enforce `self.attendance.checkin` and/or assisted check-in permissions for Admin/Manager if you truly support it.

### Super Admin UX gap to fix next
- Enforce canonical role-name string returned by backend as `SuperAdmin`.
- Frontend should treat Super Admin actions as business-governed permissions, not only UI flags.

---

## 6) Migration recommendations

1. **Canonicalize role names** in seed/migrations:
   - Replace `
