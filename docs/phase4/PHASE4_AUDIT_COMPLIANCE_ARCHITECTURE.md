# PHASE4_AUDIT_COMPLIANCE_ARCHITECTURE.md
Date: 2026-06-21
Scope: Phase 4.2 — Enterprise Audit & Compliance Module (Architecture Design Only; no code, no migrations).

> Compliance is implemented as an enterprise-grade, append-only audit architecture that is
> multi-tenant aware, permission-aware, tamper-evident, and searchable.

---

## 1) Enterprise Audit Architecture (Overview)

### 1.1 Core principles
1. **Append-only audit trail**: every security-relevant action produces an immutable audit record.
2. **Tenant boundary enforcement**: every audit event is tagged with `org_id` where applicable.
3. **Attribution**: audit record always includes:
   - `actor_user_id` (or platform actor)
   - `actor_role_name` (role at time of action)
   - `action` (namespaced)
   - `target_type` / `target_id`
   - `ip_address`, `user_agent`
   - `correlation_id` (request trace)
4. **Before/After state**: store structured JSON state deltas for changes.
5. **Tamper evidence**:
   - keep current `blockchain_audit_logs` as a separate immutable anchoring stream.
   - compute cryptographic hashes for each audit record and optionally anchor hashes.

### 1.2 Existing repository audit inputs (reuse)
- `backend/app/db/models/all_models.py` contains:
  - `BlockchainAuditLog` (append-only compliance signal)
- Attendance system already persists rich operational events:
  - `AttendanceLog`
  - `ManualOverride`
  - enrollment/recognition/spoof logs

### 1.3 Proposed architecture components

**Client → API → AuthZ → Services → Audit Service → DB**

- **API Layer (FastAPI Routers)**
  - does authentication (`get_current_active_user`)
  - does authorization (permission dependencies)
  - provides request context headers to downstream services (correlation id, ip)

- **Audit Service (New, service-layer)**
  - single entry point: `audit_log(event)`
  - formats and validates event payload
  - persists to `audit_logs`
  - optionally emits blockchain anchoring jobs

- **Event Capture / Middleware**
  - request correlation id middleware
  - auth decision hooks (optional)
  - exception-based audit capture for rejected/failed security operations

- **Search/Export Layer (API only; later)**
  - audit query endpoints with indexing-aware filters
  - CSV/PDF export generation via existing `reports` table job mechanism

---

## 2) Complete Database Schema (Audit-Focused)

> This is the schema design needed for Phase 4.2. It is described here without assuming current tables already exist.

### 2.1 New tables

#### `audit_logs`
Purpose: unified enterprise audit trail with full structured fields.

Columns (recommended):
- `id` (BIGSERIAL / UUID)
- `occurred_at` (timestamptz, default now())
- `tenant_org_id` (uuid, FK → organizations.id, nullable for platform-global events)
- `actor_user_id` (int FK → users.id, nullable if platform actor)
- `actor_role_name` (text) — role name at time of action
- `action` (text) — namespaced string, e.g. `users.update`
- `target_type` (text) — `User`, `Role`, `AttendanceLog`, `ManualOverride`, `Organization`, `Permission`, etc.
- `target_id` (text) — string representation for polymorphic targeting
- `resource_org_id` (uuid) — explicit scoping of audited resource (can differ from tenant_org_id in legacy cases)
- `before_state` (jsonb) — structured snapshot
- `after_state` (jsonb) — structured snapshot
- `reason` (text, nullable) — required for overrides/approvals
- `ip_address` (inet / text)
- `user_agent` (text)
- `correlation_id` (text)
- `status` (text) — `success|failure`
- `failure_reason` (text, nullable)

Indexes:
- `(tenant_org_id, occurred_at DESC)`
- `(actor_user_id, occurred_at DESC)`
- `(action, occurred_at DESC)`
- `(target_type, target_id)`
- `(correlation_id)`

Row-level immutability:
- no UPDATE/DELETE
- enforce via app-layer and optionally DB triggers.

#### `audit_blockchain_anchors` (optional but recommended)
Purpose: track anchoring status for audit log record hashes to blockchain.

Columns:
- `id`
- `audit_log_id`
- `record_hash` (char(64))
- `tx_hash` (nullable)
- `anchored_at` (nullable)
- `status` (`pending|anchored|failed`)

Indexes:
- `(status, anchored_at)`

> If you prefer strict reuse of `BlockchainAuditLog`, this table can be omitted.

### 2.2 Relationships (audit schema)
- `audit_logs.tenant_org_id` → `organizations.id` (nullable)
- `audit_logs.actor_user_id` → `users.id` (nullable)

---

## 3) SQLAlchemy Model Design

### 3.1 `AuditLog` model
Key design points:
- use SQLAlchemy JSONB columns for before/after/reason metadata
- store `target_type` + `target_id` for polymorphic associations
- store `tenant_org_id` and/or `resource_org_id` explicitly for consistent scoping

