"""Correção coordenada de 03/09/2026, seção 10 (schema/migrations) — testes de
contrato para não regredir silenciosamente as garantias estruturais que a
migration `b7ri20260903` acrescentou (content_hash/embedding_model NOT NULL,
CHECK de entity_type, tabela de auditoria de execução do backfill), além de
travar a existência dos índices HNSW já criados por migrations anteriores."""

import pytest
from sqlalchemy import text

from app.services.rag_sources import FONTES_POR_TIPO

# Espelha ENTITY_TYPES_PERMITIDOS de
# migrations/versions/b7ri20260903_rag_integridade_observabilidade.py —
# migration já aplicada não se edita, então a lista do CHECK constraint é
# literal e fixa lá. Este teste é o tripwire: se alguém adicionar uma frente
# nova a `rag_sources.FONTES_RAG` sem escrever uma migration nova para o
# CHECK, este teste quebra ANTES de virar um IntegrityError genérico e sem
# contexto no primeiro INSERT em produção (achado da revisão adversarial de
# 03/09/2026).
_ENTITY_TYPES_NO_CHECK_ATUAL = frozenset({
    "evidencia", "estudo", "caso_clinico", "trilha", "material_paciente",
    "checklist", "exame", "medicamento", "galeria", "protocolo_emergencia",
    "doenca", "triagem_sintoma", "calculadora",
})


def test_document_chunks_tem_content_hash_e_embedding_model_not_null(db):
    linhas = db.execute(text(
        "SELECT column_name, is_nullable FROM information_schema.columns "
        "WHERE table_name = 'document_chunks' AND column_name IN ('content_hash', 'embedding_model')"
    )).all()
    por_coluna = {nome: nulavel for nome, nulavel in linhas}
    assert por_coluna.get("content_hash") == "NO"
    assert por_coluna.get("embedding_model") == "NO"


def test_knowledge_chunks_tem_content_hash_e_embedding_model_not_null(db):
    linhas = db.execute(text(
        "SELECT column_name, is_nullable FROM information_schema.columns "
        "WHERE table_name = 'knowledge_chunks' AND column_name IN ('content_hash', 'embedding_model')"
    )).all()
    por_coluna = {nome: nulavel for nome, nulavel in linhas}
    assert por_coluna.get("content_hash") == "NO"
    assert por_coluna.get("embedding_model") == "NO"


def test_knowledge_chunks_entity_type_tem_check_constraint(db):
    existe = db.execute(text(
        "SELECT 1 FROM pg_constraint WHERE conname = 'ck_knowledge_chunks_entity_type_permitido'"
    )).scalar()
    assert existe == 1, (
        "CHECK ck_knowledge_chunks_entity_type_permitido não existe — o allowlist de "
        "entity_type voltaria a existir só em Python (app.services.rag_sources), sem "
        "trava estrutural contra INSERT com tipo inválido."
    )


def test_knowledge_chunks_check_rejeita_entity_type_fora_do_allowlist(db):
    from sqlalchemy.exc import IntegrityError

    with pytest.raises(IntegrityError):
        db.execute(text(
            "INSERT INTO knowledge_chunks "
            "(entity_type, entity_id, ordem, conteudo, embedding, content_hash, embedding_model) "
            "VALUES ('tipo_inexistente_teste', 999999, 0, 'x', "
            "(SELECT array_fill(0.0::float4, ARRAY[1536])::vector), 'x', 'x')"
        ))
    db.rollback()


def test_indices_hnsw_existem_em_document_chunks_e_knowledge_chunks(db):
    linhas = db.execute(text(
        "SELECT tablename, indexname FROM pg_indexes "
        "WHERE indexname IN ('document_chunks_embedding_idx', 'knowledge_chunks_embedding_idx')"
    )).all()
    encontrados = {(tabela, indice) for tabela, indice in linhas}
    assert ("document_chunks", "document_chunks_embedding_idx") in encontrados
    assert ("knowledge_chunks", "knowledge_chunks_embedding_idx") in encontrados
    # confirma que é HNSW de fato (não um índice qualquer com o mesmo nome)
    definicoes = db.execute(text(
        "SELECT indexdef FROM pg_indexes WHERE indexname IN "
        "('document_chunks_embedding_idx', 'knowledge_chunks_embedding_idx')"
    )).scalars().all()
    assert all("hnsw" in d.lower() for d in definicoes)


