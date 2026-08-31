"""Contrato declarativo da certificação final do CorVIA.

Este módulo não altera comportamento clínico nem de runtime. Ele torna explícita
no código versionado a regra operacional usada no release: depois que o SHA
final chega a ``main``, todos os gates mandatórios precisam ser executados para
aquela mesma revisão antes do deploy.
"""
from __future__ import annotations

MANDATORY_FINAL_GATES: tuple[str, ...] = (
    "CI",
    "RC2 Acceptance — Canonical CorVIA",
    "Visual QA — Clinical OS",
    "Corpus database reconciliation",
    "Deep functional inventory and public apps",
    "Native installers",
)


def mandatory_final_gates() -> tuple[str, ...]:
    """Retorna a lista imutável de gates exigidos para a decisão de release."""
    return MANDATORY_FINAL_GATES
