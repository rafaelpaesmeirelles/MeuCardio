from __future__ import annotations

"""Camada de execução idempotente para os overrides do CorVIA Intelligence.

Além da idempotência, esta camada aplica o gate editorial de fonte original:
metadados bibliográficos, DOI, PubMed ou texto de falha de recuperação não são
conteúdo clínico publicável. Sínteses antigas nessa situação são retiradas do
acervo, removidas do índice RAG e reenfileiradas para reconstrução.
"""

import copy
import logging
import re
from datetime import datetime, timezone
from typing import Any

from app.models.guideline import Guideline, GuidelineNotification
from app.models.rag import DocumentChunk
from app.services import guideline_clinical_update as core
from app.services.guideline_source_trust import is_trusted_official_guideline

log = logging.getLogger("corvia.guideline_clinical_update.runtime")

_ORIGINAL_APPLY_OVERRIDE = core._apply_override
_ORIGINAL_ENSURE_SUMMARY = core._ensure_summary_document
_ORIGINAL_ANALYZE_SOURCE = core._analyze_source
_ORIGINAL_TRUSTED_DOMAINS = tuple(core.TRUSTED_DOMAINS)

COMPLETE_PUBLICATION_LIMIT = 300
SOURCE_REBUILD_STATUS = "reconstrucao_fonte_original_necessaria"
_PENDING_STATUSES = (
    "oficial_aprovada",
    "detected",
    "aguardando_revisao",
)

# Editores científicos que faltavam no allow-list. O incidente de 29/08/2026
# ocorreu com um artigo open access da Springer que o modelo não conseguia abrir
# porque o domínio do texto integral não estava entre os domínios permitidos.
_ADDITIONAL_PUBLISHER_DOMAINS = (
    "springer.com",
    "sciencedirect.com",
    "wiley.com",
    "jamanetwork.com",
    "frontiersin.org",
)

# Essas páginas confirmam identidade bibliográfica, mas não equivalem ao
# documento original. Elas podem localizar a publicação; sozinhas não liberam
# uma síntese para publicação clínica.
_METADATA_ONLY_HOSTS = frozenset({
    "doi.org",
    "pubmed.ncbi.nlm.nih.gov",
})

_FALLBACK_MARKERS = (
    "não foi possível recuperar",
    "nao foi possivel recuperar",
    "não foi possível verificar",
    "nao foi possivel verificar",
    "não foi possível confirmar",
    "nao foi possivel confirmar",
    "não estavam acessíveis",
    "nao estavam acessiveis",
    "não é seguro atribuir",
    "nao e seguro atribuir",
    "resumo indisponível",
    "resumo indisponivel",
    "fontes oficiais permitidas",
    "não foi possível acessar",
    "nao foi possivel acessar",
)

# A análise reconstruída precisa declarar explicitamente o nível de acesso à
# fonte. Isso evita confundir uma URL de editor/periódico com leitura real do
# documento. O modelo só pode declarar full_text quando conseguiu inspecionar
# conteúdo além de título/resumo e identificar pelo menos duas seções/partes do
# original. Esses campos são exigidos pelo JSON Schema estrito.
_ORIGINAL_ANALYSIS_SCHEMA = copy.deepcopy(core.ANALYSIS_SCHEMA)
_ORIGINAL_ANALYSIS_SCHEMA["properties"].update({
    "source_access_level": {
        "type": "string",
        "enum": ["full_text", "abstract_only", "metadata_only", "inaccessible"],
    },
    "primary_source_url": {"type": "string"},
    "original_sections_seen": {"type": "array", "items": {"type": "string"}},
    "source_access_reason_pt": {"type": "string"},
})
_ORIGINAL_ANALYSIS_SCHEMA["required"] = [
    *_ORIGINAL_ANALYSIS_SCHEMA["required"],
    "source_access_level",
    "primary_source_url",
    "original_sections_seen",
    "source_access_reason_pt",
]


def _plain_override(guideline, impact: dict) -> str:
    date = guideline.published_at.date().isoformat() if guideline.published_at else str(guideline.ano)
    return (
        f"<!-- corvia-intelligence:{guideline.slug}:plain:start -->\n"
        f"**Atualização CorVIA Intelligence — {date}:** {impact['override_pt']} "
        f"**Prevalência:** esta atualização prevalece sobre orientação anterior deste item em caso de conflito. "
        f"**Fonte oficial:** {impact['source_url']}\n"
        f"<!-- corvia-intelligence:{guideline.slug}:plain:end -->"
    )


