# Enterprise RBAC Audit and Responsibility Redesign

Date: 2026-06-14

## Executive Summary

The project has the foundation for enterprise RBAC: `roles`, `permissions`, `role_permissions`, and `user_roles` tables exist, authentication uses protected FastAPI dependencies, and the frontend already hides some role-specific menu items. However, responsibility boundaries are not yet enterprise-grade.

The main issue is that the implementation mixes role-string checks with permission checks. Several backend endpoints grant Managers Admin-level administration, SuperAdmin is under-seeded or inconsistently named, and employee self-service is broader on the backend than the frontend suggests. The system should move to permission-first authorization, with roles treated as default bundles of permissions rather than hard-coded business logic.

## Current RBAC Findings

### Authentication and Claims

- Access and refresh tokens are generated from the user id, not a full role or permission claim.
- `get_current_user` loads the user and primary role from the database on each request, which is good for immediate revocation.
- Token type enforcement exists for refresh-token misuse.
- JWTs do not include tenant/org, role version, session id, MFA status, or permission version claims. This limits auditability and policy enforcement.

### Database State

- `Role`, `Permission`, `RolePermission`, and `UserRole` exist in `backend/app/db/models/all_models.py`.
- `User` still has a primary `role_id`, while `user_roles` supports additional roles. This dual model can drift unless one source is declared authoritative.
- `Role.permissions` JSONB duplicates `role_permissions`; this creates two permission sources.
- Seed data creates `Admin`, `Manager`, `Employee`, and `Device`, but not consistently `SuperAdmin`.
- `seed_comprehensive.py` uses `"Super Admin"` while the app checks `"SuperAdmin"`. This breaks authorization for seeded super admins.

### Authorization Mechanisms

- `deps.require_permission()` exists and supports both JSON permissions and role-permission mappings.
- Many routers still use direct checks like `current_user.role.name in ["Admin", "Manager"]`.
- `require_admin()` currently allows `Admin`, `Manager`, and `SuperAdmin`, which collapses separation of duties.
- Organization scoping is present in several queries and is a strength of the current implementation.

### Frontend State

- `ProtectedRoute` previously treated `requiredRole="Admin"` as `Admin` plus `Manager`.
- Sidebar visibility previously allowed Managers to see `Users` and `Payroll`.
- SuperAdmin only had visible settings/blockchain governance, not full platform-owner workflows.
- Employee, Manager, Admin, and SuperAdmin dashboards share too much of the same shape.

## Role-by-Role Current State

| Role | Existing permissions and screens | Missing capabilities | Overlaps and risks |
| --- | --- | --- | --- |
| SuperAdmin | Can access blockchain settings if the role name exactly equals `SuperAdmin`; can access user routes where hard-coded. | Organization lifecycle, license/subscription management, global users, platform analytics, security policy, audit logs, feature toggles, backup/restore. | Seed mismatch may prevent access. User APIs still scope to the current org, so SuperAdmin is not truly global. |
| Admin | Can manage users, attendance, reports, payroll, reimbursements, tickets, and organization-level settings in places. | Department/team/designation management screens, face-enrollment approvals, policy configuration, imports, bulk onboarding, exception queues. | Seed grants all default permissions including `org.manage`; Admin may be too broad. |
| Manager | Can read users, create users, enroll faces, generate/update payroll, approve reimbursements, update tickets, and view org-wide attendance in several endpoints. | Team-scoped supervision, approval queues, leave/regularization workflow, direct-report reporting. | Managers can perform Admin and payroll work. This violates least privilege and separation of duties. |
| Employee | Can access dashboard, attendance, support, reimbursements, settings. Backend permits self check-in and own records in some modules. | Regularization requests, leave requests, face-enrollment request status, personal exports, notification center. | Attendance logs endpoint currently returns org-wide logs to any authenticated user unless restricted by route or query logic. |
| Device | Seeded with check-in/device permissions. | Dedicated API-key auth and device-only endpoint separation. | Device role is not cleanly separated from user JWT auth in the reviewed frontend/backend routes. |

## Incorrect Assignments and Security Concerns

