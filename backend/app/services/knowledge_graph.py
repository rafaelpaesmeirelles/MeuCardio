"""Serviço do Grafo de Conhecimento Clínico Universal (issue #52, nova fase).

Três responsabilidades, deliberadamente separadas:

1. **Registro de entidade/relação** (`registrar_entidade`, `registrar_relacao`)
   — idempotente (upsert por chave única), nunca duplica nó nem aresta,
   rejeita estruturalmente qualquer `entity_type` fora do allowlist global
   (ver `app/models/knowledge.py` para a régua de segurança completa).

2. **Backfill** (`backfill_mesmo_tema`) — deriva o grafo a partir de metadado
   já existente, sem inventar relação nenhuma: usa o MESMO casamento por
   `theme`/`tema` exato que `app/services/related_content.py` já usa em
   produção, mas agora PERSISTIDO como aresta tipada (`same_theme`,
   proveniência `structured_metadata`, confiança `derived`) em vez de
   recalculado a cada requisição. Idempotente (upsert), auditável (cada
   aresta sabe de onde veio), não-destrutivo (nunca apaga aresta que já
   existe — rodar de novo só preenche o que falta), repetível (pode rodar a
   qualquer momento sem duplicar nada, graças à UniqueConstraint do modelo).
   Deliberadamente limitado por item (evita explosão cartesiana — "tudo
   relacionado com tudo" não significa conectar cada nó a todos os outros do
   mesmo tema, e sim aos mais recentes/relevantes de cada tipo vizinho).

3. **Consulta** (`relacionados_de`) — API de leitura paginada, ordenada por
   relevância, agrupada por tipo de entidade alvo — o que alimenta tanto o
   endpoint REST quanto (futuramente) a recuperação da IA por subgrafo.
"""
from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.checklist import DischargeChecklist
from app.models.clinical_case import ClinicalCase
from app.models.content import Document
from app.models.drug import Drug
from app.models.emergency import EmergencyProtocol
from app.models.evidence import EvidenceRecord
from app.models.gallery import GalleryImage
from app.models.knowledge import (
    NIVEIS_CONFIANCA_PERMITIDOS,
    REVIEW_STATUS_RELACAO_PERMITIDOS,
    TIPOS_ENTIDADE_PERMITIDOS,
    TIPOS_PROVENIENCIA_PERMITIDOS,
    TIPOS_RELACAO_PERMITIDOS,
    KnowledgeEntity,
    KnowledgeRelation,
)
from app.models.lab_test import LabTest
from app.models.patient_material import PatientMaterial
from app.models.study import ScientificStudy
from app.models.study_track import StudyTrack
from app.services import calculators as calc

# Limite de arestas "same_theme" por par de tipos, por entidade de origem —
# a mesma filosofia de `related_content.LIMITE_POR_CATEGORIA`, aplicada aqui
# na hora de SEMEAR o grafo, não só na hora de exibi-lo. Evita que um tema
# com centenas de itens gere um grafo denso demais para navegar ou indexar.
LIMITE_BACKFILL_POR_TIPO_VIZINHO = 5

# Rota pública de cada tipo de entidade — usada para montar o `href` na
# resposta da API, mesma convenção de `related_content.py`.
ROTA_LISTA_POR_TIPO = {
    "documento": "/biblioteca",
    "fluxograma": "/fluxogramas",
    "evidencia": "/evidencias",
    "estudo": "/estudos",
    "medicamento": "/medicamentos",
    "exame": "/exames",
    "caso_clinico": "/casos-clinicos",
    "trilha": "/trilhas",
    "galeria": "/galeria",
    "checklist": "/checklists",
    "material_paciente": "/material-paciente",
    "protocolo_emergencia": "/emergencia",
    "calculadora": "/calculadoras",
}


class TipoEntidadeNaoPermitido(ValueError):
    """Levantado quando algo tenta registrar um `entity_type` fora do
    allowlist — nunca deve acontecer em uso normal; existe para impedir,
    de forma estrutural (não só documental), que dado de paciente vire nó
    do grafo global."""


