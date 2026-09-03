"""Correção coordenada de 03/09/2026, seção 10 (schema/migrations) — testes de
contrato para não regredir silenciosamente as garantias estruturais que a
migration `b7ri20260903` acrescentou (content_hash/embedding_model NOT NULL,
CHECK de entity_type, tabela de auditoria de execução do backfill), além de
travar a existência dos índices HNSW já criados por migrations anteriores."""

from sqlalchemy import text


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

    with __import__("pytest").raises(IntegrityError):
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
