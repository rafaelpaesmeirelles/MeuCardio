"""Leitura canônica do catálogo de doenças com fragmentos aditivos.

`doencas/metadados.json` permanece a base histórica. Novos hubs podem ser
versionados em `doencas/fragmentos/*.json` para reduzir colisões entre frentes
paralelas. A combinação é determinística e falha diante de slug duplicado.
"""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
from typing import Any


def _read_list(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"{path}: manifesto deve ser uma lista JSON")
    invalid = [index for index, item in enumerate(payload) if not isinstance(item, dict)]
    if invalid:
        raise ValueError(f"{path}: itens não-objeto nos índices {invalid}")
    return list(payload)


def disease_fragment_paths(base_manifest: str | Path) -> list[Path]:
    base = Path(base_manifest)
    directory = base.parent / "fragmentos"
    if not directory.exists():
        return []
    return sorted(path for path in directory.glob("*.json") if path.is_file())


def load_disease_records(base_manifest: str | Path) -> list[dict[str, Any]]:
    base = Path(base_manifest)
    records = _read_list(base)
    for fragment in disease_fragment_paths(base):
        records.extend(_read_list(fragment))

    slugs = [str(item.get("slug") or "").strip() for item in records]
    invalid = [index for index, slug in enumerate(slugs) if not slug]
    if invalid:
        raise ValueError(f"Catálogo de doenças contém slug vazio nos índices {invalid}")

    duplicates = sorted(slug for slug, count in Counter(slugs).items() if count > 1)
    if duplicates:
        raise ValueError(f"Catálogo de doenças contém slugs duplicados: {duplicates}")
    return records
