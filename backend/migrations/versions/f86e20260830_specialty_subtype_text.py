"""Preserva subtipos clínicos descritivos sem truncamento.

Revision ID: f86e20260830
Revises: f86d20260829
Create Date: 2026-08-30
"""
from alembic import op
import sqlalchemy as sa

revision = "f86e20260830"
down_revision = "f86d20260829"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "specialty_diseases",
        "subtype",
        existing_type=sa.String(length=120),
        type_=sa.Text(),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "specialty_diseases",
        "subtype",
        existing_type=sa.Text(),
        type_=sa.String(length=120),
        existing_nullable=True,
    )
