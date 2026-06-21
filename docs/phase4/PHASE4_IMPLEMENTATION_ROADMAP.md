# PHASE4_IMPLEMENTATION_ROADMAP.md

## Phase 4 — Enterprise Implementation Roadmap (Dependency-Aware, Analysis Only)
Date: 2026-06-21

> This document is design-only. No code will be written.

### Cross-Cutting Dependencies (applies to all modules)
- Unified permission taxonomy and enforcement strategy must be established first.
- Audit logging must be integrated early so that subsequent workflows are auditable.

---

## Module 1 — Enterprise RBAC

### Objective
- Enforce permission-based access control uniformly across backend and frontend.

### Dependencies
- Existing RBAC DB schema: `roles/permissions/role_permissions/user_roles`
- Existing auth: JWT + `get_current_user`
- Existing permission guard: `require_permission`

### Database Changes
- Canonicalize role names (ensure `SuperAdmin` string consistency)
- Optional: deprecate `roles.permissions` JSONB duplication
- Add role_version / permission_version fields (recommended)

### Backend Work
- Implement permission resolver with caching
- Replace all router-level `role.name` checks with permission dependencies
- Ensure tenant scoping in query layer

### Frontend Work
- Permission-aware menu rendering
- ProtectedRoute based on permissions
- Role-permission matrix UI config generation

### Tests Required
- Route-level RBAC tests for each protected endpoint
- Permission matrix tests per role
- Negative tests (deny) for each permission

### Estimated Effort
- Medium-large (cross-cutting; ~2–4 sprints depending on endpoint count)

### Risk Level
- **High** due to security implications and potential breaking changes

---

## Module 2 — Audit & Compliance

### Objective
- Implement enterprise `audit_logs` table and consistent audit logging service.

### Dependencies
- Module 1 RBAC enforcement for permission change auditing
- Existing blockchain audit logs can remain as secondary compliance evidence

### Database Changes
- Create `audit_logs`
- Indexing strategy: `(org_id, occurred_at)`, `(actor_user_id, occurred_at)`, `(target_type, target_id)`

### Backend Work
- Audit logging service API
- Instrument critical operations:
  - user CRUD
  - face enrollment
  - attendance overrides/corrections
  - payroll generation/approval
  - permission changes
  - org changes

### Frontend Work
- Audit dashboard + searchable audit trail

### Tests Required
- Audit emission unit tests
- Integration tests verifying audit records for critical flows

### Estimated Effort
- Medium (~1–2 sprints)

### Risk Level
- **High** (must not miss critical events)

---

## Module 3 — Attendance Corrections

### Objective
- Implement regularization workflow with request/approval/override and full audit history.

### Dependencies
- Module 2 Audit
- Module 1 RBAC permission taxonomy

### Database Changes
- Decide mapping:
  - either extend `manual_overrides` to function as requests+approvals
  - or add `attendance_requests` and `attendance_approvals`
- Ensure relationships to `attendance_logs` and audit

### Backend Work
- Endpoints:
  - employee submit correction request
  - manager approve/reject
  - admin override
- State machine enforcement

### Frontend Work
- Employee request submission UI
- Manager approval UI
- Admin override UI

### Tests Required
- Workflow lifecycle tests (pending → approved/rejected)
- Permission boundary tests for each role
- Audit record tests per state transition

### Estimated Effort
- Medium (~1–2 sprints)

### Risk Level
- **Medium/High** (state machine correctness)

---

## Module 4 — Payroll Engine

### Objective
- Attendance-driven payroll generation with policies/components/runs/entries.

### Dependencies
- Module 3 Attendance corrections (for final attendance inputs)
- Module 2 Audit (payroll audit trail)
- Module 1 RBAC (finance/admin approvals)

### Database Changes
- Add payroll enterprise tables:
  - `salary_policies`, `salary_components`
  - `payroll_runs`, `payroll_entries`
  - `payroll_approvals` (if approval stage is required)
- Deprecate or migrate existing `payrolls`

### Backend Work
- Implement payroll generation workflow (`POST /payroll/run`)
- Approval workflow and status transitions
- Payslip generation PDF + export endpoints