def _strip_plain_override(text: str | None, guideline_slug: str) -> str:
    if not text:
        return ""
    pattern = re.compile(
        rf"<!-- corvia-intelligence:{re.escape(guideline_slug)}:plain:start -->.*?"
        rf"<!-- corvia-intelligence:{re.escape(guideline_slug)}:plain:end -->\s*",
        re.S,
    )
    return pattern.sub("", text).lstrip()


def _already_applied(target: Any, item_type: str, guideline_slug: str) -> bool:
    markdown_marker = f"<!-- corvia-intelligence:{guideline_slug}:start -->"
    plain_marker = f"<!-- corvia-intelligence:{guideline_slug}:plain:start -->"
    if item_type == "document":
        return markdown_marker in str(getattr(target, "body_md", "") or "")
    if item_type == "evidence":
        return plain_marker in str(getattr(target, "summary", "") or "")
    if item_type == "disease":
        return (
            plain_marker in str(getattr(target, "summary", "") or "")
            or plain_marker in str(getattr(target, "treatment_summary", "") or "")
        )
    if item_type == "drug":
        notes = dict(getattr(target, "notes", {}) or {})
        return any(
            isinstance(item, dict) and item.get("guideline_slug") == guideline_slug
            for item in (notes.get("corvia_intelligence_updates") or [])
        )
    if item_type == "checklist":
        return plain_marker in str(getattr(target, "resumo", "") or "")
    if item_type == "triage":
        return plain_marker in str(getattr(target, "summary", "") or "")
    return False


def _guarded_apply_override(db, guideline, impact: dict, *, record: bool = True) -> bool:
    item_type = str(impact.get("item_type") or "")
    item_id = int(impact.get("item_id") or 0)
    target = core._get_target(db, item_type, item_id)
    if target is not None and _already_applied(target, item_type, guideline.slug):
        return False
    return _ORIGINAL_APPLY_OVERRIDE(db, guideline, impact, record=record)


def _install_source_domains() -> None:
    """Inclui editoras necessárias sem ultrapassar o limite de 30 domínios."""
    core.TRUSTED_DOMAINS = tuple(dict.fromkeys([
        *_ORIGINAL_TRUSTED_DOMAINS,
        *_ADDITIONAL_PUBLISHER_DOMAINS,
    ]))


def _is_primary_content_url(guideline: Guideline, url: str) -> bool:
    """Distingue texto científico consultável de simples página bibliográfica."""
    allowed = core._domains_for(guideline)
    if not core._trusted_url(url, allowed):
        return False
    host = core._canonical_host(url)
    if not host or host in _METADATA_ONLY_HOSTS:
        return False
    # Europe PMC pode ser apenas registro/abstract; só tratamos como texto
    # original quando a URL aponta explicitamente para um registro PMC.
    if host == "europepmc.org" and "pmc" not in url.casefold():
        return False
    return True


def _has_primary_content_source(guideline: Guideline, sources: list[str]) -> bool:
    return any(_is_primary_content_url(guideline, url) for url in sources)


def _normalize_seen_url(value: str) -> str:
    return re.sub(r"[?#].*$", "", str(value or "").strip()).rstrip("/").casefold()


def _source_url_was_seen(primary_url: str, sources: list[str]) -> bool:
    primary = _normalize_seen_url(primary_url)
    if not primary:
        return False
    if any(_normalize_seen_url(url) == primary for url in sources):
        return True
    # Algumas citações do web_search devolvem uma âncora/variante da mesma
    # página. Aceitamos a mesma origem + caminho-base, mas não apenas o host.
    primary_base = primary.rsplit("/", 1)[0]
    return bool(primary_base and any(
        _normalize_seen_url(url).startswith(primary_base + "/")
        for url in sources
    ))


def _full_text_access_confirmed(guideline: Guideline, analysis: dict, sources: list[str]) -> bool:
    primary_url = str(analysis.get("primary_source_url") or "").strip()
    sections = [
        re.sub(r"\s+", " ", str(item or "")).strip()
        for item in (analysis.get("original_sections_seen") or [])
        if str(item or "").strip()
    ]
    return bool(
        analysis.get("source_access_level") == "full_text"
        and _is_primary_content_url(guideline, primary_url)
        and _source_url_was_seen(primary_url, sources)
        and len(sections) >= 2
    )


