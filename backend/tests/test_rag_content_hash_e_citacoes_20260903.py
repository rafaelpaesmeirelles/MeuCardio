"""Correção coordenada de 03/09/2026 — testes focados nas seções 3 (content_hash
real), 6 (fallback léxico de documento sem chunk) e 7 (rota/entity_type nas
citações), que faltavam cobertura dedicada."""

import pytest
from sqlalchemy import text

from app.models.content import Document
from app.models.rag import DocumentChunk
from app.services.rag import indexar_documento, montar_contexto, recuperar


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
def _acervo_limpo(db):
    tabelas = "documents, document_chunks"
    db.execute(text(f"TRUNCATE {tabelas} RESTART IDENTITY CASCADE"))
    db.commit()
    yield
    db.execute(text(f"TRUNCATE {tabelas} RESTART IDENTITY CASCADE"))
    db.commit()


def _doc(slug: str, corpo: str) -> Document:
    return Document(
        slug=slug, title="Documento de teste", kind="documento", theme="Farmacologia",
        body_md=corpo, source_tier="A", review_status="revisado", published=True,
    )


def test_conteudo_alterado_e_reindexado_automaticamente(db, monkeypatch):
    """Documento já indexado, cujo corpo muda depois: apenas_pendentes precisa
    reconhecer isso como pendente (era o bug central da seção 3 — antes,
    'tem chunk' bastava para sempre considerar em dia)."""
    provedor = _ProvedorFake()
    monkeypatch.setattr("app.services.rag.obter_provedor_embeddings", lambda: provedor)

    doc = _doc("content-hash-editado-teste", "## Seção\nTexto original.")
    db.add(doc)
    db.commit()

    trechos1 = indexar_documento(db, doc, provedor)
    assert trechos1 > 0
    hash_antigo = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).first().content_hash

    # segunda chamada sem mudar nada: zero trechos (já em dia)
    assert indexar_documento(db, doc, provedor) == 0

    doc.body_md = "## Seção\nTexto EDITADO — precisa reindexar."
    db.commit()

    trechos2 = indexar_documento(db, doc, provedor)
    assert trechos2 > 0
    hash_novo = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).first().content_hash
    assert hash_novo != hash_antigo


def test_falha_do_provedor_preserva_chunk_anterior_valido(db, monkeypatch):
    """Fluxo: indexa com sucesso, edita o corpo, o provedor passa a falhar —
    o chunk ANTIGO (do corpo anterior) precisa continuar servível, nunca
    apagado antes de o novo embedding estar em mãos (seção 3: 'nenhuma
    chamada HTTP lenta deve manter DELETE/lock aberto', e 'em falha externa,
    preservar índice anterior válido')."""
    provedor_ok = _ProvedorFake()
    monkeypatch.setattr("app.services.rag.obter_provedor_embeddings", lambda: provedor_ok)

    doc = _doc("content-hash-falha-preserva-teste", "## Seção\nTexto original válido.")
    db.add(doc)
    db.commit()

    assert indexar_documento(db, doc, provedor_ok) > 0
    conteudo_antigo = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).first().conteudo

    doc.body_md = "## Seção\nTexto novo, mas o provedor vai falhar agora."
    db.commit()

    with pytest.raises(RuntimeError):
        indexar_documento(db, doc, _ProvedorSemCredito())

    # o chunk do corpo ANTERIOR precisa continuar exatamente como estava —
    # nenhum DELETE deve ter acontecido antes da falha do provedor.
    chunk_sobrevivente = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).first()
    assert chunk_sobrevivente is not None
    assert chunk_sobrevivente.conteudo == conteudo_antigo


def test_documento_publicado_sem_chunk_aparece_no_fallback_lexico(db, monkeypatch):
    """Seção 6: documento publicado que ainda não foi indexado (backlog, ou
    embeddings fora do ar) não pode ser invisível para a busca léxica.
    `SQL_LEXICO` (rag.py) faz INNER JOIN com document_chunks — sozinho, ele
    NUNCA acharia este documento. A cobertura real vem de
    `rag_multi.buscar_lexico_multi`, que trata a frente 'documento' via
    catalog_search (sem depender de chunk) e é chamada por `recuperar()`.
    Provedor de embeddings falhando de propósito, para isolar o caminho
    puramente léxico."""
    monkeypatch.setattr(
        "app.services.rag.obter_provedor_embeddings",
        lambda: (_ for _ in ()).throw(RuntimeError("sem crédito")),
    )
    db.add(_doc(
        "fallback-lexico-sem-chunk-metoprolol-teste",
        "## Farmacologia\nMetoprolol succinato uso em insuficiência cardíaca descompensada.",
    ))
    db.commit()

    trechos = recuperar(db, "metoprolol succinato insuficiência cardíaca descompensada")

    slugs = {t["slug"] for t in trechos}
    assert "fallback-lexico-sem-chunk-metoprolol-teste" in slugs
    achado = next(t for t in trechos if t["slug"] == "fallback-lexico-sem-chunk-metoprolol-teste")
    assert achado["entity_type"] == "documento"
    assert achado["rota"] == "/biblioteca/fallback-lexico-sem-chunk-metoprolol-teste"


def test_citacao_de_documento_carrega_rota_e_entity_type(db):
    """Seção 7: montar_contexto() precisa preservar rota/entity_type mesmo
    quando o trecho vem só do caminho léxico de documento (sem embedding)."""
    trechos = [{
        "referencia": "Ref.", "slug": "citacao-rota-teste", "titulo": "Título",
        "tema": "Farmacologia", "secao": None, "conteudo": "Corpo do trecho.",
        "review_status": "revisado", "gaps": [], "rota": "/biblioteca/citacao-rota-teste",
        "entity_type": "documento",
    }]
    _, fontes = montar_contexto(trechos)
    assert len(fontes) == 1
    assert fontes[0]["rota"] == "/biblioteca/citacao-rota-teste"
    assert fontes[0]["entity_type"] == "documento"


def test_citacao_de_frente_nao_documento_nao_usa_rota_de_biblioteca(db):
    """Regressão do bug relatado: toda citação virava /biblioteca/{slug},
    link quebrado para qualquer entity_type que não fosse documento."""
    trechos = [{
        "referencia": "Ref.", "slug": "evidencia-rota-teste", "titulo": "Evidência",
        "tema": "Farmacologia", "secao": None, "conteudo": "Corpo.", "review_status": "revisado",
        "gaps": [], "rota": "/evidencias/evidencia-rota-teste", "entity_type": "evidencia",
    }]
    _, fontes = montar_contexto(trechos)
    assert fontes[0]["rota"] != f"/biblioteca/{fontes[0]['slug']}"
    assert fontes[0]["rota"] == "/evidencias/evidencia-rota-teste"
    assert fontes[0]["entity_type"] == "evidencia"
