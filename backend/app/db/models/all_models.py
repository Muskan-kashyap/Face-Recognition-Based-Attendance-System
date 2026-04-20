# =============================================================================
#  db/models/all_models.py
#  All 11 SQLAlchemy models in one file — zero circular import risk.
#  Individual model files import from here via __init__.py
# =============================================================================
from __future__ import annotations

import uuid
from datetime import datetime, time
from typing import List, Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import (BigInteger, Boolean, CheckConstraint, DateTime,
                         ForeignKey, Index, Integer, Numeric, Text, Time,
                         UniqueConstraint, text)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base, NVARCHAR


# ── Role ──────────────────────────────────────────────────────────────────────
class Role(Base):
    __tablename__ = "roles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    name: Mapped[str] = mapped_column(NVARCHAR(50), nullable=False, unique=True, index=True,
                                       comment="Admin | Manager | Employee | Device")
    permissions: Mapped[dict] = mapped_column(JSONB, nullable=False,
                                               server_default=text("'[]'::jsonb"))
    users: Mapped[List["User"]] = relationship("User", back_populates="role")
    def __repr__(self): return f"<Role {self.id} {self.name!r}>"


# ── Organization ──────────────────────────────────────────────────────────────
class Organization(Base):
    __tablename__ = "organizations"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True,
                                           server_default=text("uuid_generate_v4()"))
    name: Mapped[str] = mapped_column(NVARCHAR(200), nullable=False, index=True)
    legal_id: Mapped[str] = mapped_column(NVARCHAR(100), nullable=False, unique=True)
    blockchain_root_key: Mapped[Optional[str]] = mapped_column(NVARCHAR(255), nullable=True)
    zkp_threshold: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False,
                                                  server_default=text("0.98"))
    is_active: Mapped[int] = mapped_column(Integer, nullable=False, default=1,
                                            server_default=text("1"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False,
                                                  default=datetime.utcnow, server_default=text("NOW()"))
    api_keys:    Mapped[List["OrgApiKey"]]  = relationship("OrgApiKey",  back_populates="organization",
                                                            cascade="all, delete-orphan")
    departments: Mapped[List["Department"]] = relationship("Department", back_populates="organization")
    shifts:      Mapped[List["Shift"]]      = relationship("Shift",      back_populates="organization")
    users:       Mapped[List["User"]]       = relationship("User",       back_populates="organization")
    def __repr__(self): return f"<Organization {self.id} {self.name!r}>"


# ── OrgApiKey ─────────────────────────────────────────────────────────────────
class OrgApiKey(Base):
    __tablename__ = "org_api_keys"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    org_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                               ForeignKey("organizations.id", ondelete="CASCADE"),
                                               nullable=False, index=True)
    key_hash: Mapped[str] = mapped_column(NVARCHAR(255), nullable=False, unique=True,
                                           comment="SHA-256 of raw key — pgcrypto digest()")
    scope: Mapped[str] = mapped_column(NVARCHAR(50), nullable=False,
                                        server_default=text("'write_checkin'"))
    rate_limit: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("100"))
    is_revoked: Mapped[int] = mapped_column(Integer, nullable=False, default=0,
                                             server_default=text("0"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False,
                                                  default=datetime.utcnow, server_default=text("NOW()"))
    organization: Mapped["Organization"] = relationship("Organization", back_populates="api_keys")
    offline_sync_queue: Mapped[List["OfflineSyncQueue"]] = relationship(
        "OfflineSyncQueue", back_populates="api_key")
    __table_args__ = (
        Index("ix_org_api_keys_active", "key_hash", postgresql_where=text("is_revoked = 0")),
        CheckConstraint("is_revoked IN (0, 1)", name="ck_api_key_revoked"),
    )
    def __repr__(self): return f"<OrgApiKey {self.id} scope={self.scope!r}>"


# ── Department ────────────────────────────────────────────────────────────────
class Department(Base):
    __tablename__ = "departments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    org_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                               ForeignKey("organizations.id", ondelete="CASCADE"),
                                               nullable=False, index=True)
    name: Mapped[str] = mapped_column(NVARCHAR(100), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_deleted: Mapped[int] = mapped_column(Integer, nullable=False, default=0,
                                             server_default=text("0"),
                                             comment="0=active, 1=soft-deleted")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False,
                                                  default=datetime.utcnow, server_default=text("NOW()"))
    organization: Mapped["Organization"] = relationship("Organization", back_populates="departments")
    users: Mapped[List["User"]] = relationship("User", back_populates="department")
    __table_args__ = (
        CheckConstraint("is_deleted IN (0, 1)", name="ck_dept_is_deleted"),
        Index("ix_departments_active", "org_id", postgresql_where=text("is_deleted = 0")),
    )
    def __repr__(self): return f"<Department {self.id} {self.name!r}>"


