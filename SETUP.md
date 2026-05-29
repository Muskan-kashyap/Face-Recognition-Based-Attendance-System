# Face-Recognition-Based-Attendance-System — Setup Guide

This document describes how to install, configure, and run the project locally (backend + frontend). It covers cross-platform instructions (Linux, macOS, Windows/WSL) and includes optional Docker guidance for Postgres and Redis.

---

## Contents

- Overview
- Prerequisites
- Environment file
- Quick Start (Docker Compose)
- Manual Local Setup
  - Backend
  - PostgreSQL and required extensions
  - Redis (optional)
  - Seeding the database
  - Frontend
- Running the app
- Troubleshooting
- Production notes
- Useful file locations

---

## Overview

This repository contains a FastAPI backend and a Vite + React frontend for a face-recognition-based attendance system. The backend exposes a REST API under `/api/v1`. The frontend runs on a separate dev server and communicates with the backend via HTTP.

This guide assumes you clone the repo into a working directory and run commands from the repository root.

---

## Prerequisites

Install the following on your machine (or use Docker):

- Git
- Python 3.11+ (3.12 tested)
- Node.js 18+ (Node 22 recommended) and npm
- PostgreSQL 13+ (Postgres 16 recommended if using pgvector package)
- Redis (optional — the app supports it for token blacklisting; the app will operate without Redis by treating the blacklist as best-effort)
- (Optional) Docker & Docker Compose for running Postgres/Redis quickly

Platform tips:
- macOS: use Homebrew (`brew install python node redis postgresql`) or Docker
- Windows: use WSL2 (Ubuntu) and follow the Linux steps inside WSL
- Ubuntu/Debian: `sudo apt update && sudo apt install -y git python3 python3-venv python3-pip nodejs npm postgresql postgresql-contrib`

---

## Environment file

Create `backend/.env` (do NOT commit real secrets). Example minimal values:

```env
API_V1_STR=/api/v1
APP_NAME=Face Attendance
APP_VERSION=0.1.0
ENVIRONMENT=development

SECRET_KEY=replace_with_a_secure_key_at_least_32_chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

DATABASE_URL=postgresql+psycopg2://postgres:postgres@127.0.0.1:5432/attendance_db
REDIS_URL=redis://127.0.0.1:6379/0

CORS_ORIGINS=http://127.0.0.1:5173
```

Adjust `DATABASE_URL`, `REDIS_URL` and other values for your environment.

---

## Quick Start (Docker Compose)

If you have Docker and Docker Compose, you can run Postgres (with pgvector), Redis, backend and frontend with a `docker-compose.yml`. This repo does not include one by default; here is an example you can adapt:

```yaml
version: '3.8'
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: postgres
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - '5432:5432'

  redis:
    image: redis:7
    ports:
      - '6379:6379'

volumes:
  pgdata:
```

Notes:
- After starting the Postgres container, you must enable extensions (`uuid-ossp`, `pgcrypto`, `vector`) inside the database before running the app. See the Manual Local Setup section.
- You can add service definitions for the backend and frontend in the compose file if you want everything containerized.

---

## Manual Local Setup

Follow these steps to run the backend and frontend locally (recommended for development).

### Backend (FastAPI)

1. From the repo root, create a Python virtual environment and activate it:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate      # macOS/Linux
# On Windows PowerShell: .\.venv\Scripts\Activate.ps1
```

2. Install Python dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

3. Create and configure `backend/.env` (see Environment file).

### PostgreSQL and required extensions

The backend expects PostgreSQL with the following extensions available in the target database:
- uuid-ossp
- pgcrypto
- vector (pgvector)

Option A — Local Postgres (system install):

```bash
# create DB (example uses postgres superuser)
sudo -u postgres psql
CREATE DATABASE attendance_db;
# optional: create user and grant
CREATE USER attendance_user WITH PASSWORD 'secure_pw';
GRANT ALL PRIVILEGES ON DATABASE attendance_db TO attendance_user;
\q

