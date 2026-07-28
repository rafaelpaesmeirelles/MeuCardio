"""diretrizes como entidade propria e vinculo com o conteudo

Pré-requisito da Tarefa 9 (alerta de atualização de diretriz). A diretriz de
origem existia só dentro do texto livre de `source_refs`: legível por gente,
inconsultável por código. Sem isto não há como responder "a ESC de fibrilação
atrial foi revisada; que conteúdo depende dela e quem usa esse conteúdo?".

`guideline_links` é genérico em (item_type, item_id), no mesmo padrão de
`favorites`, porque a tarefa fala de protocolo, medicamento e calculadora — e
uma chave estrangeira por tipo exigiria tabela nova a cada frente.

Revision ID: a3f91c7e5b28
Revises: f2b8c41d7a93
Create Date: 2026-07-28 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'a3f91c7e5b28'
down_revision = 'f2b8c41d7a93'
branch_labels = None
depends_on = None


def upgrade() -> None:
    tabelas = set(sa.inspect(op.get_bind()).get_table_names())

    if "guidelines" not in tabelas:
        op.create_table(
            "guidelines",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("slug", sa.String(160), nullable=False),
            sa.Column("org", sa.String(40), nullable=False),
            sa.Column("titulo", sa.String(300), nullable=False),
            sa.Column("ano", sa.Integer(), nullable=False),
            sa.Column("tema", sa.String(120), nullable=True),
            sa.Column("doi", sa.String(160), nullable=True),
            sa.Column("url", sa.String(500), nullable=True),
            sa.Column("superseded_by_id", sa.Integer(), sa.ForeignKey("guidelines.id"), nullable=True),
            sa.Column("substituida_em", sa.DateTime(timezone=True), nullable=True),
            sa.Column("alerta_enviado_em", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True),
                      server_default=sa.text("now()"), nullable=False),
            sa.UniqueConstraint("slug", name="uq_guideline_slug"),
        )
        op.create_index("ix_guidelines_slug", "guidelines", ["slug"])
        op.create_index("ix_guidelines_org", "guidelines", ["org"])
        op.create_index("ix_guidelines_ano", "guidelines", ["ano"])
        op.create_index("ix_guidelines_superseded", "guidelines", ["superseded_by_id"])

    if "guideline_links" not in tabelas:
        op.create_table(
            "guideline_links",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("guideline_id", sa.Integer(),
                      sa.ForeignKey("guidelines.id", ondelete="CASCADE"), nullable=False),
            sa.Column("item_type", sa.String(30), nullable=False),
            sa.Column("item_id", sa.Integer(), nullable=False),
            sa.Column("origem", sa.String(20), nullable=False, server_default="extraido"),
            sa.Column("confirmado", sa.Boolean(), nullable=False, server_default=sa.text("false")),
            sa.Column("trecho", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True),
                      server_default=sa.text("now()"), nullable=False),
            sa.UniqueConstraint("guideline_id", "item_type", "item_id", name="uq_vinculo_diretriz"),
        )
        op.create_index("ix_guideline_links_guideline", "guideline_links", ["guideline_id"])
        op.create_index("ix_guideline_links_item", "guideline_links", ["item_type", "item_id"])
        op.create_index("ix_guideline_links_confirmado", "guideline_links", ["confirmado"])


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS guideline_links CASCADE")
    op.execute("DROP TABLE IF EXISTS guidelines CASCADE")
