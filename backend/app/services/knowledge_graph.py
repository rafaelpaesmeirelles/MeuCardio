"""Serviço do Grafo de Conhecimento Clínico Universal (issue #52, nova fase).

Responsabilidades deliberadamente separadas:

1. **Registro de entidade/relação** (`registrar_entidade`, `registrar_relacao`)
   — idempotente (upsert por chave única), nunca duplica nó nem aresta,
   rejeita estruturalmente qualquer `entity_type` fora do allowlist global.

2. **Backfill por tema** — deriva `same_theme` a partir do MESMO casamento
   exato de `theme`/`tema` usado por `related_content.py`, sem heurística.

3. **Backfill de conteúdo especializado** — registra doenças e triagens por
   sintoma publicadas e cria apenas relações já expressas em metadado
   estruturado: `related_document_slugs`, `patient_material_slug` e
   diferenciais cujo nome/alias casa exatamente com uma doença publicada.
   Não há inferência por similaridade de texto, embeddings ou IA.

4. **Consulta** (`relacionados_de`) — leitura agrupada por tipo, nas duas
   direções, filtrando conteúdo arquivado/rejeitado.
"""
from __future__ import annotations

from dataclasses import dataclass
import unicodedata

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
from app.models.specialty_guide import SpecialtyDisease, SymptomTriageGuide
from app.models.study import ScientificStudy
from app.models.study_track import StudyTrack
from app.services import calculators as calc

# Limite de arestas "same_theme" por par de tipos, por entidade de origem.
LIMITE_BACKFILL_POR_TIPO_VIZINHO = 5

# Rota pública de cada tipo de entidade — usada para montar o `href` na API.
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
    "doenca": "/doencas",
    "triagem_sintoma": "/triagem-sintomas",
}


class TipoEntidadeNaoPermitido(ValueError):
    """Levantado quando algo tenta registrar `entity_type` fora do allowlist."""


def _rota_item(tipo: str, slug: str) -> str:
    if tipo == "medicamento":
        return f"/medicamentos?slug={slug}"
    if tipo in ("documento", "fluxograma"):
        return f"/biblioteca/{slug}"
    if tipo == "doenca":
        return f"/doencas/{slug}"
    if tipo == "triagem_sintoma":
        return f"/triagem-sintomas?slug={slug}"
    if tipo in ("protocolo_emergencia", "checklist", "material_paciente"):
        return ROTA_LISTA_POR_TIPO[tipo]
    return f"{ROTA_LISTA_POR_TIPO.get(tipo, '')}/{slug}"


def registrar_entidade(
    db: Session, *, entity_type: str, canonical_id: int, slug: str, title: str,
) -> KnowledgeEntity:
    """Upsert idempotente de nó global/editorial."""
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
    """Upsert idempotente de aresta; auto-relação é ignorada."""
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
    """Agrupa as frentes clássicas por tema exato — só itens publicados."""
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

    # Medicamentos entram só sob o tema Farmacologia — mesma convenção de
    # related_content.py; Drug não possui tema clínico próprio.
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
            _add(c.theme, _ItemTema(
                "calculadora", abs(hash(c.slug)) % 2_147_483_647, c.slug, c.name,
            ))

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


def _normalizar_chave_clinica(valor: str) -> str:
    """Normalização conservadora para casamento EXATO de nome/alias.

    Remove apenas diferenças ortográficas superficiais (caixa, acento e
    espaços). Não faz stemming, fuzzy matching, embeddings nem aproximação
    semântica — uma relação clínica não nasce porque duas strings 'parecem'.
    """
    decomposed = unicodedata.normalize("NFKD", valor or "")
    sem_acentos = "".join(c for c in decomposed if not unicodedata.combining(c))
    return " ".join(sem_acentos.casefold().strip().split())


def _texto_diferencial(valor: object) -> str | None:
    if isinstance(valor, str):
        return valor.strip() or None
    if isinstance(valor, dict):
        for campo in ("name", "label", "text", "title"):
            candidato = valor.get(campo)
            if isinstance(candidato, str) and candidato.strip():
                return candidato.strip()
    return None


def _entidade_por_slug(
    db: Session, *, tipos: tuple[str, ...], slug: str,
) -> KnowledgeEntity | None:
    return db.execute(
        select(KnowledgeEntity).where(
            KnowledgeEntity.entity_type.in_(tipos),
            KnowledgeEntity.slug == slug,
        )
    ).scalars().first()