def _analyze_source_from_original(guideline: Guideline) -> dict:
    """Reconstrói a síntese somente depois de acessar o documento original."""
    domains = core._domains_for(guideline)
    instructions = """Você integra o CorVIA Intelligence, um sistema de apoio a cardiologistas.
A tarefa obrigatória é reconstruir a síntese A PARTIR DO DOCUMENTO ORIGINAL. Use DOI, PubMed,
Europe PMC ou Crossref apenas para confirmar identidade e localizar a fonte. Antes de escrever
conteúdo clínico, abra e consulte o texto original no site da sociedade científica, periódico,
editor ou PMC. Um registro bibliográfico, página de DOI ou resumo do PubMed isoladamente NÃO é
fonte suficiente para liberar publicação no CorVIA.

Produza síntese ORIGINAL em português; nunca reproduza ou traduza integralmente texto protegido.
Extraia somente o que o original sustenta: população/escopo, recomendações, classe e nível de
evidência quando existirem, doses, cortes, algoritmos, mudanças, limitações e impacto prático.
Não invente classe, nível, dose, corte, estratégia ou mudança. Se o documento original não puder
ser efetivamente acessado, NÃO preencha a lacuna com conhecimento geral: registre a limitação e
não fabrique conteúdo clínico para tornar o texto aparentemente completo.

Classifique source_access_level com rigor:
- full_text: você conseguiu efetivamente inspecionar conteúdo do documento além de título e resumo/abstract;
- abstract_only: você acessou apenas o abstract/resumo;
- metadata_only: apenas DOI/PubMed/Crossref/título/autores/metadados;
- inaccessible: nem conteúdo suficiente nem metadados confiáveis foram acessíveis.
Só use full_text se puder preencher original_sections_seen com pelo menos DUAS seções, partes,
tabelas ou blocos temáticos realmente observados no original. Não invente nomes de seção.
primary_source_url deve ser a página efetivamente consultada que contém o documento original,
não a página DOI/PubMed usada para encontrá-lo. source_access_reason_pt deve explicar brevemente
o que foi possível ler. Use source_url nas mudanças apenas para páginas efetivamente consultadas.
Responda somente no JSON solicitado."""
    user_text = (
        f"Organização/indexador: {guideline.org}\n"
        f"Título original: {guideline.titulo}\n"
        f"Ano: {guideline.ano}\n"
        f"DOI: {guideline.doi or 'não informado'}\n"
        f"URL conhecida: {guideline.url or 'não informada'}\n"
        f"Data de publicação: {guideline.published_at.isoformat() if guideline.published_at else 'não informada'}\n"
        "Localize e LEIA o documento original antes de construir a síntese clínica."
    )
    analysis, sources = core._responses_json(
        instructions=instructions,
        user_text=user_text,
        schema=_ORIGINAL_ANALYSIS_SCHEMA,
        schema_name="corvia_guideline_analysis_original_source",
        allowed_domains=domains,
    )
    for change in analysis.get("key_changes") or []:
        source_url = str(change.get("source_url") or "")
        if not _is_primary_content_url(guideline, source_url):
            change["explicit_in_source"] = False
            analysis.setdefault("limitations", []).append(
                "A mudança não foi validada em página com conteúdo do documento original: "
                f"{source_url[:160]}"
            )
    analysis["source_urls_seen"] = sources[:40]
    analysis["analyzed_at"] = datetime.now(timezone.utc).isoformat()
    analysis["analysis_model"] = core._model()
    analysis["translation_mode"] = "sintese_original_pt_br"
    analysis["original_source_accessed"] = _full_text_access_confirmed(
        guideline, analysis, sources
    )
    if not analysis["original_source_accessed"]:
        analysis.setdefault("limitations", []).append(
            "O texto do documento original não teve leitura integral/substantiva confirmada; "
            "metadados ou abstract isolados não são suficientes para publicação."
        )
    return analysis


