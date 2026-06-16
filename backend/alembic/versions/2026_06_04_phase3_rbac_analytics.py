"""Phase 3: RBAC and Analytics (no-op revision)

Revision ID: phase3_rbac_analytics
Revises: 3eaaee4c0cc5
Create Date: 2026-06-04 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'phase3_rbac_analytics'
down_revision = '3eaaee4c0cc5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """This revision intentionally left as a no-op.

    The RBAC and analytics models were introduced in the initial migration
    for development convenience. This revision records Phase 3 in the
    migration history and can be extended with corrective SQL if needed.
    """
    pass


def downgrade() -> None:
    # no-op
    pass
