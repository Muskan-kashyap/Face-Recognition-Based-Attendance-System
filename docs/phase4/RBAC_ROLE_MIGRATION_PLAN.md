# RBAC_ROLE_MIGRATION_PLAN.md
Date: 2026-06-21
Scope: Migration planning only. No code changes, no migrations generated.

## 1) Goals
1. Canonicalize role names to exactly:
   - `SuperAdmin`
   - `Admin`
   - `Manager`
   - `HR`
   - `Finance`
   - `Employee`
   - `Auditor`
2. Eliminate ambiguity caused by legacy variants:
   - `"Super Admin"` (space)
   - `"Superadmin"` / case variants
3. Remove authorization drift by aligning role-name usage with permission-based enforcement.

## 2) Canonicalization Strategy

### Step A: Identify existing role rows
- Query `roles.name` values and build a mapping:
  - If `name` matches any case/space variant of Super Admin, map to `SuperAdmin`.
  - Ensure `Admin`, `Manager`, `Employee` are exact.

### Step B: Backfill/merge role permissions
Because the system currently has duplicated permission sources (`roles.permissions` JSONB + `role_permissions`), migration plan must define source-of-truth.

- **Recommended source-of-truth:** `role_permissions` join table.
- For each canonical role:
  - Ensure `role_permissions` contains the full permission set required.
  - Treat `roles.permissions` JSONB as compatibility layer during a transition window.

### Step C: Deprecate JSONB permissions (compat window)
- After canonicalization + permission seeding:
  - Keep JSONB populated to avoid breakage.
  - Disable JSONB checks later by changing `require_permission()` implementation (future step).

## 3) Migration Compatibility Constraints
- Existing JWT tokens only carry `sub` and `type`. Role changes take effect immediately via DB lookup.
- Therefore, canonicalizing `roles.name` does not require token invalidation, but authorization decisions using role-name checks will change immediately.
- Since we are planning migration only: schedule rollout in a maintenance window.

## 4) Rollout Order (no code, no migrations executed here)
1. Seed/ensure canonical roles exist.
2. Update role name strings for existing super admin variants.
3. Backfill/normalize `role_permissions` for canonical roles.
4. Confirm effective permissions for representative users.
5. Only then proceed to router standardization (replace role-name checks with permission guards).

## 5) Acceptance Criteria
- No role exists with non-canonical name variants.
- Permission guard outcomes for test users are identical (or improved) across environments.


