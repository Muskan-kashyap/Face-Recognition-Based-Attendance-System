# =============================================================================
#  Face Detection Attendance System — SQLAlchemy Models
#  FastAPI + PostgreSQL (pgvector, pgcrypto, uuid-ossp)
#  All VARCHAR → NVARCHAR (Unicode-safe), soft-delete pattern throughout
# =============================================================================

from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    Time,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# pgvector extension type
from pgvector.sqlalchemy import Vector


# =============================================================================
#  Base + shared naming convention
# =============================================================================

class Base(DeclarativeBase):
    """
    Single declarative base for the entire schema.
    All models inherit from this class.
    """
    pass


# Shorthand: NVARCHAR is just String — SQLAlchemy renders it as VARCHAR on
# PostgreSQL, but annotating with Unicode=True ensures the driver treats it
# as NVARCHAR-equivalent (UTF-8 / multi-byte safe).
def NVARCHAR(length: int) -> String:
    """
    Drop-in replacement for VARCHAR that enforces Unicode storage.
    Renders as VARCHAR(n) on PostgreSQL with Unicode collation support.
    """
    return String(length, collation="pg_catalog.default")


# =============================================================================
#  LAYER 0 — Shared / Public Schema Tables
#  (roles, organizations, org_api_keys live in the public schema and are
#   shared across all tenants)
# =============================================================================

class Role(Base):
    """
    Static permission levels shared across all tenants.
    Seeded once: Admin | Manager | Employee | Device
    PostgreSQL extension used: none (pure relational)
    """
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
    )
    name: Mapped[str] = mapped_column(
        NVARCHAR(50),
        nullable=False,
        unique=True,                      # Admin, Manager, Employee, Device
        index=True,
    )
    permissions: Mapped[Optional[dict]] = mapped_column(
        JSONB,                            # extension: pgcrypto not needed here
        nullable=False,
        server_default=text("'[]'::jsonb"),
        comment="JSON array of allowed route/action strings",
    )

    # ── relationships ────────────────────────────────────────────────────────
    users: Mapped[List["User"]] = relationship("User", back_populates="role")

    def __repr__(self) -> str:
        return f"<Role id={self.id} name={self.name!r}>"


class Organization(Base):
    """
    Top-level tenant. Each company gets an isolated PostgreSQL schema.
    PostgreSQL extensions used:
        • uuid-ossp  → uuid_generate_v4() for the primary key default
        • pgcrypto   → used externally to hash API keys before storage
    """
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("uuid_generate_v4()"),  # requires uuid-ossp
        comment="Tenant UUID — also used as the PostgreSQL schema name suffix",
    )
    name: Mapped[str] = mapped_column(
        NVARCHAR(200),
        nullable=False,
        index=True,
    )
    legal_id: Mapped[str] = mapped_column(
        NVARCHAR(100),
        nullable=False,
        unique=True,                      # GST / CIN / EIN
        comment="Government-issued company registration number",
    )
    blockchain_root_key: Mapped[Optional[str]] = mapped_column(
        NVARCHAR(255),
        nullable=True,
        comment="Genesis hash anchored on L2 chain at onboarding",
    )
    zkp_threshold: Mapped[float] = mapped_column(
        Numeric(4, 2),
        nullable=False,
        server_default=text("0.98"),
        comment="Minimum ZKP match confidence (0.00–1.00)",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("TRUE"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        server_default=text("NOW()"),
    )

    # ── relationships ────────────────────────────────────────────────────────
    api_keys:    Mapped[List["OrgApiKey"]]    = relationship("OrgApiKey",    back_populates="organization")
    departments: Mapped[List["Department"]]   = relationship("Department",   back_populates="organization")
    shifts:      Mapped[List["Shift"]]        = relationship("Shift",        back_populates="organization")
    users:       Mapped[List["User"]]         = relationship("User",         back_populates="organization")

    def __repr__(self) -> str:
        return f"<Organization id={self.id} name={self.name!r}>"


class OrgApiKey(Base):
    """
    Scoped API keys issued to edge devices (cameras, kiosks).
    PostgreSQL extensions used:
        • pgcrypto → encode(digest(raw_key, 'sha256'), 'hex') stored in key_hash
    Never store the plaintext key — store only the SHA-256 hash.
    """
    __tablename__ = "org_api_keys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    key_hash: Mapped[str] = mapped_column(
        NVARCHAR(255),
        nullable=False,
        unique=True,
        comment="SHA-256 hash of the raw API key (pgcrypto: digest())",
    )
    scope: Mapped[str] = mapped_column(
        NVARCHAR(50),
        nullable=False,
        server_default=text("'write_checkin'"),
        comment="write_checkin | read_report | admin",
    )
    rate_limit: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("100"),
        comment="Maximum requests per minute for this device",
    )
    is_revoked: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("FALSE"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        server_default=text("NOW()"),
    )

    # ── relationships ────────────────────────────────────────────────────────
    organization:      Mapped["Organization"]        = relationship("Organization", back_populates="api_keys")
    offline_sync_queue: Mapped[List["OfflineSyncQueue"]] = relationship("OfflineSyncQueue", back_populates="api_key")

    __table_args__ = (
        Index("ix_org_api_keys_active", "key_hash", postgresql_where=text("is_revoked = FALSE")),
    )

    def __repr__(self) -> str:
        return f"<OrgApiKey id={self.id} org_id={self.org_id} scope={self.scope!r}>"


