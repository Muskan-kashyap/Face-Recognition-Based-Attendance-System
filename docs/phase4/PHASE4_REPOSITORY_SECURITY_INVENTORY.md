# PHASE4_REPOSITORY_SECURITY_INVENTORY.md
Date: 2026-06-21
Scope: Analysis-only RBAC/tenant security inventory (Phase 4.1-A).

## Important Limitation / No-Go Condition
This inventory is **incomplete** because multiple repository-wide commands were observed to run indefinitely in the user’s terminal during this session (likely due to tooling/environment constraints). Only the following backend files were fully available for line-by-line inspection via tools:
- `backend/app/api/deps.py`
- `backend/app/routers/admin.py`
- `backend/app/routers/org.py`
- `backend/app/routers/payroll.py`
- `backend/app/routers/users.py`

Routers referenced in the project tree exist (e.g., attendance, reimbursement, ticketing), but they were not successfully read line-by-line within this session.

Therefore: **NO-GO** per the decision criteria.

---

## SECTION 1 — Router inventory

### Confirmed routers inspected (line-by-line)
| File | Router purpose (inferred from code) |
|---|---|
| `backend/app/routers/auth.py` | Auth endpoints (not inspected in this session) |
| `backend/app/routers/admin.py` | Global settings (blockchain toggle) |
| `backend/app/routers/org.py` | Organization create endpoint |
| `backend/app/routers/payroll.py` | Payroll read/generate/update |
| `backend/app/routers/users.py` | User CRUD + face enrollment |

### Routers present in repo tree but not inspected line-by-line
- `backend/app/routers/attendance.py`
- `backend/app/routers/reimbursement.py`
- `backend/app/routers/ticketing.py`

---

## SECTION 2 — Endpoint inventory (inspected files only)

### `backend/app/routers/admin.py`
1. **GET** `/settings/blockchain`
   - Current authorization mechanism:
     - `deps.get_current_active_user` for authentication
     - role-name check: `current_user.role.name != "SuperAdmin"`
   - Permission dependency present?: **No**
   - role-name check present?: **Yes**
   - has_any_role present?: **No**
   - require_admin present?: **No**
   - tenant scoping present?: N/A (global SystemSetting)
   - tenant scoping verified?: **N/A**
   - Recommended permission:
     - `platform.settings.manage`

2. **POST** `/settings/blockchain/toggle`
   - Current authorization mechanism:
     - role-name check `current_user.role.name != "SuperAdmin"`
   - Permission dependency present?: **No**
   - role-name check present?: **Yes**
   - tenant scoping present?: N/A (global SystemSetting)
   - Recommended permission:
     - `platform.settings.manage`

---

### `backend/app/routers/org.py`
1. **POST** `/`
   - Current authorization mechanism:
     - `deps.require_admin_or_super_admin` (role-name based)
     - allows `admin` and `superadmin` variants
   - Permission dependency present?: **No**
   - role-name check present?: **Indirectly Yes** (via dependency)
   - require_admin present?: **No** (but similar)
   - tenant scoping present?: N/A (creates organization)
   - tenant scoping verified?: **N/A**
   - Recommended permission:
     - `platform.organizations.manage` (SuperAdmin only)

---

### `backend/app/routers/payroll.py`
Key code paths rely on `is_admin_or_manager(current_user)` which normalizes role name.

1. **GET** `/`
   - Current authorization mechanism:
     - auth: `deps.get_current_active_user`
     - role-name logic:
       - if not admin/manager: returns only own payrolls (filter by `Payroll.user_id == current_user.id`)
       - else: returns org payrolls via `crud_payroll.get_multi_by_org(org_id=current_user.org_id, ...)`
   - Permission dependency present?: **No**
   - role-name check present?: **Yes**
   - tenant scoping present?: **Yes**
     - explicit `Payroll.user_id == current_user.id` for non-admins
     - org scoping via `org_id=current_user.org_id` for admins/managers
   - tenant scoping verified?: **PARTIAL** (route-level confirmation incomplete)
   - Recommended permissions:
     - `payroll.view` for reads
     - `payroll.manage` / `payroll.run` for generation

2. **POST** `/generate`
   - Current authorization mechanism:
     - auth + role-name check (admin/manager)
     - on fail: 403
   - Permission dependency present?: **No**
   - role-name check present?: **Yes**
   - tenant scoping present?: **Yes** (`User.org_id == current_user.org_id`, `Reimbursement.org_id == current_user.org_id`, `Payroll.org_id == current_user.org_id`)
   - tenant scoping verified?: **PARTIAL**
   - Recommended permissions:
     - `payroll.run`

3. **PATCH** `/{payroll_id}`
   - Current authorization mechanism:
     - auth + role-name check (admin/manager)
   - Permission dependency present?: **No**
   - role-name check present?: **Yes**
   - tenant scoping present?: **Yes** (`Payroll.org_id == current_user.org_id`)
   - tenant scoping verified?: **PARTIAL**
   - Recommended permissions:
     - `payroll.approve` or `payroll.manage`

---

