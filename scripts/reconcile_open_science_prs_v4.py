#!/usr/bin/env python3
"""Entrada v4 do reconciliador científico.

Corrige a principal fonte de supercontagem em PRs empilhados: cada PR deve
ser analisado pelo seu delta próprio (``base.sha -> head``), e não pelo
merge-base entre o head e a ``main`` atual. O workflow fornece o mapa
``PR -> base.sha`` via ``CORVIA_PR_BASES_JSON``.

Mantém as correções anteriores:
- TODO técnico é case-sensitive, sem confundir a palavra portuguesa "todo";
- doença/triagem já composta em fragmento canônico não volta ao manifesto;
- estudos com PMID/DOI/NCT já existente representam a mesma publicação.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

import reconcile_open_science_prs as base

base.PLACEHOLDER_RE = re.compile(
    r"(?:\bTODO\b|\bTBD\b|\bFIXME\b|\bXXX\b|"
    r"(?i:fonte\s+(?:a\s+)?confirmar|refer[eê]ncia\s+pendente|"
    r"pendente\s+de\s+fonte|exemplo\.com|lorem\s+ipsum|"
    r"inserir\s+(?:pmid|doi|fonte|refer[eê]ncia)))"
)


def cli_base_ref() -> str:
    try:
        idx = sys.argv.index("--base")
    except ValueError:
        return "origin/main"
    return sys.argv[idx + 1] if idx + 1 < len(sys.argv) else "origin/main"


def canonical_fragment_slugs(ref: str) -> set[str]:
    slugs: set[str] = set()
    for root in base.FRAGMENT_ROOTS:
        for path in base.git_paths(ref, root):
            if not path.endswith(".json"):
                continue
            raw = base.git_show(ref, path)
            if raw is None:
                continue
            try:
                payload = json.loads(raw)
            except Exception:
                continue
            records = payload if isinstance(payload, list) else [payload]
            for record in records:
                if isinstance(record, dict):
                    key = base.key_of(record)
                    if key:
                        slugs.add(key)
    return slugs


BASE_REF = cli_base_ref()
FRAGMENT_SLUGS = canonical_fragment_slugs(BASE_REF)

# Usa o base SHA REAL do PR para isolar apenas a contribuição daquele PR.
pr_bases_path = os.environ.get("CORVIA_PR_BASES_JSON", "").strip()
PR_BASES: dict[int, str] = {}
if pr_bases_path:
    payload = json.loads(Path(pr_bases_path).read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        PR_BASES = {int(key): str(value) for key, value in payload.items() if value}

_original_merge_base = base.merge_base
_original_validate = base.validate_record
_original_likely_duplicate = base.likely_duplicate


def actual_pr_base(fallback_base: str, ref: str) -> str:
    match = re.search(r"/(\d+)$", ref)
    if match:
        number = int(match.group(1))
        sha = PR_BASES.get(number)
        if sha and base.git_ref_exists(sha):
            return sha
    return _original_merge_base(fallback_base, ref)


def validate_record(kind: str, record):
    ok, reason = _original_validate(kind, record)
    if not ok:
        return ok, reason
    key = base.key_of(record) if isinstance(record, dict) else None
    if kind in {"doencas", "triagem"} and key and key in FRAGMENT_SLUGS:
        return False, "slug já existe como fragmento canônico no baseline"
    return True, ""


def likely_duplicate(kind: str, candidate, existing) -> bool:
    if _original_likely_duplicate(kind, candidate, existing):
        return True
    if kind == "estudos" and (base.source_signature(candidate) & base.source_signature(existing)):
        return True
    return False


base.merge_base = actual_pr_base
base.validate_record = validate_record
base.likely_duplicate = likely_duplicate

if __name__ == "__main__":
    raise SystemExit(base.main())
