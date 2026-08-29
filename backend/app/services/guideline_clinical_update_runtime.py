from __future__ import annotations

"""Camada de execução idempotente para os overrides do CorVIA Intelligence."""

import logging
import re
from datetime import datetime, timezone
from typing import Any

from app.models.guideline import Guideline, GuidelineNotification
from app.services import guideline_clinical_update as core
from app.services.guideline_source_trust import is_trusted_official_guideline

log = logging.getLogger("corvia.guideline_clinical_update.runtime")

_ORIGINAL_APPLY_OVERRIDE = core._apply_override
_ORIGINAL_ENSURE_SUMMARY = core._ensure_summary_document
COMPLETE_PUBLICATION_LIMIT = 300
_PENDING_STATUSES = (
    "oficial_aprovada",
    "detected",
    "aguardando_revisao",
)


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
        return plain_marker in str(getattr(target, "summary", "") or "") or plain_marker in str(getattr(target, "treatment_summary", "") or "")
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


def _ensure_summary_published(db, guideline, analysis: dict, impacts: list[dict]):
    doc = _ORIGINAL_ENSURE_SUMMARY(db, guideline, analysis, impacts)
    doc.published = True
    doc.review_status = "revisado"
    doc.source_tier = "A"
    doc.reviewed_at = doc.reviewed_at or datetime.now(timezone.utc)
    db.flush()
    return doc


def install_runtime_guards() -> None:
    core._plain_override = _plain_override
    core._strip_plain_override = _strip_plain_override
    core._apply_override = _guarded_apply_override
    core._ensure_summary_document = _ensure_summary_published


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


def process_pending_guidelines(db, *, limit: int = COMPLETE_PUBLICATION_LIMIT) -> dict:
    """Processa automaticamente toda publicação de fonte confiável.

    PubMed, Europe PMC e Crossref são tratados como fontes confiáveis quando o
    item já passou pelos filtros de alto sinal dos indexadores. Fontes não
    reconhecidas não são autoaprovadas. Em 429 do provedor, a execução para
    imediatamente: a fila permanece persistida e será retomada no próximo ciclo,
    evitando transformar um rate limit transitório em centenas de falhas.

    ``revisao_necessaria`` não entra de novo nesta fila: esse status só aparece
    depois de a análise/resumo já terem sido concluídos e significa que uma
    alteração estrutural do conteúdo-base merece revisão adicional. O documento
    científico em si continua analisado, resumido e publicado normalmente.
    """
    install_runtime_guards()
    candidates = _official_pending_query(db).order_by(
        Guideline.published_at.desc().nullslast(),
        Guideline.discovered_at.asc(),
    ).limit(limit).all()
    guidelines = [item for item in candidates if is_trusted_official_guideline(item)]

    items: list[dict] = []
    failures: list[dict] = []
    rate_limited = False
    if not core.settings.ai_enabled or core.settings.ai_provider != "openai" or not core.settings.openai_api_key.strip():
        return {
            "processed": 0,
            "skipped": "ai_unavailable",
            "requested": len(guidelines),
            "remaining": len(guidelines),
            "items": [],
            "failures": [],
        }

    with core._PROCESS_LOCK:
        for guideline in guidelines:
            # Garante que um item confiável nunca volte a depender de revisão manual
            # apenas porque uma tentativa anterior de análise falhou.
            if guideline.detection_status != "oficial_aprovada":
                guideline.detection_status = "oficial_aprovada"
                db.commit()
            try:
                result = core.process_guideline(db, guideline)
                _reopen_in_app_alerts(db, guideline.id)
                items.append(result)
            except Exception as exc:
                db.rollback()
                if _is_rate_limit(exc):
                    rate_limited = True
                    log.warning("Rate limit ao analisar %s; fila oficial preservada para retomada.", guideline.slug)
                    break
                log.exception("Falha ao analisar/aplicar diretriz %s", guideline.slug)
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
        "requested": len(guidelines),
        "remaining": remaining,
        "rate_limited": rate_limited,
        "items": items,
        "failures": failures,
    }


def reapply_confirmed_updates(db) -> dict:
    install_runtime_guards()
    return core.reapply_confirmed_updates(db)
