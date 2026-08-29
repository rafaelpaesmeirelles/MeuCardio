"""Preserva titulos cientificos longos do CorVIA Intelligence.

Revision ID: f86a20260829
Revises: f85b20260825
Create Date: 2026-08-29
"""
from alembic import op
import sqlalchemy as sa

revision = "f86a20260829"
down_revision = "f85b20260825"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "guidelines",
        "titulo",
        existing_type=sa.String(length=300),
        type_=sa.Text(),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "guidelines",
        "titulo",
        existing_type=sa.Text(),
        type_=sa.String(length=300),
        existing_nullable=False,
        postgresql_using="left(titulo, 300)",
    )
