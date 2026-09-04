"""Tabela genérica de chunks para RAG fora de `documents` (Parte D da
correção coordenada de 02/09/2026 — expandir o RAG a todo o acervo
científico elegível, não só Documentos).

Revision ID: f94a20260902
Revises: f93s20260901
Create Date: 2026-09-02

`documents` continua indexado em `document_chunks`, intocado. Esta tabela
cobre as outras 12 frentes elegíveis (evidências, estudos, casos clínicos,
trilhas, material ao paciente, checklists, exames, medicamentos, galeria,
protocolos de emergência, doenças especializadas, triagem por sintoma) mais
calculadoras (sem tabela própria — `entity_id` usa o mesmo id estável já
usado pelo grafo de conhecimento). Ver `app/models/rag.py::KnowledgeChunk`.
"""
from alembic import op
import pgvector
import sqlalchemy as sa


revision = "f94a20260902"
down_revision = "f93s20260901"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "knowledge_chunks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("entity_type", sa.String(length=40), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("ordem", sa.Integer(), nullable=False),
        sa.Column("titulo_secao", sa.String(length=300), nullable=True),
        sa.Column("conteudo", sa.Text(), nullable=False),
        sa.Column("embedding", pgvector.sqlalchemy.vector.VECTOR(dim=1536), nullable=False),
        sa.Column("tokens_aprox", sa.Integer(), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("entity_type", "entity_id", "ordem", name="uq_knowledge_chunk_posicao"),
    )
    op.create_index(
        op.f("ix_knowledge_chunks_entity_type"), "knowledge_chunks", ["entity_type"], unique=False,
    )
    op.create_index(
        op.f("ix_knowledge_chunks_entity_id"), "knowledge_chunks", ["entity_id"], unique=False,
    )
    op.create_index(
        op.f("ix_knowledge_chunks_content_hash"), "knowledge_chunks", ["content_hash"], unique=False,
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS knowledge_chunks_embedding_idx
        ON knowledge_chunks USING hnsw (embedding vector_cosine_ops)
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS knowledge_chunks_embedding_idx")
    op.drop_index(op.f("ix_knowledge_chunks_content_hash"), table_name="knowledge_chunks")
    op.drop_index(op.f("ix_knowledge_chunks_entity_id"), table_name="knowledge_chunks")
    op.drop_index(op.f("ix_knowledge_chunks_entity_type"), table_name="knowledge_chunks")
    op.drop_table("knowledge_chunks")
