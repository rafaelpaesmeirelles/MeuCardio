"""Persist loader review notes and production provenance.

Revision ID: f89s20260901
Revises: f88w20260831
"""

from alembic import op
import sqlalchemy as sa


revision = "f89s20260901"
down_revision = "f88w20260831"
branch_labels = None
depends_on = None

TABLES = ("scientific_studies", "patient_materials")
COLUMNS = (
    ("review_note", sa.Text()),
    ("fonte_producao", sa.Text()),
)


def _columns(table: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    if not inspector.has_table(table):
        raise RuntimeError(f"expected table is missing: {table}")
    return {column["name"] for column in inspector.get_columns(table)}


def upgrade() -> None:
    for table in TABLES:
        existing = _columns(table)
        for name, column_type in COLUMNS:
            if name not in existing:
                op.add_column(table, sa.Column(name, column_type, nullable=True))


def downgrade() -> None:
    for table in reversed(TABLES):
        existing = _columns(table)
        for name, _column_type in reversed(COLUMNS):
            if name in existing:
                op.drop_column(table, name)
