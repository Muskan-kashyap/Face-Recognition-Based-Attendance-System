# PHASE4_TECHNICAL_DEBT_REPORT.md

## Phase 4 — Technical Debt Inventory (Analysis Only)
Date: 2026-06-21

### Legend
- **CRITICAL**: likely breaks security/compliance or blocks Phase 4 implementation
- **HIGH**: major correctness/performance risk
- **MEDIUM**: maintainability/feature gaps likely to slow Phase 4
- **LOW**: cosmetic/low impact issues

---

## 1) Dead Code / Legacy / Deprecated Paths
1. **Hard-coded role checks still used in some routers**
   - Evidence: `backend/app/routers/admin.py` checks `current_user.role.name != "SuperAdmin"`.
   - Evidence: RBAC redesign docs highlight seed naming mismatch.
   - **CRITICAL**

2. **Duplicate permission sources (`Role.permissions` JSONB vs join-table `role_permissions`)**
   - Evidence: `Role.permissions` exists; require_permission also checks both.
   - **HIGH**

3. **Blockchain audit logging used as proxy for compliance/audit**
   - Evidence: `BlockchainAuditLog` append-only exists.
   - Phase 4 requires an `audit_logs` table with rich before/after state.
   - If currently relied upon, it can be incomplete.
   - **HIGH**

---

## 2) Duplicate Business Logic / Inconsistent Implementations
1. **Authorization behavior duplicated between role-name guards and permission guards**
   - Evidence: `require_admin()` exists; many endpoints likely use role-name string checks.
   - Risk: drift and gaps.
   - **CRITICAL**

2. **Org scoping likely inconsistent across routers**
   - Risk: tenant boundary leaks.
   - **CRITICAL**

---

## 3) Router Inconsistencies
1. **Authorization not declared at the router-level uniformly**
   - Some routes require permission, others rely on `require_admin` or raw role-name checks.
   - **CRITICAL**

2. **Mismatch between seeded super admin role naming and authorization checks**
   - Evidence: RBAC audit report indicates seed mismatch: `"Super Admin"` vs `"SuperAdmin"`.
   - **HIGH**

---

## 4) Service Inconsistencies
1. **Permission caching missing**
   - `require_permission` performs DB queries per request.
   - **HIGH**

2. **Reporting/payroll services may not follow enterprise model layering**
   - Risk: analytics derived ad-hoc rather than via consistent service layer.
   - **MEDIUM**

---

## 5) Migration Issues
1. **Model/table proliferation risks (all_models.py monolith)**
   - Harder to reason about migrations.
   - Some tables might exist but not indexed for Phase 4 query patterns.
   - **MEDIUM**

2. **No explicit enterprise payroll schema shown (policies/components/runs/entries)**
   - Might require migrations and migration planning.
   - **HIGH**

---

## 6) Testing Gaps
1. **RBAC test suite scope appears narrow**
   - Evidence: `backend/app/tests/test_deps_permission.py` stubs and tests only basic permission guard behavior.
   - Missing: route-level enforcement tests.
   - **HIGH**

2. **Attendance correction workflow tests likely missing**
   - ManualOverride exists, but correction request/approval models required by Phase 4 may be absent.
   - **HIGH**

3. **Audit coverage not validated end-to-end**
   - Blockchain audit log exists but enterprise `audit_logs` framework not present.
   - **HIGH**

---

## 7) Performance Bottlenecks
1. **Permission checks hitting DB**
   - **HIGH**

2. **Reporting aggregation over raw attendance_logs without precomputed summaries**
   - **MEDIUM/HIGH** depending on data volume (not measured here)

---

## Summary Table
| Item | Severity |
|---|---|
| Inconsistent authorization (role-name vs permission guards) | CRITICAL |
| Tenant scoping inconsistency risk | CRITICAL |
| Duplicate permission sources (JSON + join tables) | HIGH |
| Seed naming mismatch for SuperAdmin | HIGH |
| Missing enterprise audit_logs / audit framework | HIGH |
| Missing payroll enterprise schema | HIGH |
| Missing notifications framework | MEDIUM/HIGH |
| Missing route-level RBAC tests | HIGH |
| Missing caching for permissions | HIGH |