# ── Shift ─────────────────────────────────────────────────────────────────────
class Shift(Base):
    __tablename__ = "shifts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    org_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                               ForeignKey("organizations.id", ondelete="CASCADE"),
                                               nullable=False, index=True)
    shift_name: Mapped[str] = mapped_column(NVARCHAR(100), nullable=False)
    start_time: Mapped[time] = mapped_column(Time(timezone=False), nullable=False)
    end_time: Mapped[time] = mapped_column(Time(timezone=False), nullable=False)
    grace_period_mins: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("5"),
                                                    comment="Minutes after start before 'Late'")
    buffer_mins: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("15"),
                                              comment="Minutes before start for early clock-in")
    break_deduct_mins: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    is_deleted: Mapped[int] = mapped_column(Integer, nullable=False, default=0,
                                             server_default=text("0"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False,
                                                  default=datetime.utcnow, server_default=text("NOW()"))
    organization: Mapped["Organization"] = relationship("Organization", back_populates="shifts")
    users: Mapped[List["User"]] = relationship("User", back_populates="shift")
    __table_args__ = (
        CheckConstraint("is_deleted IN (0, 1)", name="ck_shifts_is_deleted"),
        CheckConstraint("grace_period_mins >= 0", name="ck_shifts_grace"),
    )
    def __repr__(self): return f"<Shift {self.id} {self.shift_name!r}>"


# ── User ──────────────────────────────────────────────────────────────────────
class User(Base):
    """
    Central identity table.
    hashed_password : bcrypt via passlib (never raw SQL)
    enrollment_token: pgcrypto server_default encode(gen_random_bytes(32),'hex')
    is_deleted      : 0=active 1=soft-deleted — NEVER hard DELETE
    """
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    org_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                               ForeignKey("organizations.id", ondelete="RESTRICT"),
                                               nullable=False, index=True)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("roles.id", ondelete="RESTRICT"),
                                          nullable=False, index=True)
    dept_id: Mapped[Optional[int]] = mapped_column(Integer,
                                                    ForeignKey("departments.id", ondelete="SET NULL"),
                                                    nullable=True, index=True)
    shift_id: Mapped[Optional[int]] = mapped_column(Integer,
                                                     ForeignKey("shifts.id", ondelete="SET NULL"),
                                                     nullable=True, index=True)
    full_name: Mapped[str] = mapped_column(NVARCHAR(100), nullable=False)
    username: Mapped[str] = mapped_column(NVARCHAR(80), nullable=False, unique=True, index=True)
    email: Mapped[str] = mapped_column(NVARCHAR(150), nullable=False, unique=True, index=True)
    phone: Mapped[Optional[str]] = mapped_column(NVARCHAR(20), nullable=True)
    employee_id: Mapped[str] = mapped_column(NVARCHAR(50), nullable=False,
                                              unique=True, index=True,
                                              comment="HR / payroll reference code")
    enrollment_token: Mapped[Optional[str]] = mapped_column(
        NVARCHAR(255), nullable=True, unique=True, index=True,
        server_default=text("encode(gen_random_bytes(32), 'hex')"),
        comment="pgcrypto gen_random_bytes — one-time ZKP onboarding link")
    token_expires: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    hashed_password: Mapped[str] = mapped_column(NVARCHAR(255), nullable=False,
                                                  comment="bcrypt passlib — mirrors pgcrypto crypt()")
    is_deleted: Mapped[int] = mapped_column(Integer, nullable=False, default=0,
                                             server_default=text("0"),
                                             comment="0=active 1=soft-deleted")
    is_active: Mapped[int] = mapped_column(Integer, nullable=False, default=1,
                                            server_default=text("1"),
                                            comment="1=active 0=suspended")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False,
                                                  default=datetime.utcnow, server_default=text("NOW()"))
    organization: Mapped["Organization"] = relationship("Organization", back_populates="users",
                                                         foreign_keys=[org_id])
    role: Mapped["Role"] = relationship("Role", back_populates="users", foreign_keys=[role_id])
    department: Mapped[Optional["Department"]] = relationship("Department", back_populates="users",
                                                               foreign_keys=[dept_id])
    shift: Mapped[Optional["Shift"]] = relationship("Shift", back_populates="users",
                                                     foreign_keys=[shift_id])
    face_embedding: Mapped[Optional["FaceEmbedding"]] = relationship(
        "FaceEmbedding", back_populates="user", uselist=False)
    attendance_logs: Mapped[List["AttendanceLog"]] = relationship(
        "AttendanceLog", back_populates="user", foreign_keys="AttendanceLog.user_id")
    manual_overrides_as_target: Mapped[List["ManualOverride"]] = relationship(
        "ManualOverride", back_populates="target_user", foreign_keys="ManualOverride.target_user_id")
    manual_overrides_as_admin: Mapped[List["ManualOverride"]] = relationship(
        "ManualOverride", back_populates="admin_user", foreign_keys="ManualOverride.admin_user_id")
    monthly_summaries: Mapped[List["MonthlyGrowthSummary"]] = relationship(
        "MonthlyGrowthSummary", back_populates="user")
    tickets: Mapped[List["Ticket"]] = relationship("Ticket", back_populates="user")
    reimbursements: Mapped[List["Reimbursement"]] = relationship("Reimbursement", back_populates="user")
    payrolls: Mapped[List["Payroll"]] = relationship("Payroll", back_populates="user")
    __table_args__ = (
        CheckConstraint("is_deleted IN (0, 1)", name="ck_users_is_deleted"),
        CheckConstraint("is_active IN (0, 1)", name="ck_users_is_active"),
        Index("ix_users_active_org", "org_id", postgresql_where=text("is_deleted = 0")),
        Index("ix_users_org_email", "org_id", "email"),
    )
    def __repr__(self): return f"<User {self.id} {self.username!r} active={self.is_active}>"


