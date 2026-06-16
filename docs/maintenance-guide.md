# Maintenance Guide

## 1. Repository Maintenance

### Dependency Updates
Run monthly to identify outdated packages:
```bash
cd backend
pip list --outdated
pip install -U <package-name>
# Run full test suite after each major upgrade
pytest
```

Key packages to monitor for breaking changes:
- `fastapi` / `starlette` — Check for deprecation warnings on each release.
- `sqlalchemy` — ORM API changes can break CRUD layer.
- `deepface` — Model update may change embedding vector dimensionality.
- `web3` — Web3.py v6 has a breaking API compared to v5.

### Database Maintenance
Monthly tasks:
```sql
-- Reclaim storage from deleted rows (soft-deletes accumulate over time)
VACUUM ANALYZE attendance_logs;

-- Rebuild pgvector HNSW index if query times degrade
REINDEX INDEX face_embeddings_embedding_idx;
```

## 2. Versioning Strategy
This project uses **Semantic Versioning** (`MAJOR.MINOR.PATCH`):
- `MAJOR`: Breaking API changes or major architectural shifts.
- `MINOR`: New features (new endpoints, new DB tables).
- `PATCH`: Bug fixes and security patches.

Tag each release: `git tag -a v1.2.0 -m "Release notes here"`

## 3. Release Process
1. Create a `release/v1.x.x` branch from `main`.
2. Run full test suite (`pytest`).
3. Update `CHANGELOG.md` with a summary of changes.
4. Merge into `main` — GitHub Actions auto-deploys to production.
5. Create a GitHub Release and tag.

## 4. Monitoring Responsibilities
- **Backend API Health**: Monitor `/health` endpoint. Set a UptimeRobot alert if it returns non-200.
- **Database Disk**: Set a CloudWatch alarm at 80% disk utilization for the RDS instance.
- **Redis Memory**: Monitor `used_memory_human` via Redis INFO command. Eviction policies should be set to `allkeys-lru`.
- **Blockchain Backlog**: Weekly check that `blockchain_audit_logs` rows with `status='pending'` are not accumulating (indicates RPC node failure).