def _analysis_publishable(guideline: Guideline, analysis: dict | None) -> bool:
    """Quality gate: metadado/fallback nunca vira conteúdo clínico publicado."""
    if not isinstance(analysis, dict):
        return False

    summary = re.sub(r"\s+", " ", str(analysis.get("summary_pt") or "")).strip()
    if len(summary) < 450 or len(summary.split()) < 70:
        return False

    normalized = summary.casefold()
    if any(marker in normalized for marker in _FALLBACK_MARKERS):
        return False

    sources = [
        str(url or "").strip()
        for url in (analysis.get("source_urls_seen") or [])
        if str(url or "").strip()
    ]
    if not _has_primary_content_source(guideline, sources):
        return False

    # Análises novas usam o contrato forte de acesso. Análises legadas sem
    # esses campos ainda podem permanecer se já forem substantivas, tiverem
    # fonte primária e não apresentarem assinatura de fallback; as ruins são
    # reenfileiradas e, a partir daí, passam obrigatoriamente pelo contrato novo.
    if "source_access_level" in analysis:
        if not _full_text_access_confirmed(guideline, analysis, sources):
            return False
    elif analysis.get("original_source_accessed") is False:
        return False

    explicit_changes = [
        item for item in (analysis.get("key_changes") or [])
        if isinstance(item, dict) and item.get("explicit_in_source") is True
    ]
    limitations = " ".join(
        str(item or "") for item in (analysis.get("limitations") or [])
    ).casefold()
    limitation_hits = sum(marker in limitations for marker in _FALLBACK_MARKERS)
    if limitation_hits >= 2 and not explicit_changes:
        return False

    return True


def _quarantine_document(db, doc) -> bool:
    """Retira imediatamente conteúdo inadequado da biblioteca e do RAG."""
    if doc is None:
        return False
    changed = bool(doc.published or doc.review_status == "revisado")
    doc.published = False
    doc.review_status = "pendente_revisao"
    doc.reviewed_at = None
    doc.gaps = list(dict.fromkeys([
        *(doc.gaps or []),
        "reconstrucao_fonte_original_necessaria",
    ]))
    db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).delete(
        synchronize_session=False
    )
    return changed


def _summary_document(db, guideline: Guideline):
    link = db.query(core.GuidelineLink).filter(
        core.GuidelineLink.guideline_id == guideline.id,
        core.GuidelineLink.item_type == core.SUMMARY_ITEM_TYPE,
    ).order_by(core.GuidelineLink.id.desc()).first()
    return db.get(core.Document, link.item_id) if link else None


def _quarantine_summary_for_guideline(db, guideline: Guideline) -> bool:
    return _quarantine_document(db, _summary_document(db, guideline))


def _document_looks_like_fallback(doc) -> bool:
    summary = str(getattr(doc, "summary", "") or "").casefold()
    body = str(getattr(doc, "body_md", "") or "").casefold()
    summary_hits = sum(marker in summary for marker in _FALLBACK_MARKERS)
    body_hits = sum(marker in body for marker in _FALLBACK_MARKERS)
    bibliographic_only = (
        "identidade bibliográfica confirmada" in summary
        or "identidade bibliográfica confirmada" in body
    )
    return bool(
        (bibliographic_only and (summary_hits + body_hits) >= 1)
        or (summary_hits >= 1 and body_hits >= 2)
        or (len(summary.split()) < 35 and body_hits >= 3)
    )


def _quarantine_published_fallback_documents(db) -> int:
    """Varre TODO o acervo publicado, inclusive documentos sem link de guideline."""
    quarantined = 0
    docs = db.query(core.Document).filter(core.Document.published.is_(True)).all()
    for doc in docs:
        if _document_looks_like_fallback(doc) and _quarantine_document(db, doc):
            quarantined += 1
    if quarantined:
        db.commit()
    return quarantined


def _ensure_summary_published(db, guideline, analysis: dict, impacts: list[dict]):
    doc = _ORIGINAL_ENSURE_SUMMARY(db, guideline, analysis, impacts)
    if _analysis_publishable(guideline, analysis):
        doc.published = True
        doc.review_status = "revisado"
        doc.source_tier = "A"
        doc.reviewed_at = doc.reviewed_at or datetime.now(timezone.utc)
        doc.gaps = [
            gap for gap in (doc.gaps or [])
            if gap != "reconstrucao_fonte_original_necessaria"
        ]
    else:
        _quarantine_document(db, doc)
        log.warning(
            "Síntese %s bloqueada: fonte original não sustenta publicação clínica.",
            guideline.slug,
        )
    db.flush()
    return doc


def install_runtime_guards() -> None:
    _install_source_domains()
    core._plain_override = _plain_override
    core._strip_plain_override = _strip_plain_override
    core._apply_override = _guarded_apply_override
    core._ensure_summary_document = _ensure_summary_published
    core._analyze_source = _analyze_source_from_original


def _reopen_in_app_alerts(db, guideline_id: int) -> None:
    db.query(GuidelineNotification).filter(
        GuidelineNotification.guideline_id == guideline_id,
        GuidelineNotification.channel == "in_app",
        GuidelineNotification.status == "disponivel",
    ).update({GuidelineNotification.read_at: None}, synchronize_session=False)
    db.commit()