- Managers can create users through `POST /users/`.
- Managers can enroll face templates for other users through `POST /users/{user_id}/enroll-face`.
- Managers can generate payroll and update payroll status through `/payroll`.
- Any authenticated user can call `GET /attendance/logs` and receive organization-wide logs.
- `GET /attendance/productivity-report` is available to any active user.
- `POST /org/` requires `Admin`, but creating organizations is platform governance and belongs to SuperAdmin.
- SuperAdmin is not seeded consistently and is missing from the default permission map.
- Audit logging is fragmented through blockchain audit records and does not cover all critical administrative actions.

## Enterprise RBAC Principles

### Separation of Duties

SuperAdmin governs the platform, Admin administers one organization, Manager supervises a team, and Employee performs self-service. Payroll, user provisioning, role assignment, and attendance overrides should not be casually shared across these roles.

### Least Privilege

Each role should receive only the permissions needed for its business function. Team-level access must be scoped by manager relationship, department, or team assignment instead of org-wide reads.

### Delegation

Operational decisions move to Managers. Organizational administration remains with Admins. Global system policy remains with SuperAdmin.

### Auditability

Every critical change must produce an immutable audit event with actor, target, before/after values, tenant, request metadata, and reason.

### Scalability

Future roles should be added by creating permission bundles, not by editing every route.

## Target Role Responsibilities

### SuperAdmin

Business purpose: owns the SaaS/platform governance boundary.

- Create, edit, activate, suspend, and delete organizations.
- Manage subscription plans, license limits, feature toggles, and platform announcements.
- View global users and assign/revoke organization Admin access.
- Disable compromised accounts and reset credentials.
- Configure global authentication, password, MFA, session, and biometric threshold policies.
- View system-wide analytics, API usage, storage, organization health, and recognition accuracy.
- Review and export access logs, audit logs, security events, and compliance reports.
- Manage backup, restore, scheduled jobs, and global notification templates.

### Admin

Business purpose: administers one organization.

- Manage departments, teams, designations, shifts, holidays, and attendance rules.
- Create/edit/deactivate employees, import data, onboard in bulk, and transfer employees.
- Register, re-enroll, approve, and retire face templates for employees.
- View and correct attendance records within the organization.
- Resolve attendance exceptions and document override reasons.
- Produce department, attendance, late-arrival, and monthly summary reports.
- Configure organization alerts, reminders, and announcements.

### Manager

Business purpose: supervises a defined team.

- View direct and delegated team members.
- View team attendance, schedules, absence, lateness, and shift adherence.
- Approve or reject attendance correction/regularization requests.
- Review leave requests and escalate conflicts.
- Generate and export team reports.
- Monitor probation or attendance-risk employees and raise concerns to Admin.

Managers should not create users, assign roles, configure organizations, enroll biometrics for unrelated employees, generate payroll, or override global policies.

### Employee

Business purpose: manages personal attendance and self-service.

- View personal attendance, hours, punctuality, and history.
- Check in/out as self.
- Request attendance correction or regularization.
- Apply for and cancel leave.
- Update allowed profile fields.
- Submit face-enrollment requests and view status.
- Receive announcements, reminders, attendance alerts, and decision notifications.
- Export personal monthly attendance records.

## Permission Matrix

