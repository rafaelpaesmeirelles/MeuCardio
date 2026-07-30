"""Dois planos de assinatura da plataforma (pedido do Rafael, 30/07/2026)

Até aqui só existia um plano (R$20/mês, sem discriminação). Passa a existir
`subscriptions.plano`: "basico" (R$20/mês, sem CorvIA Mail — o que já existia,
renomeado na interface) e "completo" (R$30/mês, com CorvIA Mail incluso).
Só é significativo para `kind='meucardio'`; nas demais linhas (curso, email)
fica no valor padrão e não é lido.

Coluna com `server_default='basico'` para as linhas já existentes não ficarem
NULL — nenhuma delas é "completo" porque o plano completo não existia até
agora.

Revision ID: a3f9c1d5e820
Revises: 9faec593af6e
Create Date: 2026-07-30 12:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'a3f9c1d5e820'
down_revision = '9faec593af6e'
branch_labels = None
depends_on = None


def _colunas(bind, tabela):
    return {c["name"] for c in sa.inspect(bind).get_columns(tabela)}


def upgrade() -> None:
    bind = op.get_bind()
    if "plano" not in _colunas(bind, "subscriptions"):
        op.add_column(
            "subscriptions",
            sa.Column("plano", sa.String(20), nullable=False, server_default="basico"),
        )


def downgrade() -> None:
    bind = op.get_bind()
    if "plano" in _colunas(bind, "subscriptions"):
        op.drop_column("subscriptions", "plano")
