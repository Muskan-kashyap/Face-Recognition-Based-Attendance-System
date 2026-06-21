# RBAC_CACHE_DESIGN.md
Date: 2026-06-21
Scope: Permission caching design only (no implementation).

## 1) Objective
Reduce DB load from permission checks by caching permission sets for users (or roles) and minimizing repeated queries.

## 2) Cache Scope Options

### Option A (Recommended): Cache effective permissions per user
- Key: `rbac:perms:user:{user_id}:{org_id}:{perm_version}`
- Value: serialized list/set of permission strings
- TTL: 5–30 minutes (short enough to reflect changes quickly)

### Option B: Cache per role and union
- Key: `rbac:perms:role:{role_id}:{perm_version}`
- Value: permission set
- Effective permissions computed by union across user's roles each request
- TTL: 5–30 minutes

**Decision:** Start with Option B if users have many roles; use Option A if single-role dominant.

## 3) Invalidation Strategy
Permission changes happen via:
- roles.permissions JSONB update (if still used)
- role_permissions join table changes
- role assignment changes (user_roles)

Use `perm_version` and bump it on any change.

- Add/maintain a `permission_version` or `role_version` field (recommended) in DB.
- Cache key includes version; when version increments, old keys naturally expire.

### Invalidation triggers
- After updating `role_permissions` for a role: increment role's version or global permission_version.
- After updating `user_roles` for a user: either increment user version or use short TTL.

## 4) TTL
- TTL: 10 minutes initial conservative default.
- For security-critical environments, reduce TTL to 1–5 minutes.

## 5) Role Update Behavior
- If a role’s permissions are changed:
  - invalidate cached permissions for users that hold the role (hard invalidation), OR rely on version bump.

## 6) User Role Change Behavior
- If a user’s role assignment changes:
  - invalidate cached entry by version bump OR enforce TTL small.

## 7) Failure Mode
- If Redis is unavailable:
  - fail-open is not acceptable for auth.
  - Recommended behavior: fallback to DB permission resolution (slower) but still correct.


