"""Testes dirigidos aos 4 bloqueadores de corretude apontados pela revisão
independente do PR #811 (03/09/2026):

1. legacy document_chunks/proveniência — a migration não pode inventar
   metadata histórica que faça chunk legado passar por "atual".
2. source fingerprint exato — título faz parte do texto embedado; mudar só
   o título tem que tornar o índice stale.
3. embedding model / index fingerprint — modelo/config incompatível com
   texto idêntico também tem que gerar stale, nunca misturar vetores em
   silêncio.
4. fallback léxico para chunk stale — documento com chunk antigo continua
   recuperável com conteúdo ATUAL, não o texto desatualizado do chunk."""

import pytest
from sqlalchemy import text

from app.models.content import Document
from app.models.rag import DocumentChunk
from app.services.rag import (
    esta_atualizado,
    fingerprint_fonte,
    indexar_documento,
    recuperar,
)
from app.core.config import settings
from app.services.rag_multi import indexar_entidade


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


def _doc(slug: str, titulo: str, corpo: str) -> Document:
    return Document(
        slug=slug, title=titulo, kind="documento", theme="Farmacologia",
        body_md=corpo, source_tier="A", review_status="revisado", published=True,
    )


# --- Bloqueador 1: proveniência legada -------------------------------------

def test_chunk_com_modelo_sentinela_legado_nunca_e_atual(db):
    """Simula exatamente o que a migration b7ri20260903 grava nas 16.330
    linhas legadas — sentinelas, não proveniência inventada. Independente do
    que `hash_gravado` disser, `modelo_gravado` sentinela nunca bate com o
    modelo configurado agora: `esta_atualizado()` tem que recusar."""
    from migrations.versions.b7ri20260903_rag_integridade_observabilidade import (
        LEGADO_CONTENT_HASH,
        LEGADO_EMBEDDING_MODEL,
    )

    hash_atual = fingerprint_fonte("Qualquer título", "Qualquer corpo")
    # mesmo se o hash gravado, por coincidência, batesse com o atual — o
    # modelo sentinela sozinho já é suficiente para recusar.
    assert esta_atualizado(hash_atual, LEGADO_EMBEDDING_MODEL, hash_atual) is False
    assert esta_atualizado(LEGADO_CONTENT_HASH, LEGADO_EMBEDDING_MODEL, hash_atual) is False


def test_chunk_legado_e_reindexado_pelo_backfill_sem_perder_vetor_ate_la(db, monkeypatch):
    """Um chunk gravado com as sentinelas legadas (proveniência não
    confirmada) precisa ser pego pela próxima passada de indexação — mas o
    vetor antigo continua servível até essa passada rodar (nenhum DELETE só
    por causa da migration)."""
    from migrations.versions.b7ri20260903_rag_integridade_observabilidade import (
        LEGADO_CONTENT_HASH,
        LEGADO_EMBEDDING_MODEL,
    )

    doc = _doc("legado-proveniencia-teste", "Documento legado", "## Seção\nTexto legado, nunca reindexado de verdade.")
    db.add(doc)
    db.commit()
    # insere um chunk "pré-migration" direto, como a migration teria feito
    db.execute(text(
        "INSERT INTO document_chunks (document_id, ordem, conteudo, embedding, tokens_aprox, content_hash, embedding_model) "
        "VALUES (:did, 0, 'conteudo legado', (SELECT array_fill(0.0::float4, ARRAY[1536])::vector), 0, :hash, :modelo)"
    ), {"did": doc.id, "hash": LEGADO_CONTENT_HASH, "modelo": LEGADO_EMBEDDING_MODEL})
    db.commit()

    assert db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).count() == 1

    provedor = _ProvedorFake()
    trechos = indexar_documento(db, doc, provedor)  # apenas_pendentes é o default (True)

    assert trechos > 0, "chunk legado (proveniência sentinela) tinha que ser tratado como pendente"
    novo_chunk = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).first()
    assert novo_chunk.embedding_model == "text-embedding-3-small"  # settings.openai_embedding_model
    assert novo_chunk.content_hash != LEGADO_CONTENT_HASH


# --- Bloqueador 2: fingerprint cobre título ---------------------------------

