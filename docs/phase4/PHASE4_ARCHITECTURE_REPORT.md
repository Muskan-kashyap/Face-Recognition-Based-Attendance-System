# PHASE4_ARCHITECTURE_REPORT.md

## Phase 4 — Enterprise Architecture Review (Analysis Only)
Date: 2026-06-21

### 1. Current Repository Scope
**Backend (FastAPI / SQLAlchemy):**
- JWT authentication with token revocation via Redis blacklist (`backend/app/core/security.py`)
- Authorization dependencies exist (`backend/app/api/deps.py`), including a `require_permission(permission_name)` dependency
- Attendance pipeline + logging (attendance logs table, adapters and controller)
- RBAC/tenant models exist (`backend/app/db/models/all_models.py`)
- Reporting/payroll models exist partially (reports table, payrolls table)
- Blockchain audit append-only log table exists (`BlockchainAuditLog`)

**Frontend (React / Vite):**
- Protected routing and navigation already implemented at UI level (`frontend/src/components/ProtectedRoute.jsx`)
- Pages exist for Payroll, Reports, Settings, Attendance, Ticketing, UserManagement, Reimbursements
- Services layer calls backend (`frontend/src/services/*`)

**Infrastructure:**
- docker-compose and prod docker files exist (`docker-compose.prod.yml`, `Dockerfile.prod`, `infrastructure/docker-compose.yml`)
- Kubernetes manifests present under `infrastructure/k8s/`
- Monitoring folder exists under `infrastructure/monitoring/`

### 2. Text Architecture Diagram (Current)

```
                         ┌──────────────────────────────┐
                         │            Client            │
                         │ React (Vite)                │
                         │ - UI permission hiding      │
                         │ - ProtectedRoute            │
                         └──────────────┬──────────────┘
                                        │ HTTPS (JWT)
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                               API Layer (FastAPI)                            │
│  routers/*                                                                    │
│  - auth endpoints (/auth/*)                                               │
│  - user/org/attendance/payroll/ticketing routers                            │
│  deps.py: get_current_user, require_admin, require_permission               │
│  middleware: metrics, rate_limit, observability (where configured)          │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │ SQLAlchemy ORM
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Domain/Service Layer                           │
│ app/services/*                                                             │
│ - attendance pipeline orchestration                                      │
│ - analytics service (exists)                                             │
│ - cache service (exists)                                                  │
│ - blockchain service integration (exists)                                 │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │ Queries/Mutations
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                  Data Layer (Postgres)                       │
│ app/db/models/* (all_models.py)                                              │
│ - RBAC: roles, permissions, role_permissions, user_roles                     │
│ - Tenancy: organizations, org_api_keys                                       │
│ - Attendance: attendance_logs, manual_overrides, recognition/enrollment logs│
│ - Reporting: reports                                                          │
│ - Payroll: payrolls (limited)                                                │
│ - Audit: blockchain_audit_logs (append-only)                                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │ Redis
                                      ▼
                           ┌─────────────────────────┐
                           │ Token blacklist / cache │
                           └─────────────────────────┘
```

### 3. Layer Responsibilities

#### Client (React)
- UI-level permission gating (hide menu items, restrict routes)
- Displays dashboards (Overview/Reports/Payroll/Attendance)
- Submits actions (attendance, payroll-related, user management)

#### API Routers
- Translate HTTP requests to domain/service calls
- Enforce authentication dependencies (`get_current_active_user`)
- Some routers still use **role-name checks** (not consistently permission-based)
- Some routers use `require_permission` from `app/api/deps.py`

#### Dependencies / Authorization
- `get_current_user()` verifies JWT, validates token type, checks blacklist, loads user
- `get_current_active_user()` checks `is_active` and role presence
- `require_permission(permission_name)` checks:
  - role.permissions JSONB membership
  - role_permissions join table mapping via Permission + RolePermission
- Missing parts observed:
  - caching layer for permissions
  - consistent use across every protected endpoint
  - consistent role-name canonicalization across seeds/UX

#### Services
- Attendance pipeline orchestration
- Analytics service exists but reporting endpoints may be incomplete/partial
- Blockchain audit service exists
- Cache service exists (but not verified for RBAC caching usage)

#### Data Layer
- SQLAlchemy models include most Phase-4 entities already (RBAC, manual overrides, reports, payroll stub, blockchain audit log)

