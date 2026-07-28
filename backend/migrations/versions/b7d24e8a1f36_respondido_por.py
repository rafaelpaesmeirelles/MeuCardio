"""service_orders.respondido_por

O painel de indicadores pessoais (Tarefa 10) fala em "meus laudos emitidos" e
"receita gerada". Sem registrar quem respondeu, esses números não têm dono.

Hoje só existe um respondente, o que faz o campo parecer redundante — e é
justamente por isso que ele precisa existir **antes** do segundo, e não depois:
contratado um segundo cardiologista, não haveria como atribuir o histórico.

Revision ID: b7d24e8a1f36
Revises: a3f91c7e5b28
Create Date: 2026-07-28 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'b7d24e8a1f36'
down_revision = 'a3f91c7e5b28'
branch_labels = None
depends_on = None


def upgrade() -> None:
    colunas = {c["name"] for c in sa.inspect(op.get_bind()).get_columns("service_orders")}
    if "respondido_por" not in colunas:
        op.add_column("service_orders", sa.Column(
            "respondido_por", sa.Integer(), sa.ForeignKey("users.id"), nullable=True))
        op.create_index("ix_service_orders_respondido_por", "service_orders", ["respondido_por"])


def downgrade() -> None:
    colunas = {c["name"] for c in sa.inspect(op.get_bind()).get_columns("service_orders")}
    if "respondido_por" in colunas:
        op.drop_column("service_orders", "respondido_por")
