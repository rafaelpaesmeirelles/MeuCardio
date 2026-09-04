#!/usr/bin/env python3
"""Entrada v3 do reconciliador científico.

Além da correção v2 para o falso positivo da palavra portuguesa ``todo``:
- não reapresenta no manifesto base uma doença/triagem que já existe como
  fragmento canônico na main;
- em ``estudos``, um PMID/DOI/NCT já existente identifica a mesma publicação,
  ainda que uma branch antiga use outro slug/título.

Essas duas regras impedem os erros estruturais encontrados pelo gate da v2
sem relaxar a validação científica.
"""
from __future__ import annotations

import json
import re
import sys

import reconcile_open_science_prs as base

# Marcadores técnicos continuam sensíveis a maiúsculas; expressões editoriais
# reais permanecem case-insensitive.
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
_original_validate = base.validate_record
_original_likely_duplicate = base.likely_duplicate


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
    if kind == "estudos":
        shared = base.source_signature(candidate) & base.source_signature(existing)
        # Para estudos, PMID/DOI/NCT são identidade bibliográfica. Compartilhar
        # qualquer um desses identificadores é suficiente para não criar uma
        # segunda publicação com outro slug.
        if shared:
            return True
    return False


base.validate_record = validate_record
base.likely_duplicate = likely_duplicate

if __name__ == "__main__":
    raise SystemExit(base.main())
