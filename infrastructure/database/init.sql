CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS organizations (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    name varchar(200) NOT NULL,
    legal_id varchar(100) NOT NULL UNIQUE,
    blockchain_root_key varchar(255),
    is_active boolean NOT NULL DEFAULT true,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS departments (
    id serial PRIMARY KEY,
    org_id uuid NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name varchar(100) NOT NULL,
    description varchar(255),
    is_deleted integer NOT NULL DEFAULT 0,
    UNIQUE (org_id, name)
);

CREATE TABLE IF NOT EXISTS roles (
    id serial PRIMARY KEY,
    name varchar(50) NOT NULL UNIQUE,
    description varchar(255),
    permissions jsonb NOT NULL DEFAULT '[]'::jsonb
);

CREATE TABLE IF NOT EXISTS shifts (
    id serial PRIMARY KEY,
    org_id uuid NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    shift_name varchar(100) NOT NULL,
    start_time time NOT NULL,
    end_time time NOT NULL,
    grace_period_mins integer NOT NULL DEFAULT 5,
    buffer_mins integer NOT NULL DEFAULT 15,
    is_deleted integer NOT NULL DEFAULT 0,
    UNIQUE (org_id, shift_name),
    CONSTRAINT ck_shifts_is_deleted CHECK (is_deleted IN (0, 1)),
    CONSTRAINT ck_shifts_grace CHECK (grace_period_mins >= 0)
);

CREATE TABLE IF NOT EXISTS users (
    id serial PRIMARY KEY,
    org_id uuid NOT NULL REFERENCES organizations(id) ON DELETE RESTRICT,
    dept_id integer REFERENCES departments(id) ON DELETE SET NULL,
    shift_id integer REFERENCES shifts(id) ON DELETE SET NULL,
    full_name varchar(100) NOT NULL,
    username varchar(80) NOT NULL UNIQUE,
    email varchar(150) NOT NULL UNIQUE,
    employee_id varchar(50) NOT NULL UNIQUE,
    enrollment_token varchar(255) UNIQUE,
    hashed_password varchar(255) NOT NULL,
    is_deleted integer NOT NULL DEFAULT 0,
    is_active integer NOT NULL DEFAULT 1,
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT ck_users_is_deleted CHECK (is_deleted IN (0, 1)),
    CONSTRAINT ck_users_is_active CHECK (is_active IN (0, 1))
);

CREATE TABLE IF NOT EXISTS user_roles (
    user_id integer NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id integer NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);

CREATE TABLE IF NOT EXISTS face_embeddings (
    id serial PRIMARY KEY,
    user_id integer NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    embedding vector(128) NOT NULL,
    zkp_public_commitment varchar(512),
    model_name varchar(50) NOT NULL DEFAULT 'ArcFace',
    is_active integer NOT NULL DEFAULT 1,
    enrolled_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT ck_face_embed_is_active CHECK (is_active IN (0, 1))
);

CREATE TABLE IF NOT EXISTS attendance_logs (
    id serial PRIMARY KEY,
    user_id integer NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    check_in timestamptz NOT NULL DEFAULT now(),
    check_out timestamptz,
    status varchar(30) NOT NULL,
    is_live integer NOT NULL DEFAULT 0,
    recognition_distance numeric(6,4),
    source varchar(20) NOT NULL DEFAULT 'ai',
    emotion varchar(30),
    is_deleted integer NOT NULL DEFAULT 0,
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT ck_attendance_is_deleted CHECK (is_deleted IN (0, 1)),
    CONSTRAINT ck_attendance_is_live CHECK (is_live IN (0, 1)),
    CONSTRAINT ck_attendance_status CHECK (status IN ('on_time', 'late', 'early', 'absent', 'manual_override')),
    CONSTRAINT ck_attendance_source CHECK (source IN ('ai', 'manual', 'edge'))
);

CREATE TABLE IF NOT EXISTS emotion_logs (
    id serial PRIMARY KEY,
    attendance_log_id integer NOT NULL REFERENCES attendance_logs(id) ON DELETE CASCADE,
    dominant_emotion varchar(30) NOT NULL,
    emotion_score numeric(4,3) NOT NULL,
    CONSTRAINT ck_emotion_type CHECK (dominant_emotion IN ('happy', 'sad', 'neutral', 'stressed', 'angry', 'fear', 'disgust'))
);

CREATE TABLE IF NOT EXISTS sync_queue (
    id serial PRIMARY KEY,
    device_key_id integer NOT NULL,
    payload jsonb NOT NULL,
    captured_at timestamptz NOT NULL,
    synced integer NOT NULL DEFAULT 0,
    synced_at timestamptz,
    error_msg text,
    CONSTRAINT ck_sync_synced CHECK (synced IN (0, 1))
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id serial PRIMARY KEY,
    user_id integer REFERENCES users(id) ON DELETE SET NULL,
    action varchar(100) NOT NULL,
    ref_table varchar(50) NOT NULL,
    ref_id integer NOT NULL,
    old_values jsonb,
    new_values jsonb,
    timestamp timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_departments_org ON departments(org_id);
CREATE INDEX IF NOT EXISTS ix_users_active_org ON users(org_id) WHERE is_deleted = 0;
CREATE INDEX IF NOT EXISTS ix_attendance_user_checkin ON attendance_logs(user_id, check_in) WHERE is_deleted = 0;
CREATE INDEX IF NOT EXISTS ix_attendance_checkin ON attendance_logs(check_in);
CREATE INDEX IF NOT EXISTS ix_face_embeddings_active_user ON face_embeddings(user_id) WHERE is_active = 1;
CREATE INDEX IF NOT EXISTS ix_face_embeddings_embedding_hnsw ON face_embeddings USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS ix_sync_queue_pending ON sync_queue(captured_at) WHERE synced = 0;

INSERT INTO organizations (id, name, legal_id, blockchain_root_key)
VALUES ('11111111-1111-1111-1111-111111111111', 'VisionCore Demo Organization', 'DEMO-ORG-001', 'local-dev-root')
ON CONFLICT (legal_id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO roles (name, description, permissions)
VALUES
    ('Admin', 'Full platform administrator', '["attendance:override","attendance:view","attendance:checkin","users:view","analytics:view","biometrics:enroll"]'::jsonb),
    ('Employee', 'Employee self-service user', '["attendance:view","attendance:checkin"]'::jsonb)
ON CONFLICT (name) DO UPDATE
SET description = EXCLUDED.description,
    permissions = EXCLUDED.permissions;

INSERT INTO departments (org_id, name, description)
VALUES ('11111111-1111-1111-1111-111111111111', 'Engineering', 'Local development team')
ON CONFLICT (org_id, name) DO UPDATE SET description = EXCLUDED.description;

INSERT INTO shifts (org_id, shift_name, start_time, end_time, grace_period_mins, buffer_mins)
VALUES ('11111111-1111-1111-1111-111111111111', 'General', '09:00', '17:00', 10, 15)
ON CONFLICT (org_id, shift_name) DO UPDATE
SET start_time = EXCLUDED.start_time,
    end_time = EXCLUDED.end_time,
    grace_period_mins = EXCLUDED.grace_period_mins,
    buffer_mins = EXCLUDED.buffer_mins;

WITH refs AS (
    SELECT
        d.id AS dept_id,
        s.id AS shift_id
    FROM departments d
    JOIN shifts s ON s.org_id = d.org_id
    WHERE d.org_id = '11111111-1111-1111-1111-111111111111'
      AND d.name = 'Engineering'
      AND s.shift_name = 'General'
)
INSERT INTO users (org_id, dept_id, shift_id, full_name, username, email, employee_id, hashed_password, is_active, is_deleted)
SELECT
    '11111111-1111-1111-1111-111111111111',
    dept_id,
    shift_id,
    'System Administrator',
    'admin@example.com',
    'admin@example.com',
    'ADM-001',
    '$2y$12$cKhK1JyLAL2VZ2/4CPUCLOps7esk2xUB6LykKRNVtlaDcVRCIiZNC',
    1,
    0
FROM refs
ON CONFLICT (username) DO UPDATE
SET hashed_password = EXCLUDED.hashed_password,
    is_active = 1,
    is_deleted = 0;

WITH refs AS (
    SELECT
        d.id AS dept_id,
        s.id AS shift_id
    FROM departments d
    JOIN shifts s ON s.org_id = d.org_id
    WHERE d.org_id = '11111111-1111-1111-1111-111111111111'
      AND d.name = 'Engineering'
      AND s.shift_name = 'General'
)
INSERT INTO users (org_id, dept_id, shift_id, full_name, username, email, employee_id, hashed_password, is_active, is_deleted)
SELECT
    '11111111-1111-1111-1111-111111111111',
    dept_id,
    shift_id,
    'Demo Employee',
    'employee@example.com',
    'employee@example.com',
    'EMP-001',
    '$2y$12$sdpuG74oD0Yd8Vg8Umw4NOXZEi016400SoZj3e3p2ibR/jEVh6Klu',
    1,
    0
FROM refs
ON CONFLICT (username) DO UPDATE
SET hashed_password = EXCLUDED.hashed_password,
    is_active = 1,
    is_deleted = 0;

INSERT INTO user_roles (user_id, role_id)
SELECT u.id, r.id
FROM users u, roles r
WHERE u.username = 'admin@example.com' AND r.name = 'Admin'
ON CONFLICT DO NOTHING;

INSERT INTO user_roles (user_id, role_id)
SELECT u.id, r.id
FROM users u, roles r
WHERE u.username = 'employee@example.com' AND r.name = 'Employee'
ON CONFLICT DO NOTHING;
