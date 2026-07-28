"""cursos parceiros: revenda com repasse via Stripe Connect

Três coisas nesta migração, e a primeira é a de maior risco do projeto até
aqui, porque mexe na tabela que controla o acesso de todo assinante pagante:

1. `subscriptions.user_id` deixa de ser `unique`. A restrição impunha uma
   assinatura por médico e inviabilizava "MeuCardio + um ou mais cursos". A
   unicidade não some: vira índice parcial, garantindo uma assinatura viva do
   MeuCardio por médico e uma por par médico/curso. Fica mais estrita do que
   antes em um ponto — antes, uma assinatura cancelada ocupava a vaga.
2. Colunas `kind` e `course_id` em `subscriptions`. Toda linha existente é do
   MeuCardio, então `kind` nasce com 'meucardio' e `server_default` cobre o
   backfill sem UPDATE separado.
3. Tabelas novas de curso, material e pagamento.

Idempotente do começo ao fim: este banco já teve `alembic_version` fora de
sincronia, e uma migração que só roda em base limpa é armadilha esperando o
próximo incidente.

Revision ID: e1a7b93c2d64
Revises: d9c4b3e28f15
Create Date: 2026-07-28 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'e1a7b93c2d64'
down_revision = 'd9c4b3e28f15'
branch_labels = None
depends_on = None


def _tabelas(bind):
    return set(sa.inspect(bind).get_table_names())


def upgrade() -> None:
    bind = op.get_bind()
    inspetor = sa.inspect(bind)
    tabelas = _tabelas(bind)

    if "partner_courses" not in tabelas:
        op.create_table(
            "partner_courses",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("slug", sa.String(120), nullable=False),
            sa.Column("nome", sa.String(200), nullable=False),
            sa.Column("parceiro", sa.String(200), nullable=False),
            sa.Column("descricao", sa.Text(), nullable=True),
            sa.Column("frase_destaque", sa.String(300), nullable=True),
            sa.Column("frase_destaque_fonte", sa.String(300), nullable=True),
            sa.Column("link_aula_ao_vivo", sa.String(500), nullable=True),
            sa.Column("link_aulas_gravadas", sa.String(500), nullable=True),
            sa.Column("preco_parceiro_centavos", sa.Integer(), nullable=False),
            sa.Column("margem_centavos", sa.Integer(), nullable=False),
            sa.Column("stripe_account_id", sa.String(255), nullable=True),
            sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.text("false")),
            sa.Column("destaque", sa.Boolean(), nullable=False, server_default=sa.text("false")),
            sa.Column("trilhas_vinculadas", postgresql.JSONB(), nullable=False,
                      server_default=sa.text("'[]'::jsonb")),
            sa.Column("casos_vinculados", postgresql.JSONB(), nullable=False,
                      server_default=sa.text("'[]'::jsonb")),
            sa.Column("created_at", sa.DateTime(timezone=True),
                      server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True),
                      server_default=sa.text("now()"), nullable=False),
        )
        op.create_index("ix_partner_courses_slug", "partner_courses", ["slug"], unique=True)
        op.create_index("ix_partner_courses_ativo", "partner_courses", ["ativo"])
        op.create_index("ix_partner_courses_destaque", "partner_courses", ["destaque"])

    if "course_materials" not in tabelas:
        op.create_table(
            "course_materials",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("course_id", sa.Integer(),
                      sa.ForeignKey("partner_courses.id", ondelete="CASCADE"), nullable=False),
            sa.Column("titulo", sa.String(200), nullable=False),
            sa.Column("nome_arquivo", sa.String(255), nullable=False),
            sa.Column("caminho", sa.String(500), nullable=False),
            sa.Column("tamanho_bytes", sa.Integer(), nullable=False),
            sa.Column("content_type", sa.String(100), nullable=False),
            sa.Column("enviado_por", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True),
                      server_default=sa.text("now()"), nullable=False),
        )
        op.create_index("ix_course_materials_course_id", "course_materials", ["course_id"])

    if "course_payments" not in tabelas:
        op.create_table(
            "course_payments",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("course_id", sa.Integer(), sa.ForeignKey("partner_courses.id"), nullable=False),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("stripe_invoice_id", sa.String(255), nullable=True),
            sa.Column("stripe_subscription_id", sa.String(255), nullable=True),
            sa.Column("bruto_centavos", sa.Integer(), nullable=False),
            sa.Column("repasse_centavos", sa.Integer(), nullable=False),
            sa.Column("margem_centavos", sa.Integer(), nullable=False),
            sa.Column("moeda", sa.String(3), nullable=False, server_default="brl"),
            sa.Column("competencia", sa.DateTime(timezone=True), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True),
                      server_default=sa.text("now()"), nullable=False),
        )
        op.create_index("ix_course_payments_course_id", "course_payments", ["course_id"])
        op.create_index("ix_course_payments_user_id", "course_payments", ["user_id"])
        op.create_index("ix_course_payments_invoice", "course_payments",
                        ["stripe_invoice_id"], unique=True)
        op.create_index("ix_course_payments_subscription", "course_payments",
                        ["stripe_subscription_id"])

    colunas = {c["name"] for c in inspetor.get_columns("subscriptions")}
    if "kind" not in colunas:
        op.add_column("subscriptions", sa.Column(
            "kind", sa.String(20), nullable=False, server_default="meucardio"))
        op.create_index("ix_subscriptions_kind", "subscriptions", ["kind"])
    if "course_id" not in colunas:
        op.add_column("subscriptions", sa.Column(
            "course_id", sa.Integer(), sa.ForeignKey("partner_courses.id"), nullable=True))
        op.create_index("ix_subscriptions_course_id", "subscriptions", ["course_id"])

    # A restrição de unicidade em user_id pode ter sido criada como UNIQUE
    # CONSTRAINT ou como UNIQUE INDEX, dependendo de ter vindo do create_all ou
    # de migração. Derrubar as duas formas, sem assumir o nome.
    for uc in inspetor.get_unique_constraints("subscriptions"):
        if uc["column_names"] == ["user_id"]:
            op.drop_constraint(uc["name"], "subscriptions", type_="unique")
    for ix in inspetor.get_indexes("subscriptions"):
        if ix["column_names"] == ["user_id"] and ix.get("unique"):
            op.drop_index(ix["name"], table_name="subscriptions")

    indices = {i["name"] for i in sa.inspect(bind).get_indexes("subscriptions")}
    if "ix_subscriptions_user_id" not in indices:
        op.create_index("ix_subscriptions_user_id", "subscriptions", ["user_id"])
    if "uq_assinatura_meucardio_por_usuario" not in indices:
        op.execute(
            "CREATE UNIQUE INDEX uq_assinatura_meucardio_por_usuario "
            "ON subscriptions (user_id) "
            "WHERE kind = 'meucardio' AND status <> 'cancelado'"
        )
    if "uq_assinatura_curso_por_usuario" not in indices:
        op.execute(
            "CREATE UNIQUE INDEX uq_assinatura_curso_por_usuario "
            "ON subscriptions (user_id, course_id) "
            "WHERE kind = 'curso' AND status <> 'cancelado'"
        )


def downgrade() -> None:
    bind = op.get_bind()
    op.execute("DROP INDEX IF EXISTS uq_assinatura_curso_por_usuario")
    op.execute("DROP INDEX IF EXISTS uq_assinatura_meucardio_por_usuario")
    colunas = {c["name"] for c in sa.inspect(bind).get_columns("subscriptions")}
    if "course_id" in colunas:
        op.drop_column("subscriptions", "course_id")
    if "kind" in colunas:
        op.drop_column("subscriptions", "kind")
    for t in ("course_payments", "course_materials", "partner_courses"):
        op.execute(f"DROP TABLE IF EXISTS {t} CASCADE")