# =============================================================================
#  LAYER 1 — Org Structure  (tenant-scoped)
# =============================================================================

class Department(Base):
    """
    Organisational units within a tenant (Engineering, HR, Sales …).
    PostgreSQL extensions used: none
    """
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        NVARCHAR(100),
        nullable=False,
        index=True,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    is_deleted: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default=text("0"),
        comment="0 = active, 1 = soft-deleted — never hard DELETE",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        server_default=text("NOW()"),
    )

    # ── relationships ────────────────────────────────────────────────────────
    organization: Mapped["Organization"] = relationship("Organization", back_populates="departments")
    users:        Mapped[List["User"]]   = relationship("User", back_populates="department")

    __table_args__ = (
        Index("ix_departments_active", "org_id", postgresql_where=text("is_deleted = 0")),
    )

    def __repr__(self) -> str:
        return f"<Department id={self.id} name={self.name!r}>"


class Shift(Base):
    """
    Working-hour rules per tenant.
    Drives the 'on_time' / 'late' status calculation in attendance_logs.
    PostgreSQL extensions used: none
    """
    __tablename__ = "shifts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    shift_name: Mapped[str] = mapped_column(
        NVARCHAR(100),
        nullable=False,
        comment="e.g. Morning Batch | Night Shift",
    )
    start_time: Mapped[datetime] = mapped_column(
        Time(timezone=False),
        nullable=False,
        comment="e.g. 09:00:00",
    )
    end_time: Mapped[datetime] = mapped_column(
        Time(timezone=False),
        nullable=False,
        comment="e.g. 17:00:00",
    )
    grace_period_mins: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("5"),
        comment="Minutes after start_time before check-in becomes 'late'",
    )
    buffer_mins: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("15"),
        comment="Minutes before start_time that early clock-in is allowed",
    )
    break_deduct_mins: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
        comment="Auto-deducted lunch break minutes from total hours",
    )
    is_deleted: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default=text("0"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        server_default=text("NOW()"),
    )

    # ── relationships ────────────────────────────────────────────────────────
    organization: Mapped["Organization"] = relationship("Organization", back_populates="shifts")
    users:        Mapped[List["User"]]   = relationship("User", back_populates="shift")

    def __repr__(self) -> str:
        return f"<Shift id={self.id} name={self.shift_name!r} start={self.start_time}>"


# =============================================================================
#  LAYER 2 — Users & Identity  (tenant-scoped)
# =============================================================================

