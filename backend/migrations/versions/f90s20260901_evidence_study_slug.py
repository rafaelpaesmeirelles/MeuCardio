"""Persist the typed study link carried by evidence records.

Revision ID: f90s20260901
Revises: f89s20260901
"""

from alembic import op
import sqlalchemy as sa


revision = "f90s20260901"
down_revision = "f89s20260901"
branch_labels = None
depends_on = None

TABLE = "evidence_records"
COLUMN = "study_slug"
INDEX = "ix_evidence_records_study_slug"


def _schema() -> tuple[set[str], set[str]]:
    inspector = sa.inspect(op.get_bind())
    if not inspector.has_table(TABLE):
        raise RuntimeError(f"expected table is missing: {TABLE}")
    columns = {column["name"] for column in inspector.get_columns(TABLE)}
    indexes = {index["name"] for index in inspector.get_indexes(TABLE)}
    return columns, indexes


def upgrade() -> None:
    columns, indexes = _schema()
    if COLUMN not in columns:
        op.add_column(
            TABLE,
            sa.Column(COLUMN, sa.String(length=255), nullable=True),
        )
    if INDEX not in indexes:
        op.create_index(INDEX, TABLE, [COLUMN], unique=False)


def downgrade() -> None:
    columns, indexes = _schema()
    if INDEX in indexes:
        op.drop_index(INDEX, table_name=TABLE)
    if COLUMN in columns:
        op.drop_column(TABLE, COLUMN)