# ── FaceEmbedding ─────────────────────────────────────────────────────────────
class FaceEmbedding(Base):
    """pgvector VECTOR(128). HNSW index created via Alembic raw SQL."""
    __tablename__ = "face_embeddings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"),
                                          nullable=False, index=True)
    embedding: Mapped[List[float]] = mapped_column(Vector(128), nullable=False,
                                                    comment="FaceNet 128-d — pgvector VECTOR(128)")
    zkp_public_commitment: Mapped[Optional[str]] = mapped_column(
        NVARCHAR(512), nullable=True, comment="Schnorr P=x·G — no raw biometric stored")
    model_name: Mapped[str] = mapped_column(NVARCHAR(50), nullable=False,
                                             server_default=text("'Facenet'"))
    is_active: Mapped[int] = mapped_column(Integer, nullable=False, default=1,
                                            server_default=text("1"),
                                            comment="1=current 0=superseded by re-enrollment")
    enrolled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False,
                                                   default=datetime.utcnow, server_default=text("NOW()"))
    user: Mapped["User"] = relationship("User", back_populates="face_embedding")
    __table_args__ = (
        CheckConstraint("is_active IN (0, 1)", name="ck_face_embed_is_active"),
        Index("ix_face_embeddings_active_user", "user_id",
              postgresql_where=text("is_active = 1")),
    )
    def __repr__(self): return f"<FaceEmbedding {self.id} user={self.user_id} active={self.is_active}>"


