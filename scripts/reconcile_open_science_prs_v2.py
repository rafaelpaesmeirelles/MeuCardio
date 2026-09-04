#!/usr/bin/env python3
"""Entrada v2 do reconciliador científico.

Corrige um falso positivo da primeira passagem: o marcador técnico ``TODO``
deve ser sensível a maiúsculas; a palavra portuguesa ``todo``/``todos`` não é
placeholder editorial. As demais expressões de pendência continuam
case-insensitive e fail-closed.
"""
from __future__ import annotations

import re

import reconcile_open_science_prs as base

base.PLACEHOLDER_RE = re.compile(
    r"(?:\bTODO\b|\bTBD\b|\bFIXME\b|\bXXX\b|"
    r"(?i:fonte\s+(?:a\s+)?confirmar|refer[eê]ncia\s+pendente|"
    r"pendente\s+de\s+fonte|exemplo\.com|lorem\s+ipsum|"
    r"inserir\s+(?:pmid|doi|fonte|refer[eê]ncia)))"
)

if __name__ == "__main__":
    raise SystemExit(base.main())
