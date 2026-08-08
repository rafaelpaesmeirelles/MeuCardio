"""Periodicidade da assinatura — mensal/semestral/anual (08/08/2026).

Pedido do Rafael: planos semestral e anual, além do mensal já existente
(sem mudança de valor no mensal). `periodicidade` guarda qual dos três foi
contratado, para o checkout resolver o preço certo no servidor e para o
webhook reconciliar depois de uma troca de plano/periodicidade feita via
`stripe.Subscription.modify(...)`. Nasce "mensal" para toda linha já
existente — é o único valor que já existia antes desta migração, então não
teria como interpretar retroativamente uma assinatura antiga como semestral
ou anual sem checar o Stripe, e o mensal é o comportamento real de 100% das
assinaturas já ativas hoje.

`down_revision` foi rebaseado em 08/08/2026 para `f6dn20260808` (head real de
`main` no momento em que este branch foi integrado) — várias outras sessões
adicionaram migrações entre a criação original desta (`f67i20260808`) e a
integração, então a cadeia precisou avançar para continuar linear.

Revision ID: 26751b9d12f0
Revises: f6dn20260808
Create Date: 2026-08-08
"""

from alembic import op
import sqlalchemy as sa

revision = "26751b9d12f0"
down_revision = "f6dn20260808"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Idempotente (CLAUDE.md já documenta armadilha de alembic_version fora
    # de sincronia neste banco): em produção a coluna já existia como
    # VARCHAR(10) — alguma sessão paralela aplicou por SQL direto sem
    # stampar a revisão. VARCHAR(10) comporta os três valores atuais
    # ("mensal"/"semestral"/"anual"), mas o modelo ORM declara String(20) —
    # alinhamos ao tipo do modelo em vez de deixar disco/banco divergentes.
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    colunas = {c["name"] for c in inspector.get_columns("subscriptions")}
    if "periodicidade" not in colunas:
        op.add_column(
            "subscriptions",
            sa.Column("periodicidade", sa.String(length=20), nullable=False, server_default="mensal"),
        )
    else:
        op.alter_column(
            "subscriptions", "periodicidade",
            type_=sa.String(length=20), existing_type=sa.String(length=10),
            existing_nullable=False, existing_server_default="mensal",
        )


def downgrade() -> None:
    op.drop_column("subscriptions", "periodicidade")
