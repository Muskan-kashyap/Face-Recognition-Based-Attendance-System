"""phase3_enrollment_spoof_recognition_events_and_embedding_fields

Revision ID: 14931530a9c9
Revises: 8b8317215b9f
Create Date: 2026-06-18 10:23:24.786368

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa




# revision identifiers, used by Alembic.
revision: str = '14931530a9c9'
down_revision: Union[str, Sequence[str], None] = '8b8317215b9f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Phase 3 additions (tables + FaceEmbedding quality/metadata fields)
    # Note: This migration is written manually because Alembic autogenerate
    # cannot reliably run in this environment (DB connection/auth failure).

    # --- face_embeddings additions ---
    with op.batch_alter_table("face_embeddings") as batch_op:
        batch_op.add_column(
            sa.Column(
                "quality_score",
                sa.Numeric(5, 2),
                nullable=True,
                comment="Enrollment image quality score (blur/brightness/pose heuristics)",
            )
        )
        batch_op.add_column(
            sa.Column(
                "embedding_version",
                sa.NVARCHAR(length=50),
                nullable=True,
                comment="Version tag for the embedding/extraction pipeline/model",
            )
        )
        batch_op.add_column(
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("NOW()"),
                comment="Row creation timestamp (UTC)",
            )
        )

    # --- enrollment_events ---
    op.create_table(
        "enrollment_events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), nullable=False, index=True),
        sa.Column("org_id", sa.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("status", sa.NVARCHAR(length=20), nullable=False),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column("quality_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("embedding_version", sa.NVARCHAR(length=50), nullable=True),
        sa.Column("image_resolution", sa.NVARCHAR(length=30), nullable=True),
        sa.Column("brightness_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("blur_score", sa.Numeric(6, 3), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
            index=True,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["org_id"], ["organizations.id"], ondelete="RESTRICT"),
        sa.CheckConstraint("status IN ('success','failed')", name="ck_enrollment_status"),
    )
    op.create_index(
        "ix_enrollment_events_org_time",
        "enrollment_events",
        ["org_id", "created_at"],
    )

    # --- spoof_detection_logs ---
    op.create_table(
        "spoof_detection_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), nullable=True, index=True),
        sa.Column("org_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("attempt_type", sa.NVARCHAR(length=20), nullable=False),
        sa.Column("is_spoof", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("spoof_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("model_name", sa.NVARCHAR(length=50), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
            index=True,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["org_id"], ["organizations.id"], ondelete="RESTRICT"),
        sa.CheckConstraint("is_spoof IN (0,1)", name="ck_spoof_is_spoof"),
    )
    op.create_index(
        "ix_spoof_logs_org_time",
        "spoof_detection_logs",
        ["org_id", "created_at"],
    )

    # --- recognition_events ---
    op.create_table(
        "recognition_events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("org_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("user_id", sa.Integer(), nullable=True, index=True),
        sa.Column("status", sa.NVARCHAR(length=20), nullable=False),
        sa.Column("distance", sa.Numeric(6, 4), nullable=True),
        sa.Column("confidence", sa.Numeric(5, 3), nullable=True),
        sa.Column("is_live", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("liveness_score", sa.Numeric(5, 3), nullable=True),
        sa.Column("model_name", sa.NVARCHAR(length=50), nullable=True),
        sa.Column("embedding_version", sa.NVARCHAR(length=50), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
            index=True,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["org_id"], ["organizations.id"], ondelete="RESTRICT"),
        sa.CheckConstraint("status IN ('matched','not_matched')", name="ck_recognition_status"),
        sa.CheckConstraint("is_live IN (0,1)", name="ck_recognition_is_live"),
    )
    op.create_index(
        "ix_recognition_events_org_time",
        "recognition_events",
        ["org_id", "created_at"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_recognition_events_org_time", table_name="recognition_events")
    op.drop_table("recognition_events")

    op.drop_index("ix_spoof_logs_org_time", table_name="spoof_detection_logs")
    op.drop_table("spoof_detection_logs")

    op.drop_index("ix_enrollment_events_org_time", table_name="enrollment_events")
    op.drop_table("enrollment_events")

    with op.batch_alter_table("face_embeddings") as batch_op:
        batch_op.drop_column("created_at")
        batch_op.drop_column("embedding_version")
        batch_op.drop_column("quality_score")

