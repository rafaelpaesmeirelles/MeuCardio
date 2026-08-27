"""Serviço do Grafo de Conhecimento Clínico Universal (issue #52, nova fase).

Responsabilidades deliberadamente separadas:

1. **Registro de entidade/relação** (`registrar_entidade`, `registrar_relacao`)
   — idempotente (upsert por chave única), nunca duplica nó nem aresta,
   rejeita estruturalmente qualquer `entity_type` fora do allowlist global.

2. **Backfill por tema** — registra `item -> tema` em O(N), usando o mesmo
   metadado/canonicalização de `theme`/`tema`, sem malha cartesiana.

3. **Backfill de referências explícitas e conteúdo especializado** — importa
   links editoriais, etapas, origens e relações já declaradas; registra doenças e triagens por
   sintoma publicadas e cria apenas relações já expressas em metadado
   estruturado: `related_document_slugs`, `patient_material_slug` e
   diferenciais cujo nome/alias casa exatamente com uma doença publicada.
   Não há inferência por similaridade de texto, embeddings ou IA.

4. **Consulta** (`relacionados_de`) — leitura agrupada por tipo, nas duas
   direções, filtrando conteúdo arquivado/rejeitado.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import unicodedata
from urllib.parse import unquote

from sqlalchemy import select, text
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
from app.services.topic_relevance import (
    SUPPORTED_DRUG_TOPICS,
    canonical_theme,
    drug_matches_theme,
)

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
    "tema": "/busca?modo=tudo-com-tudo",
}


class TipoEntidadeNaoPermitido(ValueError):
    """Levantado quando algo tenta registrar `entity_type` fora do allowlist."""


class BackfillEmAndamento(RuntimeError):
    """Levantado quando outra reconciliação já detém a trava transacional."""


def _rota_item(tipo: str, slug: str) -> str:
    if tipo == "tema":
        return f"/busca?modo=tudo-com-tudo&tema={slug}"
    if tipo == "medicamento":
        return f"/medicamentos?slug={slug}"
    if tipo in ("documento", "fluxograma"):
        return f"/biblioteca/{slug}"
    if tipo == "doenca":
        return f"/doencas/{slug}"
    if tipo == "triagem_sintoma":
        return f"/triagem-sintomas?slug={slug}"
    if tipo == "protocolo_emergencia":
        return f"/emergencia?protocolo={slug}"
    if tipo in ("checklist", "material_paciente"):
        return f"{ROTA_LISTA_POR_TIPO[tipo]}/{slug}"
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
    # Calculadoras não têm PK de tabela. Versões antigas usavam `hash(slug)`,
    # instável entre processos. Reaproveitar o nó lógico pelo slug migra o ID
    # no lugar e evita dois nós ativos para a mesma calculadora.
    if existente is None and entity_type == "calculadora":
        existente = db.execute(
            select(KnowledgeEntity).where(
                KnowledgeEntity.entity_type == entity_type,
                KnowledgeEntity.slug == slug,
            )
        ).scalars().first()
        if existente is not None:
            existente.canonical_id = canonical_id
    if existente:
        if existente.slug != slug or existente.title != title:
            existente.slug = slug
            existente.title = title
        # O chamador só registra conteúdo que acabou de confirmar como
        # publicado. Reativar antes de semear relações evita uma janela em que
        # `_entidade_por_slug()` ainda trataria o nó republicado como ausente.
        existente.status = "ativo"
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


_PRODUTOR_BACKFILL = "tudo_com_tudo_v2"
_ARQUIVO_RELACOES_EXPLICITAS = Path("/doencas/relacoes-explicitas.json")
_ARQUIVO_RELACOES_EXPLICITAS_FALLBACK = (
    Path(__file__).resolve().parents[3] / "doencas/relacoes-explicitas.json"
)
_ASSINATURAS_AUTOMATICAS_LEGADAS = {
    # campo: (verbo, tipos de origem, tipos de destino)
    "EvidenceRecord.document_slug": (
        "supported_by", {"documento", "fluxograma"}, {"evidencia"},
    ),
    "PatientMaterial.documento_slug": (
        "derived_from", {"material_paciente"}, {"documento", "fluxograma"},
    ),
    "DischargeChecklist.documento_origem": (
        "derived_from", {"checklist"}, {"documento", "fluxograma"},
    ),
    "EmergencyProtocol.documento_slug": (
        "derived_from", {"protocolo_emergencia"}, {"documento", "fluxograma"},
    ),
    "EmergencyProtocol.fluxograma_slug": (
        "uses_flowchart", {"protocolo_emergencia"}, {"fluxograma", "documento"},
    ),
    "EmergencyProtocol.relacionados": (
        "associated_with", {"protocolo_emergencia"},
        {"protocolo_emergencia", "documento", "fluxograma"},
    ),
    "StudyTrack.etapas": (
        "contains", {"trilha"}, {
            "documento", "fluxograma", "estudo", "medicamento", "checklist",
            "caso_clinico", "evidencia", "calculadora",
        },
    ),
    "Document.body_md.link": (
        "mentioned_in", {"documento", "fluxograma"}, {"documento", "fluxograma"},
    ),
    "medicamentos/interacoes.json.farmacos": (
        "interacts_with", {"medicamento"}, {"medicamento"},
    ),
    "related_document_slugs": (
        "mentioned_in", {"doenca"}, {"documento", "fluxograma"},
    ),
    "patient_material_slug": (
        "patient_education_for", {"material_paciente"}, {"doenca"},
    ),
    "differentials": (
        "differential_for", {"doenca"}, {"triagem_sintoma"},
    ),
    "SpecialtyDisease.area": (
        "belongs_to_topic", {"doenca"}, {"tema"},
    ),
    "SymptomTriageGuide.areas": (
        "belongs_to_topic", {"triagem_sintoma"}, {"tema"},
    ),
    "SpecialtyDisease.related_document_slugs|patient_material_slug": (
        "belongs_to_topic", {"doenca"}, {"tema"},
    ),
    "SymptomTriageGuide.differentials": (
        "belongs_to_topic", {"triagem_sintoma"}, {"tema"},
    ),
}
_CHAVES_EXTRA_GERENCIADAS = frozenset({
    "campo", "tema", "origem_slug", "destino_slug", "metadata_owner_slug",
    "declared_target_slug", "graph_source_slug", "graph_target_slug", "slug",
    "valor", "valor_original", "via_doenca", "destino_original", "item_type",
    "ordem", "por_que", "registro", "gravidade", "efeito", "conduta", "fonte",
})


@dataclass
class _LoteRelacoes:
    """Estado de uma reconciliação idempotente das arestas automáticas.

    Relações editoriais/manuais nunca são sobrescritas. Arestas produzidas
    por este backfill recebem uma impressão digital do metadado de origem;
    assim mudanças de ordem, justificativa, tema ou fonte são atualizadas e
    vínculos que desapareceram da fonte ficam rejeitados (não apagados),
    preservando a trilha de auditoria.
    """

    existentes: dict[tuple[int, int, str], KnowledgeRelation]
    desejadas: set[tuple[int, int, str]]


def _relacao_pertence_ao_backfill(relacao: KnowledgeRelation) -> bool:
    """Reconhece também arestas automáticas legadas por assinatura fechada."""
    extra = relacao.extra or {}
    produtor = extra.get("_producer")
    if produtor:
        return produtor == _PRODUTOR_BACKFILL
    campo = extra.get("campo")
    assinatura = _ASSINATURAS_AUTOMATICAS_LEGADAS.get(campo)
    if assinatura is None:
        # Primeira versão temática só gravava `{"tema": ...}`.
        if not (relacao.relation_type == "belongs_to_topic" and extra.get("tema")):
            return False
        return (
            relacao.source_entity.entity_type != "tema"
            and relacao.target_entity.entity_type == "tema"
            and relacao.provenance_type == "structured_metadata"
            and relacao.confidence == "derived"
        )
    verbo, origens, destinos = assinatura
    if relacao.relation_type != verbo:
        return False
    if (
        relacao.source_entity.entity_type not in origens
        or relacao.target_entity.entity_type not in destinos
    ):
        return False
    if campo == "medicamentos/interacoes.json.farmacos":
        return bool(
            relacao.evidence_source
            and relacao.evidence_source.startswith("medicamentos/interacoes.json#")
            and relacao.provenance_type == "editorial"
            and relacao.confidence == "explicit"
        )
    return relacao.provenance_type == "structured_metadata" and relacao.confidence == "derived"


def _id_estavel(namespace: str, valor: str) -> int:
    """ID inteiro determinístico para registros sem PK persistida própria.

    `hash()` do Python muda entre processos. Isso fazia a mesma calculadora
    ganhar outro `canonical_id` após um restart e podia duplicar nós. SHA-256
    mantém o ID estável; o namespace separa temas de calculadoras.
    """
    digest = hashlib.sha256(f"{namespace}:{valor}".encode("utf-8")).digest()
    return int.from_bytes(digest[:4], "big") & 0x7FFF_FFFF


def _slug_tema(tema: str) -> str:
    decomposed = unicodedata.normalize("NFKD", tema)
    ascii_value = "".join(c for c in decomposed if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "-", ascii_value.casefold()).strip("-")


def _itens_por_tema(
    db: Session,
) -> tuple[dict[str, list[_ItemTema]], list[_ItemTema]]:
    """Inventaria todos os publicados e agrupa por tema quando disponível."""
    por_tema: dict[str, list[_ItemTema]] = {}
    publicados: dict[tuple[str, int], _ItemTema] = {}

    def _add(tema: str | None, item: _ItemTema) -> None:
        publicados[(item.tipo, item.id_origem)] = item
        tema = canonical_theme(tema)
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
        # Indicações revisadas podem sustentar mais de um contexto clínico.
        # A mesma regra conservadora já usada pelo painel Tudo com Tudo é
        # reaproveitada aqui; texto livre/fuzzy não cria associação.
        for tema in SUPPORTED_DRUG_TOPICS:
            if drug_matches_theme(d, tema):
                _add(tema, _ItemTema("medicamento", d.id, d.slug, d.generic_name))

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
                "calculadora", _id_estavel("calculadora", c.slug), c.slug, c.name,
            ))

    prot_q = (
        select(EmergencyProtocol, Document.theme)
        .outerjoin(
            Document,
            (Document.slug == EmergencyProtocol.documento_slug)
            & Document.published.is_(True),
        )
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

    return por_tema, list(publicados.values())


def _normalizar_chave_clinica(valor: str) -> str:
    """Normalização conservadora para casamento EXATO de nome/alias.

    Remove apenas diferenças ortográficas superficiais (caixa, acento e
    espaços). Não faz stemming, fuzzy matching, embeddings nem aproximação
    semântica — uma relação clínica não nasce porque duas strings 'parecem'.
    """
    decomposed = unicodedata.normalize("NFKD", valor or "")
    sem_acentos = "".join(c for c in decomposed if not unicodedata.combining(c))
    return " ".join(sem_acentos.casefold().strip().split())


TOPICOS_POR_AREA_ESPECIALIZADA = {
    "geral": "Geral",
    "cardiopediatria": "Cardiologia pediátrica",
    "cardiogeriatria": "Cardiologia geriátrica",
    "cardiooncologia": "Cardio-oncologia",
    "gravidez": "Gravidez",
}

RELACOES_PENDENTES_PUBLICAVEIS = frozenset({
    # Somente navegação/taxonomia. Qualquer tipo novo fica oculto enquanto
    # pendente por padrão, evitando vazamento acidental de afirmação clínica.
    "belongs_to_topic", "same_theme", "derived_from", "uses_flowchart",
    "contains", "mentioned_in",
})


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
            KnowledgeEntity.status == "ativo",
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
    lote: _LoteRelacoes | None = None,
    provenance_type: str = "structured_metadata",
    confidence: str = "derived",
    review_status: str = "pendente_revisao",
    evidence_source: str | None = None,
) -> int:
    """Reconcilia aresta derivada e devolve 1 somente quando ela é nova."""
    if source.id == target.id:
        return 0
    if relation_type not in TIPOS_RELACAO_PERMITIDOS:
        raise ValueError(f"relation_type={relation_type!r} fora do catálogo permitido.")
    if provenance_type not in TIPOS_PROVENIENCIA_PERMITIDOS:
        raise ValueError(f"provenance_type={provenance_type!r} fora do catálogo permitido.")
    if confidence not in NIVEIS_CONFIANCA_PERMITIDOS:
        raise ValueError(f"confidence={confidence!r} fora do catálogo permitido.")
    if review_status not in REVIEW_STATUS_RELACAO_PERMITIDOS:
        raise ValueError(f"review_status={review_status!r} fora do catálogo permitido.")

    chave = (source.id, target.id, relation_type)
    metadados = dict(extra)
    if "origem_slug" in metadados:
        metadados.setdefault("metadata_owner_slug", metadados["origem_slug"])
    if "destino_slug" in metadados:
        metadados.setdefault("declared_target_slug", metadados["destino_slug"])
    conteudo_fingerprint = {
        "source": source.slug,
        "target": target.slug,
        "relation_type": relation_type,
        "provenance_type": provenance_type,
        "confidence": confidence,
        "relevance_score": relevance_score,
        "evidence_source": evidence_source,
        "extra": metadados,
    }
    fingerprint = hashlib.sha256(
        json.dumps(
            conteudo_fingerprint, ensure_ascii=False, sort_keys=True, default=str,
        ).encode("utf-8")
    ).hexdigest()
    metadados.update({
        "_producer": _PRODUTOR_BACKFILL,
        "_fingerprint": fingerprint,
        "graph_source_slug": source.slug,
        "graph_target_slug": target.slug,
    })

    if lote is not None:
        lote.desejadas.add(chave)
        existente = lote.existentes.get(chave)
        if existente is not None:
            extra_existente = existente.extra or {}
            # Curadoria/manual vence o gerador. Relações deste produtor são
            # atualizadas somente quando sua fonte estruturada mudou ou foram
            # desativadas por uma rodada anterior.
            if _relacao_pertence_ao_backfill(existente):
                era_legada = not extra_existente.get("_producer")
                fonte_mudou = extra_existente.get("_fingerprint") != fingerprint
                estava_inativa = extra_existente.get("_inactive_reason") == "source_removed"
                if fonte_mudou or estava_inativa:
                    status_anterior = existente.review_status
                    existente.provenance_type = provenance_type
                    existente.confidence = confidence
                    existente.relevance_score = relevance_score
                    existente.evidence_source = evidence_source
                    existente.review_status = (
                        status_anterior
                        if (
                            (era_legada and status_anterior in {"revisado", "rejeitado"})
                            or (status_anterior == "rejeitado" and not estava_inativa)
                        )
                        else review_status
                    )
                    # Preserve anotações editoriais que não pertencem ao
                    # snapshot automático. Chaves internas e campos de fonte
                    # são reconstruídos pelo produtor para evitar resíduos.
                    curadoria = {
                        chave_extra: valor_extra
                        for chave_extra, valor_extra in extra_existente.items()
                        if (
                            chave_extra not in _CHAVES_EXTRA_GERENCIADAS
                            and (
                                not chave_extra.startswith("_")
                                or (
                                    chave_extra == "_inactive_reason"
                                    and valor_extra != "source_removed"
                                )
                            )
                        )
                    }
                    existente.extra = {**curadoria, **metadados}
            return 0

        relacao = KnowledgeRelation(
            source_entity_id=source.id,
            target_entity_id=target.id,
            relation_type=relation_type,
            provenance_type=provenance_type,
            confidence=confidence,
            relevance_score=relevance_score,
            evidence_source=evidence_source,
            review_status=review_status,
            extra=metadados,
        )
        db.add(relacao)
        lote.existentes[chave] = relacao
        return 1

    existia = _relacao_ja_existe(db, source, target, relation_type)
    registrar_relacao(
        db,
        source=source,
        target=target,
        relation_type=relation_type,
        provenance_type=provenance_type,
        confidence=confidence,
        relevance_score=relevance_score,
        evidence_source=evidence_source,
        review_status=review_status,
        extra=metadados,
    )
    return 0 if existia else 1


def _rejeitar_relacoes_automaticas_ausentes(lote: _LoteRelacoes) -> int:
    """Desativa, sem apagar, arestas do produtor ausentes na fonte atual."""
    rejeitadas = 0
    for chave, relacao in lote.existentes.items():
        extra = relacao.extra or {}
        if chave in lote.desejadas or not _relacao_pertence_ao_backfill(relacao):
            continue
        # Uma rejeição humana existente não pode ser convertida em rejeição
        # automática, pois isso permitiria reativá-la quando a fonte voltasse.
        if relacao.review_status == "rejeitado":
            continue
        relacao.review_status = "rejeitado"
        relacao.extra = {
            **extra,
            "_producer": _PRODUTOR_BACKFILL,
            "_inactive_reason": "source_removed",
        }
        rejeitadas += 1
    return rejeitadas


_LINK_MARKDOWN = re.compile(r"(?<!!)\[[^\]]+\]\(([^)\s]+)\)")
_BLOCO_CODIGO_MARKDOWN = re.compile(r"```.*?```|~~~.*?~~~", re.DOTALL)
_CODIGO_INLINE_MARKDOWN = re.compile(r"`[^`\n]*`")
_ESQUEMA_URL = re.compile(r"^[a-z][a-z0-9+.-]*:", re.IGNORECASE)


def _markdown_sem_codigo(corpo: str) -> str:
    return _CODIGO_INLINE_MARKDOWN.sub("", _BLOCO_CODIGO_MARKDOWN.sub("", corpo))


def _slug_de_link_markdown(destino: str) -> str | None:
    """Extrai somente links internos inequívocos da Biblioteca."""
    caminho = unquote(destino).split("#", 1)[0].split("?", 1)[0].strip()
    if _ESQUEMA_URL.match(caminho) or caminho.startswith("//"):
        return None
    if caminho.startswith("/biblioteca/"):
        return caminho.removeprefix("/biblioteca/").strip("/") or None
    if caminho.casefold().endswith(".md"):
        return caminho.rsplit("/", 1)[-1][:-3] or None
    return None


def _registrar_referencias_explicitas(
    db: Session,
    *,
    lote: _LoteRelacoes,
    entidades_por_slug: dict[tuple[str, str], KnowledgeEntity],
) -> tuple[int, list[dict]]:
    """Transforma referências editoriais já publicadas em arestas auditáveis.

    Todos os vínculos vêm de slug/campo explícito. Texto clínico, similaridade,
    embeddings e LLM não participam deste caminho.
    """
    criadas = 0
    nao_resolvidas: list[dict] = []

    def _no(tipos: tuple[str, ...], slug: str | None) -> KnowledgeEntity | None:
        if not slug:
            return None
        return next(
            (entidades_por_slug.get((tipo, slug)) for tipo in tipos
             if entidades_por_slug.get((tipo, slug)) is not None),
            None,
        )

    def _ligar(
        source: KnowledgeEntity | None,
        target: KnowledgeEntity | None,
        relation_type: str,
        *,
        score: float,
        extra: dict,
    ) -> None:
        nonlocal criadas
        if source is None or target is None:
            nao_resolvidas.append(extra)
            return
        criadas += _registrar_relacao_estruturada(
            db,
            source=source,
            target=target,
            relation_type=relation_type,
            relevance_score=score,
            extra=extra,
            lote=lote,
        )

    # Documento -> evidência: o campo da evidência aponta para a análise da
    # Biblioteca que ela sustenta. A direção segue o verbo `supported_by`.
    evidencias = db.execute(
        select(EvidenceRecord).where(EvidenceRecord.published.is_(True))
    ).scalars().all()
    for evidencia in evidencias:
        if not evidencia.document_slug:
            continue
        _ligar(
            _no(("documento", "fluxograma"), evidencia.document_slug),
            _no(("evidencia",), evidencia.slug),
            "supported_by",
            score=0.95,
            extra={
                "campo": "EvidenceRecord.document_slug",
                "origem_slug": evidencia.slug,
                "destino_slug": evidencia.document_slug,
            },
        )

    for material in db.execute(
        select(PatientMaterial).where(PatientMaterial.published.is_(True))
    ).scalars():
        if material.documento_slug:
            _ligar(
                _no(("material_paciente",), material.slug),
                _no(("documento", "fluxograma"), material.documento_slug),
                "derived_from",
                score=0.95,
                extra={
                    "campo": "PatientMaterial.documento_slug",
                    "origem_slug": material.slug,
                    "destino_slug": material.documento_slug,
                },
            )

    for checklist in db.execute(
        select(DischargeChecklist).where(DischargeChecklist.published.is_(True))
    ).scalars():
        if checklist.documento_origem:
            _ligar(
                _no(("checklist",), checklist.slug),
                _no(("documento", "fluxograma"), checklist.documento_origem),
                "derived_from",
                score=0.95,
                extra={
                    "campo": "DischargeChecklist.documento_origem",
                    "origem_slug": checklist.slug,
                    "destino_slug": checklist.documento_origem,
                },
            )

    protocolos = db.execute(
        select(EmergencyProtocol).where(EmergencyProtocol.published.is_(True))
    ).scalars().all()
    for protocolo in protocolos:
        no_protocolo = _no(("protocolo_emergencia",), protocolo.slug)
        _ligar(
            no_protocolo,
            _no(("documento", "fluxograma"), protocolo.documento_slug),
            "derived_from",
            score=1.0,
            extra={
                "campo": "EmergencyProtocol.documento_slug",
                "origem_slug": protocolo.slug,
                "destino_slug": protocolo.documento_slug,
            },
        )
        if protocolo.fluxograma_slug:
            _ligar(
                no_protocolo,
                _no(("fluxograma", "documento"), protocolo.fluxograma_slug),
                "uses_flowchart",
                score=1.0,
                extra={
                    "campo": "EmergencyProtocol.fluxograma_slug",
                    "origem_slug": protocolo.slug,
                    "destino_slug": protocolo.fluxograma_slug,
                },
            )
        for slug in dict.fromkeys(protocolo.relacionados or []):
            _ligar(
                no_protocolo,
                _no(("protocolo_emergencia", "documento", "fluxograma"), slug),
                "associated_with",
                score=0.9,
                extra={
                    "campo": "EmergencyProtocol.relacionados",
                    "origem_slug": protocolo.slug,
                    "destino_slug": slug,
                },
            )

    tipos_etapa = {
        "documento": ("documento", "fluxograma"),
        "estudo": ("estudo",),
        "medicamento": ("medicamento",),
        "checklist": ("checklist",),
        "caso_clinico": ("caso_clinico",),
        "evidencia": ("evidencia",),
        "calculadora": ("calculadora",),
    }
    for trilha in db.execute(
        select(StudyTrack).where(StudyTrack.published.is_(True))
    ).scalars():
        no_trilha = _no(("trilha",), trilha.slug)
        for etapa in trilha.etapas or []:
            if not isinstance(etapa, dict):
                continue
            tipo = str(etapa.get("item_type") or "")
            slug = str(etapa.get("item_slug") or "")
            tipos = tipos_etapa.get(tipo)
            if not tipos or not slug:
                nao_resolvidas.append({
                    "campo": "StudyTrack.etapas",
                    "origem_slug": trilha.slug,
                    "destino_slug": slug,
                    "item_type": tipo,
                })
                continue
            _ligar(
                no_trilha,
                _no(tipos, slug),
                "contains",
                score=0.98,
                extra={
                    "campo": "StudyTrack.etapas",
                    "origem_slug": trilha.slug,
                    "destino_slug": slug,
                    "ordem": etapa.get("ordem"),
                    "por_que": etapa.get("por_que"),
                },
            )

    # Links Markdown são atos editoriais explícitos. A direção segue o verbo:
    # o conteúdo alvo está `mentioned_in` no documento de origem.
    documentos = db.execute(
        select(Document).where(Document.published.is_(True))
    ).scalars().all()
    for documento in documentos:
        no_origem = _no(
            ("fluxograma",) if documento.kind == "fluxograma" else ("documento",),
            documento.slug,
        )
        for destino in _LINK_MARKDOWN.findall(_markdown_sem_codigo(documento.body_md or "")):
            slug = _slug_de_link_markdown(destino)
            if not slug:
                continue
            _ligar(
                _no(("documento", "fluxograma"), slug),
                no_origem,
                "mentioned_in",
                score=0.9,
                extra={
                    "campo": "Document.body_md.link",
                    "origem_slug": documento.slug,
                    "destino_slug": slug,
                    "destino_original": destino,
                },
            )

    # O arquivo curado distingue pares nominais de alertas por classe e de
    # interações ternárias/contextuais. Somente os registros revisados com
    # EXATAMENTE dois slugs viram `interacts_with`, mesma regra da API.
    arquivo_interacoes = Path("/medicamentos/interacoes.json")
    if not arquivo_interacoes.is_file():
        arquivo_interacoes = Path(__file__).resolve().parents[3] / "medicamentos/interacoes.json"
    try:
        interacoes = json.loads(arquivo_interacoes.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(
            f"Fonte curada de interações indisponível ou inválida: {arquivo_interacoes}"
        ) from exc
    if not isinstance(interacoes, list):
        raise RuntimeError(f"Fonte curada de interações não é uma lista: {arquivo_interacoes}")
    for interacao in interacoes:
        if not isinstance(interacao, dict):
            continue
        farmacos = interacao.get("farmacos") or []
        if len(farmacos) != 2 or interacao.get("review_status") != "revisado":
            continue
        slug_a, slug_b = sorted(str(slug) for slug in farmacos)
        source = _no(("medicamento",), slug_a)
        target = _no(("medicamento",), slug_b)
        # Testes/instalações parciais podem não ter carregado nenhum dos
        # fármacos. Um par parcialmente resolvido, porém, é erro real.
        if source is None and target is None:
            continue
        if source is None or target is None:
            nao_resolvidas.append({
                "campo": "medicamentos/interacoes.json.farmacos",
                "origem_slug": slug_a,
                "destino_slug": slug_b,
                "registro": interacao.get("slug"),
            })
            continue
        criadas += _registrar_relacao_estruturada(
            db,
            source=source,
            target=target,
            relation_type="interacts_with",
            relevance_score=1.0,
            extra={
                "campo": "medicamentos/interacoes.json.farmacos",
                "registro": interacao.get("slug"),
                "gravidade": interacao.get("gravidade"),
                "efeito": interacao.get("efeito"),
                "conduta": interacao.get("conduta"),
                "fonte": interacao.get("fonte"),
            },
            lote=lote,
            provenance_type="editorial",
            confidence="explicit",
            review_status="revisado",
            evidence_source=f"medicamentos/interacoes.json#{interacao.get('slug')}",
        )

    return criadas, nao_resolvidas


def _carregar_manifesto_relacoes_explicitas() -> list[dict]:
    """Lê e valida o manifesto de arestas curadas doença -> coleção.

    O manifesto é deliberadamente pequeno e estrito: ele não descobre nem
    infere relações. Cada aresta declara os dois slugs, o verbo, a decisão de
    revisão e sua proveniência. Erros de schema interrompem a reconciliação;
    referências a conteúdo ausente/despublicado são relatadas pelo backfill e
    não viram aresta pública.
    """
    caminho = (
        _ARQUIVO_RELACOES_EXPLICITAS
        if _ARQUIVO_RELACOES_EXPLICITAS.is_file()
        else _ARQUIVO_RELACOES_EXPLICITAS_FALLBACK
    )
    try:
        payload = json.loads(caminho.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(
            f"Manifesto de relações explícitas indisponível ou inválido: {caminho}"
        ) from exc
    if not isinstance(payload, list):
        raise RuntimeError(f"Manifesto de relações explícitas deve ser lista: {caminho}")

    campos_texto = (
        "source_disease_slug", "target_type", "target_slug", "relation_type",
        "review_status", "provenance_type", "confidence",
    )
    vistos: set[tuple[str, str, str, str]] = set()
    for indice, item in enumerate(payload):
        if not isinstance(item, dict):
            raise RuntimeError(f"Relação explícita #{indice} não é objeto JSON.")
        ausentes = [
            campo for campo in campos_texto
            if not isinstance(item.get(campo), str) or not item[campo].strip()
        ]
        if ausentes:
            raise RuntimeError(
                f"Relação explícita #{indice} tem campos ausentes/inválidos: {ausentes}"
            )
        if item["target_type"] not in TIPOS_ENTIDADE_PERMITIDOS - {"tema", "doenca"}:
            raise RuntimeError(
                f"Relação explícita #{indice}: target_type não permitido: "
                f"{item['target_type']!r}"
            )
        if item["relation_type"] not in TIPOS_RELACAO_PERMITIDOS:
            raise RuntimeError(
                f"Relação explícita #{indice}: relation_type não permitido: "
                f"{item['relation_type']!r}"
            )
        if item["review_status"] not in REVIEW_STATUS_RELACAO_PERMITIDOS:
            raise RuntimeError(
                f"Relação explícita #{indice}: review_status não permitido: "
                f"{item['review_status']!r}"
            )
        if item["provenance_type"] not in TIPOS_PROVENIENCIA_PERMITIDOS:
            raise RuntimeError(
                f"Relação explícita #{indice}: provenance_type não permitido: "
                f"{item['provenance_type']!r}"
            )
        if item["confidence"] not in NIVEIS_CONFIANCA_PERMITIDOS:
            raise RuntimeError(
                f"Relação explícita #{indice}: confidence não permitido: "
                f"{item['confidence']!r}"
            )
        chave = (
            item["source_disease_slug"], item["target_type"],
            item["target_slug"], item["relation_type"],
        )
        if chave in vistos:
            raise RuntimeError(f"Relação explícita duplicada: {chave!r}")
        vistos.add(chave)
    return payload


def _registrar_relacoes_explicitas_de_doenca(
    db: Session,
    *,
    lote: _LoteRelacoes,
    entidades_por_slug: dict[tuple[str, str], KnowledgeEntity],
    publicados_por_slug: set[tuple[str, str]],
) -> tuple[int, list[dict]]:
    """Importa somente arestas curadas cujos dois extremos estão publicados.

    A checagem usa o inventário da rodada atual, e não apenas o status antigo
    do nó. Isso evita uma janela de publicação quando a doença foi devolvida a
    ``pendente_revisao`` no mesmo reconcile e seu nó ainda não foi arquivado.
    A consulta do grafo já percorre entrada e saída, portanto uma aresta única
    garante navegação bidirecional sem duplicar a afirmação clínica.
    """
    criadas = 0
    nao_resolvidas: list[dict] = []
    for item in _carregar_manifesto_relacoes_explicitas():
        source_key = ("doenca", item["source_disease_slug"])
        target_key = (item["target_type"], item["target_slug"])
        extra_base = {
            "campo": "doencas/relacoes-explicitas.json",
            "origem_slug": item["source_disease_slug"],
            "destino_slug": item["target_slug"],
            "target_type": item["target_type"],
            "review_note": item.get("review_note"),
        }
        if source_key not in publicados_por_slug:
            nao_resolvidas.append({**extra_base, "motivo": "doenca_nao_publicada"})
            continue
        if target_key not in publicados_por_slug:
            nao_resolvidas.append({**extra_base, "motivo": "destino_nao_publicado"})
            continue
        source = entidades_por_slug.get(source_key)
        target = entidades_por_slug.get(target_key)
        if source is None or target is None:
            nao_resolvidas.append({**extra_base, "motivo": "no_ativo_ausente"})
            continue
        criadas += _registrar_relacao_estruturada(
            db,
            source=source,
            target=target,
            relation_type=item["relation_type"],
            relevance_score=float(item.get("relevance_score", 1.0)),
            extra=extra_base,
            lote=lote,
            provenance_type=item["provenance_type"],
            confidence=item["confidence"],
            review_status=item["review_status"],
            evidence_source=item.get("evidence_source")
            or (
                "doencas/relacoes-explicitas.json#"
                f"{item['source_disease_slug']}:{item['target_type']}:{item['target_slug']}"
            ),
        )
    return criadas, nao_resolvidas


def _semear_conteudo_especializado(
    db: Session,
    *,
    lote: _LoteRelacoes | None = None,
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
    topicos_por_doenca: dict[int, set[KnowledgeEntity]] = {}

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
        topicos_da_doenca: dict[int, KnowledgeEntity] = {}
        titulo_area = TOPICOS_POR_AREA_ESPECIALIZADA.get(d.area)
        if titulo_area:
            no_tema_area = _entidade_por_slug(
                db, tipos=("tema",), slug=_slug_tema(titulo_area),
            )
            if no_tema_area is None:
                raise RuntimeError(f"Tema canônico ausente para SpecialtyDisease.area={d.area!r}")
            topicos_da_doenca[no_tema_area.id] = no_tema_area
            relacoes_novas += _registrar_relacao_estruturada(
                db,
                source=no_doenca,
                target=no_tema_area,
                relation_type="belongs_to_topic",
                relevance_score=0.35,
                extra={
                    "tema": titulo_area,
                    "campo": "SpecialtyDisease.area",
                    "valor_original": d.area,
                },
                lote=lote,
            )
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
                lote=lote,
            )
            for relacao_tema, no_tema in db.execute(
                select(KnowledgeRelation, KnowledgeEntity)
                .join(
                    KnowledgeEntity,
                    KnowledgeEntity.id == KnowledgeRelation.target_entity_id,
                )
                .where(
                    KnowledgeRelation.source_entity_id == no_doc.id,
                    KnowledgeRelation.relation_type == "belongs_to_topic",
                    KnowledgeEntity.entity_type == "tema",
                    KnowledgeEntity.status == "ativo",
                )
            ).all():
                topicos_da_doenca[no_tema.id] = no_tema

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
                    lote=lote,
                )
                for _relacao_tema, no_tema in db.execute(
                    select(KnowledgeRelation, KnowledgeEntity)
                    .join(
                        KnowledgeEntity,
                        KnowledgeEntity.id == KnowledgeRelation.target_entity_id,
                    )
                    .where(
                        KnowledgeRelation.source_entity_id == no_material.id,
                        KnowledgeRelation.relation_type == "belongs_to_topic",
                        KnowledgeEntity.entity_type == "tema",
                        KnowledgeEntity.status == "ativo",
                    )
                ).all():
                    topicos_da_doenca[no_tema.id] = no_tema

        # Tema herdado apenas de um vínculo explícito já existente. Não há
        # classificação textual do nome/resumo da doença.
        topicos_por_doenca[d.id] = set(topicos_da_doenca.values())
        for no_tema in topicos_da_doenca.values():
            relacoes_novas += _registrar_relacao_estruturada(
                db,
                source=no_doenca,
                target=no_tema,
                relation_type="belongs_to_topic",
                relevance_score=0.35,
                extra={
                    "tema": no_tema.title,
                    "campo": "SpecialtyDisease.related_document_slugs|patient_material_slug",
                },
                lote=lote,
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
        for area in dict.fromkeys(t.areas or []):
            titulo_area = TOPICOS_POR_AREA_ESPECIALIZADA.get(area)
            if not titulo_area:
                continue
            no_tema_area = _entidade_por_slug(
                db, tipos=("tema",), slug=_slug_tema(titulo_area),
            )
            if no_tema_area is None:
                raise RuntimeError(
                    f"Tema canônico ausente para SymptomTriageGuide.areas={area!r}"
                )
            relacoes_novas += _registrar_relacao_estruturada(
                db,
                source=no_triagem,
                target=no_tema_area,
                relation_type="belongs_to_topic",
                relevance_score=0.35,
                extra={
                    "tema": titulo_area,
                    "campo": "SymptomTriageGuide.areas",
                    "valor_original": area,
                },
                lote=lote,
            )
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
                lote=lote,
            )
            for no_tema in topicos_por_doenca.get(_d.id, set()):
                relacoes_novas += _registrar_relacao_estruturada(
                    db,
                    source=no_triagem,
                    target=no_tema,
                    relation_type="belongs_to_topic",
                    relevance_score=0.35,
                    extra={
                        "tema": no_tema.title,
                        "campo": "SymptomTriageGuide.differentials",
                        "via_doenca": _d.slug,
                    },
                    lote=lote,
                )

    return ids_publicados, entidades_novas, relacoes_novas


def backfill_mesmo_tema(db: Session, *, commit: bool = True) -> dict:
    """Semeia o grafo a partir de metadado estruturado publicado.

    Mantém o nome histórico por compatibilidade da API, mas hoje executa três
    etapas: associação linear a temas, importação de referências explícitas e
    conteúdo especializado (doença/triagem). Continua idempotente, auditável,
    reversível por publicação e sem inferência clínica por IA.
    """
    bind = db.get_bind()
    if bind.dialect.name == "postgresql":
        # Uma reconciliação por vez: evita duas sessões criarem a mesma chave
        # entre o SELECT inicial e o flush apesar da restrição UNIQUE.
        obteve_trava = db.execute(text(
            "SELECT pg_try_advisory_xact_lock(:namespace, :operation)"
        ), {"namespace": 0x436F7256, "operation": 2}).scalar_one()
        if not obteve_trava:
            raise BackfillEmAndamento("Outra reconciliação do Tudo com Tudo está em andamento.")

    por_tema, itens_publicados = _itens_por_tema(db)
    # Áreas estruturadas de doença/triagem também são temas canônicos, mesmo
    # que nesta instalação não haja outro tipo de conteúdo naquele tema.
    for tema in TOPICOS_POR_AREA_ESPECIALIZADA.values():
        por_tema.setdefault(tema, [])

    entidades_criadas = 0
    relacoes_tema_criadas = 0

    # Registra cada item uma só vez, mesmo quando possui múltiplos temas (caso
    # dos medicamentos). Depois cria um nó canônico por tema e uma associação
    # item -> tema. Assim todos participam sem malha cartesiana.
    nos_por_origem: dict[tuple[str, int], KnowledgeEntity] = {}
    entidades_atuais = db.execute(select(KnowledgeEntity)).scalars().all()
    existentes_por_origem = {
        (entidade.entity_type, entidade.canonical_id): entidade
        for entidade in entidades_atuais
    }
    calculadoras_duplicadas_arquivadas = 0
    relacoes_manuais_calculadora_migradas = 0
    calculadora_canonica_por_id: dict[int, int] = {}
    calculadoras_agrupadas: dict[str, list[KnowledgeEntity]] = {}
    for entidade in entidades_atuais:
        if entidade.entity_type == "calculadora":
            calculadoras_agrupadas.setdefault(entidade.slug, []).append(entidade)
    calculadoras_por_slug: dict[str, KnowledgeEntity] = {}
    for slug, entidades in calculadoras_agrupadas.items():
        id_canonico = _id_estavel("calculadora", slug)
        canonicas = [e for e in entidades if e.canonical_id == id_canonico]
        manter = min(canonicas or entidades, key=lambda e: e.id)
        if manter.canonical_id != id_canonico:
            colisao = existentes_por_origem.get(("calculadora", id_canonico))
            if colisao is not None and colisao.id != manter.id:
                raise RuntimeError(f"Colisão de canonical_id de calculadora: {slug}")
            existentes_por_origem.pop(("calculadora", manter.canonical_id), None)
            manter.canonical_id = id_canonico
            existentes_por_origem[("calculadora", id_canonico)] = manter
        calculadoras_por_slug[slug] = manter
        for duplicada in entidades:
            if duplicada.id != manter.id and duplicada.status != "arquivado":
                duplicada.status = "arquivado"
                calculadoras_duplicadas_arquivadas += 1
            if duplicada.id == manter.id:
                continue
            calculadora_canonica_por_id[duplicada.id] = manter.id

    def _upsert_no(tipo: str, canonical_id: int, slug: str, titulo: str) -> KnowledgeEntity:
        nonlocal entidades_criadas
        chave = (tipo, canonical_id)
        entidade = existentes_por_origem.get(chave)
        if entidade is None and tipo == "calculadora":
            # Migra no lugar o ID legado baseado em `hash()`.
            entidade = calculadoras_por_slug.get(slug)
            if entidade is not None:
                existentes_por_origem.pop((tipo, entidade.canonical_id), None)
                entidade.canonical_id = canonical_id
                existentes_por_origem[chave] = entidade
        if entidade is None:
            entidade = KnowledgeEntity(
                entity_type=tipo,
                canonical_id=canonical_id,
                slug=slug,
                title=titulo,
                status="ativo",
            )
            db.add(entidade)
            existentes_por_origem[chave] = entidade
            entidades_criadas += 1
        else:
            entidade.slug = slug
            entidade.title = titulo
            entidade.status = "ativo"
        return entidade

    # O inventário de nós não depende de taxonomia: conteúdo publicado sem
    # tema continua referenciável e nunca é arquivado apenas por esse motivo.
    for item in itens_publicados:
        chave = (item.tipo, item.id_origem)
        nos_por_origem[chave] = _upsert_no(
            item.tipo, item.id_origem, item.slug, item.titulo,
        )

    ids_tema: dict[int, str] = {}
    ids_publicados_tema: set[int] = set()
    for tema, itens in por_tema.items():
        id_tema = _id_estavel("tema", tema)
        outro = ids_tema.setdefault(id_tema, tema)
        if outro != tema:
            raise RuntimeError(f"Colisão de ID entre temas {outro!r} e {tema!r}")
        ids_publicados_tema.add(id_tema)

        chave_tema = ("tema", id_tema)
        no_tema = nos_por_origem.get(chave_tema)
        if no_tema is None:
            no_tema = _upsert_no("tema", id_tema, _slug_tema(tema), tema)
            nos_por_origem[chave_tema] = no_tema

        for item in itens:
            chave = (item.tipo, item.id_origem)
            entidade = nos_por_origem[chave]

    db.flush()
    entidades_por_slug = {
        (entidade.entity_type, entidade.slug): entidade
        for entidade in db.execute(
            select(KnowledgeEntity).where(KnowledgeEntity.status == "ativo")
        ).scalars()
    }
    relacoes_atuais = db.execute(select(KnowledgeRelation)).scalars().all()
    relacoes_por_chave = {
        (rel.source_entity_id, rel.target_entity_id, rel.relation_type): rel
        for rel in relacoes_atuais
    }

    # Depois de conhecer todas as duplicatas, transforma os dois endpoints de
    # uma só vez. Isso cobre inclusive uma relação duplicadaA -> duplicadaB e
    # evita o custo O(duplicatas × arestas) da migração histórica.
    for relacao in list(relacoes_atuais):
        if (
            relacao.source_entity_id not in calculadora_canonica_por_id
            and relacao.target_entity_id not in calculadora_canonica_por_id
        ):
            continue
        if _relacao_pertence_ao_backfill(relacao):
            continue
        novo_source = calculadora_canonica_por_id.get(
            relacao.source_entity_id, relacao.source_entity_id,
        )
        novo_target = calculadora_canonica_por_id.get(
            relacao.target_entity_id, relacao.target_entity_id,
        )
        if novo_source == novo_target:
            continue
        nova_chave = (novo_source, novo_target, relacao.relation_type)
        existente = relacoes_por_chave.get(nova_chave)
        extra_migrado = {
            **(relacao.extra or {}),
            "_migrated_from_entity_ids": sorted({
                entidade_id
                for entidade_id in (
                    relacao.source_entity_id, relacao.target_entity_id,
                )
                if entidade_id in calculadora_canonica_por_id
            }),
        }
        criada = existente is None
        if existente is None:
            existente = KnowledgeRelation(
                source_entity_id=novo_source,
                target_entity_id=novo_target,
                relation_type=relacao.relation_type,
            )
            db.add(existente)
            relacoes_atuais.append(existente)
            relacoes_por_chave[nova_chave] = existente

        # Um candidato manual substitui o vínculo canônico apenas quando ele
        # ainda é automático e não recebeu decisão humana. Relação revisada,
        # ou rejeitada sem o marcador automático `source_removed`, vence
        # sempre — inclusive quando ainda carrega `_producer` para auditoria.
        extra_existente = existente.extra or {}
        automatica_substituivel = (
            _relacao_pertence_ao_backfill(existente)
            and (
                existente.review_status == "pendente_revisao"
                or (
                    existente.review_status == "rejeitado"
                    and extra_existente.get("_inactive_reason") == "source_removed"
                )
            )
        )
        atualizou = criada or automatica_substituivel
        if atualizou:
            existente.relevance_score = relacao.relevance_score
            existente.confidence = relacao.confidence
            existente.provenance_type = relacao.provenance_type
            existente.evidence_source = relacao.evidence_source
            existente.review_status = relacao.review_status
            existente.extra = extra_migrado
            relacoes_manuais_calculadora_migradas += 1

    db.flush()
    lote = _LoteRelacoes(
        existentes=relacoes_por_chave,
        desejadas=set(),
    )

    for tema, itens in por_tema.items():
        no_tema = nos_por_origem[("tema", _id_estavel("tema", tema))]
        for item in itens:
            relacoes_tema_criadas += _registrar_relacao_estruturada(
                db,
                source=nos_por_origem[(item.tipo, item.id_origem)],
                target=no_tema,
                relation_type="belongs_to_topic",
                relevance_score=0.35,
                extra={"tema": tema},
                lote=lote,
            )

    db.flush()
    relacoes_explicitas, referencias_nao_resolvidas = _registrar_referencias_explicitas(
        db,
        lote=lote,
        entidades_por_slug=entidades_por_slug,
    )

    ids_especializados, entidades_especializadas, relacoes_especializadas = (
        _semear_conteudo_especializado(
            db, lote=lote,
        )
    )
    db.flush()
    entidades_por_slug = {
        (entidade.entity_type, entidade.slug): entidade
        for entidade in db.execute(
            select(KnowledgeEntity).where(KnowledgeEntity.status == "ativo")
        ).scalars()
    }
    publicados_por_slug = {
        (item.tipo, item.slug) for item in itens_publicados
    }
    for tipo, ids in ids_especializados.items():
        if not ids:
            continue
        publicados_por_slug.update(
            (entidade.entity_type, entidade.slug)
            for entidade in db.execute(
                select(KnowledgeEntity).where(
                    KnowledgeEntity.entity_type == tipo,
                    KnowledgeEntity.canonical_id.in_(ids),
                )
            ).scalars()
        )
    relacoes_doenca_explicitas, relacoes_doenca_nao_resolvidas = (
        _registrar_relacoes_explicitas_de_doenca(
            db,
            lote=lote,
            entidades_por_slug=entidades_por_slug,
            publicados_por_slug=publicados_por_slug,
        )
    )
    relacoes_automaticas_rejeitadas = _rejeitar_relacoes_automaticas_ausentes(lote)
    ids_especializados["tema"] = ids_publicados_tema
    for item in itens_publicados:
        ids_especializados.setdefault(item.tipo, set()).add(item.id_origem)
    entidades_arquivadas = _arquivar_entidades_sem_conteudo_publicado_correspondente(
        db, por_tema, ids_publicados_adicionais=ids_especializados,
    )

    if commit:
        db.commit()
    else:
        db.flush()
    return {
        "temas_processados": len(por_tema),
        "entidades_criadas_ou_atualizadas": entidades_criadas + entidades_especializadas,
        "relacoes_tema_criadas": relacoes_tema_criadas,
        "relacoes_explicitas_criadas": relacoes_explicitas,
        "referencias_explicitas_nao_resolvidas": len(referencias_nao_resolvidas),
        "amostra_referencias_nao_resolvidas": referencias_nao_resolvidas[:25],
        "entidades_especializadas_criadas": entidades_especializadas,
        "relacoes_estruturadas_especializadas_criadas": relacoes_especializadas,
        "relacoes_doenca_explicitas_criadas": relacoes_doenca_explicitas,
        "relacoes_doenca_explicitas_nao_resolvidas": len(relacoes_doenca_nao_resolvidas),
        "amostra_relacoes_doenca_nao_resolvidas": relacoes_doenca_nao_resolvidas[:25],
        "relacoes_automaticas_rejeitadas": relacoes_automaticas_rejeitadas,
        "entidades_arquivadas": entidades_arquivadas + calculadoras_duplicadas_arquivadas,
        "calculadoras_duplicadas_arquivadas": calculadoras_duplicadas_arquivadas,
        "relacoes_manuais_calculadora_migradas": relacoes_manuais_calculadora_migradas,
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

    # Relações com semântica clínica forte só ficam públicas após revisão.
    # Vínculos de navegação/taxonomia determinísticos podem ser exibidos como
    # pendentes, mantendo o status explícito na resposta.
    def _publicavel(relacao: KnowledgeRelation) -> bool:
        if (
            relacao.review_status == "revisado"
            or relacao.relation_type in RELACOES_PENDENTES_PUBLICAVEIS
        ):
            return True
        # `associated_with` é genérico demais para uma permissão global. Só
        # a navegação determinística entre protocolos explicitamente listada
        # em EmergencyProtocol.relacionados pode aparecer ainda pendente.
        return (
            relacao.relation_type == "associated_with"
            and (relacao.extra or {}).get("campo") == "EmergencyProtocol.relacionados"
            and _relacao_pertence_ao_backfill(relacao)
        )

    saida = [(rel, no) for rel, no in saida if _publicavel(rel)]
    entrada = [(rel, no) for rel, no in entrada if _publicavel(rel)]

    # A associação temática nova é O(N): item -> tema. O nó de tema é
    # taxonômico e não aparece na UI; seus demais membros são expandidos em um
    # segundo salto. Se o item já tem essa associação, as antigas arestas
    # `same_theme` ficam fora da resposta (permanecem no banco para rollback).
    todos_os_topicos = {
        outro.id
        for relacao, outro in list(saida) + list(entrada)
        if relacao.relation_type == "belongs_to_topic" and outro.entity_type == "tema"
    }
    topicos = {
        outro.id
        for relacao, outro in list(saida) + list(entrada)
        if relacao.relation_type == "belongs_to_topic"
        and outro.entity_type == "tema"
        # A página de medicamento nunca expande o catch-all Farmacologia:
        # apenas contextos sustentados pelas indicações do próprio fármaco.
        and not (origem.entity_type == "medicamento" and outro.title == "Farmacologia")
    }
    vizinhos_de_tema: list[tuple[KnowledgeRelation, KnowledgeEntity]] = []
    if topicos:
        vizinhos_de_tema = db.execute(
            select(KnowledgeRelation, KnowledgeEntity)
            .join(
                KnowledgeEntity,
                KnowledgeEntity.id == KnowledgeRelation.source_entity_id,
            )
            .where(
                KnowledgeRelation.target_entity_id.in_(topicos),
                KnowledgeRelation.relation_type == "belongs_to_topic",
                KnowledgeRelation.review_status != "rejeitado",
                KnowledgeEntity.status == "ativo",
                KnowledgeEntity.entity_type != "tema",
                KnowledgeEntity.id != origem.id,
            )
        ).all()

    vistos: set[tuple[str, str]] = set()
    por_tipo: dict[str, list[dict]] = {}
    candidatos_diretos = sorted(
        list(saida) + list(entrada),
        key=lambda par: (
            par[0].review_status != "revisado",
            par[0].confidence != "explicit",
            par[0].relation_type in {"same_theme", "belongs_to_topic"},
            -par[0].relevance_score,
            par[0].relation_type,
            par[1].entity_type,
            par[1].slug,
        ),
    )
    for relacao, outro in candidatos_diretos:
        if outro.entity_type == "tema" or relacao.relation_type == "belongs_to_topic":
            continue
        if todos_os_topicos and relacao.relation_type == "same_theme":
            continue
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

    # Relações diretas entram primeiro no conjunto de deduplicação e têm score
    # maior. O tema completa a cobertura sem substituir vínculos explícitos.
    for relacao, outro in sorted(
        vizinhos_de_tema,
        key=lambda par: (
            -par[0].relevance_score,
            par[1].entity_type,
            par[1].title.casefold(),
            par[1].slug,
        ),
    ):
        chave = (outro.entity_type, outro.slug)
        if chave in vistos:
            continue
        vistos.add(chave)
        por_tipo.setdefault(outro.entity_type, []).append({
            "slug": outro.slug,
            "titulo": outro.title,
            "relation_type": "belongs_to_topic",
            "relevance_score": relacao.relevance_score,
            "confidence": relacao.confidence,
            "provenance_type": relacao.provenance_type,
            "review_status": relacao.review_status,
            "rota": _rota_item(outro.entity_type, outro.slug),
        })

    grupos = []
    total = 0
    for tipo, itens in sorted(por_tipo.items()):
        itens_ordenados = sorted(
            itens,
            key=lambda i: (-i["relevance_score"], i["titulo"].casefold(), i["slug"]),
        )
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
