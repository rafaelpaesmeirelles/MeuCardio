from __future__ import annotations

"""Higiene de textos clínicos expostos por APIs públicas/autenticadas."""

import json
import hashlib
import re
from typing import Any
from urllib.parse import urlsplit


_CORVIA_INTELLIGENCE_PLAIN_BLOCK = re.compile(
    r"<!--\s*corvia-intelligence:(?P<slug>[^>:\s]+):plain:start\s*-->.*?"
    r"<!--\s*corvia-intelligence:(?P=slug):plain:end\s*-->\s*",
    re.IGNORECASE | re.DOTALL,
)
_CORVIA_INTELLIGENCE_PLAIN_MARKER = re.compile(
    r"<!--\s*corvia-intelligence:[^>]*:plain:(?:start|end)\s*-->\s*",
    re.IGNORECASE,
)


def clinical_text_without_internal_overrides(value: str | None) -> str | None:
    """Descarta envelopes internos legados sem alterar o texto canônico.

    O conteúdo entre os marcadores também é removido: ele descreve uma
    atualização de diretriz e não pertence ao resumo/definição clínica base.
    """
    if value is None:
        return None
    without_complete_blocks = _CORVIA_INTELLIGENCE_PLAIN_BLOCK.sub("", value)
    # Em envelope incompleto ou corrompido, remova só os tokens internos. É
    # deliberadamente conservador: nunca apague texto clínico sem um par com o
    # mesmo slug comprovando os limites do bloco.
    return _CORVIA_INTELLIGENCE_PLAIN_MARKER.sub("", without_complete_blocks).strip()


def _safe_http_url(value: object) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    candidate = value.strip().rstrip(".,;)")
    try:
        parsed = urlsplit(candidate)
    except ValueError:
        return None
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.netloc
        or parsed.username
        or parsed.password
    ):
        return None
    return candidate


def _approved_change_payload(link_payload, proposal, *, item_type, item_id, slug,
                             source_snapshot, target_snapshot, approval_proven):
    """Read-only proof: a human-origin label alone is never authorization."""
    if not proposal or proposal.status != "approved" or not approval_proven:
        return None
    payload = proposal.payload
    if not isinstance(payload, dict) or not proposal.reviewer_id or not proposal.reviewed_at:
        return None
    fingerprint = hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True,
        separators=(",", ":"), default=str).encode()).hexdigest()
    if fingerprint != proposal.fingerprint or link_payload.get("fingerprint") != fingerprint:
        return None
    if (link_payload.get("proposal_id") != proposal.id
            or link_payload.get("reviewer_id") != proposal.reviewer_id
            or link_payload.get("mode") != "owner_approved_exact_snapshot"
            or proposal.guideline_id != source_snapshot.get("id")
            or source_snapshot.get("superseded_by_id") is not None
            or payload.get("source") != source_snapshot):
        return None
    changes = payload.get("changes")
    if not isinstance(changes, list):
        return None
    matching = [change for change in changes if isinstance(change, dict)
        and change.get("item_type") == item_type and change.get("item_id") == item_id
        and change.get("slug") == slug]
    if len(matching) != 1:
        return None
    change = matching[0]
    impact = change.get("impact")
    if (not isinstance(impact, dict) or change.get("after") != target_snapshot
            or impact.get("item_type") != item_type or impact.get("item_id") != item_id
            or link_payload.get("before") != change.get("before")):
        return None
    # Compare all display-bearing fields to the approved snapshot, not to an
    # arbitrary GuidelineLink JSON that happens to cite a valid proposal id.
    for field in ("item_type", "item_id", "target_section", "override_pt", "change_summary_pt", "source_url"):
        if link_payload.get(field) != impact.get(field):
            return None
    if (link_payload.get("change_summary_pt") != change.get("change_summary_pt")
            or link_payload.get("source_url") != change.get("source_url")):
        return None
    return {**impact, "applied_at": link_payload.get("applied_at")}


def structured_clinical_updates(
    db: Any,
    item_type: str,
    item_id: int,
    *,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Expõe links confirmados vigentes sem contaminar o texto canônico."""
    # Imports locais evitam acoplar o sanitizador puro à inicialização dos
    # modelos e mantêm o helper utilizável nos testes sem carregar a aplicação.
    from app.models.guideline import Guideline, GuidelineLink

    rows = (
        db.query(GuidelineLink, Guideline)
        .join(Guideline, Guideline.id == GuidelineLink.guideline_id)
        .filter(
            GuidelineLink.item_type == item_type,
            GuidelineLink.item_id == item_id,
            GuidelineLink.origem.in_(("intelligence", "human_approval")),
            GuidelineLink.confirmado.is_(True),
            Guideline.superseded_by_id.is_(None),
        )
        .order_by(Guideline.published_at.desc().nullslast(), GuidelineLink.id.desc())
        .limit(max(1, min(limit, 50)))
        .all()
    )
    updates: list[dict[str, Any]] = []
    for link, guideline in rows:
        try:
            payload = json.loads(link.trecho or "{}")
        except (TypeError, json.JSONDecodeError):
            continue
        if not isinstance(payload, dict):
            continue
        if link.origem == "human_approval":
            from app.models.clinical_change_proposal import ClinicalChangeProposal
            from app.services import clinical_change_approvals as approvals
            from app.services.guideline_clinical_update import _get_target

            proposal_id = payload.get("proposal_id")
            if type(proposal_id) is not int or proposal_id <= 0:
                continue
            proposal = db.get(ClinicalChangeProposal, proposal_id)
            target = _get_target(db, item_type, item_id)
            if proposal is None or target is None:
                continue
            payload = _approved_change_payload(payload, proposal, item_type=item_type,
                item_id=item_id, slug=target.slug, source_snapshot=approvals.source_identity(guideline),
                target_snapshot=approvals.snapshot(target), approval_proven=approvals.approval_proof(db, proposal))
            if payload is None:
                continue
        change_summary = payload.get("change_summary_pt")
        recommendation = payload.get("override_pt")
        if not change_summary and not recommendation:
            continue
        updates.append({
            "guideline": {
                "org": guideline.org,
                "title": guideline.titulo,
                "year": guideline.ano,
            },
            "target_section": payload.get("target_section"),
            "change_summary": change_summary,
            "recommendation": recommendation,
            "source_url": (
                _safe_http_url(payload.get("source_url"))
                or _safe_http_url(guideline.url)
            ),
            "applied_at": payload.get("applied_at"),
        })
    return updates
