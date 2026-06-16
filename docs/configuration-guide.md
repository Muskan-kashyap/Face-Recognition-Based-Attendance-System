# Configuration Guide

## Environment Variables Reference

All configuration is managed through the `backend/.env` file. Never commit this file to version control.

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | ✅ Yes | None | Full SQLAlchemy connection string to PostgreSQL. Must use `+psycopg2` dialect. |
| `REDIS_URL` | ✅ Yes | None | Redis connection URL. System gracefully degrades if unavailable. |
| `SECRET_KEY` | ✅ Yes | None | Minimum 32-character secret for JWT signing. Generate with `openssl rand -hex 32`. |
| `API_V1_STR` | No | `/api/v1` | API prefix for all routes. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `30` | JWT access token lifetime in minutes. |
| `REFRESH_TOKEN_EXPIRE_DAYS` | No | `7` | JWT refresh token lifetime in days. |
| `BLOCKCHAIN_ENABLED` | No | `false` | Master switch for the Web3 feature. Can also be controlled via the DB `system_settings` table. |
| `BLOCKCHAIN_URL` | No | None | RPC endpoint (Infura/Alchemy). Required only when `BLOCKCHAIN_ENABLED=true`. |
| `BLOCKCHAIN_PRIVATE_KEY` | No | None | Ethereum wallet private key for signing transactions. Store in Secrets Manager — NEVER in `.env`. |
| `BLOCKCHAIN_CONTRACT_ADDRESS` | No | None | Deployed `AttendanceAudit.sol` address. |
| `ENVIRONMENT` | No | `development` | Controls logging verbosity. Set to `production` in prod. |

## Configuration Files

### `backend/alembic.ini`
Controls database migration behavior. The critical setting is `sqlalchemy.url`, which is populated from the `DATABASE_URL` environment variable automatically via `alembic/env.py`.

### `backend/pyproject.toml`
Defines Python project metadata and `pytest` configuration. Do not modify unless adding new test plugins.

### `docker-compose.prod.yml`
Defines the production container stack. Services are configured to pull environment variables from the host `.env` or GitHub Actions secrets.

## Security Recommendations
> [!CAUTION]
> **Never** store `BLOCKCHAIN_PRIVATE_KEY` in a file. Use AWS Secrets Manager, HashiCorp Vault, or a `.env` file with strict `chmod 600` permissions that is gitignored.

> [!WARNING]
> Rotate `SECRET_KEY` immediately if it is ever accidentally committed to git. All existing JWTs will be invalidated on rotation, forcing all users to log back in.