| Module | SuperAdmin | Admin | Manager | Employee |
| --- | --- | --- | --- | --- |
| Organization lifecycle | Full Access | No Access | No Access | No Access |
| Subscription/license management | Full Access | Read Only | No Access | No Access |
| Global security policy | Full Access | No Access | No Access | No Access |
| Organization settings | Read Only/Override | Full Access | Read Only | No Access |
| Departments/teams/designations | Read Only/Override | Full Access | Read Only team scope | No Access |
| Shifts/holidays | Read Only/Override | Full Access | Read Only team scope | Read Only personal |
| User directory | Full Access | Full Access org scope | Read Only team scope | Read Only self |
| User creation/deactivation | Assign Admins globally | Full Access org scope | No Access | No Access |
| Role assignment | Full Access for SuperAdmin/Admin assignment | Limited Access within org policy | No Access | No Access |
| Face enrollment administration | Read Only/Override | Full Access org scope | Approval Access for team requests only | Limited Access self request |
| Attendance check-in | No Access except impersonation audit mode | Limited Access assisted check-in | Limited Access team exception flow | Full Access self |
| Attendance records | Full Access global read | Full Access org scope | Read Only team scope | Read Only self |
| Attendance overrides | Read Only/Override audit | Full Access org scope | Approval Access for team regularization | Request Access self |
| Wellness/productivity analytics | Full Access aggregate | Full Access org aggregate | Read Only team aggregate | No Access |
| Reports | Full Access global | Full Access org | Limited Access team | Limited Access self |
| Payroll | Read Only platform diagnostics | Full Access or Payroll Officer only | No Access | Read Only self |
| Reimbursements | Read Only aggregate | Full Access org policy | Approval Access team | Full Access self submission |
| Tickets/support | Full Access platform support | Full Access org tickets | Limited Access team tickets | Full Access self tickets |
| Notifications | Full Access global templates | Full Access org announcements | Limited Access team announcements | Read Only received |
| Audit logs | Full Access global | Read Only org | No Access or Limited team workflow audit | No Access |
| Blockchain/Web3 settings | Full Access | No Access | No Access | No Access |
| Device/API keys | Full Access global | Full Access org devices | No Access | No Access |
| Backup/restore/jobs | Full Access | No Access | No Access | No Access |

## Recommended Permission Catalog

Use namespaced permissions and make route dependencies require these names, not role strings.

| Permission | Business use |
| --- | --- |
| `platform.organizations.manage` | SuperAdmin tenant lifecycle |
| `platform.security.manage` | Global password/MFA/session/threshold policy |
| `platform.audit.view` | Global compliance and security review |
| `platform.settings.manage` | Blockchain, feature toggles, jobs, backups |
| `org.settings.manage` | Admin organization configuration |
| `org.structure.manage` | Admin departments, teams, shifts, holidays |
| `users.view.org` | Admin org directory |
| `users.manage.org` | Admin employee lifecycle |
| `users.view.team` | Manager direct-report directory |
| `roles.assign.org_admin` | SuperAdmin assignment of Admins |
| `face.manage.org` | Admin biometric enrollment management |
| `face.approve.team` | Manager team enrollment approval |
| `face.request.self` | Employee enrollment request |
| `attendance.view.org` | Admin attendance review |
| `attendance.view.team` | Manager team attendance review |
| `attendance.view.self` | Employee personal attendance |
| `attendance.checkin.self` | Employee self check-in |
| `attendance.override.org` | Admin manual correction |
| `attendance.approve.team` | Manager regularization approval |
| `reports.export.org` | Admin organization exports |
| `reports.export.team` | Manager team exports |
| `reports.export.self` | Employee personal exports |
| `payroll.manage.org` | Admin or future Payroll Officer payroll actions |
| `reimbursements.approve.team` | Manager reimbursement approvals |
| `reimbursements.submit.self` | Employee reimbursement submission |
| `tickets.manage.org` | Admin support queue management |
| `tickets.manage.team` | Manager team ticket handling |
| `tickets.manage.self` | Employee self tickets |

## Backend and Database Recommendations

### Schema

Keep:

- `roles`
- `permissions`
- `role_permissions`
- `user_roles`

Modify:

- Add `roles.scope` with values like `platform`, `organization`, `team`, `self`, `device`.
- Add `roles.is_system_role`, `roles.description`, and `roles.created_at`.
- Deprecate or remove `roles.permissions` JSONB once all permissions are in `role_permissions`.
- Add `user_roles.org_id`, `assigned_by`, `expires_at`, and `assignment_reason`.
- Add `permissions.description`, `permissions.risk_level`, and `permissions.requires_reason`.
- Add `role_permission.created_by`.
- Add a `role_version` or `permission_version` field to users or roles for token/session invalidation.

### Audit Log Schema

Create a first-class `audit_logs` table:

