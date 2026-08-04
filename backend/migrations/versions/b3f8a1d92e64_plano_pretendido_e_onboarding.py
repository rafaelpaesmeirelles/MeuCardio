"""users.plano_pretendido/periodicidade_pretendida/onboarding_visto

Funil público→assinante (pedido do Rafael em 03/08/2026): landing pública →
comparação de planos → cadastro → validação → checkout → ativação →
onboarding guiado. `plano_pretendido`/`periodicidade_pretendida` guardam a
escolha feita na comparação de planos PÚBLICA (antes do cadastro), pra
pré-selecionar o plano certo quando o profissional aprovado chega no
checkout — sem isso ele cairia sempre no básico/mensal por padrão,
perdendo a escolha original. `onboarding_visto` controla o tour guiado do
primeiro acesso já com assinatura ativa (Rafael pediu como etapa própria,
distinta do popup pessoal de `boas_vindas_pendente`).

Revision ID: b3f8a1d92e64
Revises: a7c92e4f6b18
Create Date: 2026-08-03 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'b3f8a1d92e64'
down_revision = 'a7c92e4f6b18'
branch_labels = None
depends_on = None


def upgrade() -> None:
    colunas = {c["name"] for c in sa.inspect(op.get_bind()).get_columns("users")}
    if "plano_pretendido" not in colunas:
        op.add_column("users", sa.Column("plano_pretendido", sa.String(20), nullable=True))
    if "periodicidade_pretendida" not in colunas:
        op.add_column("users", sa.Column("periodicidade_pretendida", sa.String(10), nullable=True))
    if "onboarding_visto" not in colunas:
        op.add_column(
            "users",
            sa.Column("onboarding_visto", sa.Boolean(), nullable=False, server_default=sa.false()),
        )


def downgrade() -> None:
    colunas = {c["name"] for c in sa.inspect(op.get_bind()).get_columns("users")}
    for nome in ("plano_pretendido", "periodicidade_pretendida", "onboarding_visto"):
        if nome in colunas:
            op.drop_column("users", nome)