def _rota_item(tipo: str, slug: str) -> str:
    if tipo == "medicamento":
        return f"/medicamentos?slug={slug}"
    if tipo in ("documento", "fluxograma"):
        return f"/biblioteca/{slug}"
    if tipo in ("protocolo_emergencia", "checklist", "material_paciente"):
        return ROTA_LISTA_POR_TIPO[tipo]
    return f"{ROTA_LISTA_POR_TIPO.get(tipo, '')}/{slug}"


def registrar_entidade(
    db: Session, *, entity_type: str, canonical_id: int, slug: str, title: str,
) -> KnowledgeEntity:
    """Upsert idempotente de um nó — nunca cria duplicata para o mesmo
    (entity_type, canonical_id); atualiza slug/título se mudaram na fonte."""
    if entity_type not in TIPOS_ENTIDADE_PERMITIDOS:
        raise TipoEntidadeNaoPermitido(
            f"entity_type={entity_type!r} não está no allowlist do grafo global — "
            "dado de paciente/consulta/prescrição nunca pode virar nó público."
        )
    existente = db.execute(
        select(KnowledgeEntity).where(
            KnowledgeEntity.entity_type == entity_type,
            KnowledgeEntity.canonical_id == canonical_id,
        )
    ).scalar_one_or_none()
    if existente:
        if existente.slug != slug or existente.title != title:
            existente.slug = slug
            existente.title = title
        return existente
    novo = KnowledgeEntity(
        entity_type=entity_type, canonical_id=canonical_id, slug=slug, title=title,
    )
    db.add(novo)
    db.flush()
    return novo


def registrar_relacao(
    db: Session,
    *,
    source: KnowledgeEntity,
    target: KnowledgeEntity,
    relation_type: str,
    provenance_type: str,
    confidence: str,
    relevance_score: float = 0.5,
    evidence_source: str | None = None,
    review_status: str = "pendente_revisao",
    extra: dict | None = None,
) -> KnowledgeRelation | None:
    """Upsert idempotente de uma aresta — nunca duplica (source, target,
    relation_type). Devolve None (sem erro) quando source == target, porque
    um item nunca precisa "se relacionar consigo mesmo"."""
    if source.id == target.id:
        return None
    if relation_type not in TIPOS_RELACAO_PERMITIDOS:
        raise ValueError(f"relation_type={relation_type!r} fora do catálogo permitido.")
    if provenance_type not in TIPOS_PROVENIENCIA_PERMITIDOS:
        raise ValueError(f"provenance_type={provenance_type!r} fora do catálogo permitido.")
    if confidence not in NIVEIS_CONFIANCA_PERMITIDOS:
        raise ValueError(f"confidence={confidence!r} fora do catálogo permitido.")
    if review_status not in REVIEW_STATUS_RELACAO_PERMITIDOS:
        raise ValueError(f"review_status={review_status!r} fora do catálogo permitido.")

    existente = db.execute(
        select(KnowledgeRelation).where(
            KnowledgeRelation.source_entity_id == source.id,
            KnowledgeRelation.target_entity_id == target.id,
            KnowledgeRelation.relation_type == relation_type,
        )
    ).scalar_one_or_none()
    if existente:
        return existente

    relacao = KnowledgeRelation(
        source_entity_id=source.id,
        target_entity_id=target.id,
        relation_type=relation_type,
        provenance_type=provenance_type,
        confidence=confidence,
        relevance_score=relevance_score,
        evidence_source=evidence_source,
        review_status=review_status,
        extra=extra or {},
    )
    db.add(relacao)
    db.flush()
    return relacao


@dataclass
class _ItemTema:
    tipo: str
    id_origem: int
    slug: str
    titulo: str


