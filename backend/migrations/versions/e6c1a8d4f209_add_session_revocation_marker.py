"""add session revocation marker to users

Revision ID: e6c1a8d4f209
Revises: d5b9f2c7a104
Create Date: 2026-08-03
"""

from alembic import op
import sqlalchemy as sa

revision = "e6c1a8d4f209"
down_revision = "d5b9f2c7a104"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("sessions_valid_after", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "sessions_valid_after")
