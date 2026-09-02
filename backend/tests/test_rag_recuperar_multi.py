"""Regressão de `rag.recuperar()` após a Parte D/F (correção coordenada de
02/09/2026): a busca híbrida da IA passa a fundir documentos com as outras
12 frentes, sem confundir as duas sequências de id de chunk (document_chunks
e knowledge_chunks são tabelas INDEPENDENTES — o mesmo inteiro pode existir
nas duas ao mesmo tempo sem relação nenhuma)."""

import pytest
from sqlalchemy import text

from app.models.content import Document
from app.models.evidence import EvidenceRecord
from app.services.rag import indexar_documento, recuperar
from app.services.rag_multi import indexar_tipo


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


def test_recuperar_funde_documento_e_evidencia_sem_colidir_ids(db, monkeypatch):
    monkeypatch.setattr("app.services.rag.obter_provedor_embeddings", lambda: _ProvedorFake())
    monkeypatch.setattr("app.services.rag_multi.obter_provedor_embeddings", lambda: _ProvedorFake())

    doc = Document(
        slug="documento-hibrido-teste", title="Documento de teste", kind="documento",
        theme="Farmacologia", body_md="## Seção\nConteúdo de teste do documento.",
        source_tier="A", review_status="revisado", published=True,
    )
    db.add(doc)
    db.flush()
    indexar_documento(db, doc, provedor=_ProvedorFake())

    evidencia = EvidenceRecord(
        slug="evidencia-hibrida-teste", statement="Statement de teste da evidência.",
        summary="Resumo.", recommendation_class="I", evidence_level="A",
        society="Sociedade de teste", year=2024, guideline_title="Diretriz de teste",
        reference="Referência de teste", theme="Farmacologia",
        review_status="revisado", published=True,
    )
    db.add(evidencia)
    db.commit()
    indexar_tipo(db, "evidencia", apenas_pendentes=False)

    # As duas tabelas de chunk têm sequence própria — força a mesma faixa de
    # id nas duas (1, 2, 3...) pra provar que a mistura de namespaces no RRF
    # não junta por engano um document_chunk com um knowledge_chunk de mesmo
    # id numérico.
    trechos = recuperar(db, "conteúdo de teste")

    tipos = {t["entity_type"] for t in trechos}
    assert "documento" in tipos
    assert "evidencia" in tipos
    slugs = {t["slug"] for t in trechos}
    assert "documento-hibrido-teste" in slugs
    assert "evidencia-hibrida-teste" in slugs
    for trecho in trechos:
        assert trecho["conteudo"]
        assert trecho["rota"]


def test_recuperar_nunca_traz_evidencia_despublicada(db, monkeypatch):
    monkeypatch.setattr("app.services.rag.obter_provedor_embeddings", lambda: _ProvedorFake())
    monkeypatch.setattr("app.services.rag_multi.obter_provedor_embeddings", lambda: _ProvedorFake())

    evidencia = EvidenceRecord(
        slug="evidencia-retida-teste", statement="Statement retido de teste.",
        summary="Resumo.", recommendation_class="I", evidence_level="A",
        society="Sociedade de teste", year=2024, guideline_title="Diretriz de teste",
        reference="Referência de teste", theme="Farmacologia",
        review_status="revisado", published=True,
    )
    db.add(evidencia)
    db.commit()
    indexar_tipo(db, "evidencia", apenas_pendentes=False)

    evidencia.published = False
    db.commit()

    trechos = recuperar(db, "statement retido")
    assert all(t["slug"] != "evidencia-retida-teste" for t in trechos)
