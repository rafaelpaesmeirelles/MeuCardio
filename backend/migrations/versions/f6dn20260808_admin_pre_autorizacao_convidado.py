"""Admin cadastra pré-autorização de convidado por nome e/ou e-mail, com escolha de CorvIA Mail (08/08/2026).

Pedido do Rafael: opção no menu Administração (só admin) para cadastrar a
pré-autorização de um novo convidado — antes só dava para fazer isso via
container exec. Ele quer poder identificar o convidado por nome completo
e/ou e-mail pessoal (nem sempre sabe de antemão qual e-mail a pessoa vai
escolher no cadastro), e escolher se esse convidado específico terá acesso
ao CorvIA Mail ou não (hoje todo convidado nasce sempre no plano Completo,
que inclui CorvIA Mail automaticamente — passa a ser opcional por linha).

`email` deixa de ser obrigatório (mas continua único quando presente — index
único do Postgres trata múltiplos NULL como distintos, sem precisar de index
parcial). `nome_completo` é o segundo identificador possível. Um CHECK
garante que pelo menos um dos dois está preenchido — pré-autorização sem
nenhum identificador não serve para casar com cadastro nenhum.

`users.convidado_plano_preferido` guarda o plano escolhido (PLANO_BASICO ou
PLANO_COMPLETO) quando o cadastro casa com uma pré-autorização — lido por
`criar_checkout()` (app/api/billing.py) no lugar do PLANO_COMPLETO fixo que
valia antes. None (convidado marcado direto pelo admin via toggle, sem
pré-autorização) continua caindo no padrão PLANO_COMPLETO, sem mudança de
comportamento para quem já usava esse caminho.

Revision ID: f6dn20260808
Revises: f6cm20260808
Create Date: 2026-08-08
"""

from alembic import op
import sqlalchemy as sa

revision = "f6dn20260808"
down_revision = "f6cm20260808"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("convidados_pre_autorizados", "email", nullable=True)
    op.add_column(
        "convidados_pre_autorizados",
        sa.Column("nome_completo", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "convidados_pre_autorizados",
        sa.Column("incluir_corvia_mail", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_check_constraint(
        "ck_convidados_pre_autorizados_identificador",
        "convidados_pre_autorizados",
        "email IS NOT NULL OR nome_completo IS NOT NULL",
    )
    op.add_column(
        "users",
        sa.Column("convidado_plano_preferido", sa.String(length=20), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "convidado_plano_preferido")
    op.drop_constraint("ck_convidados_pre_autorizados_identificador", "convidados_pre_autorizados", type_="check")
    op.drop_column("convidados_pre_autorizados", "incluir_corvia_mail")
    op.drop_column("convidados_pre_autorizados", "nome_completo")
    op.alter_column("convidados_pre_autorizados", "email", nullable=False)
