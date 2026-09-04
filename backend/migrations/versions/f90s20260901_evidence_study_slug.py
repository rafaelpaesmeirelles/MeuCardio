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
OWNER_COMMENT = "alembic:f90s20260901"


def _schema() -> tuple[dict[str, dict], dict[str, dict]]:
    inspector = sa.inspect(op.get_bind())
    if not inspector.has_table(TABLE):
        raise RuntimeError(f"expected table is missing: {TABLE}")
    columns = {column["name"]: column for column in inspector.get_columns(TABLE)}
    indexes = {index["name"]: index for index in inspector.get_indexes(TABLE)}
    return columns, indexes


def _validate_column(column: dict) -> None:
    column_type = column.get("type")
    if (
        not isinstance(column_type, sa.String)
        or isinstance(column_type, sa.Text)
        or column_type.length != 255
        or column.get("nullable") is not True
    ):
        raise RuntimeError(
            f"incompatible pre-existing column: {TABLE}.{COLUMN}; "
            "expected nullable VARCHAR(255)"
        )


def _validate_index(index: dict) -> None:
    if index.get("column_names") != [COLUMN] or index.get("unique") is not False:
        raise RuntimeError(
            f"incompatible pre-existing index: {INDEX}; "
            f"expected non-unique index on {TABLE}({COLUMN})"
        )


def upgrade() -> None:
    columns, indexes = _schema()
    if COLUMN in columns:
        _validate_column(columns[COLUMN])
    if INDEX in indexes:
        _validate_index(indexes[INDEX])

    if COLUMN not in columns:
        op.add_column(
            TABLE,
            sa.Column(
                COLUMN,
                sa.String(length=255),
                nullable=True,
                comment=OWNER_COMMENT,
            ),
        )
    if INDEX not in indexes:
        op.create_index(INDEX, TABLE, [COLUMN], unique=False)


def downgrade() -> None:
    columns, indexes = _schema()
    column = columns.get(COLUMN)
    # O índice só é removido quando a própria coluna traz a marca persistida de
    # propriedade desta migration. Se a coluna já existia, o downgrade mantém
    # tanto ela quanto eventual índice, mesmo quando o upgrade criou o índice.
    if column is not None and column.get("comment") == OWNER_COMMENT:
        _validate_column(column)
        if INDEX in indexes:
            _validate_index(indexes[INDEX])
            op.drop_index(INDEX, table_name=TABLE)
        op.drop_column(TABLE, COLUMN)