| Column | Purpose |
| --- | --- |
| `id` | Primary key |
| `occurred_at` | UTC timestamp |
| `actor_user_id` | User performing action |
| `actor_role` | Role at action time |
| `org_id` | Tenant boundary, nullable for platform-global events |
| `action` | Namespaced action, e.g. `users.create` |
| `resource_type` | User, Role, AttendanceLog, Organization |
| `resource_id` | Target id |
| `previous_value` | JSON before state |
| `new_value` | JSON after state |
| `reason` | Required for overrides/policy changes |
| `ip_address` | Request IP |
| `user_agent` | Client/device information |
| `correlation_id` | Request trace id |
| `status` | success/failure |

### Migration Plan

1. Normalize role names to `SuperAdmin`, `Admin`, `Manager`, `Employee`, `Device`.
2. Seed SuperAdmin and permission mappings explicitly.
3. Backfill `role_permissions` from `Role.permissions`.
4. Replace hard-coded role checks with `require_permission`.
5. Add team/manager relationships before enabling team-scope permissions.
6. Add audit logging middleware/service and call it from critical mutations.
7. Deprecate `Role.permissions` JSONB after a compatibility window.

## API Security Review

| Endpoint | Current access | Target authorization | Audit requirement |
| --- | --- | --- | --- |
| `POST /auth/login` | Public with rate limit | Public with rate limit, login failure tracking, MFA policy | Log failures and suspicious success |
| `POST /auth/refresh` | Refresh token | Valid refresh token, active account, session not revoked | Log abnormal refresh |
| `POST /auth/logout` | Authenticated | Authenticated current session | Log token revocation |
| `GET /users/` | Admin, Manager, SuperAdmin | `users.view.org` or `users.view.team`; Employee no org-wide list | No, unless exported |
| `POST /users/` | Admin, Manager, SuperAdmin | `users.manage.org`; SuperAdmin only for assigning Admins | Yes |
| `GET /users/me` | Authenticated | Authenticated self | No |
| `GET /users/{id}` | Self or Admin/Manager/SuperAdmin | Self, `users.view.org`, or `users.view.team` | No unless sensitive fields |
| `POST /users/{id}/enroll-face` | Self or Admin/Manager/SuperAdmin | `face.manage.org` or `face.request.self`; Manager approval via separate request endpoint | Yes |
| `GET /attendance/logs` | Any authenticated org user | `attendance.view.org`, `attendance.view.team`, or `attendance.view.self` with query scoping | Export yes; view no |
| `POST /attendance/check-in` | Authenticated, self unless Admin/Manager | `attendance.checkin.self`; assisted check-in separate Admin permission | Yes for assisted/manual |
| `PATCH /attendance/logs/{id}` | `attendance.override` | `attendance.override.org`; reason required | Yes |
| `GET /attendance/wellness-heatmap` | `attendance.view` | Org/team aggregate only; never Employee | No |
| `GET /attendance/productivity-report` | Any authenticated | `reports.view.org` or `reports.view.team` | No |
| `POST /org/` | Admin | `platform.organizations.manage` | Yes |
| `GET /admin/settings/blockchain` | SuperAdmin role string | `platform.settings.manage` or `platform.settings.view` | Yes if sensitive |
| `POST /admin/settings/blockchain/toggle` | SuperAdmin role string | `platform.settings.manage`; reason required | Yes |
| `GET /ticketing/` | Admin/Manager org-wide, Employee self | `tickets.manage.org`, `tickets.manage.team`, or `tickets.manage.self` | No |
| `POST /ticketing/` | Authenticated | `tickets.manage.self` or org/team ticket create | Yes for administrative ticket updates |
| `PATCH /ticketing/{id}` | Admin/Manager or owner | `tickets.manage.org`, `tickets.manage.team`, or owner limited fields | Yes for status/priority changes |
| `GET /reimbursement/` | Admin/Manager org-wide, Employee self | Admin org, Manager team, Employee self | No |
| `POST /reimbursement/` | Authenticated | `reimbursements.submit.self` | Yes |
| `PATCH /reimbursement/{id}/approve` | Admin/Manager | `reimbursements.approve.team` or finance/admin permission | Yes |
| `GET /payroll/` | Admin/Manager org-wide, Employee self | `payroll.manage.org` or `payroll.view.self`; Manager no access by default | Yes for exports |
| `POST /payroll/generate` | Admin/Manager | `payroll.manage.org` or future `payroll.generate.org` | Yes |
| `PATCH /payroll/{id}` | Admin/Manager | `payroll.manage.org` | Yes |