# ── AttendanceLog ─────────────────────────────────────────────────────────────
class AttendanceLog(Base):
    __tablename__ = "attendance_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="RESTRICT"),
                                          nullable=False, index=True)
    check_in: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False,
                                                default=datetime.utcnow, server_default=text("NOW()"),
                                                index=True)
    check_out: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True,
                                                           comment="NULL until clock-out")
    status: Mapped[str] = mapped_column(NVARCHAR(30), nullable=False,
                                         comment="on_time|late|early|absent|excused|manual_override")
    emotion: Mapped[Optional[str]] = mapped_column(NVARCHAR(30), nullable=True)
    emotion_score: Mapped[Optional[float]] = mapped_column(Numeric(4, 3), nullable=True)
    is_live: Mapped[int] = mapped_column(Integer, nullable=False, default=0,
                                          server_default=text("0"),
                                          comment="1=liveness passed")
    recognition_distance: Mapped[Optional[float]] = mapped_column(Numeric(6, 4), nullable=True,
                                                                    comment="pgvector cosine distance at match")
    source: Mapped[str] = mapped_column(NVARCHAR(20), nullable=False,
                                         server_default=text("'ai'"),
                                         comment="ai|manual|edge|bulk_import")
    geofence_pass: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    gps_lat: Mapped[Optional[float]] = mapped_column(Numeric(9, 6), nullable=True)
    gps_lng: Mapped[Optional[float]] = mapped_column(Numeric(9, 6), nullable=True)
    is_deleted: Mapped[int] = mapped_column(Integer, nullable=False, default=0,
                                             server_default=text("0"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False,
                                                  default=datetime.utcnow, server_default=text("NOW()"))
    user: Mapped["User"] = relationship("User", back_populates="attendance_logs",
                                         foreign_keys=[user_id])
    manual_override: Mapped[Optional["ManualOverride"]] = relationship(
        "ManualOverride", back_populates="attendance_log", uselist=False)
    __table_args__ = (
        Index("ix_attendance_user_checkin", "user_id", "check_in",
              postgresql_where=text("is_deleted = 0")),
        Index("ix_attendance_checkin_brin", "check_in", postgresql_using="brin"),
        CheckConstraint("is_deleted IN (0,1)", name="ck_attendance_is_deleted"),
        CheckConstraint("is_live IN (0,1)", name="ck_attendance_is_live"),
        CheckConstraint(
            "status IN ('on_time','late','early','absent','excused','manual_override')",
            name="ck_attendance_status"),
        CheckConstraint("source IN ('ai','manual','edge','bulk_import')",
                        name="ck_attendance_source"),
    )
    def __repr__(self): return f"<AttendanceLog {self.id} user={self.user_id} {self.status!r}>"


# ── ManualOverride ────────────────────────────────────────────────────────────
class ManualOverride(Base):
    __tablename__ = "manual_overrides"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    target_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="RESTRICT"),
                                                 nullable=False, index=True)
    admin_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="RESTRICT"),
                                                nullable=False, index=True)
    attendance_log_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("attendance_logs.id", ondelete="SET NULL"), nullable=True, index=True)
    reason_category: Mapped[str] = mapped_column(NVARCHAR(100), nullable=False)
    override_status: Mapped[str] = mapped_column(NVARCHAR(30), nullable=False)
    override_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    employee_approved: Mapped[int] = mapped_column(Integer, nullable=False, default=0,
                                                    server_default=text("0"),
                                                    comment="0=pending ZKP approval 1=approved")
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False,
                                                  default=datetime.utcnow, server_default=text("NOW()"))
    target_user: Mapped["User"] = relationship("User", back_populates="manual_overrides_as_target",
                                                foreign_keys=[target_user_id])
    admin_user: Mapped["User"] = relationship("User", back_populates="manual_overrides_as_admin",
                                               foreign_keys=[admin_user_id])
    attendance_log: Mapped[Optional["AttendanceLog"]] = relationship(
        "AttendanceLog", back_populates="manual_override", foreign_keys=[attendance_log_id])
    __table_args__ = (
        CheckConstraint("employee_approved IN (0,1)", name="ck_override_approved"),
        CheckConstraint(
            "reason_category IN ('device_malfunction','forgot_phone','network_outage',"
            "'camera_failure','admin_correction','other')", name="ck_override_reason"),
        Index("ix_override_pending", "target_user_id",
              postgresql_where=text("employee_approved = 0")),
    )
    def __repr__(self): return f"<ManualOverride {self.id} approved={self.employee_approved}>"


# ── BlockchainAuditLog ────────────────────────────────────────────────────────
class BlockchainAuditLog(Base):
    """APPEND-ONLY — no UPDATE, no DELETE, no is_deleted column."""
    __tablename__ = "blockchain_audit_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    ref_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    ref_type: Mapped[str] = mapped_column(NVARCHAR(50), nullable=False, index=True,
                                           comment="attendance|manual_override|org_onboard|user_enroll|key_revoke")
    record_hash: Mapped[str] = mapped_column(NVARCHAR(64), nullable=False,
                                              comment="SHA-256 hex — pgcrypto encode(digest(),'hex')")
    tx_hash: Mapped[Optional[str]] = mapped_column(NVARCHAR(128), nullable=True)
    block_number: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    anchored_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False,
                                                   default=datetime.utcnow, server_default=text("NOW()"),
                                                   index=True)
    __table_args__ = (
        Index("ix_blockchain_ref", "ref_type", "ref_id"),
        CheckConstraint(
            "ref_type IN ('attendance','manual_override','org_onboard','user_enroll','key_revoke','ticket','payroll','reimbursement')",
            name="ck_blockchain_ref_type"),
    )
    def __repr__(self): return f"<BlockchainAuditLog {self.id} {self.ref_type!r} ref={self.ref_id}>"