def _relacao_ja_existe(
    db: Session, source: KnowledgeEntity, target: KnowledgeEntity, relation_type: str,
) -> bool:
    return db.execute(
        select(KnowledgeRelation.id).where(
            KnowledgeRelation.source_entity_id == source.id,
            KnowledgeRelation.target_entity_id == target.id,
            KnowledgeRelation.relation_type == relation_type,
        )
    ).scalar_one_or_none() is not None


def _registrar_relacao_estruturada(
    db: Session,
    *,
    source: KnowledgeEntity,
    target: KnowledgeEntity,
    relation_type: str,
    relevance_score: float,
    extra: dict,
) -> int:
    """Registra aresta derivada de metadado e devolve 1 somente se nova."""
    existia = _relacao_ja_existe(db, source, target, relation_type)
    registrar_relacao(
        db,
        source=source,
        target=target,
        relation_type=relation_type,
        provenance_type="structured_metadata",
        confidence="derived",
        relevance_score=relevance_score,
        review_status="pendente_revisao",
        extra=extra,
    )
    return 0 if existia else 1


def _semear_conteudo_especializado(
    db: Session,
) -> tuple[dict[str, set[int]], int, int]:
    """Registra doença/triagem e relações sustentadas por campos explícitos.

    Nenhuma aresta aqui é inferida de texto livre por proximidade. O vínculo
    doença↔documento vem de `related_document_slugs`; material↔doença de
    `patient_material_slug`; e doença↔triagem apenas quando um item de
    `differentials` casa exatamente, após normalização ortográfica, com um
    único nome/alias de doença publicada. Relações permanecem
    `pendente_revisao`: derivação determinística não equivale a revisão humana.
    """
    doencas = db.execute(
        select(SpecialtyDisease).where(SpecialtyDisease.published.is_(True))
    ).scalars().all()
    triagens = db.execute(
        select(SymptomTriageGuide).where(SymptomTriageGuide.published.is_(True))
    ).scalars().all()

    ids_publicados = {
        "doenca": {d.id for d in doencas},
        "triagem_sintoma": {t.id for t in triagens},
    }
    entidades_novas = 0
    relacoes_novas = 0
    no_doenca_por_id: dict[int, KnowledgeEntity] = {}
    no_triagem_por_id: dict[int, KnowledgeEntity] = {}

    for d in doencas:
        existia = db.execute(
            select(KnowledgeEntity.id).where(
                KnowledgeEntity.entity_type == "doenca",
                KnowledgeEntity.canonical_id == d.id,
            )
        ).scalar_one_or_none()
        no_doenca_por_id[d.id] = registrar_entidade(
            db, entity_type="doenca", canonical_id=d.id, slug=d.slug, title=d.name,
        )
        if existia is None:
            entidades_novas += 1

    for t in triagens:
        existia = db.execute(
            select(KnowledgeEntity.id).where(
                KnowledgeEntity.entity_type == "triagem_sintoma",
                KnowledgeEntity.canonical_id == t.id,
            )
        ).scalar_one_or_none()
        no_triagem_por_id[t.id] = registrar_entidade(
            db, entity_type="triagem_sintoma", canonical_id=t.id, slug=t.slug, title=t.name,
        )
        if existia is None:
            entidades_novas += 1

    # Relações declaradas diretamente no cadastro da doença.
    for d in doencas:
        no_doenca = no_doenca_por_id[d.id]
        for slug_doc in dict.fromkeys(d.related_document_slugs or []):
            no_doc = _entidade_por_slug(
                db, tipos=("documento", "fluxograma"), slug=slug_doc,
            )
            if no_doc is None:
                continue
            relacoes_novas += _registrar_relacao_estruturada(
                db,
                source=no_doenca,
                target=no_doc,
                relation_type="mentioned_in",
                relevance_score=0.85,
                extra={"campo": "related_document_slugs", "slug": slug_doc},
            )

        slug_material = (d.patient_material_slug or "").strip()
        if slug_material:
            no_material = _entidade_por_slug(
                db, tipos=("material_paciente",), slug=slug_material,
            )
            if no_material is not None:
                relacoes_novas += _registrar_relacao_estruturada(
                    db,
                    source=no_material,
                    target=no_doenca,
                    relation_type="patient_education_for",
                    relevance_score=0.9,
                    extra={"campo": "patient_material_slug", "slug": slug_material},
                )

    # Índice conservador de nomes/aliases. Se uma chave apontar para mais de
    # uma doença, ela é ambígua e NÃO gera relação automática.
    por_nome: dict[str, list[tuple[SpecialtyDisease, KnowledgeEntity]]] = {}
    for d in doencas:
        no = no_doenca_por_id[d.id]
        for nome in [d.name, *(d.aliases or [])]:
            chave = _normalizar_chave_clinica(nome)
            if chave:
                por_nome.setdefault(chave, []).append((d, no))

    for t in triagens:
        no_triagem = no_triagem_por_id[t.id]
        for diferencial_bruto in t.differentials or []:
            diferencial = _texto_diferencial(diferencial_bruto)
            if not diferencial:
                continue
            candidatos = por_nome.get(_normalizar_chave_clinica(diferencial), [])
            ids_unicos = {d.id for d, _ in candidatos}
            if len(ids_unicos) != 1:
                continue
            _d, no_doenca = candidatos[0]
            relacoes_novas += _registrar_relacao_estruturada(
                db,
                source=no_doenca,
                target=no_triagem,
                relation_type="differential_for",
                relevance_score=0.8,
                extra={"campo": "differentials", "valor": diferencial},
            )

    return ids_publicados, entidades_novas, relacoes_novas


