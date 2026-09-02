"""Parte 3 da correção coordenada de 02/09/2026: `reconcile_content` publicava
e reconciliava o grafo, mas nunca colocava o conteúdo novo na fila de
RAG/embedding — só um comando manual avulso fazia isso. `_reindexar_rag_pendente`
fecha esse gap, chamada dentro de `reconcile()` logo após `backfill_mesmo_tema`."""

import pytest
from sqlalchemy import text

from app.commands.reconcile_content import _reindexar_rag_pendente
from app.models.content import Document
from app.models.evidence import EvidenceRecord
from app.models.rag import DocumentChunk, KnowledgeChunk


class _ProvedorFake:
    def embeddings(self, textos):
        vetores = []
        for texto in textos:
            semente = sum(ord(c) for c in texto) % 997
            vetores.append([((semente + i) % 997) / 997 for i in range(1536)])
        return vetores


@pytest.fixture(autouse=True)
def _acervo_limpo(db):
    tabelas = "documents, document_chunks, evidence_records, knowledge_chunks"
    db.execute(text(f"TRUNCATE {tabelas} RESTART IDENTITY CASCADE"))
    db.commit()
    yield
    db.execute(text(f"TRUNCATE {tabelas} RESTART IDENTITY CASCADE"))
    db.commit()


def test_reindexar_rag_pendente_indexa_documento_e_frente_multi(db, monkeypatch):
    monkeypatch.setattr("app.services.rag.obter_provedor_embeddings", lambda: _ProvedorFake())
    monkeypatch.setattr("app.services.rag_multi.obter_provedor_embeddings", lambda: _ProvedorFake())

    db.add(Document(
        slug="reconcile-rag-documento-teste", title="Documento de teste", kind="documento",
        theme="Farmacologia", body_md="## Seção\nConteúdo de teste do documento.",
        source_tier="A", review_status="revisado", published=True,
    ))
    db.add(EvidenceRecord(
        slug="reconcile-rag-evidencia-teste", statement="Statement de teste.",
        summary="Resumo.", recommendation_class="I", evidence_level="A",
        society="Sociedade de teste", year=2024, guideline_title="Diretriz de teste",
        reference="Referência de teste", theme="Farmacologia",
        review_status="revisado", published=True,
    ))
    db.commit()

    resultado = _reindexar_rag_pendente(db)

    assert resultado["documentos"]["documentos"] == 1
    assert resultado["multi_frente"]["evidencia"]["entidades"] == 1
    assert db.query(DocumentChunk).count() > 0
    assert db.query(KnowledgeChunk).filter(KnowledgeChunk.entity_type == "evidencia").count() > 0


def test_reindexar_rag_pendente_e_idempotente(db, monkeypatch):
    """Segunda chamada não reprocessa quem já tem chunk — `apenas_pendentes`."""
    monkeypatch.setattr("app.services.rag.obter_provedor_embeddings", lambda: _ProvedorFake())
    monkeypatch.setattr("app.services.rag_multi.obter_provedor_embeddings", lambda: _ProvedorFake())

    db.add(EvidenceRecord(
        slug="reconcile-rag-idempotente-teste", statement="Statement de teste.",
        summary="Resumo.", recommendation_class="I", evidence_level="A",
        society="Sociedade de teste", year=2024, guideline_title="Diretriz de teste",
        reference="Referência de teste", theme="Farmacologia",
        review_status="revisado", published=True,
    ))
    db.commit()

    primeira = _reindexar_rag_pendente(db)
    segunda = _reindexar_rag_pendente(db)

    assert primeira["multi_frente"]["evidencia"]["entidades"] == 1
    assert segunda["multi_frente"]["evidencia"]["entidades"] == 0  # já indexada, nada pendente