# ── MonthlyGrowthSummary ──────────────────────────────────────────────────────
class MonthlyGrowthSummary(Base):
    __tablename__ = "monthly_growth_summary"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"),
                                          nullable=False, index=True)
    month_year: Mapped[str] = mapped_column(NVARCHAR(7), nullable=False, comment="'2026-03'")
    total_present: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    total_late: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    total_absent: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    total_manual: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    avg_emotion_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 4), nullable=True)
    stress_event_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    burnout_risk_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True,
                                                                 comment=">40 triggers AI Nudge")
    productivity_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    growth_index: Mapped[Optional[float]] = mapped_column(Numeric(6, 2), nullable=True)
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False,
                                                   default=datetime.utcnow, server_default=text("NOW()"))
    user: Mapped["User"] = relationship("User", back_populates="monthly_summaries")
    __table_args__ = (
        UniqueConstraint("user_id", "month_year", name="uq_monthly_user_month"),
        Index("ix_monthly_burnout_risk", "burnout_risk_score",
              postgresql_where=text("burnout_risk_score > 40")),
    )
    def __repr__(self): return f"<MonthlyGrowthSummary {self.user_id} {self.month_year!r}>"


# ── OfflineSyncQueue ──────────────────────────────────────────────────────────
class OfflineSyncQueue(Base):
    __tablename__ = "offline_sync_queue"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    device_key_id: Mapped[int] = mapped_column(Integer,
                                                ForeignKey("org_api_keys.id", ondelete="RESTRICT"),
                                                nullable=False, index=True)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    synced: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default=text("0"),
                                         comment="0=pending 1=synced")
    synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    error_msg: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    api_key: Mapped["OrgApiKey"] = relationship("OrgApiKey", back_populates="offline_sync_queue",
                                                 foreign_keys=[device_key_id])
    __table_args__ = (
        CheckConstraint("synced IN (0,1)", name="ck_sync_synced"),
        Index("ix_sync_queue_pending", "captured_at", postgresql_where=text("synced = 0")),
    )
    def __repr__(self): return f"<OfflineSyncQueue {self.id} synced={self.synced}>"


# ── Ticket ────────────────────────────────────────────────────────────────────
class Ticket(Base):
    __tablename__ = "tickets"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"),
                                          nullable=False, index=True)
    org_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                               ForeignKey("organizations.id", ondelete="CASCADE"),
                                               nullable=False, index=True)
    title: Mapped[str] = mapped_column(NVARCHAR(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(NVARCHAR(30), nullable=False, default="open",
                                         server_default=text("'open'"),
                                         comment="open|resolved|escalated|closed")
    priority: Mapped[str] = mapped_column(NVARCHAR(20), nullable=False, default="medium",
                                           server_default=text("'medium'"),
                                           comment="low|medium|high|critical")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False,
                                                  default=datetime.utcnow, server_default=text("NOW()"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False,
                                                  default=datetime.utcnow, onupdate=datetime.utcnow,
                                                  server_default=text("NOW()"))
    
    user: Mapped["User"] = relationship("User", back_populates="tickets")
    organization: Mapped["Organization"] = relationship("Organization")

    __table_args__ = (
        CheckConstraint("status IN ('open','resolved','escalated','closed')", name="ck_ticket_status"),
        CheckConstraint("priority IN ('low','medium','high','critical')", name="ck_ticket_priority"),
    )

# ── Reimbursement ─────────────────────────────────────────────────────────────
class Reimbursement(Base):
    __tablename__ = "reimbursements"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"),
                                          nullable=False, index=True)
    org_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                               ForeignKey("organizations.id", ondelete="CASCADE"),
                                               nullable=False, index=True)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(NVARCHAR(30), nullable=False, default="pending",
                                         server_default=text("'pending'"),
                                         comment="pending|approved|rejected|paid")
    receipt_url: Mapped[Optional[str]] = mapped_column(NVARCHAR(512), nullable=True)
    approved_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False,
                                                    default=datetime.utcnow, server_default=text("NOW()"))
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="reimbursements", foreign_keys=[user_id])
    approver: Mapped[Optional["User"]] = relationship("User", foreign_keys=[approved_by])

    __table_args__ = (
        CheckConstraint("status IN ('pending','approved','rejected','paid')", name="ck_reimb_status"),
    )

# ── Payroll ───────────────────────────────────────────────────────────────────
class Payroll(Base):
    __tablename__ = "payrolls"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"),
                                          nullable=False, index=True)
    org_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                               ForeignKey("organizations.id", ondelete="CASCADE"),
                                               nullable=False, index=True)
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    base_salary: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    deductions: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0.0)
    reimbursements_total: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0.0)
    total_salary: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[str] = mapped_column(NVARCHAR(30), nullable=False, default="draft",
                                         server_default=text("'draft'"),
                                         comment="draft|pending|paid")
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False,
                                                    default=datetime.utcnow, server_default=text("NOW()"))

    user: Mapped["User"] = relationship("User", back_populates="payrolls")

    __table_args__ = (
        CheckConstraint("status IN ('draft','pending','paid')", name="ck_payroll_status"),
        UniqueConstraint("user_id", "month", "year", name="uq_user_monthly_payroll"),
    )