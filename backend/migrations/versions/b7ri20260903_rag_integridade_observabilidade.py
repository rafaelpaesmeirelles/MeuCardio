"""Integridade e observabilidade do RAG (correção coordenada de 03/09/2026).

Revision ID: b7ri20260903
Revises: f96m20260903
Create Date: 2026-09-03

Fecha três lacunas encontradas na investigação do backfill de
`knowledge_chunks` (03/09/2026):

1. `document_chunks` nunca teve `content_hash` — `indexar_tudo()` só sabia
   dizer "documento tem chunk ou não", nunca "o corpo mudou desde que foi
   indexado". Corpo editado depois de publicado nunca era reprocessado sem
   intervenção manual. Alinhado ao padrão que `knowledge_chunks` já tinha
   desde `f94a20260902`.
2. `embedding_model` em `document_chunks`/`knowledge_chunks` — nenhuma das
   duas tabelas registrava QUAL modelo gerou o vetor. Sem isso, misturar
   `text-embedding-3-small` com um modelo futuro na mesma tabela degradaria
   a busca em silêncio (distância de cosseno entre vetores de modelos
   diferentes não tem significado). Passa a ser gravado em toda escrita e
   pode ser auditado (`SELECT DISTINCT embedding_model FROM ...`).
3. `entity_type` de `knowledge_chunks` não tinha CHECK — o allowlist só
   existia em Python (`rag_sources.FONTES_POR_TIPO`). Trava estrutural
   equivalente, com os 13 valores reais que o código escreve hoje
   (12 frentes de `FONTES_RAG` + `calculadora`).
4. Tabela nova `rag_reindex_runs`: cada execução do backfill incremental
   (`app.commands.reindex_rag_completo_20260902`) grava UMA linha-resumo ao
   final — é o que permite a `/api/ai/status` (e qualquer operador) saber
   quando rodou pela última vez, quantas falhas teve e se ainda há backlog,
   sem precisar caçar log de container. Nenhuma delas grava conteúdo
   clínico nem dado de paciente — só contadores e metadados operacionais.

`document_chunks` já tem 16.330 linhas em produção, todas geradas por
`text-embedding-3-small` (nenhum outro modelo esteve em uso até hoje) — os
dois campos novos recebem valores de backfill computados aqui: `embedding_model`
com o literal do modelo atual, e `content_hash` com o sha256 do `body_md`
atual do documento (mesmo algoritmo que `rag.py::_hash` usa a partir de
agora), para que a primeira passada do backfill incremental já reconheça
essas linhas como íntegras em vez de tratá-las como nunca-hasheadas.
"""
from __future__ import annotations

import hashlib

import sqlalchemy as sa
from alembic import op
from sqlalchemy import text

revision = "b7ri20260903"
down_revision = "f96m20260903"
branch_labels = None
depends_on = None

# Mesma constante de `app.core.config.Settings.openai_embedding_model` no
# momento em que esta migration foi escrita — não importamos `app.core.config`
# aqui de propósito (migration não deve depender do estado de runtime da
# aplicação, só do que está gravado no arquivo).
MODELO_EMBEDDING_ATUAL = "text-embedding-3-small"

ENTITY_TYPES_PERMITIDOS = (
    "evidencia", "estudo", "caso_clinico", "trilha", "material_paciente",
    "checklist", "exame", "medicamento", "galeria", "protocolo_emergencia",
    "doenca", "triagem_sintoma", "calculadora",
)


def upgrade() -> None:
    op.add_column(
        "document_chunks",
        sa.Column("content_hash", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "document_chunks",
        sa.Column("embedding_model", sa.String(length=80), nullable=True),
    )
    op.add_column(
        "knowledge_chunks",
        sa.Column(
            "embedding_model", sa.String(length=80), nullable=False,
            server_default=MODELO_EMBEDDING_ATUAL,
        ),
    )

    # Backfill de document_chunks: um hash por documento (todos os chunks do
    # mesmo documento compartilham o mesmo content_hash, mesma convenção de
    # `knowledge_chunks`), calculado sobre o `body_md` gravado agora. Feito em
    # Python/linha a linha (não em SQL puro) porque sha256 não é função nativa
    # do PostgreSQL sem a extensão pgcrypto, que este projeto não tem instalada.
    conexao = op.get_bind()
    documentos = conexao.execute(
        text("SELECT id, body_md FROM documents WHERE id IN (SELECT DISTINCT document_id FROM document_chunks)")
    ).fetchall()
    for documento_id, body_md in documentos:
        hash_atual = hashlib.sha256((body_md or "").encode("utf-8")).hexdigest()
        conexao.execute(
            text(
                "UPDATE document_chunks SET content_hash = :hash, embedding_model = :modelo "
                "WHERE document_id = :documento_id"
            ),
            {"hash": hash_atual, "modelo": MODELO_EMBEDDING_ATUAL, "documento_id": documento_id},
        )

    # As duas colunas nascem NOT NULL a partir de agora — nenhum chunk novo
    # pode ser gravado sem hash/modelo (é exatamente o que a idempotência real
    # por conteúdo exige). Linhas de document_chunks cujo document_id não
    # exista mais em documents (não deveria acontecer, FK é ON DELETE CASCADE)
    # ficariam com content_hash NULL após o backfill acima — o ALTER abaixo
    # falharia nesse caso, o que é o comportamento certo: expõe a inconsistência
    # em vez de escondê-la atrás de um default artificial.
    op.alter_column("document_chunks", "content_hash", nullable=False)
    op.alter_column("document_chunks", "embedding_model", nullable=False)

    op.create_index(
        op.f("ix_document_chunks_content_hash"), "document_chunks", ["content_hash"], unique=False,
    )

    op.create_check_constraint(
        "ck_knowledge_chunks_entity_type_permitido",
        "knowledge_chunks",
        sa.text(
            "entity_type IN ("
            + ", ".join(f"'{tipo}'" for tipo in ENTITY_TYPES_PERMITIDOS)
            + ")"
        ),
    )

    op.create_table(
        "rag_reindex_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("dry_run", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("only_types", sa.String(length=400), nullable=True),
        sa.Column("entidades_processadas", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("trechos_gerados", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("falhas", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("backlog_restante", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("exit_code", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("detalhe", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_rag_reindex_runs_finished_at"), "rag_reindex_runs", ["finished_at"], unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_rag_reindex_runs_finished_at"), table_name="rag_reindex_runs")
    op.drop_table("rag_reindex_runs")
    op.drop_constraint("ck_knowledge_chunks_entity_type_permitido", "knowledge_chunks", type_="check")
    op.drop_index(op.f("ix_document_chunks_content_hash"), table_name="document_chunks")
    op.drop_column("knowledge_chunks", "embedding_model")
    op.drop_column("document_chunks", "embedding_model")
    op.drop_column("document_chunks", "content_hash")