def test_mesmo_corpo_titulo_alterado_torna_stale_documento(db, monkeypatch):
    provedor = _ProvedorFake()
    monkeypatch.setattr("app.services.rag.obter_provedor_embeddings", lambda: provedor)

    doc = _doc("fingerprint-titulo-doc-teste", "Título original", "## Seção\nCorpo idêntico, nunca muda.")
    db.add(doc)
    db.commit()

    assert indexar_documento(db, doc, provedor) > 0
    assert indexar_documento(db, doc, provedor) == 0  # em dia, nada mudou

    doc.title = "Título COMPLETAMENTE DIFERENTE"
    db.commit()

    trechos = indexar_documento(db, doc, provedor)
    assert trechos > 0, "só o título mudou (corpo idêntico) e isso tem que disparar reindexação"


def test_mesmo_corpo_titulo_alterado_torna_stale_entidade_multi(db, monkeypatch):
    provedor = _ProvedorFake()
    monkeypatch.setattr("app.services.rag.obter_provedor_embeddings", lambda: provedor)
    texto = "Statement idêntico, nunca muda."

    assert indexar_entidade(db, entity_type="evidencia", entity_id=1, titulo="Título A", texto=texto, provedor=provedor) > 0
    assert indexar_entidade(db, entity_type="evidencia", entity_id=1, titulo="Título A", texto=texto, provedor=provedor) == 0

    trechos = indexar_entidade(db, entity_type="evidencia", entity_id=1, titulo="Título B — bem diferente", texto=texto, provedor=provedor)
    assert trechos > 0, "só o título mudou (texto idêntico) e isso tem que disparar reindexação"


# --- Bloqueador 3: modelo/config diferente também gera stale ---------------

def test_mudanca_de_modelo_com_texto_identico_torna_stale_documento(db, monkeypatch):
    provedor = _ProvedorFake()
    monkeypatch.setattr("app.services.rag.obter_provedor_embeddings", lambda: provedor)
    monkeypatch.setattr(settings, "openai_embedding_model", "text-embedding-3-small")

    doc = _doc("fingerprint-modelo-doc-teste", "Título estável", "## Seção\nCorpo estável, texto nunca muda.")
    db.add(doc)
    db.commit()
    assert indexar_documento(db, doc, provedor) > 0

    # "troca de modelo" simulada: settings.openai_embedding_model muda, texto
    # e título continuam idênticos.
    monkeypatch.setattr(settings, "openai_embedding_model", "text-embedding-4-hipotetico")

    trechos = indexar_documento(db, doc, provedor)
    assert trechos > 0, "modelo mudou com texto idêntico — tinha que reindexar, não misturar vetores em silêncio"
    novo = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).first()
    assert novo.embedding_model == "text-embedding-4-hipotetico"


def test_mudanca_de_modelo_com_texto_identico_torna_stale_entidade_multi(db, monkeypatch):
    provedor = _ProvedorFake()
    monkeypatch.setattr("app.services.rag.obter_provedor_embeddings", lambda: provedor)
    monkeypatch.setattr(settings, "openai_embedding_model", "text-embedding-3-small")
    texto = "Texto estável, nunca muda."

    assert indexar_entidade(db, entity_type="evidencia", entity_id=2, titulo="Título", texto=texto, provedor=provedor) > 0

    monkeypatch.setattr(settings, "openai_embedding_model", "text-embedding-4-hipotetico")

    trechos = indexar_entidade(db, entity_type="evidencia", entity_id=2, titulo="Título", texto=texto, provedor=provedor)
    assert trechos > 0, "modelo mudou com texto idêntico — tinha que reindexar"