class User(Base):
    """
    Core profile for every employee / student / admin.
    PostgreSQL extensions used:
        • uuid-ossp  → uuid_generate_v4() for enrollment_token default
        • pgcrypto   → hashed_password stored via crypt() externally
    Soft-delete: set is_deleted=1 — NEVER run DELETE on this table.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    role_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("roles.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    dept_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("departments.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    shift_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("shifts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    full_name: Mapped[str] = mapped_column(
        NVARCHAR(100),
        nullable=False,
    )
    username: Mapped[str] = mapped_column(
        NVARCHAR(80),
        nullable=False,
        unique=True,
        index=True,
    )
    email: Mapped[str] = mapped_column(
        NVARCHAR(150),
        nullable=False,
        unique=True,
        index=True,
    )
    phone: Mapped[Optional[str]] = mapped_column(
        NVARCHAR(20),
        nullable=True,
    )
    employee_id: Mapped[str] = mapped_column(
        NVARCHAR(50),
        nullable=False,
        unique=True,
        index=True,
        comment="HR / payroll reference code",
    )
    # Temporary token e-mailed for silent ZKP onboarding
    enrollment_token: Mapped[Optional[str]] = mapped_column(
        NVARCHAR(255),
        nullable=True,
        unique=True,
        index=True,
        server_default=text("encode(gen_random_bytes(32), 'hex')"),  # pgcrypto
        comment="One-time enrollment link token (pgcrypto: gen_random_bytes)",
    )
    token_expires: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Enrollment token expiry — NULL after ZKP enrollment completes",
    )
    # Password stored as bcrypt hash via pgcrypto: crypt(password, gen_salt('bf'))
    hashed_password: Mapped[str] = mapped_column(
        NVARCHAR(255),
        nullable=False,
        comment="bcrypt hash — pgcrypto: crypt(plain, gen_salt('bf', 12))",
    )
    is_deleted: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default=text("0"),
        comment="0 = active, 1 = soft-deleted",
    )
    is_active: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        server_default=text("1"),
        comment="1 = active, 0 = suspended",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        server_default=text("NOW()"),
    )

    # ── relationships ────────────────────────────────────────────────────────
    organization:           Mapped["Organization"]              = relationship("Organization",          back_populates="users")
    role:                   Mapped["Role"]                      = relationship("Role",                  back_populates="users")
    department:             Mapped[Optional["Department"]]      = relationship("Department",            back_populates="users")
    shift:                  Mapped[Optional["Shift"]]           = relationship("Shift",                 back_populates="users")
    face_embedding:         Mapped[Optional["FaceEmbedding"]]   = relationship("FaceEmbedding",        back_populates="user",  uselist=False)
    attendance_logs:        Mapped[List["AttendanceLog"]]       = relationship("AttendanceLog",        back_populates="user",  foreign_keys="AttendanceLog.user_id")
    manual_overrides_as_target: Mapped[List["ManualOverride"]]  = relationship("ManualOverride",       back_populates="target_user", foreign_keys="ManualOverride.target_user_id")
    manual_overrides_as_admin:  Mapped[List["ManualOverride"]]  = relationship("ManualOverride",       back_populates="admin_user",  foreign_keys="ManualOverride.admin_user_id")
    monthly_summaries:      Mapped[List["MonthlyGrowthSummary"]] = relationship("MonthlyGrowthSummary", back_populates="user")

    __table_args__ = (
        # Fast lookup: active users only
        Index("ix_users_active", "org_id", postgresql_where=text("is_deleted = 0")),
        # Composite for "find active user by email within org"
        Index("ix_users_org_email", "org_id", "email"),
        CheckConstraint("is_deleted IN (0, 1)", name="ck_users_is_deleted"),
        CheckConstraint("is_active IN (0, 1)",  name="ck_users_is_active"),
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username!r} email={self.email!r}>"


# =============================================================================
#  LAYER 3 — Biometric / AI Layer  (tenant-scoped)
# =============================================================================

class FaceEmbedding(Base):
    """
    AI vector fingerprint — one active record per user.
    PostgreSQL extensions used:
        • pgvector → VECTOR(128) type for FaceNet embeddings + HNSW index
    ZKP: only zkp_public_commitment (Schnorr P = x·G) is stored.
    Raw face photo and raw vector x are NEVER stored server-side.
    """
    __tablename__ = "face_embeddings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # pgvector VECTOR(128) — FaceNet produces 128-dimensional embeddings
    embedding: Mapped[List[float]] = mapped_column(
        Vector(128),
        nullable=False,
        comment="FaceNet 128-d embedding — pgvector VECTOR type",
    )
    # ZKP public key: Schnorr commitment P = x·G
    # x (the raw vector) never leaves the edge device
    zkp_public_commitment: Mapped[Optional[str]] = mapped_column(
        NVARCHAR(512),
        nullable=True,
        comment="Schnorr ZKP public commitment P = x·G (no raw biometric)",
    )
    model_name: Mapped[str] = mapped_column(
        NVARCHAR(50),
        nullable=False,
        server_default=text("'Facenet'"),
        comment="Facenet | ArcFace | InsightFace",
    )
    is_active: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        server_default=text("1"),
        comment="1 = current active embedding, 0 = superseded by re-enrollment",
    )
    enrolled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        server_default=text("NOW()"),
    )

    # ── relationships ────────────────────────────────────────────────────────
    user: Mapped["User"] = relationship("User", back_populates="face_embedding")

    __table_args__ = (
        # HNSW index for O(log N) cosine nearest-neighbour search (pgvector)
        # Requires: CREATE INDEX ... USING hnsw (embedding vector_cosine_ops)
        # SQLAlchemy cannot create HNSW indexes declaratively — add via migration:
        #   op.execute("CREATE INDEX ix_face_embed_hnsw ON face_embeddings
        #               USING hnsw (embedding vector_cosine_ops)
        #               WITH (m=16, ef_construction=64)")
        Index("ix_face_embeddings_active_user", "user_id",
              postgresql_where=text("is_active = 1")),
        CheckConstraint("is_active IN (0, 1)", name="ck_face_embed_is_active"),
    )

    def __repr__(self) -> str:
        return f"<FaceEmbedding id={self.id} user_id={self.user_id} model={self.model_name!r}>"


# =============================================================================
#  LAYER 4 — Attendance Transaction  (tenant-scoped)
# =============================================================================

class AttendanceLog(Base):
    """
    Core transaction table — highest-write table in the system.
    One row per check-in event. check_out is nullable (dual-punch support).
    PostgreSQL extensions used:
        • pgcrypto → record_hash computed externally via digest()
    Soft-delete: is_deleted=1 — NEVER run DELETE.
    """
    __tablename__ = "attendance_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    check_in: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        server_default=text("NOW()"),
        index=True,
    )
    check_out: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="NULL until the user clocks out — supports dual-punch",
    )
    status: Mapped[str] = mapped_column(
        NVARCHAR(30),
        nullable=False,
        comment="on_time | late | early | absent | excused | manual_override",
    )
    emotion: Mapped[Optional[str]] = mapped_column(
        NVARCHAR(30),
        nullable=True,
        comment="happy | neutral | sad | angry | stressed | fear | surprise",
    )
    emotion_score: Mapped[Optional[float]] = mapped_column(
        Numeric(4, 3),
        nullable=True,
        comment="DeepFace confidence score 0.000–1.000",
    )
    is_live: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default=text("0"),
        comment="1 = liveness check passed (blink / head-turn detected)",
    )
    recognition_distance: Mapped[Optional[float]] = mapped_column(
        Numeric(6, 4),
        nullable=True,
        comment="Cosine distance at match time — for retrospective audit",
    )
    source: Mapped[str] = mapped_column(
        NVARCHAR(20),
        nullable=False,
        server_default=text("'ai'"),
        comment="ai | manual | edge | bulk_import",
    )
    geofence_pass: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="1 = within geofence, 0 = outside, NULL = geofencing disabled",
    )
    gps_lat: Mapped[Optional[float]] = mapped_column(Numeric(9, 6), nullable=True)
    gps_lng: Mapped[Optional[float]] = mapped_column(Numeric(9, 6), nullable=True)
    is_deleted: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default=text("0"),
        comment="0 = active, 1 = soft-deleted",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        server_default=text("NOW()"),
    )

    # ── relationships ────────────────────────────────────────────────────────
    user:             Mapped["User"]                       = relationship("User",            back_populates="attendance_logs", foreign_keys=[user_id])
    manual_override:  Mapped[Optional["ManualOverride"]]   = relationship("ManualOverride",  back_populates="attendance_log",  uselist=False)
    blockchain_seals: Mapped[List["BlockchainAuditLog"]]   = relationship(
        "BlockchainAuditLog",
        primaryjoin="and_(BlockchainAuditLog.ref_id == AttendanceLog.id, "
                    "BlockchainAuditLog.ref_type == 'attendance')",
        foreign_keys="BlockchainAuditLog.ref_id",
        viewonly=True,
    )

    __table_args__ = (
        # Composite for "who is in today?" dashboard
        Index("ix_attendance_user_checkin", "user_id", "check_in",
              postgresql_where=text("is_deleted = 0")),
        # BRIN index for time-range exports to Parquet
        Index("ix_attendance_checkin_brin", "check_in", postgresql_using="brin"),
        CheckConstraint("is_deleted IN (0, 1)",  name="ck_attendance_is_deleted"),
        CheckConstraint("is_live IN (0, 1)",      name="ck_attendance_is_live"),
        CheckConstraint(
            "status IN ('on_time','late','early','absent','excused','manual_override')",
            name="ck_attendance_status",
        ),
        CheckConstraint(
            "source IN ('ai','manual','edge','bulk_import')",
            name="ck_attendance_source",
        ),
    )

    def __repr__(self) -> str:
        return f"<AttendanceLog id={self.id} user_id={self.user_id} status={self.status!r} check_in={self.check_in}>"


# =============================================================================
#  LAYER 5 — Integrity & Audit  (tenant-scoped)
# =============================================================================

class ManualOverride(Base):
    """
    Admin-corrected attendance records with dual-signature audit trail.
    Both admin_user_id and target_user_id reference the same users table.
    PostgreSQL extensions used:
        • pgcrypto → record hash computed externally before blockchain anchor
    """
    __tablename__ = "manual_overrides"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    target_user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="The employee whose attendance is being corrected",
    )
    admin_user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="The admin who authorized the correction",
    )
    attendance_log_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("attendance_logs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="The original log being corrected — NULL if no prior log exists",
    )
    reason_category: Mapped[str] = mapped_column(
        NVARCHAR(100),
        nullable=False,
        comment="device_malfunction | forgot_phone | network_outage | camera_failure | admin_correction | other",
    )
    override_status: Mapped[str] = mapped_column(
        NVARCHAR(30),
        nullable=False,
        comment="Final status written to the corrected attendance row",
    )
    override_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Free-text justification from the admin",
    )
    # ZKP dual-signature: employee receives a mobile notification and
    # approves via a face scan on their own device
    employee_approved: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default=text("0"),
        comment="0 = pending employee ZKP approval, 1 = approved",
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp of employee ZKP approval — NULL until approved",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        server_default=text("NOW()"),
    )

    # ── relationships ────────────────────────────────────────────────────────
    target_user:     Mapped["User"]                      = relationship("User",          back_populates="manual_overrides_as_target", foreign_keys=[target_user_id])
    admin_user:      Mapped["User"]                      = relationship("User",          back_populates="manual_overrides_as_admin",  foreign_keys=[admin_user_id])
    attendance_log:  Mapped[Optional["AttendanceLog"]]   = relationship("AttendanceLog", back_populates="manual_override")
    blockchain_seals: Mapped[List["BlockchainAuditLog"]] = relationship(
        "BlockchainAuditLog",
        primaryjoin="and_(BlockchainAuditLog.ref_id == ManualOverride.id, "
                    "BlockchainAuditLog.ref_type == 'manual_override')",
        foreign_keys="BlockchainAuditLog.ref_id",
        viewonly=True,
    )

    __table_args__ = (
        CheckConstraint("employee_approved IN (0, 1)", name="ck_override_approved"),
        CheckConstraint(
            "reason_category IN ("
            "'device_malfunction','forgot_phone','network_outage',"
            "'camera_failure','admin_correction','other')",
            name="ck_override_reason",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<ManualOverride id={self.id} target={self.target_user_id} "
            f"admin={self.admin_user_id} approved={self.employee_approved}>"
        )


class BlockchainAuditLog(Base):
    """
    Immutable hash seal for every loggable event.
    Strictly APPEND-ONLY — no UPDATE, no DELETE, no is_deleted column.
    PostgreSQL extensions used:
        • pgcrypto → encode(digest(row_data, 'sha256'), 'hex') for record_hash
    The tampered_logs VIEW recalculates hashes live and surfaces mismatches.
    """
    __tablename__ = "blockchain_audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    ref_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
        comment="Primary key of the source row being sealed",
    )
    ref_type: Mapped[str] = mapped_column(
        NVARCHAR(50),
        nullable=False,
        index=True,
        comment="attendance | manual_override | org_onboard | user_enroll | key_revoke",
    )
    record_hash: Mapped[str] = mapped_column(
        NVARCHAR(64),
        nullable=False,
        comment="SHA-256 hex digest of source row (pgcrypto: encode(digest(...,'sha256'),'hex'))",
    )
    tx_hash: Mapped[Optional[str]] = mapped_column(
        NVARCHAR(128),
        nullable=True,
        comment="On-chain transaction hash (Polygon / Ganache)",
    )
    block_number: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        nullable=True,
        comment="Block number on the L2 chain for independent verification",
    )
    anchored_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        server_default=text("NOW()"),
        index=True,
    )

    __table_args__ = (
        # Composite for integrity validation queries
        Index("ix_blockchain_ref", "ref_type", "ref_id"),
        CheckConstraint(
            "ref_type IN ('attendance','manual_override','org_onboard','user_enroll','key_revoke')",
            name="ck_blockchain_ref_type",
        ),
    )

    def __repr__(self) -> str:
        return f"<BlockchainAuditLog id={self.id} ref_type={self.ref_type!r} ref_id={self.ref_id}>"


# =============================================================================
#  LAYER 6 — Analytics & Reporting  (tenant-scoped)
# =============================================================================

class MonthlyGrowthSummary(Base):
    """
    Pre-aggregated Polars output — refreshed once per month via background job.
    Drives the Wellness Heatmap and Growth Reports without scanning raw logs.
    PostgreSQL extensions used: none (Polars writes computed values here)
    """
    __tablename__ = "monthly_growth_summary"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    month_year: Mapped[str] = mapped_column(
        NVARCHAR(7),
        nullable=False,
        comment="ISO format: '2026-03'",
    )
    total_present: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    total_late:    Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    total_absent:  Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    total_manual:  Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    avg_emotion_score: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 4),
        nullable=True,
        comment="0.0000–1.0000 positive sentiment ratio",
    )
    stress_event_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
        comment="Count of check-ins where emotion IN ('sad','stressed')",
    )
    productivity_score: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Output velocity synced from Jira / GitHub (0–100)",
    )
    burnout_risk_score: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Polars burnout model output 0–100",
    )
    growth_index: Mapped[Optional[float]] = mapped_column(
        Numeric(6, 2),
        nullable=True,
        comment="Percentage change in productivity vs prior month",
    )
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        server_default=text("NOW()"),
    )

    # ── relationships ────────────────────────────────────────────────────────
    user: Mapped["User"] = relationship("User", back_populates="monthly_summaries")

    __table_args__ = (
        UniqueConstraint("user_id", "month_year", name="uq_monthly_summary_user_month"),
        Index("ix_monthly_burnout", "burnout_risk_score",
              postgresql_where=text("burnout_risk_score > 40")),
    )

    def __repr__(self) -> str:
        return f"<MonthlyGrowthSummary id={self.id} user_id={self.user_id} month={self.month_year!r}>"


class OfflineSyncQueue(Base):
    """
    Buffer for check-in payloads captured by edge devices while offline.
    The FastAPI sync endpoint drains this table in captured_at order.
    PostgreSQL extensions used:
        • JSONB → payload stored as structured JSON for flexible schema
    """
    __tablename__ = "offline_sync_queue"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    device_key_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("org_api_keys.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    payload: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        comment="Raw check-in payload as captured by the edge device",
    )
    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="Timestamp recorded by the device at capture time (before sync)",
    )
    synced: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default=text("0"),
        comment="0 = pending, 1 = successfully synced to attendance_logs",
    )
    synced_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    error_msg: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="NULL on success, exception message on failure",
    )

    # ── relationships ────────────────────────────────────────────────────────
    api_key: Mapped["OrgApiKey"] = relationship("OrgApiKey", back_populates="offline_sync_queue")

    __table_args__ = (
        Index("ix_sync_queue_pending", "captured_at",
              postgresql_where=text("synced = 0")),
        CheckConstraint("synced IN (0, 1)", name="ck_sync_synced"),
    )

    def __repr__(self) -> str:
        return f"<OfflineSyncQueue id={self.id} device={self.device_key_id} synced={self.synced}>"


# =============================================================================
#  Migration note — run these RAW SQL statements in Alembic after create_all()
#
#  1. HNSW index (pgvector — cannot be created via SQLAlchemy declarative):
#     CREATE INDEX CONCURRENTLY ix_face_embed_hnsw
#       ON face_embeddings USING hnsw (embedding vector_cosine_ops)
#       WITH (m = 16, ef_construction = 64);
#
#  2. Extensions (run once as superuser before first migration):
#     CREATE EXTENSION IF NOT EXISTS vector;       -- pgvector
#     CREATE EXTENSION IF NOT EXISTS "uuid-ossp";  -- uuid_generate_v4()
#     CREATE EXTENSION IF NOT EXISTS pgcrypto;     -- gen_random_bytes, digest, crypt
#
#  3. Password hashing example (FastAPI service layer):
#     INSERT INTO users (hashed_password, ...)
#     VALUES (crypt('plain_password', gen_salt('bf', 12)), ...)
#
#  4. Verify password example:
#     SELECT id FROM users
#     WHERE username = :uname
#       AND hashed_password = crypt(:plain, hashed_password);
# =============================================================================