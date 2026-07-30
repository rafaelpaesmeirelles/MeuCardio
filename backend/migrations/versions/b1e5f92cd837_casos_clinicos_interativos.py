"""casos clinicos interativos

Tarefa 11a. Um caso, uma pergunta, um conjunto de opcoes e a explicacao com a
evidencia por tras da conduta correta - unico ponto de decisao por caso, sem
ramificacao. Duas tabelas com o mesmo motivo de separacao ja usado em
checklists/trilhas: o caso e conteudo curado e versionado; a tentativa e
registro de uso de um medico, e nao pode ser apagada quando o caso for
revisado.

Revision ID: b1e5f92cd837
Revises: a3f9c1d5e820
Create Date: 2026-07-30 22:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'b1e5f92cd837'
down_revision = 'a3f9c1d5e820'
branch_labels = None
depends_on = None


def upgrade() -> None:
    tabelas = set(sa.inspect(op.get_bind()).get_table_names())

    if "clinical_cases" not in tabelas:
        op.create_table(
            "clinical_cases",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("slug", sa.String(120), nullable=False, unique=True),
            sa.Column("titulo", sa.String(200), nullable=False),
            sa.Column("tema", sa.String(120), nullable=True),
            sa.Column("nivel", sa.String(30), nullable=True),
            sa.Column("enunciado", sa.Text(), nullable=False),
            sa.Column("pergunta", sa.Text(), nullable=False),
            sa.Column("opcoes", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
            sa.Column("resposta_correta", sa.Integer(), nullable=False),
            sa.Column("explicacao", sa.Text(), nullable=False),
            sa.Column("source_refs", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
            sa.Column("review_status", sa.String(30), nullable=False, server_default="pendente_revisao"),
            sa.Column("revisao", sa.Text(), nullable=True),
            sa.Column("published", sa.Boolean(), nullable=False, server_default=sa.text("false")),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        )
        op.create_index("ix_clinical_cases_slug", "clinical_cases", ["slug"], unique=True)
        op.create_index("ix_clinical_cases_tema", "clinical_cases", ["tema"])
        op.create_index("ix_clinical_cases_published", "clinical_cases", ["published"])

    if "clinical_case_attempts" not in tabelas:
        op.create_table(
            "clinical_case_attempts",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("case_id", sa.Integer(), sa.ForeignKey("clinical_cases.id", ondelete="CASCADE"), nullable=False),
            sa.Column("opcao_escolhida", sa.Integer(), nullable=False),
            sa.Column("acertou", sa.Boolean(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        )
        op.create_index("ix_clinical_case_attempts_user", "clinical_case_attempts", ["user_id"])
        op.create_index("ix_clinical_case_attempts_case", "clinical_case_attempts", ["case_id"])
        op.create_index("ix_clinical_case_attempts_created", "clinical_case_attempts", ["created_at"])


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS clinical_case_attempts CASCADE")
    op.execute("DROP TABLE IF EXISTS clinical_cases CASCADE")
