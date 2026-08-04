"""subscriptions.periodicidade

Plano anual, pedido pelo Rafael em 03/08/2026: R$500/ano (básico, sem CorvIA
Mail) e R$700/ano (completo, com CorvIA Mail) — desconto sobre os 12 meses
(R$598,80 e R$718,80 respectivamente). O valor cobrado já vem certo no
`price_data` do checkout (`app/api/billing.py`); esta coluna só registra QUAL
periodicidade foi escolhida, pra `/billing/status` e relatório futuro
saberem mostrar "R$500/ano" em vez de inferir errado a partir do plano.

Revision ID: a7c92e4f6b18
Revises: c4a8e6f1b3d7
Create Date: 2026-08-03 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'a7c92e4f6b18'
down_revision = 'c4a8e6f1b3d7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    colunas = {c["name"] for c in sa.inspect(op.get_bind()).get_columns("subscriptions")}
    if "periodicidade" not in colunas:
        op.add_column(
            "subscriptions",
            sa.Column("periodicidade", sa.String(10), nullable=False, server_default="mensal"),
        )


def downgrade() -> None:
    colunas = {c["name"] for c in sa.inspect(op.get_bind()).get_columns("subscriptions")}
    if "periodicidade" in colunas:
        op.drop_column("subscriptions", "periodicidade")