# enable extensions (connect as a superuser)
psql -d attendance_db -U postgres -h 127.0.0.1
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS vector;  -- if pgvector installed
\q
```

If `vector` fails, install the `pgvector` extension for your PostgreSQL version or use a Docker Postgres image with pgvector preinstalled.

Option B — Docker Postgres:

```bash
docker run -d --name attendance_postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:16
# then exec into the container and run: psql -U postgres -d postgres -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### Redis (optional)

- System install (Ubuntu):

```bash
sudo apt install redis-server
sudo systemctl enable --now redis
```

- Docker:

```bash
docker run -d --name attendance_redis -p 6379:6379 redis:7
```

If Redis is not present, the application tolerates Redis being unavailable (token blacklist checks are best-effort).

### Seeding the database

The project contains `app/db/seed_comprehensive.py` (comprehensive test data).

```bash
# from backend/ (with venv activated)
python app/db/seed_comprehensive.py
```

This script creates organizations, roles, departments, shifts and seeded user accounts. Check the script output for printed test credentials.

### Run backend

From `backend/` with the venv active:

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

- Health: `http://127.0.0.1:8000/health`
- API root: `http://127.0.0.1:8000/api/v1/`

The server logs are printed to the terminal. The app's startup lifecycle will create tables if missing.

---

### Frontend (Vite + React)

1. From repo root:

```bash
cd frontend
npm install
```

2. Run the dev server:

```bash
npm run dev -- --host 127.0.0.1 --port 5173
```

3. Open the app in your browser:

```
http://127.0.0.1:5173
```

Frontend configuration:
- API base URL is configured in `frontend/src/services/apiClient.ts`. Ensure it points to `http://127.0.0.1:8000/api/v1` for local dev, or update `.env` variables in your setup.

---

## Running & Testing Auth Flow (example)

1. Login (example uses a seeded user printed by the seed script):

```bash
curl -X POST 'http://127.0.0.1:8000/api/v1/auth/login' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=james.rodriguez@visioncore.com&password=AdminJ1!2024'
```

2. Use returned `access_token` for protected endpoint:

```bash
curl -H "Authorization: Bearer <ACCESS_TOKEN>" http://127.0.0.1:8000/api/v1/users/me
```

---

## Troubleshooting

- 500 on auth endpoints: if Redis is unreachable the app will currently treat the blacklist as best-effort; check backend logs in `backend/` terminal for stack traces and warnings.
- Database connection issues:
  - Ensure `DATABASE_URL` points to the right host/port and the DB user has privileges.
  - Confirm extensions `uuid-ossp`, `pgcrypto` and `vector` are installed.
- `pgvector` extension missing: either install `postgresql-<version>-pgvector` for your system packages or use a Docker image with pgvector preinstalled.
- Missing Python packages: ensure virtualenv activated and run `pip install -r requirements.txt`.
- Frontend 404 or CORS issues: confirm `CORS_ORIGINS` in `backend/.env` includes the frontend origin (e.g., `http://127.0.0.1:5173`).

---

## Production notes

- Use secure secret keys, HTTPS, and proper CORS policies in production.
- Consider containerizing the services and using `docker-compose` or Kubernetes for deployment.
- Use a proper Redis instance for token blacklist in production and enable backups for Postgres.
- Build frontend with `npm run build` and serve via a static server (nginx) when deploying.

---

## Useful file locations

- Backend entry: `backend/main.py`
- Backend config: `backend/app/core/config.py`
- DB seed scripts: `backend/app/db/seed_comprehensive.py`, `backend/app/db/seed.py`
- Backend models: `backend/app/db/models/` (all_models.py, organization.py, etc.)
- Frontend entry: `frontend/src/main.jsx`
- Frontend API client: `frontend/src/services/apiClient.ts`

---

## Support / Next steps

If you want, I can:
- Add a `docker-compose.yml` for an opinionated local dev setup (Postgres + Redis + backend + frontend).
- Add `.env.example` at `backend/.env.example` and update `README.md` with short setup steps.

---

_Last updated: 2026-05-29_
