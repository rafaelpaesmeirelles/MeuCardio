"""Parte 3 da correção coordenada de 02/09/2026: `rag.indexar_tudo()` não
pode travar o lote inteiro quando o provedor de embeddings falha (crédito,
rede) num documento específico — mesma resiliência aplicada em
`rag_multi.indexar_tipo()`."""

import pytest
from sqlalchemy import text

from app.models.content import Document
from app.models.rag import DocumentChunk
from app.services.rag import indexar_tudo


class _ProvedorFake:
    def embeddings(self, textos):
        vetores = []
        for texto in textos:
            semente = sum(ord(c) for c in texto) % 997
            vetores.append([((semente + i) % 997) / 997 for i in range(1536)])
        return vetores


class _ProvedorSemCredito:
    def embeddings(self, textos):
        raise RuntimeError("insufficient_quota: sem crédito no provedor de embeddings")


@pytest.fixture(autouse=True)
def _documentos_limpos(db):
    db.execute(text("TRUNCATE documents, document_chunks RESTART IDENTITY CASCADE"))
    db.commit()
    yield
    db.execute(text("TRUNCATE documents, document_chunks RESTART IDENTITY CASCADE"))
    db.commit()


def _documento(slug: str) -> Document:
    return Document(
        slug=slug, title=f"Documento {slug}", kind="documento", theme="Farmacologia",
        body_md=f"## Seção\nConteúdo de teste do documento {slug}.",
        source_tier="A", review_status="revisado", published=True,
    )


def test_indexar_tudo_nao_propaga_falha_do_provedor_e_deixa_pendente(db, monkeypatch):
    monkeypatch.setattr("app.services.rag.obter_provedor_embeddings", lambda: _ProvedorSemCredito())
    db.add(_documento("indexar-tudo-sem-credito"))
    db.commit()

    resultado = indexar_tudo(db, apenas_pendentes=False)  # não deve levantar

    assert resultado["documentos"] == 0
    assert resultado["falhas"] == 1
    assert db.query(DocumentChunk).count() == 0


def test_indexar_tudo_retoma_apos_credito_voltar(db, monkeypatch):
    db.add(_documento("indexar-tudo-retry"))
    db.commit()

    monkeypatch.setattr("app.services.rag.obter_provedor_embeddings", lambda: _ProvedorSemCredito())
    primeira = indexar_tudo(db, apenas_pendentes=True)
    assert primeira["falhas"] == 1

    monkeypatch.setattr("app.services.rag.obter_provedor_embeddings", lambda: _ProvedorFake())
    segunda = indexar_tudo(db, apenas_pendentes=True)
    assert segunda["documentos"] == 1
    assert segunda["falhas"] == 0
    assert db.query(DocumentChunk).count() > 0


def test_indexar_tudo_interrompe_lote_apos_3_falhas_seguidas(db, monkeypatch):
    monkeypatch.setattr("app.services.rag.obter_provedor_embeddings", lambda: _ProvedorSemCredito())
    db.add_all([_documento(f"indexar-tudo-circuito-{i}") for i in range(10)])
    db.commit()

    resultado = indexar_tudo(db, apenas_pendentes=False)

    assert resultado["documentos"] == 0
    assert resultado["falhas"] == 3  # para exatamente na 3ª, não tenta os outros 7
