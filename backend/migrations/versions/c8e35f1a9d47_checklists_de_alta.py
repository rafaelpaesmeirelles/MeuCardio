"""checklists de alta pos-evento cardiovascular

Tarefa 18. Duas tabelas com papeis distintos, e a separacao e o ponto: o
modelo e conteudo curado e versionado; a aplicacao e registro de trabalho de um
medico numa alta concreta. Guardar a marcacao dentro do modelo faria a revisao
do conteudo apagar o trabalho de quem estava usando.

Revision ID: c8e35f1a9d47
Revises: b7d24e8a1f36
Create Date: 2026-07-28 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'c8e35f1a9d47'
down_revision = 'b7d24e8a1f36'
branch_labels = None
depends_on = None


def upgrade() -> None:
    tabelas = set(sa.inspect(op.get_bind()).get_table_names())

    if "discharge_checklists" not in tabelas:
        op.create_table(
            "discharge_checklists",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("slug", sa.String(120), nullable=False, unique=True),
            sa.Column("condicao", sa.String(200), nullable=False),
            sa.Column("resumo", sa.Text(), nullable=True),
            sa.Column("theme", sa.String(120), nullable=True),
            sa.Column("documento_origem", sa.String(255), nullable=True),
            sa.Column("itens", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
            sa.Column("source_refs", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
            sa.Column("review_status", sa.String(30), nullable=False, server_default="pendente_revisao"),
            sa.Column("published", sa.Boolean(), nullable=False, server_default=sa.text("false")),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        )
        op.create_index("ix_discharge_checklists_slug", "discharge_checklists", ["slug"], unique=True)
        op.create_index("ix_discharge_checklists_published", "discharge_checklists", ["published"])
        op.create_index("ix_discharge_checklists_theme", "discharge_checklists", ["theme"])
        op.create_index("ix_discharge_checklists_origem", "discharge_checklists", ["documento_origem"])

    if "discharge_checklist_runs" not in tabelas:
        op.create_table(
            "discharge_checklist_runs",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("checklist_id", sa.Integer(), sa.ForeignKey("discharge_checklists.id"), nullable=False),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("patient_id", sa.Integer(), sa.ForeignKey("patients.id", ondelete="SET NULL"), nullable=True),
            sa.Column("identificacao_livre", sa.String(200), nullable=True),
            sa.Column("marcados", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
            sa.Column("itens_no_momento", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
            sa.Column("observacoes", sa.Text(), nullable=True),
            sa.Column("finalizado_em", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        )
        op.create_index("ix_runs_checklist", "discharge_checklist_runs", ["checklist_id"])
        op.create_index("ix_runs_user", "discharge_checklist_runs", ["user_id"])
        op.create_index("ix_runs_patient", "discharge_checklist_runs", ["patient_id"])


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS discharge_checklist_runs CASCADE")
    op.execute("DROP TABLE IF EXISTS discharge_checklists CASCADE")