def test_check_de_entity_type_esta_sincronizado_com_rag_sources():
    """Tripwire: se este teste quebrar, alguém adicionou (ou removeu) uma
    frente em `rag_sources.FONTES_RAG` sem escrever a migration nova que o
    CHECK constraint de `knowledge_chunks.entity_type` exige."""
    esperado = set(FONTES_POR_TIPO.keys()) | {"calculadora"}
    assert esperado == set(_ENTITY_TYPES_NO_CHECK_ATUAL), (
        f"rag_sources tem {sorted(esperado)}, mas o CHECK constraint (fixado em "
        f"migration já aplicada) só permite {sorted(_ENTITY_TYPES_NO_CHECK_ATUAL)}. "
        "Escreva uma migration nova para o CHECK antes de publicar a frente nova."
    )


def test_document_chunks_tem_unique_constraint_document_id_ordem(db):
    """Achado de dois revisores adversariais independentes em 03/09/2026,
    reproduzido ao vivo por eles: sem esta constraint, duas chamadas
    concorrentes de indexar_documento() para o MESMO documento podiam deixar
    duas linhas sobreviverem com o mesmo (document_id, ordem) — chunk
    duplicado servido ao assistente clínico. Com a constraint, a mesma
    corrida vira IntegrityError capturada pelo circuit breaker existente."""
    existe = db.execute(text(
        "SELECT 1 FROM pg_constraint WHERE conname = 'uq_document_chunks_document_id_ordem'"
    )).scalar()
    assert existe == 1


def test_document_chunks_constraint_rejeita_duplicata_de_verdade(db):
    """Prova direta (não só 'a constraint existe'): dois INSERT com o mesmo
    (document_id, ordem) — o cenário exato que os dois revisores adversariais
    reproduziram ao vivo com transações concorrentes — precisa falhar no
    segundo, não silenciosamente duplicar."""
    from sqlalchemy.exc import IntegrityError

    from app.models.content import Document

    doc = Document(
        slug="schema-contrato-unicidade-chunk-teste", title="Doc", kind="documento",
        theme="Farmacologia", body_md="x", source_tier="A",
        review_status="revisado", published=True,
    )
    db.add(doc)
    db.commit()

    vetor_sql = "(SELECT array_fill(0.0::float4, ARRAY[1536])::vector)"
    db.execute(text(
        f"INSERT INTO document_chunks (document_id, ordem, conteudo, embedding, "
        f"tokens_aprox, content_hash, embedding_model) VALUES (:did, 0, 'a', {vetor_sql}, 0, 'h1', 'm')"
    ), {"did": doc.id})
    db.commit()

    with pytest.raises(IntegrityError):
        db.execute(text(
            f"INSERT INTO document_chunks (document_id, ordem, conteudo, embedding, "
            f"tokens_aprox, content_hash, embedding_model) VALUES (:did, 0, 'b', {vetor_sql}, 0, 'h2', 'm')"
        ), {"did": doc.id})
    db.rollback()
    db.execute(text("DELETE FROM document_chunks WHERE document_id = :did"), {"did": doc.id})
    db.execute(text("DELETE FROM documents WHERE id = :did"), {"did": doc.id})
    db.commit()


def test_rag_reindex_runs_existe_com_colunas_esperadas(db):
    colunas = set(db.execute(text(
        "SELECT column_name FROM information_schema.columns WHERE table_name = 'rag_reindex_runs'"
    )).scalars().all())
    esperadas = {
        "id", "started_at", "finished_at", "dry_run", "only_types",
        "entidades_processadas", "trechos_gerados", "falhas",
        "backlog_restante", "exit_code", "detalhe",
    }
    assert esperadas.issubset(colunas)