### 3.2 Tamper-evidence
- compute `record_hash` in app-layer using canonical JSON serialization:
  - hash of (id, occurred_at, actor_user_id, action, target_type, target_id, after_state)
- store hash in audit_logs or in a dedicated anchor table.

### 3.3 Multi-tenant enforcement in model
- model doesn’t enforce authorization, but stores enough information so API can scope.

---

## 4) Alembic Migration Strategy (Minimize Risk)

> No migrations are created in this session. This is the strategy.

### 4.1 Phased migration
1. **Create new `audit_logs` table**
   - safe CREATE TABLE
   - add indexes concurrently where possible
2. **Add anchor tracking table** (optional)
3. **Backfill strategy**
   - do not backfill historical rows unless necessary
   - for compliance, it may be acceptable to start from rollout time.
4. **Feature flag**
   - add configuration switch `audit.enabled` to allow safe rollout.

### 4.2 Compatibility
- keep `blockchain_audit_logs` untouched
- audit service can optionally anchor only new records.

---

## 5) Service Layer Architecture

### 5.1 `AuditService`
Responsibilities:
- normalize audit event payload
- validate schema of `before_state` and `after_state`
- persist audit record
- emit blockchain anchor job (optional)

Key methods:
- `log_event(event: AuditEvent) -> AuditLogId`
- `log_mutation(actor, action, target, before, after, reason, request_ctx)`
- `log_access_decision(...)` (optional; can be high volume)

### 5.2 `AuditEvent` domain object
Fields match DB columns.

### 5.3 `AuditContextProvider`
- builds request context from FastAPI request
- includes correlation id, ip, user agent, org resolution

---

## 6) Event Capture Strategy

### 6.1 Event taxonomy
Audit events should be namespaced by domain:
- `auth.*`
- `users.*`
- `org.*`
- `permissions.*`
- `attendance.*`
- `manual_overrides.*`
- `payroll.*` (future Phase 4.3/4.4)
- `reports.*`
- `security.*`

### 6.2 What to capture (Phase 4.2 minimum)
- User creation/update/deactivate/reactivate
- Face enrollment completion/failure
- Attendance check-in/out events (success/failure)
- Manual override create/approve/reject (once correction workflow is wired)
- Permission/role assignment changes
- Organization lifecycle changes
- Any security-relevant failure events:
  - permission denied
  - token revocation usage

### 6.3 Success vs failure
- Always log decision outcome:
  - `status=success|failure`
  - `failure_reason` for denials/validation errors

---

## 7) Middleware / Decorator Approach

### 7.1 Correlation ID middleware
- middleware generates or propagates `correlation_id`
- adds to response headers
- stores on `request.state`

### 7.2 Audit decorator for mutations
- `@audit(action="users.update", target_resolver=..., reason_required=...)`

Design choices:
- apply decorator only on service methods (not routers) to keep business logic clean
- router collects request ctx and passes actor + org id

### 7.3 Authorization audit
- permission middleware can optionally log denied decisions (careful with volume)
- store only minimal fields for denied events to avoid large logs

---

## 8) API Specifications

### 8.1 Core endpoints
1. `GET /audit/logs`
   - Query params:
     - `action` (exact or prefix)
     - `target_type`
     - `target_id`
     - `actor_user_id`
     - `from`, `to` timestamps
     - `status`
     - `correlation_id`
     - `page`, `page_size`
   - RBAC requirement: `audit.view` (scoped)

2. `GET /audit/export`
   - Accepts `format=csv|pdf`
   - uses `reports` job table for async generation

3. `GET /audit/summary`
   - returns counts grouped by action over time bucket

### 8.2 Response models
- `AuditLogResponse` includes pagination metadata

---

## 9) Frontend Dashboard Specifications

### 9.1 UI pages
- `Audit Center`
  - search/filter panel
  - table view (sortable columns)
  - correlation drilldown
  - details drawer showing before/after JSON

### 9.2 RBAC-aware navigation
- visible only for roles with `audit.view`

---

## 10) Search / Filter Strategy

### 10.1 Query patterns
- filter by:
  - time range
  - action prefix (e.g., `users.`)
  - actor
  - target
  - correlation id

### 10.2 Index alignment
Indexes defined in the schema must match query filters.

### 10.3 Pagination strategy
- time-based cursor pagination preferred:
  - `occurred_at` + `id`

---

## 11) CSV/PDF Export Design

### 11.1 Use existing `reports` table
- create `Report` jobs with `report_type='compliance_audit'` (or a new audit export type)
- `parameters` includes filters and columns

### 11.2 Export contents
- CSV: flat fields + compact JSON strings
- PDF: summary + tabular entries + details sections

### 11.3 RBAC gating
- export endpoints require `audit.view`
- tenant scoping: export must only include logs for allowed `org_id` scope

---

## 12) Multi-tenant Security Design

### 12.1 Tenant scoping rules
- Always resolve allowed org scope for the actor from JWT/user DB.
- For Admin/Manager roles, restrict by `current_user.org_id`.
- For SuperAdmin/platform roles, allow cross-org read but only with `platform.audit.view`.

