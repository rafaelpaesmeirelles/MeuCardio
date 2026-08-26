"""Carrega o catálogo versionado de doenças especializadas."""

from __future__ import annotations

import json
import sys
from urllib.parse import urlparse

from app.core.db import SessionLocal
from app.models.specialty_guide import SpecialtyDisease
from app.services.clinical_rule_engine import (
    validate_question_definitions,
    validate_rule_definitions,
)

CAMPOS = {
    "slug", "name", "aliases", "area", "category", "subtype", "cyanosis_class",
    "prevalence_rank", "completeness", "summary", "epidemiology", "presentation",
    "diagnostic_approach", "differentials", "tests", "red_flags", "ambulatory_flow",
    "emergency_flow", "treatment_summary", "monitoring", "special_populations",
    "assistant_questions", "assistant_rules", "tags", "source_refs", "source_urls",
    "related_document_slugs", "patient_material_slug", "review_status", "review_note",
    "version",
}

AREAS = {"geral", "cardiopediatria", "cardiogeriatria", "cardiooncologia", "gravidez"}
CYANOSIS = {None, "cianotica", "acianotica", "nao_aplicavel"}
COMPLETENESS = {"basico", "intermediario", "completo"}
REVIEW = {"pendente_revisao", "revisado", "lacuna_declarada"}


def _valid_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def carregar(caminho_json: str) -> dict:
    with open(caminho_json, encoding="utf-8") as arquivo:
        items = json.load(arquivo)
    if not isinstance(items, list):
        return {"erros": ["O manifesto deve ser uma lista JSON."]}

    db = SessionLocal()
    novos = atualizados = 0
    erros: list[str] = []
    try:
        for raw in items:
            if not isinstance(raw, dict):
                erros.append("Item do catálogo não é objeto.")
                continue
            item = {key: value for key, value in raw.items() if key in CAMPOS}
            slug = str(item.get("slug") or "").strip()
            name = str(item.get("name") or "").strip()
            summary = str(item.get("summary") or "").strip()
            if not slug or not name or not summary:
                erros.append(f"{slug or '?'}: slug, name e summary são obrigatórios")
                continue
            if item.get("area") not in AREAS:
                erros.append(f"{slug}: área inválida")
                continue
            if item.get("cyanosis_class") not in CYANOSIS:
                erros.append(f"{slug}: cyanosis_class inválida")
                continue
            if item.get("completeness", "basico") not in COMPLETENESS:
                erros.append(f"{slug}: completeness inválida")
                continue
            if item.get("review_status", "pendente_revisao") not in REVIEW:
                erros.append(f"{slug}: review_status inválido")
                continue
            urls = item.get("source_urls") or []
            if any(not isinstance(url, str) or not _valid_url(url) for url in urls):
                erros.append(f"{slug}: source_urls contém URL inválida")
                continue
            if item.get("review_status") == "revisado" and not item.get("source_refs"):
                erros.append(f"{slug}: conteúdo revisado sem referência")
                continue

            questions = item.get("assistant_questions") or []
            question_errors, question_ids = validate_question_definitions(slug, questions)
            rule_errors = validate_rule_definitions(
                slug,
                item.get("assistant_rules") or [],
                question_ids,
            )
            if question_errors or rule_errors:
                erros.extend(question_errors + rule_errors)
                continue

            existing = db.query(SpecialtyDisease).filter(SpecialtyDisease.slug == slug).first()
            if existing:
                for field, value in item.items():
                    setattr(existing, field, value)
                atualizados += 1
            else:
                db.add(SpecialtyDisease(**item))
                novos += 1
        if erros:
            db.rollback()
        else:
            db.commit()
    finally:
        db.close()

    result = {"novos": novos, "atualizados": atualizados}
    if erros:
        result["erros"] = erros
    return result


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        raise SystemExit(1)
    print(json.dumps(carregar(sys.argv[1]), ensure_ascii=False, indent=2))
