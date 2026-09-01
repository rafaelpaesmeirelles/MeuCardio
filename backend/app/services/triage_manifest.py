"""Composição canônica e sem dependências do catálogo de triagem.

O módulo permanece deliberadamente livre de banco, ORM e serviços da aplicação
para que os gates de inventário/publicação possam executá-lo no runner mínimo
do GitHub Actions. O loader persistente importa esta mesma função, evitando
duas interpretações diferentes do corpus.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path


def _read_list(path: Path) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list) or any(not isinstance(item, dict) for item in payload):
        raise ValueError(f"{path}: manifesto deve ser uma lista de objetos")
    return payload


def load_triage_records(base_manifest: str | Path) -> list[dict]:
    """Carrega base, fragmentos aditivos e correções na ordem canônica."""

    base = Path(base_manifest)
    records = [copy.deepcopy(item) for item in _read_list(base)]
    by_slug: dict[str, dict] = {}
    ordered: list[str] = []

    for item in records:
        slug = str(item.get("slug") or "").strip()
        if not slug or slug in by_slug:
            raise ValueError(f"{base}: slug vazio ou duplicado: {slug or '?'}")
        by_slug[slug] = item
        ordered.append(slug)

    fragments_dir = base.parent / "fragmentos"
    if fragments_dir.exists():
        for path in sorted(fragments_dir.glob("*.json")):
            for item in _read_list(path):
                slug = str(item.get("slug") or "").strip()
                if not slug:
                    raise ValueError(f"{path}: registro sem slug")
                existing = by_slug.get(slug)
                if existing is None:
                    by_slug[slug] = copy.deepcopy(item)
                    ordered.append(slug)
                elif existing != item:
                    raise ValueError(f"{path}: slug {slug} diverge do registro já composto")

    corrections_dir = base.parent / "correcoes"
    if corrections_dir.exists():
        for path in sorted(corrections_dir.glob("*.json")):
            for correction in _read_list(path):
                slug = str(correction.get("slug") or "").strip()
                if not slug or slug not in by_slug:
                    raise ValueError(
                        f"{path}: correção aponta para slug inexistente: {slug or '?'}"
                    )
                set_values = correction.get("set") or {}
                if not isinstance(set_values, dict):
                    raise ValueError(f"{path}:{slug}: set deve ser objeto")
                for key, value in set_values.items():
                    by_slug[slug][key] = copy.deepcopy(value)

    return [by_slug[slug] for slug in ordered]
