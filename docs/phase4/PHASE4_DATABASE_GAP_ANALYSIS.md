# PHASE4_DATABASE_GAP_ANALYSIS.md

## Phase 4 — Database Gap Analysis (Analysis Only)
Date: 2026-06-21

> Scope note: This analysis is based on the SQLAlchemy model definitions visible in `backend/app/db/models/all_models.py` and alembic versions list. Some tables required by Phase 4 may not be present in that model snapshot.

### 1. Current ERD (Text Form)

#### Tenancy
- `organizations` (id, name, legal_id, blockchain_root_key, zkp_threshold, is_active)
- `org_api_keys` (org_id → organizations.id)
- `departments` (org_id → organizations.id)
- `shifts` (org_id → organizations.id)

#### Identity & RBAC
- `users` (org_id → organizations.id, role_id → roles.id, dept_id → departments.id, shift_id → shifts.id)
- `roles` (name, permissions JSONB)
- `permissions` (name, category, is_active)
- `role_permissions` (role_id → roles.id, permission_id → permissions.id)
- `user_roles` (user_id → users.id, role_id → roles.id) for additional roles

#### Attendance
- `attendance_logs` (user_id → users.id, check_in/out, status, source, is_live, is_deleted)
- `manual_overrides` (target_user_id → users.id, admin_user_id → users.id, attendance_log_id → attendance_logs.id nullable)

#### Biometric/Recognition Events (Phase 3)
- `face_embeddings` (user_id → users.id, vector pgvector)
- `enrollment_events` (user_id → users.id, org_id → organizations.id)
- `spoof_detection_logs` (user_id nullable, org_id → organizations.id)
- `recognition_events` (org_id → organizations.id, user_id nullable)
- `emotion_logs` (user_id → users.id, attendance_log_id → attendance_logs.id)

#### Analytics/Exports
- `reports` (org_id → organizations.id, requested_by → users.id, report_type, status, output_format, storage_url)
- `monthly_growth_summary` (user_id → users.id)

#### Payroll (Phase 3 partial)
- `payrolls` (user_id → users.id, org_id → organizations.id, month/year, base_salary/deductions/reimbursements_total/total_salary, status)

#### Audit (current)
- `blockchain_audit_logs` (ref_type, ref_id, anchored_at, record_hash, tx_hash)

#### Other modules
- `tickets` (user_id → users.id, org_id → organizations.id)
- `reimbursements` (user_id → users.id, org_id → organizations.id)
- `system_settings` (global toggles)

---

### 2. Per-Table Recommendation for Phase 4
For each relevant table:

#### KEEP
- `organizations`, `org_api_keys`, `departments`, `shifts`
- `users`, `roles`, `permissions`, `role_permissions`, `user_roles`
- `attendance_logs`, `face_embeddings`, `enrollment_events`, `spoof_detection_logs`, `recognition_events`, `emotion_logs`
- `manual_overrides` (but needs workflow/audit integration)
- `reports` (export job table)
- `monthly_growth_summary` (use for performance rollups)
- `tickets`, `reimbursements` (if used in current Phase 3)
- `system_settings`
- `blockchain_audit_logs` (append-only compliance signal; may coexist)

#### REFACTOR
- `roles.permissions` JSONB (remove duplication, or keep temporarily with compatibility window)
- `ManualOverride` (ensure it maps cleanly to attendance correction workflow, status transitions, approval chain)
- `AttendanceLog.status` taxonomy may need expansion to distinguish correction-requested vs corrected

#### MERGE
- Potential merge: separate audit streams into first-class enterprise `audit_logs` while keeping blockchain audit as secondary.
- Not implemented here; recommendation only.

#### REPLACE
- `payrolls` likely replaced/augmented by enterprise payroll policy/components/runs/entries.

#### REMOVE
- No tables are explicitly recommended for removal in this analysis-only phase. Removal should be after migration compatibility assessment.

---

### 3. Missing Tables for Enterprise Scale (Phase 4)
These are required by your Phase 4 objectives and not confirmed present in the model snapshot:

#### Audit & Compliance
- `audit_logs` (fields: actor_user_id, actor_role, org_id nullable, action, target_type/id, before_state, after_state, occurred_at, ip_address, user_agent, correlation_id, status)

#### Notifications
- `notifications`
- `notification_deliveries` (per-channel delivery status) or embedded delivery state

#### Attendance Correction Workflow
- `attendance_requests`
- `attendance_approvals`

> Since `manual_overrides` exists, these may be optional depending on whether you map Phase 4 correction workflow fully onto `manual_overrides` with added fields. For enterprise clarity, request/approval should be explicit.

#### Payroll Enterprise
- `salary_policies`
- `salary_components`
- `payroll_runs`
- `payroll_entries`
- `payroll_approvals` (if approval required)

#### Reporting (optional for performance)
- `attendance_daily_summaries`
- `attendance_monthly_summaries`

---

### 4. Redundant / Future Tables Required
- Redundant RBAC permission sources: `roles.permissions` vs `role_permissions`.
- Future: token session/revocation audit table if you need strict session management (not required by current Phase 4 spec but relevant).

---

## Summary
- Strong baseline exists for RBAC, attendance, manual overrides, exports.
- Enterprise Phase 4 requires **new first-class audit_logs + notifications + payroll enterprise schema + correction request/approval tables (or robust mapping into existing models)**.

