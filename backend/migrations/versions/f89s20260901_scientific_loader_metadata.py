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
OWNER_COMMENT = "alembic:f89s20260901"


def _columns(table: str) -> dict[str, dict]:
    inspector = sa.inspect(op.get_bind())
    if not inspector.has_table(table):
        raise RuntimeError(f"expected table is missing: {table}")
    return {column["name"]: column for column in inspector.get_columns(table)}


def _validate_column(table: str, name: str, column: dict) -> None:
    column_type = column.get("type")
    if not isinstance(column_type, sa.Text) or column.get("nullable") is not True:
        raise RuntimeError(
            f"incompatible pre-existing column: {table}.{name}; "
            "expected nullable TEXT"
        )


def upgrade() -> None:
    schemas = {table: _columns(table) for table in TABLES}
    for table, existing in schemas.items():
        for name, _column_type in COLUMNS:
            if name in existing:
                _validate_column(table, name, existing[name])

    for table in TABLES:
        existing = schemas[table]
        for name, column_type in COLUMNS:
            if name not in existing:
                op.add_column(
                    table,
                    sa.Column(
                        name,
                        column_type,
                        nullable=True,
                        comment=OWNER_COMMENT,
                    ),
                )


def downgrade() -> None:
    for table in reversed(TABLES):
        existing = _columns(table)
        for name, _column_type in reversed(COLUMNS):
            column = existing.get(name)
            if column is not None and column.get("comment") == OWNER_COMMENT:
                _validate_column(table, name, column)
                op.drop_column(table, name)