def _itens_por_tema(db: Session) -> dict[str, list[_ItemTema]]:
    """Reconstrói, a partir das mesmas 12 frentes de `related_content.py`,
    o agrupamento {tema: [itens]} — só itens publicados, exatamente a
    mesma régua de "nunca fabricar relação" já documentada naquele módulo:
    casamento por igualdade exata de tema, sem heurística de texto."""
    por_tema: dict[str, list[_ItemTema]] = {}

    def _add(tema: str | None, item: _ItemTema) -> None:
        tema = (tema or "").strip()
        if not tema:
            return
        por_tema.setdefault(tema, []).append(item)

    for d in db.execute(
        select(Document).where(Document.published.is_(True), Document.kind != "fluxograma")
    ).scalars():
        _add(d.theme, _ItemTema("documento", d.id, d.slug, d.title))

    for d in db.execute(
        select(Document).where(Document.published.is_(True), Document.kind == "fluxograma")
    ).scalars():
        _add(d.theme, _ItemTema("fluxograma", d.id, d.slug, d.title))

    for e in db.execute(
        select(EvidenceRecord).where(EvidenceRecord.published.is_(True))
    ).scalars():
        titulo = (e.statement[:140] + "…") if e.statement and len(e.statement) > 140 else (e.statement or "")
        _add(e.theme, _ItemTema("evidencia", e.id, e.slug, titulo))

    for s in db.execute(
        select(ScientificStudy).where(ScientificStudy.published.is_(True))
    ).scalars():
        _add(s.theme, _ItemTema("estudo", s.id, s.slug, s.title))

    # Medicamentos entram só sob o tema "Farmacologia" — mesma convenção já
    # documentada em related_content.py (drugs não tem campo de tema próprio).
    for d in db.execute(select(Drug).where(Drug.published.is_(True))).scalars():
        _add("Farmacologia", _ItemTema("medicamento", d.id, d.slug, d.generic_name))

    for t in db.execute(select(LabTest).where(LabTest.published.is_(True))).scalars():
        _add(t.theme, _ItemTema("exame", t.id, t.slug, t.name))

    for c in db.execute(select(ClinicalCase).where(ClinicalCase.published.is_(True))).scalars():
        _add(c.tema, _ItemTema("caso_clinico", c.id, c.slug, c.titulo))

    for t in db.execute(select(StudyTrack).where(StudyTrack.published.is_(True))).scalars():
        _add(t.tema, _ItemTema("trilha", t.id, t.slug, t.titulo))

    for g in db.execute(select(GalleryImage).where(GalleryImage.published.is_(True))).scalars():
        _add(g.theme, _ItemTema("galeria", g.id, g.slug, g.title))

    for c in calc.REGISTRY.values():
        if c.status == "implementada":
            # Calculadoras não têm id de banco — o "canonical_id" é
            # sintético (hash estável do slug), já que a origem é um
            # registro em memória, não uma linha de tabela.
            _add(c.theme, _ItemTema("calculadora", abs(hash(c.slug)) % 2_147_483_647, c.slug, c.name))

    prot_q = (
        select(EmergencyProtocol, Document.theme)
        .join(Document, Document.slug == EmergencyProtocol.documento_slug)
        .where(EmergencyProtocol.published.is_(True))
    )
    for p, tema_doc in db.execute(prot_q).all():
        _add(tema_doc, _ItemTema("protocolo_emergencia", p.id, p.slug, p.titulo))

    for c in db.execute(
        select(DischargeChecklist).where(DischargeChecklist.published.is_(True))
    ).scalars():
        _add(c.theme, _ItemTema("checklist", c.id, c.slug, c.condicao))

    for m in db.execute(
        select(PatientMaterial).where(PatientMaterial.published.is_(True))
    ).scalars():
        _add(m.tema, _ItemTema("material_paciente", m.id, m.slug, m.titulo))

    return por_tema


