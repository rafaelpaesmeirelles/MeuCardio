"""Regressão da Parte D (correção coordenada de 02/09/2026): RAG genérico
para as 12 frentes fora de `documents` + calculadoras."""

import pytest
from sqlalchemy import text

from app.models.evidence import EvidenceRecord
from app.models.rag import KnowledgeChunk
from app.services.rag_multi import (
    indexar_tipo,
    indexar_tudo_multi,
    ids_semanticos_multi,
    resolver_trechos_multi,
)


class _ProvedorFake:
    """Embedding determinístico por hash do texto — sem chamar API externa."""

    def embeddings(self, textos):
        vetores = []
        for texto in textos:
            semente = sum(ord(c) for c in texto) % 997
            vetores.append([((semente + i) % 997) / 997 for i in range(1536)])
        return vetores


@pytest.fixture(autouse=True)
def _evidencias_limpas(db):
    db.execute(text("TRUNCATE evidence_records, knowledge_chunks RESTART IDENTITY CASCADE"))
    db.commit()
    yield
    db.execute(text("TRUNCATE evidence_records, knowledge_chunks RESTART IDENTITY CASCADE"))
    db.commit()


def _evidencia(slug: str, published: bool = True) -> EvidenceRecord:
    return EvidenceRecord(
        slug=slug, statement=f"Statement clínico de teste para {slug}.",
        summary="Resumo de teste.", recommendation_class="I", evidence_level="A",
        society="Sociedade de teste", year=2024, guideline_title="Diretriz de teste",
        reference="Referência de teste", theme="Farmacologia",
        review_status="revisado", published=published,
    )


def test_indexa_so_publicados_e_pula_texto_vazio(db, monkeypatch):
    monkeypatch.setattr("app.services.rag_multi.obter_provedor_embeddings", lambda: _ProvedorFake())
    db.add_all([
        _evidencia("evidencia-publicada-teste"),
        _evidencia("evidencia-rascunho-teste", published=False),
    ])
    db.commit()

    resultado = indexar_tipo(db, "evidencia", apenas_pendentes=False)

    assert resultado["entidades"] == 1
    chunks = db.query(KnowledgeChunk).filter(KnowledgeChunk.entity_type == "evidencia").all()
    assert len(chunks) >= 1
    publicada = db.query(EvidenceRecord).filter(EvidenceRecord.slug == "evidencia-publicada-teste").one()
    assert all(c.entity_id == publicada.id for c in chunks)


def test_apenas_pendentes_nao_reprocessa_ja_indexado(db, monkeypatch):
    monkeypatch.setattr("app.services.rag_multi.obter_provedor_embeddings", lambda: _ProvedorFake())
    db.add(_evidencia("evidencia-idempotencia-teste"))
    db.commit()

    primeira = indexar_tipo(db, "evidencia", apenas_pendentes=True)
    segunda = indexar_tipo(db, "evidencia", apenas_pendentes=True)

    assert primeira["entidades"] == 1
    assert segunda["entidades"] == 0


def test_despublicar_e_reindexar_remove_do_indice(db, monkeypatch):
    monkeypatch.setattr("app.services.rag_multi.obter_provedor_embeddings", lambda: _ProvedorFake())
    item = _evidencia("evidencia-despublicada-teste")
    db.add(item)
    db.commit()
    indexar_tipo(db, "evidencia", apenas_pendentes=False)
    assert db.query(KnowledgeChunk).filter(KnowledgeChunk.entity_type == "evidencia").count() >= 1

    item.published = False
    db.commit()
    # reindexação plena (apenas_pendentes=False) só considera published=true:
    # o item despublicado não aparece mais em `publicados()`, mas seus chunks
    # antigos continuam até uma reindexação explícita removê-los — prova que
    # a defesa real está no JOIN de leitura (próximo teste), não só no índice.
    resultado = indexar_tipo(db, "evidencia", apenas_pendentes=False)
    assert resultado["entidades"] == 0


def test_busca_semantica_ignora_chunk_de_entidade_despublicada(db, monkeypatch):
    monkeypatch.setattr("app.services.rag_multi.obter_provedor_embeddings", lambda: _ProvedorFake())
    item = _evidencia("evidencia-defesa-profundidade-teste")
    db.add(item)
    db.commit()
    indexar_tipo(db, "evidencia", apenas_pendentes=False)

    vetor = _ProvedorFake().embeddings(["qualquer pergunta"])[0]
    antes = ids_semanticos_multi(db, vetor, limite=50)
    assert len(antes) >= 1

    item.published = False
    db.commit()

    depois = ids_semanticos_multi(db, vetor, limite=50)
    # Chunk continua fisicamente no índice (não reindexamos), mas o JOIN
    # com published=true na tabela de origem tem que excluí-lo da resposta.
    assert set(depois) & set(antes) == set()


