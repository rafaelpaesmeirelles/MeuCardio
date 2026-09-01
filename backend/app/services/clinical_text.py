from __future__ import annotations

"""Higiene de textos clínicos expostos por APIs públicas/autenticadas."""

import json
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
            GuidelineLink.origem == "intelligence",
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
