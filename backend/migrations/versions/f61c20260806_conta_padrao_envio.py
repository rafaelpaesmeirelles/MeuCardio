"""Conta padrão de envio de e-mail no CorvIA Mail (Trabalho 9, painel
"Administre suas contas").

Revision ID: f61c20260806
Revises: f60b20260806
Create Date: 2026-08-06
"""

from alembic import op
import sqlalchemy as sa

revision = "f61c20260806"
down_revision = "f60b20260806"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("email_conta_padrao_envio", sa.String(40), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "email_conta_padrao_envio")
