"""Preserva níveis de evidência compostos sem truncamento.

Revision ID: f86d20260829
Revises: f86c20260829
Create Date: 2026-08-29
"""
from alembic import op
import sqlalchemy as sa

revision = "f86d20260829"
down_revision = "f86c20260829"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "evidence_records",
        "evidence_level",
        existing_type=sa.String(length=5),
        type_=sa.Text(),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "evidence_records",
        "evidence_level",
        existing_type=sa.Text(),
        type_=sa.String(length=5),
        existing_nullable=False,
    )
