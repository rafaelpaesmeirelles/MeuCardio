from __future__ import annotations

"""Camada de execução idempotente para os overrides do CorVIA Intelligence.

Os campos clínicos podem receber atualizações de mais de uma diretriz. Cada
bloco precisa ter marcador próprio para que reaplicar uma diretriz não remova a
atualização de outra.
"""

import re

from app.services import guideline_clinical_update as core


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


def install_runtime_guards() -> None:
    # Os métodos de aplicação resolvem estes nomes no módulo em tempo de
    # execução. A substituição é local ao processo e mantém o arquivo canônico
    # legível, além de garantir compatibilidade com registros criados antes
    # deste guard.
    core._plain_override = _plain_override
    core._strip_plain_override = _strip_plain_override


def process_pending_guidelines(db, *, limit: int = core.PROCESS_LIMIT) -> dict:
    install_runtime_guards()
    return core.process_pending_guidelines(db, limit=limit)


def reapply_confirmed_updates(db) -> dict:
    install_runtime_guards()
    return core.reapply_confirmed_updates(db)