## Frontend Redesign

The frontend should hide inaccessible functionality but must never rely on hiding alone.

### SuperAdmin Dashboard

- Widgets: active organizations, license usage, global attendance volume, security events, system health, recognition accuracy.
- Sidebar: Organizations, Global Users, Platform Policies, Security, Audit Logs, Usage Analytics, Feature Toggles, Backups, Settings.
- Quick actions: create organization, suspend organization, assign admin, export compliance report, broadcast global announcement.

### Admin Dashboard

- Widgets: total employees, pending enrollments, attendance exceptions, late arrivals, open tickets, monthly summaries.
- Sidebar: Overview, Employees, Attendance, Face Enrollment, Departments, Shifts, Holidays, Reports, Payroll, Notifications, Organization Settings.
- Quick actions: add employee, import employees, approve enrollment, correct attendance, export monthly report.

### Manager Dashboard

- Widgets: team presence, late team members, pending approvals, leave conflicts, shift adherence.
- Sidebar: Overview, Team Attendance, Approvals, Team Reports, Support, Reimbursements.
- Quick actions: approve correction, reject leave, export team report, raise concern to Admin.

### Employee Dashboard

- Widgets: today status, hours worked, punctuality, pending requests, recent notifications.
- Sidebar: Overview, My Attendance, Requests, Reimbursements, Support, My Reports, Settings.
- Quick actions: check in, request correction, apply leave, submit enrollment image, download monthly record.

## Frontend Changes Applied in This Pass

- `ProtectedRoute` now supports `requiredRoles` and no longer treats Admin routes as Manager-accessible.
- `/dashboard/users` is restricted to `SuperAdmin` and `Admin`.
- `/dashboard/payroll` is restricted to `SuperAdmin` and `Admin`.
- Reports remain visible to `SuperAdmin`, `Admin`, and `Manager`.
- Sidebar no longer shows Users or Payroll to Managers.
- User Management now treats only `Admin` and `SuperAdmin` as user managers.
- Only `SuperAdmin` can expose Admin assignment in the user creation form.

## Critical Actions Requiring Audit Logs

- Login failure, suspicious login success, logout, token revocation.
- User create/edit/deactivate/reactivate/delete.
- Role assignment and revocation.
- Admin assignment and revocation.
- Password reset, credential disablement, MFA reset.
- Organization create/edit/suspend/activate/delete.
- Subscription/license changes.
- Department, shift, holiday, and attendance-policy changes.
- Face enrollment approval, re-enrollment, deletion, and threshold change.
- Attendance override, correction approval/rejection, and status update.
- Payroll generation, approval, release, and export.
- Reimbursement approval/rejection.
- Feature toggle, blockchain setting, backup, restore, and scheduled job changes.
- Compliance report export.

Each entry must include actor, action, resource, tenant, timestamp, previous value, new value, reason, IP address, device/user agent, and correlation id.

## Future Scalability

Add future roles as permission bundles:

- HR Executive: employee lifecycle and attendance exceptions without platform settings.
- Payroll Officer: payroll processing without user role management.
- Department Head: department-wide reporting and approvals.
- Security Officer: audit/security logs and compromised-account workflows.
- Compliance Auditor: read-only reports and immutable audit exports.
- Support Agent: tenant support tickets with scoped impersonation audit mode.

The code should shift from `role.name == "Admin"` to `Depends(require_permission("domain.action.scope"))`. Role checks may remain only for bootstrap actions where no permission registry exists yet.

## Implementation Priorities

1. Normalize role names and seed SuperAdmin permissions.
2. Restrict `GET /attendance/logs` by permission and scope.
3. Remove Manager from user creation, face enrollment administration, and payroll generation.
4. Move `POST /org/` to SuperAdmin/platform permission.
5. Add `audit_logs` and audit service.
6. Add team relationships before enabling Manager team views.
7. Replace all route role strings with permission dependencies.
8. Add frontend route/menu definitions from a single RBAC config file.

