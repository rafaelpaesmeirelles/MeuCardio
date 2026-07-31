"""boas_vindas_pendente em users

Revision ID: 78ee6d515a27
Revises: b1e5f92cd837
Create Date: 2026-07-31
"""
from alembic import op
import sqlalchemy as sa

revision = "78ee6d515a27"
down_revision = "b1e5f92cd837"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    colunas = [c["name"] for c in sa.inspect(conn).get_columns("users")]
    if "boas_vindas_pendente" not in colunas:
        op.add_column(
            "users",
            sa.Column("boas_vindas_pendente", sa.Boolean(), nullable=False, server_default=sa.false()),
        )


def downgrade() -> None:
    conn = op.get_bind()
    colunas = [c["name"] for c in sa.inspect(conn).get_columns("users")]
    if "boas_vindas_pendente" in colunas:
        op.drop_column("users", "boas_vindas_pendente")
