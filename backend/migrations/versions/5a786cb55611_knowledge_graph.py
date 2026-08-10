"""Grafo de conhecimento clínico universal — knowledge_entities/knowledge_relations
(issue #52, nova fase).

Duas tabelas novas, aditivas, sem migração de dado (nascem vazias — o
backfill que as popula é um passo separado, idempotente, executado depois
desta migração). Nenhuma coluna de tabela existente é alterada.

Revision ID: 5a786cb55611
Revises: 525c83496f23
Create Date: 2026-08-11
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "5a786cb55611"
down_revision = "525c83496f23"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Idempotente — mesma cautela já documentada no projeto para sessão
    # paralela aplicando DDL fora do alembic_version.
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tabelas = set(inspector.get_table_names())

    if "knowledge_entities" not in tabelas:
        op.create_table(
            "knowledge_entities",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("entity_type", sa.String(length=40), nullable=False),
            sa.Column("canonical_id", sa.Integer(), nullable=False),
            sa.Column("slug", sa.String(length=255), nullable=False),
            sa.Column("title", sa.String(length=500), nullable=False),
            sa.Column("status", sa.String(length=20), nullable=False, server_default="ativo"),
            sa.Column(
                "created_at", sa.DateTime(timezone=True), nullable=False,
                server_default=sa.text("now()"),
            ),
            sa.Column(
                "updated_at", sa.DateTime(timezone=True), nullable=False,
                server_default=sa.text("now()"),
            ),
            sa.UniqueConstraint("entity_type", "canonical_id", name="uq_knowledge_entity_origem"),
        )
        op.create_index("ix_knowledge_entities_entity_type", "knowledge_entities", ["entity_type"])
        op.create_index("ix_knowledge_entities_slug", "knowledge_entities", ["slug"])

    if "knowledge_relations" not in tabelas:
        op.create_table(
            "knowledge_relations",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "source_entity_id", sa.Integer(),
                sa.ForeignKey("knowledge_entities.id", ondelete="CASCADE"), nullable=False,
            ),
            sa.Column(
                "target_entity_id", sa.Integer(),
                sa.ForeignKey("knowledge_entities.id", ondelete="CASCADE"), nullable=False,
            ),
            sa.Column("relation_type", sa.String(length=40), nullable=False),
            sa.Column("relevance_score", sa.Float(), nullable=False, server_default="0.5"),
            sa.Column("confidence", sa.String(length=20), nullable=False, server_default="derived"),
            sa.Column(
                "provenance_type", sa.String(length=30), nullable=False,
                server_default="structured_metadata",
            ),
            sa.Column("evidence_source", sa.String(length=500), nullable=True),
            sa.Column(
                "review_status", sa.String(length=20), nullable=False,
                server_default="pendente_revisao",
            ),
            sa.Column(
                "extra", postgresql.JSONB(astext_type=sa.Text()), nullable=False,
                server_default="{}",
            ),
            sa.Column(
                "created_at", sa.DateTime(timezone=True), nullable=False,
                server_default=sa.text("now()"),
            ),
            sa.Column(
                "updated_at", sa.DateTime(timezone=True), nullable=False,
                server_default=sa.text("now()"),
            ),
            sa.UniqueConstraint(
                "source_entity_id", "target_entity_id", "relation_type",
                name="uq_knowledge_relation_aresta",
            ),
        )
        op.create_index(
            "ix_knowledge_relations_source_entity_id", "knowledge_relations", ["source_entity_id"]
        )
        op.create_index(
            "ix_knowledge_relations_target_entity_id", "knowledge_relations", ["target_entity_id"]
        )
        op.create_index(
            "ix_knowledge_relations_relation_type", "knowledge_relations", ["relation_type"]
        )
        op.create_index(
            "ix_knowledge_relations_source_type", "knowledge_relations",
            ["source_entity_id", "relation_type"],
        )
        op.create_index(
            "ix_knowledge_relations_target_type", "knowledge_relations",
            ["target_entity_id", "relation_type"],
        )
        op.create_index(
            "ix_knowledge_relations_review_status", "knowledge_relations", ["review_status"]
        )


def downgrade() -> None:
    op.drop_table("knowledge_relations")
    op.drop_table("knowledge_entities")