def test_chunk_com_modelo_diferente_vira_elegivel_ao_fallback(db, monkeypatch):
    """Mesmo que o texto-fonte não tenha mudado, um chunk gravado por outro
    modelo (settings.openai_embedding_model divergente do gravado) não pode
    ser tratado como índice atual — a busca semântica/lexical de documento
    não pode misturar vetores incompatíveis em silêncio. Verificado no nível
    onde a decisão realmente acontece: `buscar_lexico_multi` deixa de
    excluir esse documento do fallback assim que o modelo diverge."""
    from app.services.rag_multi import buscar_lexico_multi

    provedor = _ProvedorFake()
    monkeypatch.setattr("app.services.rag.obter_provedor_embeddings", lambda: provedor)

    doc = _doc("recuperar-modelo-diferente-teste", "Furosemida", "## Farmacologia\nFurosemida dose em insuficiência cardíaca aguda.")
    db.add(doc)
    db.commit()
    indexar_documento(db, doc, provedor)

    # antes de adulterar: chunk está em dia, fallback não precisa dele
    resultados_antes = buscar_lexico_multi(db, "furosemida dose insuficiência cardíaca aguda", limite=10)
    assert doc.slug not in [r["slug"] for r in resultados_antes if r["entity_type"] == "documento"]

    # adultera o embedding_model gravado, simulando um vetor de outro modelo
    # — nenhum campo de texto muda, só a proveniência do vetor.
    db.execute(text("UPDATE document_chunks SET embedding_model = 'modelo-diferente' WHERE document_id = :did"), {"did": doc.id})
    db.commit()

    resultados_depois = buscar_lexico_multi(db, "furosemida dose insuficiência cardíaca aguda", limite=10)
    assert doc.slug in [r["slug"] for r in resultados_depois if r["entity_type"] == "documento"], (
        "modelo divergente tinha que tornar o documento elegível ao fallback de novo"
    )

    # e recuperar() de ponta a ponta não pode quebrar nem sumir com o
    # documento — ele continua recuperável, só não mais via o chunk stale.
    trechos = recuperar(db, "furosemida dose insuficiência cardíaca aguda")
    assert doc.slug in [t["slug"] for t in trechos]


# --- Bloqueador 4: fallback léxico serve conteúdo atual, não o stale -------

def test_chunk_stale_provider_indisponivel_busca_devolve_conteudo_atual(db, monkeypatch):
    """Cenário exato pedido pela revisão: documento publicado + chunk antigo
    + conteúdo editado + provider indisponível => a busca devolve o
    conteúdo ATUAL (via fallback léxico), não o texto stale do chunk."""
    provedor_ok = _ProvedorFake()
    monkeypatch.setattr("app.services.rag.obter_provedor_embeddings", lambda: provedor_ok)

    doc = _doc(
        "chunk-stale-conteudo-atual-teste", "Anticoagulação",
        "## Farmacologia\nVarfarina dose inicial 5mg ao dia, ajuste por RNI.",
    )
    db.add(doc)
    db.commit()
    indexar_documento(db, doc, provedor_ok)  # indexa a versão ANTIGA

    # conteúdo editado DEPOIS da indexação — o chunk gravado agora é stale
    doc.body_md = "## Farmacologia\nVarfarina dose inicial CORRIGIDA 2,5mg ao dia em idosos, ajuste por RNI."
    db.commit()

    # provider indisponível — recuperar() precisa continuar funcionando só
    # com léxico, e o fallback tem que reconhecer o chunk como stale.
    monkeypatch.setattr(
        "app.services.rag.obter_provedor_embeddings",
        lambda: (_ for _ in ()).throw(RuntimeError("insufficient_quota")),
    )

    trechos = recuperar(db, "varfarina dose inicial corrigida idosos RNI")

    achados_do_doc = [t for t in trechos if t["slug"] == doc.slug]
    assert achados_do_doc, "documento com chunk stale precisa continuar recuperável"
    conteudos = " ".join(t["conteudo"] for t in achados_do_doc)
    assert "CORRIGIDA" in conteudos, "tem que devolver o conteúdo ATUAL do documento"
    assert "2,5mg" in conteudos, "dose atual (2,5mg) tem que aparecer"
    assert "inicial 5mg ao dia, ajuste" not in conteudos, (
        "não pode devolver o texto antigo/stale do chunk como se fosse a resposta"
    )


def test_chunk_realmente_atual_nao_duplica_via_fallback(db, monkeypatch):
    """Documento com chunk EM DIA não deve aparecer duas vezes (uma via
    chunk real, outra via fallback léxico com snippet de catalog_search)."""
    from app.services.rag_multi import buscar_lexico_multi

    provedor = _ProvedorFake()
    monkeypatch.setattr("app.services.rag.obter_provedor_embeddings", lambda: provedor)

    doc = _doc(
        "chunk-atual-sem-duplicata-teste", "Amiodarona",
        "## Farmacologia\nAmiodarona dose de manutenção em fibrilação atrial.",
    )
    db.add(doc)
    db.commit()
    indexar_documento(db, doc, provedor)

    resultados = buscar_lexico_multi(db, "amiodarona dose manutenção fibrilação atrial", limite=10)
    slugs_documento = [r["slug"] for r in resultados if r["entity_type"] == "documento"]
    assert doc.slug not in slugs_documento, "chunk já está em dia — não deveria vir pelo fallback"
