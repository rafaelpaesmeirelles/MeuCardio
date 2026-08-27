"""Leitura canônica do catálogo de doenças com fragmentos e correções aditivas.

`doencas/metadados.json` permanece a base histórica. Novos hubs podem ser
versionados em `doencas/fragmentos/*.json` para reduzir colisões entre frentes
paralelas. Um fragmento pode ser um recorte mínimo ou um snapshot histórico do
manifesto: registros já existentes e idênticos são ignorados; divergências em
slug existente são bloqueadas. Correções pequenas e auditáveis podem ser
aplicadas por `doencas/correcoes/*.json` depois da composição.
"""

from __future__ import annotations

import copy
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


def _paths(base_manifest: str | Path, directory_name: str) -> list[Path]:
    base = Path(base_manifest)
    directory = base.parent / directory_name
    if not directory.exists():
        return []
    return sorted(path for path in directory.glob("*.json") if path.is_file())


def disease_fragment_paths(base_manifest: str | Path) -> list[Path]:
    return _paths(base_manifest, "fragmentos")


def disease_correction_paths(base_manifest: str | Path) -> list[Path]:
    return _paths(base_manifest, "correcoes")


def _replace_recursive(value: Any, old: str, new: str) -> Any:
    if isinstance(value, str):
        return value.replace(old, new)
    if isinstance(value, list):
        return [_replace_recursive(item, old, new) for item in value]
    if isinstance(value, dict):
        return {key: _replace_recursive(item, old, new) for key, item in value.items()}
    return value


def _merge_by_id(items: Any, updates: dict[str, dict[str, Any]], *, label: str) -> None:
    if not isinstance(items, list):
        raise ValueError(f"{label}: coleção alvo não é lista")
    by_id = {
        str(item.get("id")): item
        for item in items
        if isinstance(item, dict) and item.get("id") is not None
    }
    missing = sorted(identifier for identifier in updates if identifier not in by_id)
    if missing:
        raise ValueError(f"{label}: ids inexistentes para correção: {missing}")
    for identifier, patch in updates.items():
        if not isinstance(patch, dict):
            raise ValueError(f"{label}:{identifier}: correção deve ser objeto")
        by_id[identifier].update(copy.deepcopy(patch))


def _add_by_id(items: Any, additions: Any, *, label: str) -> None:
    if not isinstance(items, list):
        raise ValueError(f"{label}: coleção alvo não é lista")
    if not isinstance(additions, list):
        raise ValueError(f"{label}: adições devem ser lista")
    existing = {
        str(item.get("id"))
        for item in items
        if isinstance(item, dict) and item.get("id") is not None
    }
    for item in additions:
        if not isinstance(item, dict) or not str(item.get("id") or "").strip():
            raise ValueError(f"{label}: toda adição deve ser objeto com id")
        identifier = str(item["id"])
        if identifier in existing:
            raise ValueError(f"{label}: id duplicado na adição: {identifier}")
        items.append(copy.deepcopy(item))
        existing.add(identifier)


def _apply_corrections(
    records_by_slug: dict[str, dict[str, Any]],
    base_manifest: Path,
) -> None:
    for path in disease_correction_paths(base_manifest):
        corrections = _read_list(path)
        for correction in corrections:
            slug = str(correction.get("slug") or "").strip()
            if not slug or slug not in records_by_slug:
                raise ValueError(f"{path}: correção aponta para slug inexistente: {slug or '?'}")
            record = records_by_slug[slug]

            set_values = correction.get("set") or {}
            if not isinstance(set_values, dict):
                raise ValueError(f"{path}:{slug}: set deve ser objeto")
            for key, value in set_values.items():
                record[key] = copy.deepcopy(value)

            replacements = correction.get("replace") or []
            if not isinstance(replacements, list):
                raise ValueError(f"{path}:{slug}: replace deve ser lista")
            for operation in replacements:
                if not isinstance(operation, dict):
                    raise ValueError(f"{path}:{slug}: replace contém item inválido")
                old = operation.get("old")
                new = operation.get("new")
                if not isinstance(old, str) or not isinstance(new, str) or not old:
                    raise ValueError(f"{path}:{slug}: replace exige old/new strings")
                before = json.dumps(record, ensure_ascii=False, sort_keys=True)
                record = _replace_recursive(record, old, new)
                after = json.dumps(record, ensure_ascii=False, sort_keys=True)
                if before == after:
                    raise ValueError(f"{path}:{slug}: texto de correção não encontrado: {old[:80]}")
                records_by_slug[slug] = record

            rule_updates = correction.get("assistant_rules") or {}
            if rule_updates:
                if not isinstance(rule_updates, dict):
                    raise ValueError(f"{path}:{slug}: assistant_rules deve ser objeto por id")
                _merge_by_id(record.get("assistant_rules"), rule_updates, label=f"{path}:{slug}:assistant_rules")

            question_updates = correction.get("assistant_questions") or {}
            if question_updates:
                if not isinstance(question_updates, dict):
                    raise ValueError(f"{path}:{slug}: assistant_questions deve ser objeto por id")
                _merge_by_id(record.get("assistant_questions"), question_updates, label=f"{path}:{slug}:assistant_questions")

            rule_additions = correction.get("assistant_rules_add") or []
            if rule_additions:
                _add_by_id(record.get("assistant_rules"), rule_additions, label=f"{path}:{slug}:assistant_rules_add")

            question_additions = correction.get("assistant_questions_add") or []
            if question_additions:
                _add_by_id(record.get("assistant_questions"), question_additions, label=f"{path}:{slug}:assistant_questions_add")


def load_disease_records(base_manifest: str | Path) -> list[dict[str, Any]]:
    base = Path(base_manifest)
    records = [copy.deepcopy(item) for item in _read_list(base)]
    by_slug: dict[str, dict[str, Any]] = {}
    ordered_slugs: list[str] = []

    for index, item in enumerate(records):
        slug = str(item.get("slug") or "").strip()
        if not slug:
            raise ValueError(f"Catálogo-base contém slug vazio no índice {index}")
        if slug in by_slug:
            raise ValueError(f"Catálogo-base contém slug duplicado: {slug}")
        by_slug[slug] = item
        ordered_slugs.append(slug)

    for fragment in disease_fragment_paths(base):
        for item in _read_list(fragment):
            slug = str(item.get("slug") or "").strip()
            if not slug:
                raise ValueError(f"{fragment}: item sem slug")
            existing = by_slug.get(slug)
            if existing is None:
                copied = copy.deepcopy(item)
                by_slug[slug] = copied
                ordered_slugs.append(slug)
                continue
            if existing != item:
                raise ValueError(
                    f"{fragment}: slug {slug} diverge de registro já composto; "
                    "use doencas/correcoes para alterações explícitas"
                )

    _apply_corrections(by_slug, base)
    return [by_slug[slug] for slug in ordered_slugs]
