#!/usr/bin/env python3
"""Fail closed when deduplicated studies could be reintroduced by staging replay."""

from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any, Iterator


ROOT = Path(__file__).resolve().parents[1]
CANONICAL_PATH = ROOT / "estudos" / "metadados.json"
APPROVAL_PATH = ROOT / "editorial-approvals" / "grok-science-overnight-20260829.json"
TARGETS = (
    {
        "batch": ROOT / ".science-staging" / "lote-select-sglt2-drc.json",
        "old_slug": "select-lincoff-semaglutida-24mg-mace-obesidade-sem-diabetes",
        "new_slug": "select-semaglutida-desfechos-cardiovasculares-obesidade-sem-diabetes",
        "pmid": "37952131",
        "doi": "10.1056/NEJMoa2307563",
    },
    {
        "batch": ROOT / ".science-staging" / "lote-hf-incretina.json",
        "old_slug": "summit-tirzepatida-icfep-com-obesidade",
        "new_slug": "tirzepatida-e-icfep-com-obesidade-o-ensaio-summit",
        "pmid": "39555826",
        "doi": "10.1056/NEJMoa2410027",
    },
)


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def nested_document_slugs(value: Any) -> Iterator[str]:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in {"document_slug", "documento_slug"} and isinstance(child, str):
                yield child
            yield from nested_document_slugs(child)
    elif isinstance(value, list):
        for child in value:
            yield from nested_document_slugs(child)


def content_slugs() -> set[str]:
    slugs: set[str] = set()
    slug_pattern = re.compile(r"^slug:\s*[\"']?([^\"'\n]+?)[\"']?\s*$", re.MULTILINE)
    for path in (ROOT / "content").rglob("*.md"):
        match = slug_pattern.search(path.read_text(encoding="utf-8"))
        if match:
            slugs.add(match.group(1).strip())
    return slugs


def assert_batch_links(batch: dict[str, Any], known_slugs: set[str]) -> None:
    for document in batch.get("documentos", []):
        document_path = ROOT / document["path"]
        assert document_path.is_file(), f"documento ausente: {document_path}"
        text = document_path.read_text(encoding="utf-8")
        declared_slug = re.search(
            r"^slug:\s*[\"']?([^\"'\n]+?)[\"']?\s*$", text, re.MULTILINE
        )
        assert declared_slug, f"frontmatter sem slug: {document_path}"
        assert declared_slug.group(1).strip() == document["slug"], (
            f"slug divergente em {document_path}: {document['slug']}"
        )

    missing = sorted(set(nested_document_slugs(batch)) - known_slugs)
    assert not missing, f"document_slug/documento_slug sem conteúdo: {missing}"


def main() -> None:
    canonical = load_json(CANONICAL_PATH)
    canonical_by_slug = {study["slug"]: study for study in canonical}
    assert len(canonical_by_slug) == len(canonical), "slugs duplicados no corpus de estudos"

    approval = load_json(APPROVAL_PATH)
    approved_studies = approval["fronts"]["estudos"]
    assert len(approved_studies) == len(set(approved_studies)), (
        "fronts.estudos contém slugs duplicados"
    )
    migrations = approval.get("canonical_slug_migrations", [])
    known_slugs = content_slugs()

    checked: list[dict[str, str]] = []
    for target in TARGETS:
        old_slug = target["old_slug"]
        new_slug = target["new_slug"]
        canonical_study = canonical_by_slug.get(new_slug)
        assert canonical_study is not None, f"canônico ausente: {new_slug}"

        same_pmid = [study for study in canonical if study.get("pmid") == target["pmid"]]
        assert [study["slug"] for study in same_pmid] == [new_slug], (
            f"PMID {target['pmid']} não resolve unicamente para {new_slug}"
        )
        assert canonical_study.get("doi") == target["doi"], f"DOI divergente: {new_slug}"

        batch = load_json(target["batch"])
        assert_batch_links(batch, known_slugs)
        staged = batch.get("estudos", [])
        staged_by_slug = {study["slug"]: study for study in staged}
        assert len(staged_by_slug) == len(staged), f"slugs repetidos em {target['batch']}"
        assert old_slug not in staged_by_slug, f"duplicata antiga no staging: {old_slug}"
        assert staged_by_slug.get(new_slug) == canonical_study, (
            f"staging não é cópia exata do canônico: {new_slug}"
        )

        replayed = deepcopy(canonical_by_slug)
        count_before = len(replayed)
        for study in staged:
            replayed[study["slug"]] = study
        assert len(replayed) == count_before, (
            f"replay criaria novo estudo em vez de atualizar identidade canônica: {new_slug}"
        )
        assert replayed[new_slug] == canonical_study, f"replay sobrescreveria {new_slug}"
        assert old_slug not in replayed, f"replay reintroduziria {old_slug}"

        assert new_slug in approved_studies, f"aprovação não referencia {new_slug}"
        assert old_slug not in approved_studies, f"aprovação ainda referencia {old_slug}"
        expected_migration = {
            "front": "estudos",
            "old_slug": old_slug,
            "new_slug": new_slug,
            "pmid": target["pmid"],
            "doi": target["doi"],
        }
        assert migrations.count(expected_migration) == 1, (
            f"migração auditável ausente ou duplicada: {old_slug} -> {new_slug}"
        )
        checked.append({"slug": new_slug, "pmid": target["pmid"]})

    assert len(migrations) == len(TARGETS), "canonical_slug_migrations contém entrada inesperada"
    print(json.dumps({"status": "ok", "checked": checked}, ensure_ascii=False))


if __name__ == "__main__":
    main()
