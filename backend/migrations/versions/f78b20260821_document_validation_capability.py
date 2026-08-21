"""Capability pública forte por emissão de documento clínico.

Revision ID: f78b20260821
Revises: f77a20260820
Create Date: 2026-08-21
"""

from alembic import op
import sqlalchemy as sa


revision = "f78b20260821"
down_revision = "f77a20260820"
branch_labels = None
depends_on = None


_TABLE = "documentos_emitidos"
_COLUMN = "validation_token_hash"
_INDEX = "ix_documentos_emitidos_validation_token_hash"


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns(_TABLE)}
    if _COLUMN not in columns:
        op.add_column(_TABLE, sa.Column(_COLUMN, sa.String(length=64), nullable=True))

    indexes = {index["name"] for index in sa.inspect(bind).get_indexes(_TABLE)}
    if _INDEX not in indexes:
        op.create_index(_INDEX, _TABLE, [_COLUMN], unique=True)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    indexes = {index["name"] for index in inspector.get_indexes(_TABLE)}
    if _INDEX in indexes:
        op.drop_index(_INDEX, table_name=_TABLE)
    columns = {column["name"] for column in sa.inspect(bind).get_columns(_TABLE)}
    if _COLUMN in columns:
        op.drop_column(_TABLE, _COLUMN)
