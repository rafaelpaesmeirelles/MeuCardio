#!/usr/bin/env python3
"""Inventário reprodutível do corpus científico versionado.

O objetivo é detectar duas classes de regressão:
1. arquivos removidos ou não montados no deploy;
2. coleções JSON reduzidas silenciosamente.

O script não lê banco, não altera conteúdo e não imprime dados clínicos de pacientes.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

SOURCES: dict[str, dict[str, str]] = {
    "documentos": {"directory": "content", "kind": "markdown"},
    "galeria": {"directory": "galeria", "manifest": "metadados.json"},
    "exames": {"directory": "exames", "manifest": "metadados.json"},
    "evidencias": {"directory": "evidencias", "manifest": "metadados.json"},
    "estudos": {"directory": "estudos", "manifest": "metadados.json"},
    "medicamentos": {"directory": "medicamentos", "manifest": "metadados.json"},
    "checklists": {"directory": "checklists", "manifest": "metadados.json"},
    "trilhas": {"directory": "trilhas", "manifest": "metadados.json"},
    "material_paciente": {"directory": "material-paciente", "manifest": "metadados.json"},
    "emergencia": {"directory": "emergencia", "manifest": "metadados.json"},
    "casos_clinicos": {"directory": "casos-clinicos", "manifest": "metadados.json"},
    "controlados": {"directory": "controlados", "manifest": "metadados.json"},
}

LIST_KEYS = (
    "items",
    "records",
    "registros",
    "dados",
    "documents",
    "documentos",
    "entries",
    "conteudo",
)


def _records(payload: Any) -> list[Any]:
    if isinstance(payload, list):
        return payload
    if not isinstance(payload, dict):
        return []

    for key in LIST_KEYS:
        value = payload.get(key)
        if isinstance(value, list):
            return value

    list_values = [value for value in payload.values() if isinstance(value, list)]
    if len(list_values) == 1:
        return list_values[0]

    if payload and all(isinstance(value, dict) for value in payload.values()):
        return list(payload.values())
    return []


def _slug(item: Any) -> str | None:
    if not isinstance(item, dict):
        return None
    for key in ("slug", "id", "codigo", "name", "nome", "title", "titulo"):
        value = item.get(key)
        if isinstance(value, (str, int)) and str(value).strip():
            return str(value).strip()
    return None


def _file_inventory(directory: Path) -> tuple[int, int]:
    if not directory.exists():
        return 0, 0
    files = [path for path in directory.rglob("*") if path.is_file()]
    return len(files), sum(path.stat().st_size for path in files)


def inventory() -> dict[str, Any]:
    fronts: dict[str, Any] = {}
    total_files = 0
    total_records = 0
    missing: list[str] = []
    invalid: list[str] = []

    for name, config in SOURCES.items():
        directory = ROOT / config["directory"]
        file_count, byte_count = _file_inventory(directory)
        total_files += file_count

        result: dict[str, Any] = {
            "directory": config["directory"],
            "files": file_count,
            "bytes": byte_count,
            "records": 0,
            "duplicate_keys": [],
        }

        if not directory.exists():
            missing.append(config["directory"])
            fronts[name] = result
            continue

        if config.get("kind") == "markdown":
            markdown = sorted(directory.rglob("*.md"))
            result["records"] = len(markdown)
            total_records += len(markdown)
            fronts[name] = result
            continue

        manifest = directory / config.get("manifest", "metadados.json")
        if not manifest.exists():
            missing.append(str(manifest.relative_to(ROOT)))
            fronts[name] = result
            continue

        try:
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            records = _records(payload)
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            invalid.append(f"{manifest.relative_to(ROOT)}: {type(exc).__name__}")
            fronts[name] = result
            continue

        keys: dict[str, int] = {}
        for item in records:
            key = _slug(item)
            if key is not None:
                keys[key] = keys.get(key, 0) + 1

        duplicates = sorted(key for key, count in keys.items() if count > 1)
        result["records"] = len(records)
        result["duplicate_keys"] = duplicates[:100]
        result["manifest"] = str(manifest.relative_to(ROOT))
        total_records += len(records)
        fronts[name] = result

    return {
        "total_files": total_files,
        "total_records": total_records,
        "fronts": fronts,
        "missing": missing,
        "invalid": invalid,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--minimum-records", type=int, default=0)
    parser.add_argument("--minimum-files", type=int, default=0)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    result = inventory()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))

    failed = False
    if result["total_records"] < args.minimum_records:
        print(
            f"Corpus reduzido: {result['total_records']} registros; mínimo {args.minimum_records}.",
            file=sys.stderr,
        )
        failed = True
    if result["total_files"] < args.minimum_files:
        print(
            f"Arquivos reduzidos: {result['total_files']}; mínimo {args.minimum_files}.",
            file=sys.stderr,
        )
        failed = True
    if args.strict and (result["missing"] or result["invalid"]):
        print("Corpus incompleto ou inválido.", file=sys.stderr)
        failed = True
    if args.strict:
        duplicates = {
            name: data["duplicate_keys"]
            for name, data in result["fronts"].items()
            if data["duplicate_keys"]
        }
        if duplicates:
            print(f"Chaves duplicadas no corpus: {duplicates}", file=sys.stderr)
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