def _is_rate_limit(exc: Exception) -> bool:
    response = getattr(exc, "response", None)
    return getattr(response, "status_code", None) == 429


def _official_pending_query(db):
    return db.query(Guideline).filter(Guideline.detection_status.in_(_PENDING_STATUSES))


def _reset_bad_cached_analysis(db, guideline: Guideline) -> bool:
    analysis = core.get_analysis(db, guideline)
    if analysis is None or _analysis_publishable(guideline, analysis):
        return False
    _quarantine_summary_for_guideline(db, guideline)
    link = core._analysis_link(db, guideline.id)
    if link is not None:
        db.delete(link)
    guideline.detection_status = "oficial_aprovada"
    db.commit()
    return True


def _requeue_completed_low_quality(db) -> int:
    """Reabre uma vez as análises históricas contaminadas."""
    reopened = 0
    excluded = (*_PENDING_STATUSES, SOURCE_REBUILD_STATUS)
    completed = db.query(Guideline).filter(
        ~Guideline.detection_status.in_(excluded)
    ).all()
    for guideline in completed:
        if not is_trusted_official_guideline(guideline):
            continue
        analysis = core.get_analysis(db, guideline)
        if analysis is not None and not _analysis_publishable(guideline, analysis):
            if _reset_bad_cached_analysis(db, guideline):
                reopened += 1
    return reopened


def process_pending_guidelines(db, *, limit: int = COMPLETE_PUBLICATION_LIMIT) -> dict:
    """Reconstrói em lote usando o documento original e bloqueia o que não passar."""
    install_runtime_guards()
    quarantined = _quarantine_published_fallback_documents(db)
    reopened = _requeue_completed_low_quality(db)
    candidates = _official_pending_query(db).order_by(
        Guideline.published_at.desc().nullslast(),
        Guideline.discovered_at.asc(),
    ).limit(limit).all()
    guidelines = [item for item in candidates if is_trusted_official_guideline(item)]

    items: list[dict] = []
    failures: list[dict] = []
    rate_limited = False
    blocked_source_original = 0
    if not core.settings.ai_enabled or core.settings.ai_provider != "openai" or not core.settings.openai_api_key.strip():
        return {
            "processed": 0,
            "quarantined_fallback_documents": quarantined,
            "reopened_low_quality": reopened,
            "blocked_source_original": 0,
            "skipped": "ai_unavailable",
            "requested": len(guidelines),
            "remaining": len(guidelines),
            "items": [],
            "failures": [],
        }

    with core._PROCESS_LOCK:
        for guideline in guidelines:
            if guideline.detection_status != "oficial_aprovada":
                guideline.detection_status = "oficial_aprovada"
                db.commit()
            _reset_bad_cached_analysis(db, guideline)
            try:
                result = core.process_guideline(db, guideline)
                analysis = core.get_analysis(db, guideline)
                if not _analysis_publishable(guideline, analysis):
                    _quarantine_summary_for_guideline(db, guideline)
                    guideline.detection_status = SOURCE_REBUILD_STATUS
                    db.commit()
                    result["quality_gate"] = "blocked_source_original"
                    blocked_source_original += 1
                else:
                    result["quality_gate"] = "published_from_original"
                    _reopen_in_app_alerts(db, guideline.id)
                items.append(result)
            except Exception as exc:
                db.rollback()
                if _is_rate_limit(exc):
                    rate_limited = True
                    log.warning(
                        "Rate limit ao reconstruir %s; fila preservada para retomada.",
                        guideline.slug,
                    )
                    break
                log.exception("Falha ao reconstruir publicação %s", guideline.slug)
                failures.append({
                    "guideline_id": guideline.id,
                    "slug": guideline.slug,
                    "error": type(exc).__name__,
                })

    remaining = sum(
        1
        for item in _official_pending_query(db).all()
        if is_trusted_official_guideline(item)
    )
    return {
        "processed": len(items),
        "quarantined_fallback_documents": quarantined,
        "reopened_low_quality": reopened,
        "blocked_source_original": blocked_source_original,
        "requested": len(guidelines),
        "remaining": remaining,
        "rate_limited": rate_limited,
        "items": items,
        "failures": failures,
    }


def reapply_confirmed_updates(db) -> dict:
    install_runtime_guards()
    result = core.reapply_confirmed_updates(db)
    result["quarantined_fallback_documents"] = _quarantine_published_fallback_documents(db)
    result["reopened_low_quality"] = _requeue_completed_low_quality(db)
    return result
