"""Preserva subtipos clínicos descritivos sem truncamento.

Revision ID: f91s20260901
Revises: f90s20260901
Create Date: 2026-09-01
"""

from alembic import op
import sqlalchemy as sa


revision = "f91s20260901"
down_revision = "f90s20260901"
branch_labels = None
depends_on = None

TABLE = "specialty_diseases"
COLUMN = "subtype"


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if not inspector.has_table(TABLE):
        raise RuntimeError(f"expected table is missing: {TABLE}")

    columns = {column["name"]: column for column in inspector.get_columns(TABLE)}
    current = columns.get(COLUMN)
    if current is None:
        raise RuntimeError(f"expected column is missing: {TABLE}.{COLUMN}")
    if current.get("nullable") is not True:
        raise RuntimeError(f"incompatible nullability: {TABLE}.{COLUMN}; expected nullable")

    current_type = current.get("type")
    if isinstance(current_type, sa.Text):
        return
    if not isinstance(current_type, sa.String) or current_type.length != 120:
        raise RuntimeError(
            f"incompatible pre-existing column: {TABLE}.{COLUMN}; "
            "expected nullable VARCHAR(120) or TEXT"
        )

    op.alter_column(
        TABLE,
        COLUMN,
        existing_type=sa.String(length=120),
        type_=sa.Text(),
        existing_nullable=True,
    )


def downgrade() -> None:
    # O corpus canônico contém subtipos maiores que 120 caracteres. Reduzir a
    # coluna novamente causaria perda de conteúdo científico ou falha do
    # downgrade; por isso a ampliação é deliberadamente irreversível.
    pass