def backfill_mesmo_tema(db: Session) -> dict:
    """Semeia entidades e arestas `same_theme` a partir do metadado
    estruturado já existente. Idempotente e não-destrutivo: rodar de novo
    só adiciona o que ainda não existe (as UniqueConstraint do modelo
    impedem duplicata; este processo nunca faz DELETE)."""
    por_tema = _itens_por_tema(db)

    entidades_criadas = 0
    relacoes_criadas = 0

    for tema, itens in por_tema.items():
        # Cria/atualiza o nó de cada item primeiro, para que as arestas
        # abaixo sempre encontrem os dois lados já registrados.
        nos: list[tuple[_ItemTema, KnowledgeEntity]] = []
        for item in itens:
            antes = db.execute(
                select(func.count()).select_from(KnowledgeEntity).where(
                    KnowledgeEntity.entity_type == item.tipo,
                    KnowledgeEntity.canonical_id == item.id_origem,
                )
            ).scalar_one()
            entidade = registrar_entidade(
                db, entity_type=item.tipo, canonical_id=item.id_origem,
                slug=item.slug, title=item.titulo,
            )
            if antes == 0:
                entidades_criadas += 1
            nos.append((item, entidade))

        # Arestas same_theme: cada nó conecta aos N mais recentes de CADA
        # OUTRO TIPO no mesmo tema (não um Cartesiano completo) — é o que
        # torna a navegação cruzada útil sem explodir o número de arestas.
        por_tipo: dict[str, list[tuple[_ItemTema, KnowledgeEntity]]] = {}
        for item, entidade in nos:
            por_tipo.setdefault(item.tipo, []).append((item, entidade))

        for tipo_origem, lista_origem in por_tipo.items():
            for tipo_alvo, lista_alvo in por_tipo.items():
                if tipo_alvo == tipo_origem:
                    continue
                candidatos_alvo = lista_alvo[:LIMITE_BACKFILL_POR_TIPO_VIZINHO]
                for _item_o, ent_o in lista_origem[:LIMITE_BACKFILL_POR_TIPO_VIZINHO]:
                    for _item_a, ent_a in candidatos_alvo:
                        relacao = registrar_relacao(
                            db, source=ent_o, target=ent_a, relation_type="same_theme",
                            provenance_type="structured_metadata", confidence="derived",
                            relevance_score=0.4,
                            review_status="pendente_revisao",
                            extra={"tema": tema},
                        )
                        if relacao is not None and relacao.id is not None:
                            relacoes_criadas += 1

    entidades_arquivadas = _arquivar_entidades_sem_conteudo_publicado_correspondente(db, por_tema)

    db.commit()
    return {
        "temas_processados": len(por_tema),
        "entidades_criadas_ou_atualizadas": entidades_criadas,
        "relacoes_seed_tentadas": relacoes_criadas,
        "entidades_arquivadas": entidades_arquivadas,
    }


def _arquivar_entidades_sem_conteudo_publicado_correspondente(
    db: Session, por_tema: dict[str, list[_ItemTema]],
) -> int:
    """Reconciliação de segurança: se um item foi despublicado (ou apagado)
    desde o último backfill, o nó dele não pode continuar aparecendo em
    consultas — mesma regra que já vale para toda outra frente do produto
    (conteúdo retido nunca vaza). Nunca faz DELETE (preserva a auditoria de
    proveniência das arestas que apontam para ele); só marca
    `status='arquivado'`, e `relacionados_de()` já filtra por
    `status == 'ativo'`. Reversível: se o item voltar a ser publicado, o
    próximo backfill reativa o nó (mesma função `registrar_entidade`, que
    faz upsert por (entity_type, canonical_id) sem recriar linha)."""
    ids_publicados_por_tipo: dict[str, set[int]] = {}
    for itens in por_tema.values():
        for item in itens:
            ids_publicados_por_tipo.setdefault(item.tipo, set()).add(item.id_origem)

    arquivadas = 0
    for tipo in TIPOS_ENTIDADE_PERMITIDOS:
        ids_validos = ids_publicados_por_tipo.get(tipo, set())
        # Todas as entidades do tipo, ativas OU já arquivadas — precisa das
        # duas para tanto arquivar o que deixou de ser publicado quanto
        # reativar o que voltou a ser publicado, no mesmo laço.
        todas = db.execute(
            select(KnowledgeEntity).where(KnowledgeEntity.entity_type == tipo)
        ).scalars().all()
        for entidade in todas:
            deveria_estar_ativa = entidade.canonical_id in ids_validos
            if deveria_estar_ativa and entidade.status != "ativo":
                # Conteúdo republicado — reativa o nó (nunca recria a linha).
                entidade.status = "ativo"
            elif not deveria_estar_ativa and entidade.status == "ativo":
                entidade.status = "arquivado"
                arquivadas += 1
    return arquivadas