def backfill_mesmo_tema(db: Session) -> dict:
    """Semeia o grafo a partir de metadado estruturado publicado.

    Mantém o nome histórico por compatibilidade da API, mas hoje executa duas
    etapas: `same_theme` nas frentes clássicas + conteúdo especializado
    (doença/triagem) com relações declaradas em metadado. Continua idempotente,
    auditável, reversível por publicação e sem inferência clínica por IA.
    """
    por_tema = _itens_por_tema(db)

    entidades_criadas = 0
    relacoes_criadas = 0

    for tema, itens in por_tema.items():
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

    ids_especializados, entidades_especializadas, relacoes_especializadas = (
        _semear_conteudo_especializado(db)
    )
    entidades_arquivadas = _arquivar_entidades_sem_conteudo_publicado_correspondente(
        db, por_tema, ids_publicados_adicionais=ids_especializados,
    )

    db.commit()
    return {
        "temas_processados": len(por_tema),
        "entidades_criadas_ou_atualizadas": entidades_criadas + entidades_especializadas,
        "relacoes_seed_tentadas": relacoes_criadas,
        "entidades_especializadas_criadas": entidades_especializadas,
        "relacoes_estruturadas_especializadas_criadas": relacoes_especializadas,
        "entidades_arquivadas": entidades_arquivadas,
    }


def _arquivar_entidades_sem_conteudo_publicado_correspondente(
    db: Session,
    por_tema: dict[str, list[_ItemTema]],
    *,
    ids_publicados_adicionais: dict[str, set[int]] | None = None,
) -> int:
    """Reconcilia publicação sem DELETE, inclusive doença e triagem."""
    ids_publicados_por_tipo: dict[str, set[int]] = {}
    for itens in por_tema.values():
        for item in itens:
            ids_publicados_por_tipo.setdefault(item.tipo, set()).add(item.id_origem)
    for tipo, ids in (ids_publicados_adicionais or {}).items():
        ids_publicados_por_tipo.setdefault(tipo, set()).update(ids)

    arquivadas = 0
    for tipo in TIPOS_ENTIDADE_PERMITIDOS:
        ids_validos = ids_publicados_por_tipo.get(tipo, set())
        todas = db.execute(
            select(KnowledgeEntity).where(KnowledgeEntity.entity_type == tipo)
        ).scalars().all()
        for entidade in todas:
            deveria_estar_ativa = entidade.canonical_id in ids_validos
            if deveria_estar_ativa and entidade.status != "ativo":
                entidade.status = "ativo"
            elif not deveria_estar_ativa and entidade.status == "ativo":
                entidade.status = "arquivado"
                arquivadas += 1
    return arquivadas


def relacionados_de(
    db: Session, *, entity_type: str, slug: str, limite_por_tipo: int = 5,
) -> dict | None:
    """Devolve relacionados ativos nas duas direções da aresta."""
    origem = db.execute(
        select(KnowledgeEntity).where(
            KnowledgeEntity.entity_type == entity_type,
            KnowledgeEntity.slug == slug,
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