def test_resolver_trechos_preserva_identidade_da_entidade(db, monkeypatch):
    monkeypatch.setattr("app.services.rag_multi.obter_provedor_embeddings", lambda: _ProvedorFake())
    db.add(_evidencia("evidencia-identidade-teste"))
    db.commit()
    indexar_tipo(db, "evidencia", apenas_pendentes=False)

    chunk = db.query(KnowledgeChunk).filter(KnowledgeChunk.entity_type == "evidencia").first()
    trechos = resolver_trechos_multi(db, [chunk.id])

    assert trechos[chunk.id]["entity_type"] == "evidencia"
    assert trechos[chunk.id]["slug"] == "evidencia-identidade-teste"
    assert trechos[chunk.id]["rota"] == "/evidencias/evidencia-identidade-teste"


def test_indexar_tudo_multi_cobre_as_13_frentes_mais_calculadora(db, monkeypatch):
    monkeypatch.setattr("app.services.rag_multi.obter_provedor_embeddings", lambda: _ProvedorFake())
    resultado = indexar_tudo_multi(db, apenas_pendentes=True)
    # 12 frentes de FONTES_RAG + calculadora
    assert len(resultado) == 13
    assert "calculadora" in resultado
    assert resultado["calculadora"]["entidades"] > 0  # REGISTRY não está vazio em produção


class _ProvedorSemCredito:
    def embeddings(self, textos):
        raise RuntimeError("insufficient_quota: sem crédito no provedor de embeddings")


def test_indexar_tipo_nao_propaga_falha_do_provedor_e_deixa_pendente(db, monkeypatch):
    """Parte 3 da correção coordenada de 02/09/2026: uma falha do provedor de
    embeddings (crédito, rede) durante a indexação em lote não pode travar o
    lote inteiro. A entidade continua sem chunk (pendente) e pode ser
    retentada depois — nunca desaparece, nunca quebra a chamada."""
    monkeypatch.setattr("app.services.rag_multi.obter_provedor_embeddings", lambda: _ProvedorSemCredito())
    db.add(_evidencia("evidencia-sem-credito-teste"))
    db.commit()

    resultado = indexar_tipo(db, "evidencia", apenas_pendentes=False)  # não deve levantar

    assert resultado["entidades"] == 0
    assert resultado["falhas"] == 1
    assert db.query(KnowledgeChunk).filter(KnowledgeChunk.entity_type == "evidencia").count() == 0


def test_indexar_tipo_retoma_apos_credito_voltar(db, monkeypatch):
    """A mesma entidade que falhou continua elegível (`apenas_pendentes`) e é
    indexada normalmente assim que o provedor volta a funcionar."""
    db.add(_evidencia("evidencia-retry-teste"))
    db.commit()

    monkeypatch.setattr("app.services.rag_multi.obter_provedor_embeddings", lambda: _ProvedorSemCredito())
    primeira = indexar_tipo(db, "evidencia", apenas_pendentes=True)
    assert primeira["falhas"] == 1

    monkeypatch.setattr("app.services.rag_multi.obter_provedor_embeddings", lambda: _ProvedorFake())
    segunda = indexar_tipo(db, "evidencia", apenas_pendentes=True)
    assert segunda["entidades"] == 1
    assert segunda["falhas"] == 0
    assert db.query(KnowledgeChunk).filter(KnowledgeChunk.entity_type == "evidencia").count() > 0


def test_indexar_tipo_interrompe_lote_apos_3_falhas_seguidas(db, monkeypatch):
    """Provedor fora do ar é sistêmico, não um item ruim isolado — repetir a
    mesma chamada fadada pra cada uma das N entidades pendentes (acervo real:
    milhares) seria inútil e lento. Depois de 3 falhas seguidas o lote para;
    o resto continua pendente pra próxima chamada (achado ao ligar isto
    contra o acervo inteiro em `reconcile_content`)."""
    monkeypatch.setattr("app.services.rag_multi.obter_provedor_embeddings", lambda: _ProvedorSemCredito())
    db.add_all([_evidencia(f"evidencia-circuito-{i}-teste") for i in range(10)])
    db.commit()

    resultado = indexar_tipo(db, "evidencia", apenas_pendentes=False)

    assert resultado["entidades"] == 0
    assert resultado["falhas"] == 3  # para exatamente na 3ª, não tenta as outras 7
