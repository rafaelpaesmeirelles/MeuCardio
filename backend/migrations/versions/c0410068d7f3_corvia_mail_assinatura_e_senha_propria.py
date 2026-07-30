"""CorvIA Mail: assinatura separada (kind='email') e senha própria da caixa

Decisão do Rafael em 30/07/2026, mudando o desenho anterior: o e-mail deixa
de ser incluído na assinatura principal e passa a ser cobrado à parte
(mesmo padrão dos cursos parceiros: `Subscription.kind='email'`), e a caixa
passa a ter senha PRÓPRIA — distinta da senha da conta Corvia — para a
"sessão email" (login separado em `/api/email/entrar`).

Três mudanças, idempotentes:
1. `email_accounts.password_hash` — nasce nula, definida na ativação.
2. `password_reset_tokens.alvo` — 'conta' (comportamento original,
   server_default cobre o backfill) ou 'email' (reaproveita o mesmo
   mecanismo de token para a senha da caixa).
3. Índice parcial `uq_assinatura_email_por_usuario` em `subscriptions`,
   mesma lógica do índice do MeuCardio, para o novo kind='email'.

Revision ID: c0410068d7f3
Revises: 4ee4b695fa49
Create Date: 2026-07-30 01:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'c0410068d7f3'
down_revision = '4ee4b695fa49'
branch_labels = None
depends_on = None


def _colunas(bind, tabela):
    return {c["name"] for c in sa.inspect(bind).get_columns(tabela)}


def _indices(bind, tabela):
    return {i["name"] for i in sa.inspect(bind).get_indexes(tabela)}


def upgrade() -> None:
    bind = op.get_bind()

    if "password_hash" not in _colunas(bind, "email_accounts"):
        op.add_column("email_accounts", sa.Column("password_hash", sa.String(255), nullable=True))

    if "alvo" not in _colunas(bind, "password_reset_tokens"):
        op.add_column(
            "password_reset_tokens",
            sa.Column("alvo", sa.String(20), nullable=False, server_default="conta"),
        )

    if "uq_assinatura_email_por_usuario" not in _indices(bind, "subscriptions"):
        op.create_index(
            "uq_assinatura_email_por_usuario",
            "subscriptions",
            ["user_id"],
            unique=True,
            postgresql_where=sa.text("kind = 'email' AND status <> 'cancelado'"),
        )


def downgrade() -> None:
    bind = op.get_bind()

    if "uq_assinatura_email_por_usuario" in _indices(bind, "subscriptions"):
        op.drop_index("uq_assinatura_email_por_usuario", table_name="subscriptions")

    if "alvo" in _colunas(bind, "password_reset_tokens"):
        op.drop_column("password_reset_tokens", "alvo")

    if "password_hash" in _colunas(bind, "email_accounts"):
        op.drop_column("email_accounts", "password_hash")