### 4. Service Boundaries & Dependencies (Enterprise View)

- **Auth boundary:**
  - security.py + deps.py manage token lifecycle and user loading
  - Redis used for blacklist

- **RBAC boundary:**
  - DB tables provide role/permission mapping
  - deps.py provides permission dependency guard
  - Frontend uses ProtectedRoute + role strings

- **Attendance boundary:**
  - attendance pipeline → recognition/liveness → AttendanceLog
  - manual overrides already exist as `ManualOverride`

- **Reporting boundary:**
  - `Report` table provides async export artifacts, but dashboard endpoints are not verified by file reads in this run

- **Payroll boundary:**
  - `Payroll` model exists; enterprise payroll run/component/policy tables likely missing

- **Audit boundary:**
  - blockchain_audit_logs exists append-only
  - requested enterprise audit_logs table is not present in the current model snapshot

- **Notifications boundary:**
  - no notification entities verified in the models read; only architecture intent exists in TODO docs

### 5. Current Strengths
- RBAC tables exist: `roles`, `permissions`, `role_permissions`, `user_roles`
- Permission guard exists: `require_permission` dependency
- Token blacklist implemented via Redis with fail-open behavior
- Attendance pipeline and liveness/anti-spoof logs are persisted
- Tenant model exists (`Organization`, `OrgApiKey`)
- Audit append-only blockchain log exists (useful for compliance patterns)

### 6. Architectural Weaknesses / Risks

#### RBAC Enforcement Consistency
- Observed evidence (from RBAC docs and code snippets): endpoints still use **hard-coded `role.name`** checks.
- Risk: separation of duties violations and privilege escalation via inconsistent enforcement.

#### Token Claims & Auditability
- JWT contains `sub` and `type` only (observed from security.py and deps.py behavior).
- Missing claims: org_id, role/permissions version, session id.
- Audit attribution requires DB lookups only; difficult to reason about temporal permission state.

#### Duplicate Authorization Sources
- `Role.permissions` JSONB duplicates `role_permissions` join table.
- Risk: drift between two sources; caching/resolution complexity.

#### Permission Caching Gaps
- `require_permission` performs DB queries per request without caching.
- Risk: high DB load under scale.

#### Reporting/Payroll Completeness
- Models show partial payroll (`payrolls`) and report job table (`reports`).
- Phase-4 payroll requires salary policies/components/runs/entries and approval workflow—likely missing.
- Reporting analytics endpoints required by Phase 4 may be incomplete or only stubbed.

#### Audit & Notifications Missing First-Class Framework
- Enterprise `audit_logs` table requested—appears absent.
- Notifications framework (in-app + email) not found in model snapshot.

### 7. Scalability Assessment

**Likely bottlenecks:**
- Permission checks hitting DB repeatedly (no caching)
- Reporting queries aggregating over attendance_logs without dedicated summary tables
- Attendance logs indexing helps but deeper query patterns (department/employee) may still be expensive

**Recommended scaling approach:**
- Add permission caching (request-scoped + redis)
- Add materialized rollups for daily/monthly metrics (or scheduled summary tables)
- Partition attendance_logs by time/org (if data volume large)

### 8. Security Assessment

**Strengths:**
- JWT verification + token blacklist
- `is_active` enforcement
- Password strength validation exists in security.py
- Input validation via Pydantic schemas (assumed across routers)

**High-risk items:**
- Authorization inconsistency across routers: role-name checks bypass permission taxonomy
- Lack of standardized org scoping in all queries (needs audit)
- Audit logging fragmentation: blockchain audit log exists but enterprise audit_logs not validated

### 9. Performance Assessment

**Observed:**
- Permission guard may query Permission/RolePermission tables each request.
- Attendance queries may need dedicated indexes beyond what is already in models.
- Reporting endpoints should rely on efficient aggregated queries or precomputed summaries.

---

## Current Phase-4 Readiness Summary
- RBAC schema exists, but enforcement needs to be unified.
- Attendance correction and manual overrides exist structurally but workflow/audit integration must be verified.
- Reporting/payroll/audit/notifications are partially present and likely require deeper implementation.

## PHASE 4 GO / NO-GO (Architecture Review)
**GO with conditions** — enterprise implementation can begin only after identified blockers are resolved (see below section of roadmap document).