### `backend/app/routers/users.py`
1. **GET** `/`
   - Current authorization mechanism:
     - `deps.get_current_active_user`
     - role-name check via `deps.has_any_role(current_user, "Admin", "Manager", "SuperAdmin", "Super Admin")`
   - Permission dependency present?: **No**
   - role-name check present?: **Yes**
   - has_any_role present?: **Yes**
   - require_admin present?: **No**
   - tenant scoping present?: **Yes** (`User.org_id == current_user.org_id`)
   - tenant scoping verified?: **PARTIAL**
   - Recommended permissions:
     - `users.view.org`

2. **POST** `/`
   - Current authorization mechanism:
     - `deps.has_any_role(... Admin/Manager/SuperAdmin/Super Admin)`
     - additional org_id assignment to enforce admin session
   - Permission dependency present?: **No**
   - role-name check present?: **Yes**
   - tenant scoping present?: **Yes**
   - tenant scoping verified?: **PARTIAL**
   - Recommended permissions:
     - `users.create` (or `users.manage.org`) — Admin-only

3. **GET** `/me`
   - Current authorization mechanism:
     - `deps.get_current_active_user` (self)
   - Permission dependency present?: **No**
   - role-name check present?: **No**
   - Recommended permission:
     - `self.users.view` or `users.view.self`

4. **GET** `/{user_id}`
   - Current authorization mechanism:
     - tenant scoping via `User.org_id == current_user.org_id`
     - if `current_user.id != user_id` then `has_any_role(Admin/Manager/SuperAdmin/Super Admin)`
   - Permission dependency present?: **No**
   - role-name check present?: **Yes**
   - tenant scoping present?: **Yes**
   - tenant scoping verified?: **PARTIAL**
   - Recommended permissions:
     - `users.view.org` (for Admin)
     - `users.view.team` (if manager-team model exists; otherwise none)

5. **POST** `/{user_id}/enroll-face`
   - Current authorization mechanism:
     - tenant scoping: query filters by `User.org_id == current_user.org_id`
     - access if user has any role in Admin/Manager/SuperAdmin/Super Admin OR self (`current_user.id == user_id`)
   - Permission dependency present?: **No**
   - role-name check present?: **Yes**
   - tenant scoping present?: **Yes**
   - tenant scoping verified?: **PARTIAL**
   - Recommended permissions:
     - `face.manage.org` (Admin)
     - `face.request.self` (Employee)
     - Manager should likely be removed unless approvals exist.

---

## SECTION 3 — Authorization inventory (dependency layer)

### `backend/app/api/deps.py`
- Authn: `get_current_user()` loads user from DB + blacklist check.
- Authz mechanisms present:
  1) `require_permission(permission_name)`
  2) role-based guards:
     - `has_any_role()`
     - `require_admin()`
     - `require_manager_or_admin()`
     - `require_admin_or_super_admin()`

Key security issues (from inspection):
- **Mixed model**: routers do not consistently use `require_permission`.
- **Duplicate permission sources**: `Role.permissions` JSONB and `role_permissions` join table.
- **No caching** in permission resolution.
- **Tenant scoping not built into authorization guard**, which means routers must handle resource scoping correctly.

---

## SECTION 4 — Tenant isolation inventory (inspected files only)

Confirmed tenant scoping patterns:
- Users endpoints filter by `User.org_id == current_user.org_id`.
- Payroll endpoints filter by `Payroll.org_id == current_user.org_id` for org-level data and `Payroll.user_id == current_user.id` for non-admins.

Not confirmed in this session:
- Attendance endpoints
- Ticketing endpoints
- Reimbursement endpoints
- Reporting exports

---

## SECTION 5 — Missing permissions (examples)
Because permission taxonomy was not fully enumerated across the codebase in this session, missing permissions are listed as examples derived from Phase 4 requirements and router intent.

- `users.view`
- `users.create`
- `users.update`
- `users.delete`
- `attendance.view`
- `attendance.override`
- `ticket.view`
- `ticket.manage`
- `reimbursement.view`
- `reimbursement.approve`
- `payroll.view`
- `payroll.run`
- `payroll.approve`
- `platform.organizations.manage`
- `platform.admin` or `platform.settings.manage`

---

## SECTION 6 — Hardcoded role checks
Confirmed by inspection:
- `admin.py`: `current_user.role.name != "SuperAdmin"`
- `users.py`: `deps.has_any_role(... "SuperAdmin", "Super Admin")`
- `payroll.py`: role-name logic via `is_admin_or_manager()`
- `org.py`: `require_admin_or_super_admin` allows admin and superadmin

---

## SECTION 7 — Endpoints lacking authorization
All inspected endpoints that rely on role-name checks rather than `Depends(require_permission(...))` are considered “authorization standard non-compliant” for Phase 4.1.

---

## SECTION 8 — Endpoints lacking tenant scoping
- Admin blockchain settings: global; tenant scoping is N/A.
- All other audited endpoints used org filters in queries.

---

## SECTION 9 — GO / NO-GO Assessment
**Decision: NO-GO**

### Criteria not met
- Not every endpoint/authorization path was audited (inspected only a subset of routers).
- Tenant boundaries for attendance/ticketing/reimbursement/reporting are not fully verified.

### Required before GO
- Complete line-by-line inspection of every file under `backend/app/routers/**/*.py`.
- Produce full endpoint inventory for all routes including authorization + tenant scoping fields.


