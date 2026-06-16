# Database Schema & Partitioning Specifications (Raw SQL)

This document contains production-ready SQL scripts to instantiate and index the database tables for the platform services.

---

## 1. Extension Declarations
Run this script on the target databases before running schema migrations:
```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS vector;
```

---

## 2. Auth Service Database Setup

```sql
-- 1. Organizations
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    legal_id VARCHAR(100) NOT NULL UNIQUE,
    blockchain_root_key VARCHAR(255) NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX ix_organizations_name ON organizations(name);

-- 2. Roles
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(255) NULL,
    permissions JSONB NOT NULL DEFAULT '[]'::jsonb
);
CREATE INDEX ix_roles_name ON roles(name);

-- 3. Shifts
CREATE TABLE shifts (
    id SERIAL PRIMARY KEY,
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    shift_name VARCHAR(100) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    grace_period_mins INTEGER NOT NULL DEFAULT 5,
    buffer_mins INTEGER NOT NULL DEFAULT 15,
    is_deleted INTEGER NOT NULL DEFAULT 0,
    CONSTRAINT ck_shifts_is_deleted CHECK (is_deleted IN (0, 1)),
    CONSTRAINT ck_shifts_grace CHECK (grace_period_mins >= 0)
);
CREATE INDEX ix_shifts_org_active ON shifts(org_id) WHERE (is_deleted = 0);

-- 4. Users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE RESTRICT,
    shift_id INTEGER NULL REFERENCES shifts(id) ON DELETE SET NULL,
    full_name VARCHAR(100) NOT NULL,
    username VARCHAR(80) NOT NULL UNIQUE,
    email VARCHAR(150) NOT NULL UNIQUE,
    employee_id VARCHAR(50) NOT NULL UNIQUE,
    enrollment_token VARCHAR(255) NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    is_deleted INTEGER NOT NULL DEFAULT 0,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_users_is_deleted CHECK (is_deleted IN (0, 1)),
    CONSTRAINT ck_users_is_active CHECK (is_active IN (0, 1))
);
CREATE INDEX ix_users_active_org ON users(org_id) WHERE (is_deleted = 0);
CREATE INDEX ix_users_enrollment ON users(enrollment_token) WHERE (enrollment_token IS NOT NULL);

-- 5. User Roles Association
CREATE TABLE user_roles (
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);
```

---

## 3. Biometrics Database Setup

```sql
-- 6. Face Embeddings
CREATE TABLE face_embeddings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    embedding vector(128) NOT NULL,
    zkp_public_commitment VARCHAR(512) NULL,
    model_name VARCHAR(50) NOT NULL DEFAULT 'ArcFace',
    is_active INTEGER NOT NULL DEFAULT 1,
    enrolled_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_face_embed_is_active CHECK (is_active IN (0, 1))
);

-- Optimize with pgvector HNSW Index (Cosine Similarity Operator <=> )
CREATE INDEX ix_face_embeddings_hnsw ON face_embeddings 
USING hnsw (embedding vector_cosine_ops) 
WITH (m = 16, ef_construction = 64);

-- Active embedding quick lookup index
CREATE INDEX ix_face_embeddings_active_user ON face_embeddings(user_id) WHERE (is_active = 1);
```

---

## 4. Attendance Database Setup

We partition `attendance_logs` by month ranges.

```sql
-- 7. Partitioned Base Table
CREATE TABLE attendance_logs (
    id SERIAL,
    user_id INTEGER NOT NULL,
    check_in TIMESTAMP WITH TIME ZONE NOT NULL,
    check_out TIMESTAMP WITH TIME ZONE NULL,
    status VARCHAR(30) NOT NULL,
    is_live INTEGER NOT NULL DEFAULT 0,
    recognition_distance NUMERIC(6, 4) NULL,
    source VARCHAR(20) NOT NULL DEFAULT 'ai',
    is_deleted INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, check_in), -- Partition key must be part of composite primary key
    CONSTRAINT ck_attendance_is_deleted CHECK (is_deleted IN (0, 1)),
    CONSTRAINT ck_attendance_is_live CHECK (is_live IN (0, 1)),
    CONSTRAINT ck_attendance_status CHECK (status IN ('on_time', 'late', 'early', 'absent', 'manual_override')),
    CONSTRAINT ck_attendance_source CHECK (source IN ('ai', 'manual', 'edge'))
) PARTITION BY RANGE (check_in);

-- Active partitions declarations
CREATE TABLE attendance_logs_y2026m06 PARTITION OF attendance_logs
    FOR VALUES FROM ('2026-06-01 00:00:00+00') TO ('2026-07-01 00:00:00+00');

CREATE TABLE attendance_logs_y2026m07 PARTITION OF attendance_logs
    FOR VALUES FROM ('2026-07-01 00:00:00+00') TO ('2026-08-01 00:00:00+00');

-- 8. Emotion Logs
CREATE TABLE emotion_logs (
    id SERIAL PRIMARY KEY,
    attendance_log_id INTEGER NOT NULL,
    dominant_emotion VARCHAR(30) NOT NULL,
    emotion_score NUMERIC(4, 3) NOT NULL,
    CONSTRAINT ck_emotion_type CHECK (dominant_emotion IN ('happy', 'sad', 'neutral', 'stressed', 'angry'))
);
CREATE INDEX ix_emotion_logs_parent ON emotion_logs(attendance_log_id);

-- 9. Sync Queue (Kiosk offline collector queue)
CREATE TABLE sync_queue (
    id SERIAL PRIMARY KEY,
    device_key_id INTEGER NOT NULL,
    payload JSONB NOT NULL,
    captured_at TIMESTAMP WITH TIME ZONE NOT NULL,
    synced INTEGER NOT NULL DEFAULT 0,
    synced_at TIMESTAMP WITH TIME ZONE NULL,
    error_msg TEXT NULL,
    CONSTRAINT ck_sync_synced CHECK (synced IN (0, 1))
);
CREATE INDEX ix_sync_queue_pending ON sync_queue(captured_at) WHERE (synced = 0);

-- 10. Audit Logs (System administrative changes)
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NULL,
    action VARCHAR(100) NOT NULL,
    ref_table VARCHAR(50) NOT NULL,
    ref_id INTEGER NOT NULL,
    old_values JSONB NULL,
    new_values JSONB NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX ix_audit_logs_timestamp ON audit_logs(timestamp);
```

---

## 5. Blockchain Database Setup

```sql
-- 11. Blockchain anchored records lookup
CREATE TABLE blockchain_records (
    id SERIAL PRIMARY KEY,
    ref_id INTEGER NOT NULL,
    ref_type VARCHAR(50) NOT NULL,
    record_hash VARCHAR(64) NOT NULL,
    tx_hash VARCHAR(128) NULL,
    block_number BIGINT NULL,
    anchored_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_blockchain_ref_type CHECK (ref_type IN ('attendance', 'user_enroll', 'manual_override'))
);
CREATE INDEX ix_blockchain_ref ON blockchain_records(ref_type, ref_id);
```

---

## 6. Analytics Database Setup

```sql
-- 12. Generated reports metadata
CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    org_id VARCHAR(50) NOT NULL,
    report_type VARCHAR(50) NOT NULL,
    report_name VARCHAR(100) NOT NULL,
    file_path VARCHAR(255) NULL,
    query_params JSONB NULL,
    generated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX ix_reports_org ON reports(org_id);
```