### 12.2 Data leakage prevention
- API layer must enforce `WHERE tenant_org_id IN allowed_org_ids`.
- Audit logs must include `tenant_org_id` explicitly.

---

## 13) Performance Considerations

### 13.1 Log volume controls
- allow logging levels:
  - `core` (mutations only)
  - `extended` (auth failures)

### 13.2 Async processing for expensive actions
- anchoring/hash computations can be queued
- export generation is job-based via `reports`

### 13.3 Partitioning (future)
- partition `audit_logs` by month and `tenant_org_id` for very large deployments

---

## 14) Data Retention Policy

### 14.1 Recommended retention windows
- `audit_logs`: 24 months online, then archive (cold storage) for compliance
- `blockchain_audit_logs`: keep indefinitely (append-only)

### 14.2 GDPR/PII handling
- ensure `before_state/after_state` redacts sensitive fields (passwords, biometric raw)
- only store biometric references (embedding ids, version tags), not raw biometric data

---

## 15) Compliance Mapping (SOC2 / ISO27001 style)

### 15.1 SOC 2 CC series mapping (representative)
- **CC6.x**: Logical access controls
  - audit permissions view/change
- **CC7.x**: Monitoring and detection
  - audit logs for security events and anomalies
- **CC8.x**: Change management
  - audit for role/permission and config changes

### 15.2 ISO27001 mapping (representative)
- A.5: Organizational controls (governance)
- A.8: Access control
- A.12: Operations security (logging, monitoring)
- A.18: Compliance

---

## 16) Testing Strategy

### 16.1 Unit tests
- audit service payload normalization
- correct required fields enforcement (reason for overrides)
- hash computation determinism

### 16.2 Integration tests
- verify audit_logs insert on:
  - user update
  - face enrollment event
  - attendance override

### 16.3 RBAC tests
- only authorized roles can access `GET /audit/logs`
- denied users cannot infer existence via filters

### 16.4 Performance tests (non-blocking)
- ensure query endpoints use indexes and return within SLA for 1M rows dataset (estimated)

---

## 17) Sequence Diagrams (Text)

### 17.1 User mutation audit
```
Client
  -> API Router (users.update)
  -> get_current_active_user
  -> require_permission(users.update)
  -> UserService.update(user_in)
  -> AuditService.log_event(action=users.update, before, after, reason, request_ctx)
  -> DB INSERT audit_logs
  -> API returns response
```

### 17.2 Permission denied audit (optional)
```
Client
  -> API Router (sensitive endpoint)
  -> AuthZ guard evaluates permission
  -> Permission denied
  -> AuditService.log_event(status=failure, action=<endpoint_permission>)
  -> return 403
```

---

## 18) Folder / File Structure (Reuse existing repository patterns)

### 18.1 Backend structure (recommended)
- `backend/app/services/audit_service.py`
- `backend/app/services/audit/`
  - `event_types.py`
  - `hashing.py`
- `backend/app/api/routers/audit.py` (or within `backend/app/routers/audit.py`)
- `backend/app/middleware/correlation_id.py`

### 18.2 Reuse existing conventions
- router-level schema in `backend/app/schema/`
- repositories optionally for audit reads

---

## 19) Risk Analysis

### 19.1 Main risks
1. **PII leakage** via storing before/after state without redaction
   - mitigation: redaction layer in AuditService
2. **Performance impact** due to synchronous audit writes
   - mitigation: use async/queue for non-critical paths; keep core synchronous with batching if needed
3. **Authorization gaps** in audit retrieval endpoints
   - mitigation: strict org scoping at query layer + tests
4. **Schema migration risk**
   - mitigation: additive migrations with feature flag

### 19.2 Risk rating
- Schema/PII risk: Medium-High
- Performance risk: Medium
- Authorization risk: High

---

## 20) Step-by-step Implementation Roadmap (Design → Execution)

> Step-by-step roadmap is provided without code generation.

### Phase 4.2.1: Audit foundation
1. Confirm existing audit-like mechanisms (`BlockchainAuditLog`) usage and ownership.
2. Finalize `audit_logs` schema and redaction rules.
3. Implement AuditService contract and event taxonomy.
4. Add correlation-id middleware.

### Phase 4.2.2: Event instrumentation
5. Add audit hooks in critical services:
   - user CRUD
   - attendance events
   - manual overrides/corrections (once wired)
   - RBAC/permission changes
6. Add RBAC protection to `GET /audit/logs`.

### Phase 4.2.3: UI & exports
7. Build audit dashboard with filters and correlation drilldown.
8. Implement CSV/PDF exports using `reports` job model.

### Phase 4.2.4: Compliance readiness
9. Validate retention policy and redaction.
10. Run comprehensive tests and security review.

---

## Acceptance Criteria for Phase 4.2
- All audit events are recorded with correct tenant scoping.
- Audit logs are queryable with filters aligned to indexes.
- Exports respect RBAC and tenant boundaries.
- Redaction prevents storage of raw biometrics and credentials.
- Performance is acceptable for expected log volumes.

