"""Indexação RAG genérica para as 12 frentes de `rag_sources.FONTES_RAG` +
calculadoras (Parte D da correção coordenada de 02/09/2026).

Reaproveita `rag.dividir()` (o corte por seção/tamanho já usado para
documentos) e o mesmo provedor de embeddings — só a origem do texto e a
tabela de destino mudam (`knowledge_chunks` em vez de `document_chunks`).
"""
from __future__ import annotations

import hashlib
import logging

from sqlalchemy import select, union_all
from sqlalchemy.orm import Session

from app.models.rag import KnowledgeChunk
from app.services.calculators import REGISTRY as CALCULATORS_REGISTRY
from app.services.catalog_search import (
    INTERNAL_MARKER_SQL_PATTERN,
    INTERNAL_OVERRIDE_SQL_PATTERN,
    LITERAL_SQL,
    SQL,
    calculadoras_encontradas,
    literal_like,
    normalizar,
)
from app.services.knowledge_graph import _id_estavel
from app.services.rag import dividir, obter_provedor_embeddings
from app.services.rag_sources import FONTES_POR_TIPO, FONTES_RAG, publicados

# `catalog_search` usa 'emergencia' como rótulo de frente (mesmo texto
# mostrado em /api/search); `rag_sources.FONTES_RAG` usa o entity_type
# 'protocolo_emergencia' (allowlist do grafo). Único ponto onde os dois
# vocabulários divergem — todo o resto é 1:1 (frente == entity_type).
_FRENTE_PARA_ENTITY_TYPE = {fonte.entity_type: fonte.entity_type for fonte in FONTES_RAG if fonte.entity_type != "protocolo_emergencia"}
_FRENTE_PARA_ENTITY_TYPE["emergencia"] = "protocolo_emergencia"


log = logging.getLogger("corvia.rag_multi")


