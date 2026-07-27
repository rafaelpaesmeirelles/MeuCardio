"""subscriptions: coluna last_event_at para ordem de eventos do webhook

Revision ID: c3d9a1f47b20
Revises: f95465113955
Create Date: 2026-07-27 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'c3d9a1f47b20'
down_revision = 'f95465113955'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'subscriptions',
        sa.Column('last_event_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('subscriptions', 'last_event_at')