### Frontend Work
- Payroll dashboards (runs history, payslips)

### Tests Required
- Payroll calculation tests with controlled attendance dataset
- Approval workflow permission tests
- Export correctness tests

### Estimated Effort
- High (~2–4 sprints)

### Risk Level
- **High** (financial correctness + compliance)

---

## Module 5 — Reporting & Analytics

### Objective
- Implement executive reporting dashboards and export (CSV/PDF).

### Dependencies
- Module 1 RBAC
- Availability of corrected attendance data (Module 3)
- Payroll metrics optional after payroll completion

### Database Changes
- Optional summary tables for performance:
  - daily/monthly summaries

### Backend Work
- Dashboard endpoints listed in spec
- Export generation and `reports` job integration

### Frontend Work
- Charts: Daily, Monthly, Department, Executive
- CSV/PDF export UI

### Tests Required
- Metric computation tests
- Permission tests for report endpoints
- Export integration tests

### Estimated Effort
- Medium (~1–2 sprints)

### Risk Level
- **Medium**

---

## Module 6 — Notifications

### Objective
- In-app + email notifications driven by system events.

### Dependencies
- Module 2 Audit (event correlation)
- Module 1 RBAC (permission-aware notification visibility)

### Database Changes
- Add `notifications` + delivery status tables

### Backend Work
- Notification service
- Event triggers from:
  - correction approved
  - payroll generated
  - user created
  - enrollment completed
  - attendance anomaly

### Frontend Work
- Notification center UI

### Tests Required
- Notification emission tests
- Delivery status tests

### Estimated Effort
- Medium (~1 sprint)

### Risk Level
- **Medium**

---

## Module 7 — Deployment & Production Hardening

### Objective
- Production-grade deployment with security headers, rate limiting, observability.

### Dependencies
- Stable auth/authorization from Module 1
- Audit logging from Module 2

### Database/Infra Changes
- Redis + optional queue for async report/payroll
- Nginx + SSL

### Backend Work
- Rate limiting endpoints
- Security headers
- Structured logging

### Frontend Work
- Production build pipeline

### Tests Required
- Smoke tests (health endpoints)
- Security tests (rate limit and header presence)

### Estimated Effort
- Medium (~1 sprint)

### Risk Level
- **Medium/High** depending on infra complexity

---

## PHASE 4 GO / NO-GO Decision
**NO-GO (for implementation start) until the following blockers are resolved.**

### Blockers (must resolve before implementation)
1. **Authorization enforcement uniformity blocker (CRITICAL)**
   - Inventory all routers to confirm 100% endpoints use permission dependencies.
   - Eliminate `role.name` checks or guarantee they are aligned with permission taxonomy.

2. **SuperAdmin role canonicalization blocker (HIGH)**
   - Fix role naming mismatch between seed and runtime checks (`SuperAdmin` vs `Super Admin`).

3. **Tenant scoping blocker (CRITICAL)**
   - Verify every attendance/report/payroll/ticket query is scoped by `org_id` derived from authenticated user.
   - Add query-level safeguards where missing.

4. **Enterprise audit_logs blocker (HIGH)**
   - Confirm current audit coverage is sufficient.
   - Implement first-class `audit_logs` table design before building correction/payroll workflows.

5. **Payroll enterprise schema blocker (HIGH)**
   - Confirm `payrolls` model is insufficient for policy/components/runs/entries.
   - Decide migration/replacement path early.

6. **Correction workflow model mapping blocker (HIGH)**
   - Decide whether `manual_overrides` will be extended into request/approval workflow or new tables will be introduced.
   - Ensure audit history ties to every state transition.

7. **Notification framework model blocker (MEDIUM/HIGH)**
   - Confirm missing notification tables; design them prior to event triggers.

---

## Final Note
The repository has a strong foundation for RBAC, tenanting, attendance logging, exports, and append-only compliance patterns.
However, before implementation, the system must be made consistently permission-enforced and tenant-scoped, and it must establish first-class enterprise audit and workflow data models.