def _hash(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def indexar_entidade(db: Session, *, entity_type: str, entity_id: int, titulo: str, texto: str, provedor=None) -> int:
    """Upsert idempotente dos chunks de uma entidade. `content_hash` do texto
    completo evita reprocessar quando nada mudou (chamador decide se pula)."""

    provedor = provedor or obter_provedor_embeddings()
    db.query(KnowledgeChunk).filter(
        KnowledgeChunk.entity_type == entity_type, KnowledgeChunk.entity_id == entity_id,
    ).delete()

    pedacos = dividir(texto or "")
    if not pedacos:
        db.commit()
        return 0

    hash_completo = _hash(texto)
    textos = [f"{titulo}\n{t or ''}\n{c}".strip() for t, c in pedacos]

    vetores: list[list[float]] = []
    for i in range(0, len(textos), 64):
        vetores.extend(provedor.embeddings(textos[i:i + 64]))

    for ordem, ((secao_titulo, corpo), vetor) in enumerate(zip(pedacos, vetores)):
        db.add(KnowledgeChunk(
            entity_type=entity_type, entity_id=entity_id, ordem=ordem,
            titulo_secao=secao_titulo, conteudo=corpo, embedding=vetor,
            tokens_aprox=len(corpo) // 4, content_hash=hash_completo,
        ))
    db.commit()
    return len(pedacos)


def _entidades_ja_indexadas(db: Session, entity_type: str) -> set[int]:
    return set(
        db.execute(
            select(KnowledgeChunk.entity_id).where(KnowledgeChunk.entity_type == entity_type).distinct()
        ).scalars()
    )


def indexar_tipo(db: Session, entity_type: str, *, apenas_pendentes: bool = True) -> dict:
    """Indexa todas as linhas publicadas de um `entity_type` do registro."""

    if entity_type == "calculadora":
        return _indexar_calculadoras(db, apenas_pendentes=apenas_pendentes)

    fonte = FONTES_POR_TIPO[entity_type]
    provedor = obter_provedor_embeddings()
    ja_indexadas = _entidades_ja_indexadas(db, entity_type) if apenas_pendentes else set()

    total_entidades = 0
    total_trechos = 0
    falhas = 0
    for item in publicados(db, fonte):
        if apenas_pendentes and item.id in ja_indexadas:
            continue
        texto = fonte.texto(item)
        if not texto or not texto.strip():
            continue
        titulo = getattr(item, fonte.titulo_attr, "") or ""
        # Parte 3 da correção coordenada de 02/09/2026: mesma resiliência de
        # `rag.indexar_tudo()` — uma entidade que falhe (crédito, rede) não
        # trava o lote; fica pendente pra próxima chamada (idempotente).
        try:
            total_trechos += indexar_entidade(
                db, entity_type=entity_type, entity_id=item.id, titulo=titulo, texto=texto, provedor=provedor,
            )
        except Exception:
            log.exception("Falha ao indexar %s id=%s — segue pendente.", entity_type, item.id)
            db.rollback()
            falhas += 1
            continue
        total_entidades += 1
    return {"entity_type": entity_type, "entidades": total_entidades, "trechos": total_trechos, "falhas": falhas}


def _indexar_calculadoras(db: Session, *, apenas_pendentes: bool = True) -> dict:

    provedor = obter_provedor_embeddings()
    ja_indexadas = _entidades_ja_indexadas(db, "calculadora") if apenas_pendentes else set()

    total_entidades = 0
    total_trechos = 0
    falhas = 0
    for calc in CALCULATORS_REGISTRY.values():
        entity_id = _id_estavel("calculadora", calc.slug)
        if apenas_pendentes and entity_id in ja_indexadas:
            continue
        partes = [calc.purpose, calc.reference, "\n".join(calc.limitations or [])]
        texto = "\n\n".join(p for p in partes if p)
        if not texto.strip():
            continue
        try:
            total_trechos += indexar_entidade(
                db, entity_type="calculadora", entity_id=entity_id, titulo=calc.name, texto=texto, provedor=provedor,
            )
        except Exception:
            log.exception("Falha ao indexar calculadora slug=%s — segue pendente.", calc.slug)
            db.rollback()
            falhas += 1
            continue
        total_entidades += 1
    return {"entity_type": "calculadora", "entidades": total_entidades, "trechos": total_trechos, "falhas": falhas}


def indexar_tudo_multi(db: Session, *, apenas_pendentes: bool = True) -> dict:
    """Indexa as 12 frentes de `FONTES_RAG` + calculadoras. Não toca em
    `documents`/`document_chunks` — esses continuam via `rag.indexar_tudo()`."""
    resultado = {}
    for fonte in FONTES_RAG:
        resultado[fonte.entity_type] = indexar_tipo(db, fonte.entity_type, apenas_pendentes=apenas_pendentes)
    resultado["calculadora"] = indexar_tipo(db, "calculadora", apenas_pendentes=apenas_pendentes)
    return resultado


def ids_semanticos_multi(db: Session, vetor: list[float], limite: int) -> list[int]:
    """IDs de `knowledge_chunks` mais próximos da pergunta, por distância de
    cosseno — só de entidade `published=true` na tabela de origem (mesma
    defesa em profundidade de `recuperar()` para documentos: o filtro no
    índice não basta, a leitura reconfirma). Calculadora não tem tabela/
    `published` — elegibilidade é só "está no REGISTRY hoje", garantida no
    índice (`indexar_tipo` já opera só sobre `CALCULATORS_REGISTRY.values()`).
    """
    selects = []
    for fonte in FONTES_RAG:
        selects.append(
            select(KnowledgeChunk.id)
            .join(fonte.model, fonte.model.id == KnowledgeChunk.entity_id)
            .where(KnowledgeChunk.entity_type == fonte.entity_type, fonte.model.published.is_(True))
        )
    selects.append(
        select(KnowledgeChunk.id).where(KnowledgeChunk.entity_type == "calculadora")
    )
    uniao = union_all(*selects).subquery()
    consulta = (
        select(KnowledgeChunk.id)
        .join(uniao, uniao.c.id == KnowledgeChunk.id)
        .order_by(KnowledgeChunk.embedding.cosine_distance(vetor))
        .limit(limite)
    )
    return [r[0] for r in db.execute(consulta).all()]


def resolver_trechos_multi(db: Session, chunk_ids: list[int]) -> dict[int, dict]:
    """Resolve chunk_id -> dict de citação (slug/titulo/tema/rota/conteudo),
    agrupado por `entity_type` pra minimizar consultas (uma por tipo presente
    nos resultados, não uma por chunk)."""
    if not chunk_ids:
        return {}
    chunks = db.execute(
        select(KnowledgeChunk).where(KnowledgeChunk.id.in_(chunk_ids))
    ).scalars().all()

    por_tipo: dict[str, list[KnowledgeChunk]] = {}
    for chunk in chunks:
        por_tipo.setdefault(chunk.entity_type, []).append(chunk)

    resultado: dict[int, dict] = {}

    calculadoras_chunks = por_tipo.pop("calculadora", [])
    if calculadoras_chunks:
        por_id_estavel = {_id_estavel("calculadora", c.slug): c for c in CALCULATORS_REGISTRY.values()}
        for chunk in calculadoras_chunks:
            calc = por_id_estavel.get(chunk.entity_id)
            if calc is None:
                continue
            resultado[chunk.id] = {
                "slug": calc.slug, "titulo": calc.name, "tema": calc.theme,
                "secao": chunk.titulo_secao, "conteudo": chunk.conteudo,
                "review_status": "revisado", "gaps": [], "rota": f"/calculadoras/{calc.slug}",
                "entity_type": "calculadora",
            }

    for entity_type, tipo_chunks in por_tipo.items():
        fonte = FONTES_POR_TIPO[entity_type]
        ids = [c.entity_id for c in tipo_chunks]
        linhas = {item.id: item for item in db.execute(
            select(fonte.model).where(fonte.model.id.in_(ids))
        ).scalars().all()}
        for chunk in tipo_chunks:
            item = linhas.get(chunk.entity_id)
            if item is None:
                continue
            slug = getattr(item, fonte.slug_attr)
            resultado[chunk.id] = {
                "slug": slug,
                "titulo": getattr(item, fonte.titulo_attr) or "",
                "tema": getattr(item, fonte.tema_attr) if fonte.tema_attr else None,
                "secao": chunk.titulo_secao, "conteudo": chunk.conteudo,
                "review_status": getattr(item, "review_status", "revisado"),
                "gaps": [], "rota": fonte.rota.format(slug=slug),
                "entity_type": entity_type,
            }
    return resultado


def buscar_lexico_multi(db: Session, pergunta: str, limite: int) -> list[dict]:
    """Busca léxica (tsvector, com fallback literal por acento/substring —
    mesmo comportamento de `/api/search`) nas 12 frentes de `FONTES_RAG` +
    calculadoras, reaproveitando a MESMA consulta de `catalog_search`
    (Parte 2 da correção coordenada de 02/09/2026): produto e IA nunca
    divergem sobre o que é "todo o acervo elegível".

    Não depende de `knowledge_chunks`/embeddings — lê direto das tabelas de
    origem publicadas, a mesma fonte que `/api/search` usa. Por isso
    continua funcionando mesmo com o provedor de embeddings sem crédito
    (Parte 3): item pendente de embedding não desaparece da IA, só não
    aparece no braço semântico.

    Devolve citações no mesmo formato de `resolver_trechos_multi()` (sem
    `secao`, que só existe para chunk — aqui a unidade é o item inteiro).
    Frente 'documento' é ignorada: já coberta pela busca léxica de
    `document_chunks` em `rag.py` (`SQL_LEXICO`), não duplicada aqui.
    """
    values = {"q": pergunta, "q_like": literal_like(pergunta), "frente": None, "limit": limite, "offset": 0}
    search_values = {
        **values,
        "internal_override_pattern": INTERNAL_OVERRIDE_SQL_PATTERN,
        "internal_marker_pattern": INTERNAL_MARKER_SQL_PATTERN,
    }
    linhas = db.execute(SQL, search_values).mappings().all()
    if not linhas and normalizar(pergunta):
        linhas = db.execute(LITERAL_SQL, search_values).mappings().all()

    resultados: list[dict] = []
    for linha in linhas:
        entity_type = _FRENTE_PARA_ENTITY_TYPE.get(linha["frente"])
        if entity_type is None:
            continue  # 'documento' (já coberto em rag.py) ou frente desconhecida
        fonte = FONTES_POR_TIPO[entity_type]
        resultados.append({
            "slug": linha["slug"], "titulo": linha["title"], "tema": linha["theme"],
            "secao": None, "conteudo": linha["snippet"],
            "review_status": "revisado", "gaps": [],
            "rota": fonte.rota.format(slug=linha["slug"]), "entity_type": entity_type,
        })

    for calc_row in calculadoras_encontradas(pergunta):
        if len(resultados) >= limite:
            break
        resultados.append({
            "slug": calc_row["slug"], "titulo": calc_row["title"], "tema": calc_row["theme"],
            "secao": None, "conteudo": calc_row["snippet"],
            "review_status": "revisado", "gaps": [],
            "rota": f"/calculadoras/{calc_row['slug']}", "entity_type": "calculadora",
        })

    return resultados[:limite]
