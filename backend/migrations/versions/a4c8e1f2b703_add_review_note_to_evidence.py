"""add review note to evidence records

Revision ID: a4c8e1f2b703
Revises: f7d2b9c4a601
Create Date: 2026-08-03
"""

from alembic import op
import sqlalchemy as sa

revision = "a4c8e1f2b703"
down_revision = "f7d2b9c4a601"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "evidence_records",
        sa.Column("review_note", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("evidence_records", "review_note")
