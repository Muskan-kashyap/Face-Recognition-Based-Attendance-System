# Troubleshooting Guide

## Issue 1: `ConnectionRefusedError` on Redis at Startup
**Symptom**: Logs show `redis.exceptions.ConnectionError: Error 111 connecting to localhost:6379.`
**Root Cause**: The backend attempts to ping Redis during startup validation.
**Resolution**:
1. Verify Redis is running: `docker ps | grep redis`
2. If not running: `docker run -d -p 6379:6379 redis:7.2-alpine`
3. Confirm the `REDIS_URL` variable in `.env` matches the running instance.
> [!NOTE]
> The system will continue to function even without Redis due to the fail-open mechanism. The only impact is that logout (JWT blacklisting) and rate limiting will be disabled until Redis recovers.

---

## Issue 2: Face Not Recognized (`Identity not recognized` 400 error)
**Symptom**: A valid employee checks in but receives a 400 error.
**Root Cause (most common)**:
1. Employee has no face embedding enrolled (`face_embeddings` table is empty for their user).
2. Lighting conditions degraded L2 distance beyond the 0.6 threshold.
**Resolution**:
1. Check if the employee has a `FaceEmbedding` record: `SELECT * FROM face_embeddings WHERE user_id=<id>;`
2. If empty, enroll the employee via `POST /api/v1/users/{user_id}/enroll-face` with a high-quality frontal photo.
3. If embedding exists, consider re-enrolling with better lighting.

---

## Issue 3: Alembic `DatatypeMismatch` on Migration
**Symptom**: `alembic upgrade head` fails with `DatatypeMismatch: column "is_revoked" is of type boolean but expression is of type integer`.
**Root Cause**: Auto-generated Alembic migrations sometimes produce SQL that PostgreSQL cannot execute without explicit type casting.
**Resolution**: Open the failing migration file in `backend/alembic/versions/` and add a `USING` cast to the `ALTER COLUMN` statement:
```python
# Before:
op.alter_column('org_api_keys', 'is_revoked', type_=sa.Integer())

# After:
op.execute("ALTER TABLE org_api_keys ALTER COLUMN is_revoked TYPE INTEGER USING is_revoked::integer")
```

---

## Issue 4: Blockchain Anchoring Silently Failing
**Symptom**: Check-ins succeed, but `blockchain_audit_logs` shows no records or shows `tx_hash` values starting with `sim_tx_`.
**Root Cause**: Web3 integration is disabled (either by the `BLOCKCHAIN_ENABLED=false` environment variable or via the `system_settings` database toggle).
**Resolution**:
1. Call `GET /api/v1/admin/settings/blockchain` to check the current status.
2. If it shows `false`, call `POST /api/v1/admin/settings/blockchain/toggle` with `{"enabled": true}` using a SuperAdmin JWT.
3. Verify `BLOCKCHAIN_URL` and `BLOCKCHAIN_PRIVATE_KEY` are correctly set in the environment.

---

## Issue 5: Backend Container Fails to Start (`ImportError`)
**Symptom**: Docker container exits immediately with a Python `ImportError`.
**Root Cause**: The `ai-service` package (torch, deepface) is heavy and may have a version conflict.
**Resolution**:
1. Check container logs: `docker logs attendance_backend_prod`
2. The heavy ML dependencies (torch, deepface) should ONLY exist in the `ai-service` container — not in the `backend`. If they appear in `backend/requirements.txt`, remove them.
