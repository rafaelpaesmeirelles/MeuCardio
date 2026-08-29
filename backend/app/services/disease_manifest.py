"""Leitura canônica do catálogo de doenças com composição auditável.

`doencas/metadados.json` permanece a base histórica. Novos hubs podem ser
versionados em `doencas/fragmentos/*.json` para reduzir colisões entre frentes
paralelas. Snapshots legados em `doencas/snapshots/*.json` são reconciliados
contra o blob-base: somente registros que realmente divergem da base são
aplicados, permitindo combinar produções antigas sobre o mesmo manifesto sem
um snapshot reverter alterações independentes de outro. Correções pequenas e
auditáveis são aplicadas por `doencas/correcoes/*.json` ao final da composição.
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


def disease_snapshot_paths(base_manifest: str | Path) -> list[Path]:
    return _paths(base_manifest, "snapshots")


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


def _append_unique(record: dict[str, Any], append_values: Any, *, label: str) -> None:
    if not isinstance(append_values, dict):
        raise ValueError(f"{label}: append deve ser objeto")
    for field, values in append_values.items():
        if not isinstance(values, list):
            raise ValueError(f"{label}:{field}: append exige lista")
        target = record.get(field)
        if target is None:
            target = []
            record[field] = target
        if not isinstance(target, list):
            raise ValueError(f"{label}:{field}: campo alvo não é lista")
        for value in values:
            copied = copy.deepcopy(value)
            if copied not in target:
                target.append(copied)


def _canonicalize_assistant_questions(record: dict[str, Any], *, slug: str) -> None:
    """Converte o legado ``text`` para o contrato canônico ``label``."""
    questions = record.get("assistant_questions")
    if questions is None:
        return
    if not isinstance(questions, list):
        raise ValueError(f"{slug}: assistant_questions deve ser lista")
    for index, question in enumerate(questions):
        if not isinstance(question, dict):
            raise ValueError(f"{slug}: assistant_questions[{index}] deve ser objeto")
        if "text" not in question:
            continue
        legacy = question.pop("text")
        current = question.get("label")
        if current is not None and current != legacy:
            raise ValueError(
                f"{slug}: assistant_questions[{index}] possui text/label divergentes"
            )
        if current is None:
            if not isinstance(legacy, str) or not legacy.strip():
                raise ValueError(
                    f"{slug}: assistant_questions[{index}].text legado não é string válida"
                )
            question["label"] = legacy


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

            append_values = correction.get("append") or {}
            if append_values:
                _append_unique(record, append_values, label=f"{path}:{slug}")

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

    base_by_slug = {slug: copy.deepcopy(item) for slug, item in by_slug.items()}

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

    snapshot_updates: dict[str, dict[str, Any]] = {}
    for snapshot in disease_snapshot_paths(base):
        for item in _read_list(snapshot):
            slug = str(item.get("slug") or "").strip()
            if not slug or slug not in base_by_slug:
                raise ValueError(
                    f"{snapshot}: snapshot só pode alterar slug existente na base: {slug or '?'}"
                )
            if item == base_by_slug[slug]:
                continue
            previous = snapshot_updates.get(slug)
            if previous is not None and previous != item:
                raise ValueError(
                    f"{snapshot}: colisão de snapshots divergentes para o slug {slug}"
                )
            copied = copy.deepcopy(item)
            snapshot_updates[slug] = copied
            by_slug[slug] = copied

    _apply_corrections(by_slug, base)
    for slug in ordered_slugs:
        _canonicalize_assistant_questions(by_slug[slug], slug=slug)
    return [by_slug[slug] for slug in ordered_slugs]
