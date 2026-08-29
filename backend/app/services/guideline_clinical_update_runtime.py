from __future__ import annotations

"""Camada de execução idempotente para os overrides do CorVIA Intelligence.

Os campos clínicos podem receber atualizações de mais de uma diretriz. Cada
bloco tem marcador próprio; reaplicar uma diretriz já presente não altera a
ordem nem cria revisão artificial. Depois de uma reconciliação arquivos -> DB,
o marcador some e o mesmo override é restaurado automaticamente.
"""

import re
from typing import Any

from app.services import guideline_clinical_update as core

_ORIGINAL_APPLY_OVERRIDE = core._apply_override


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


def install_runtime_guards() -> None:
    core._plain_override = _plain_override
    core._strip_plain_override = _strip_plain_override
    core._apply_override = _guarded_apply_override


def process_pending_guidelines(db, *, limit: int = core.PROCESS_LIMIT) -> dict:
    install_runtime_guards()
    return core.process_pending_guidelines(db, limit=limit)


def reapply_confirmed_updates(db) -> dict:
    install_runtime_guards()
    return core.reapply_confirmed_updates(db)
