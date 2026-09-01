"""Carrega os fluxos versionados de triagem por sintomas.

O manifesto histórico continua em ``triagem-sintomas/metadados.json``.
Snapshots/fragmentos aditivos permitem reconciliar produção paralela sem
sobrescrever o array compartilhado; correções editoriais pequenas são aplicadas
depois da composição.
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

from app.core.db import SessionLocal
from app.models.specialty_guide import SymptomTriageGuide
from app.services.clinical_rule_engine import validate_question_definitions, validate_rule_definitions
from app.services.scientific_loader_safety import (
    combined_review_note,
    enforce_safe_publication,
)

CAMPOS = {"slug", "name", "aliases", "areas", "summary", "questions", "rules", "default_tests", "differentials", "red_flags", "ambulatory_flow", "emergency_flow", "tags", "source_refs", "source_urls", "review_status", "review_note", "version"}
AREAS = {"geral", "cardiopediatria", "cardiogeriatria", "cardiooncologia", "gravidez"}
REVIEW = {"pendente_revisao", "revisado", "lacuna_declarada"}


def _valid_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _read_list(path: Path) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list) or any(not isinstance(item, dict) for item in payload):
        raise ValueError(f"{path}: manifesto deve ser uma lista de objetos")
    return payload


def load_triage_records(caminho_json: str | Path) -> list[dict]:
    base = Path(caminho_json)
    records = [copy.deepcopy(item) for item in _read_list(base)]
    by_slug: dict[str, dict] = {}
    ordered: list[str] = []
    for item in records:
        slug = str(item.get("slug") or "").strip()
        if not slug or slug in by_slug:
            raise ValueError(f"{base}: slug vazio ou duplicado: {slug or '?'}")
        by_slug[slug] = item; ordered.append(slug)
    fragments_dir = base.parent / "fragmentos"
    if fragments_dir.exists():
        for path in sorted(fragments_dir.glob("*.json")):
            for item in _read_list(path):
                slug = str(item.get("slug") or "").strip()
                if not slug: raise ValueError(f"{path}: registro sem slug")
                existing = by_slug.get(slug)
                if existing is None:
                    by_slug[slug] = copy.deepcopy(item); ordered.append(slug)
                elif existing != item:
                    raise ValueError(f"{path}: slug {slug} diverge do registro já composto")
    corrections_dir = base.parent / "correcoes"
    if corrections_dir.exists():
        for path in sorted(corrections_dir.glob("*.json")):
            for correction in _read_list(path):
                slug = str(correction.get("slug") or "").strip()
                if not slug or slug not in by_slug: raise ValueError(f"{path}: correção aponta para slug inexistente: {slug or '?'}")
                set_values = correction.get("set") or {}
                if not isinstance(set_values, dict): raise ValueError(f"{path}:{slug}: set deve ser objeto")
                for key, value in set_values.items(): by_slug[slug][key] = copy.deepcopy(value)
    return [by_slug[slug] for slug in ordered]


def carregar(caminho_json: str) -> dict:
    try:
        items = load_triage_records(caminho_json)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return {"erros": [str(exc)]}
    db = SessionLocal(); novos = atualizados = 0; erros: list[str] = []
    try:
        for raw in items:
            item = {
                key: value
                for key, value in raw.items()
                if key in CAMPOS and key != "review_note"
            }
            slug = str(item.get("slug") or "").strip()
            if not slug or not str(item.get("name") or "").strip() or not str(item.get("summary") or "").strip(): erros.append(f"{slug or '?'}: slug, name e summary são obrigatórios"); continue
            areas = item.get("areas") or []
            if not areas or any(area not in AREAS for area in areas): erros.append(f"{slug}: áreas inválidas"); continue
            if item.get("review_status", "pendente_revisao") not in REVIEW: erros.append(f"{slug}: review_status inválido"); continue
            if any(not isinstance(url, str) or not _valid_url(url) for url in item.get("source_urls") or []): erros.append(f"{slug}: source_urls contém URL inválida"); continue
            if item.get("review_status") == "revisado" and not item.get("source_refs"): erros.append(f"{slug}: conteúdo revisado sem referência"); continue
            question_errors, question_ids = validate_question_definitions(slug, item.get("questions") or [])
            rule_errors = validate_rule_definitions(slug, item.get("rules") or [], question_ids)
            if question_errors or rule_errors: erros.extend(question_errors + rule_errors); continue
            existing = db.query(SymptomTriageGuide).filter(SymptomTriageGuide.slug == slug).first()
            note = combined_review_note(
                raw,
                existing=getattr(existing, "review_note", None),
            )
            if note is not None:
                item["review_note"] = note
            if existing:
                for field, value in item.items(): setattr(existing, field, value)
                enforce_safe_publication(existing, raw, is_new=False)
                atualizados += 1
            else:
                record = SymptomTriageGuide(**item)
                enforce_safe_publication(record, raw, is_new=True)
                db.add(record)
                novos += 1
        if erros: db.rollback()
        else: db.commit()
    finally: db.close()
    result = {"novos": novos, "atualizados": atualizados}
    if erros: result["erros"] = erros
    return result


if __name__ == "__main__":
    if len(sys.argv) != 2: print(__doc__); raise SystemExit(1)
    print(json.dumps(carregar(sys.argv[1]), ensure_ascii=False, indent=2))
