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

`document_chunks` já tem 16.330 linhas em produção. CORREÇÃO IMPORTANTE
(revisão independente do PR #811, 03/09/2026): a primeira versão desta
migration computava o `content_hash` dessas linhas a partir do `body_md`
ATUAL de cada documento e gravava `embedding_model = 'text-embedding-3-small'`
como se fossem fatos confirmados — não são. Não temos como provar, só lendo o
banco hoje, que (a) o vetor já gravado foi de fato gerado a partir do texto
ATUAL (o documento pode ter sido editado depois da última indexação real) ou
(b) que o modelo que gerou aquele vetor específico foi genuinamente
`text-embedding-3-small` (é a suposição mais provável — é o único modelo que
este projeto já usou — mas suposição não é proveniência confirmada).
Computar o hash "correto" e escrever o nome do modelo como se fossem
verificados classificaria esses 16.330 chunks como **certificados como
atuais** no mecanismo de freshness (`esta_atualizado()`,
`app/services/rag.py`) — inventando exatamente o tipo de garantia que este
projeto proíbe fabricar.

Em vez disso, as 16.330 linhas recebem um par de **sentinelas explícitas**
(`LEGADO_CONTENT_HASH`/`LEGADO_EMBEDDING_MODEL`, abaixo) — nunca combinam
com um fingerprint/modelo real (não são hexadecimais de 64 caracteres nem o
nome de nenhum modelo existente), então `esta_atualizado()` SEMPRE devolve
`False` para elas — garantido só pela comparação de `embedding_model`,
mesmo que algum dia um `content_hash` novo bata por coincidência com o
sentinela. Os vetores continuam intactos e servíveis (nenhum `DELETE` — a
busca semântica não fica cega enquanto o backfill incremental não passar por
elas de novo); só deixam de ser tratados como "confirmadamente em dia". A
primeira chamada de `app.commands.reindex_rag_completo_20260902` depois
desta migration reindexa as 16.330 de verdade, com proveniência real desta
vez.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import text
from sqlalchemy.dialects import postgresql

revision = "b7ri20260903"
down_revision = "f96m20260903"
branch_labels = None
depends_on = None

# Mesma constante de `app.core.config.Settings.openai_embedding_model` no
# momento em que esta migration foi escrita — usada só para o
# `server_default` de `knowledge_chunks.embedding_model` (tabela vazia em
# produção — 0 linhas confirmado por leitura direta em 03/09/2026 — então
# não há proveniência nenhuma para inventar ali; é só o valor que uma escrita
# hipotética sem o campo explícito receberia). Não importamos
# `app.core.config` aqui de propósito (migration não deve depender do estado
# de runtime da aplicação).
MODELO_EMBEDDING_ATUAL = "text-embedding-3-small"

# Sentinelas de "proveniência não confirmada" para as 16.330 linhas legadas
# de `document_chunks`. Deliberadamente NÃO são um hex de 64 caracteres nem
# o nome de um modelo real — nunca podem colidir por acaso com um
# fingerprint/modelo genuíno gravado por `app/services/rag.py` a partir de
# agora, então `esta_atualizado()` nunca as trata como atuais.
LEGADO_CONTENT_HASH = "legado_sem_procedencia_confirmada_pre_03092026___"
LEGADO_EMBEDDING_MODEL = "legado_modelo_desconhecido_pre_03092026"

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

    # Backfill de document_chunks: UPDATE em massa com as sentinelas de
    # "proveniência não confirmada" — não deriva nada de `documents.body_md`
    # (não há mais leitura por documento nem laço em Python; a versão
    # anterior desta migration fazia isso para computar um hash que a
    # revisão do PR apontou como falsa certeza de atualidade — ver docstring
    # do módulo). Uma instrução só, rápida mesmo com 16.330 linhas.
    conexao = op.get_bind()
    conexao.execute(
        text("UPDATE document_chunks SET content_hash = :hash, embedding_model = :modelo"),
        {"hash": LEGADO_CONTENT_HASH, "modelo": LEGADO_EMBEDDING_MODEL},
    )

    # As duas colunas nascem NOT NULL a partir de agora — nenhum chunk novo
    # pode ser gravado sem hash/modelo (é exatamente o que a idempotência real
    # por conteúdo exige). Como o UPDATE acima cobre TODA linha de
    # `document_chunks` sem depender de `documents` (nem sequer faz JOIN), a
    # preocupação anterior de "document_id órfão ficaria com content_hash
    # NULL" deixou de existir — o ALTER abaixo não deveria falhar por esse
    # motivo nunca mais.
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
        sa.Column("detalhe", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
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