def relacionados_de(
    db: Session, *, entity_type: str, slug: str, limite_por_tipo: int = 5,
) -> dict | None:
    """Devolve, agrupado por tipo de entidade alvo e ordenado por
    relevância, tudo que se relaciona com o item pedido — nas duas direções
    da aresta (o grafo é consultado como se fosse não-direcionado para fins
    de navegação, mesmo as arestas sendo tipadas/direcionadas no armazenamento).
    Só relação com `review_status != 'rejeitado'` aparece. Devolve None
    quando o próprio item não está no grafo, OU quando ele existe mas está
    arquivado — conteúdo despublicado depois do último backfill some da
    consulta como se nunca tivesse sido indexado, mesma régua de "nunca
    conteúdo retido chega ao assinante" já em vigor no resto do produto
    (RAG, busca, related_content)."""
    origem = db.execute(
        select(KnowledgeEntity).where(
            KnowledgeEntity.entity_type == entity_type, KnowledgeEntity.slug == slug,
            KnowledgeEntity.status == "ativo",
        )
    ).scalar_one_or_none()
    if origem is None:
        return None

    saida = db.execute(
        select(KnowledgeRelation, KnowledgeEntity)
        .join(KnowledgeEntity, KnowledgeEntity.id == KnowledgeRelation.target_entity_id)
        .where(
            KnowledgeRelation.source_entity_id == origem.id,
            KnowledgeRelation.review_status != "rejeitado",
            KnowledgeEntity.status == "ativo",
        )
    ).all()
    entrada = db.execute(
        select(KnowledgeRelation, KnowledgeEntity)
        .join(KnowledgeEntity, KnowledgeEntity.id == KnowledgeRelation.source_entity_id)
        .where(
            KnowledgeRelation.target_entity_id == origem.id,
            KnowledgeRelation.review_status != "rejeitado",
            KnowledgeEntity.status == "ativo",
        )
    ).all()

    vistos: set[tuple[str, str]] = set()
    por_tipo: dict[str, list[dict]] = {}
    for relacao, outro in list(saida) + list(entrada):
        chave = (outro.entity_type, outro.slug)
        if chave in vistos:
            continue
        vistos.add(chave)
        por_tipo.setdefault(outro.entity_type, []).append({
            "slug": outro.slug,
            "titulo": outro.title,
            "relation_type": relacao.relation_type,
            "relevance_score": relacao.relevance_score,
            "confidence": relacao.confidence,
            "provenance_type": relacao.provenance_type,
            "review_status": relacao.review_status,
            "rota": _rota_item(outro.entity_type, outro.slug),
        })

    grupos = []
    total = 0
    for tipo, itens in por_tipo.items():
        itens_ordenados = sorted(itens, key=lambda i: i["relevance_score"], reverse=True)
        pagina = itens_ordenados[:limite_por_tipo]
        total += len(itens_ordenados)
        grupos.append({
            "tipo": tipo,
            "rota_lista": ROTA_LISTA_POR_TIPO.get(tipo, ""),
            "total_disponivel": len(itens_ordenados),
            "itens": pagina,
        })

    return {
        "entity_type": entity_type, "slug": slug, "titulo": origem.title,
        "grupos": grupos, "total": total,
    }
