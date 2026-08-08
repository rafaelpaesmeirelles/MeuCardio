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

`down_revision` aponta para o último head COMMITADO em `main` no momento
desta migração (`f67i20260808`) — havia trabalho de outra sessão em
andamento na árvore (`f68j20260808`/`f6ak20260808`), ainda não commitado,
então não é seguro encadear esta migração nele. Ver CLAUDE.md, entrada desta
tarefa, para o registro do achado. Se a árvore de `f68j`/`f6ak` já estiver em
`main` no momento de aplicar esta migração, gere uma migração de merge
(mesmo padrão de `f47a20260804_merge_pr47_head.py`) antes de rodar
`alembic upgrade head`.

Revision ID: 26751b9d12f0
Revises: f67i20260808
Create Date: 2026-08-08
"""

from alembic import op
import sqlalchemy as sa

revision = "26751b9d12f0"
down_revision = "f67i20260808"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "subscriptions",
        sa.Column("periodicidade", sa.String(length=20), nullable=False, server_default="mensal"),
    )


def downgrade() -> None:
    op.drop_column("subscriptions", "periodicidade")
