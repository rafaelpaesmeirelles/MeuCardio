#!/usr/bin/env python3
"""Build and validate the audited science release approval from review trees."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "editorial-approvals" / "science-release-20260901.json"

BASE = "e16c73c0cce7df78b332768587ae73d4c0c0f583"
PR_HEAD = "ce40e82283e3a7e3fe21cb4958055b7a90066ddf"
COMMON_REVIEW_BASE = "8226e364aa140631b656226db9d2b0cf56ac8c1a"
MARKDOWN_REVIEW_BASE = "2411c3dde9739129acd9c7fb3c9dee8271581f86"

REVIEW_HEADS = {
    "estudos": "30edf7104f9034fa201ebb7a4eb2766843eafc61",
    "evidencias": "7dc84eb35fb9b76f80662874d40714c0dc63986c",
    "doencas": "250f659870c49b22385f1b3e59becdebc5d84d9d",
    "operacional": "54678846601afa441797bfd861600fda1ec9d62b",
    "documentos_markdown": "c81d987daab672bd614e76c82a9e7edfc9b61bfc",
}
REVIEW_DIFF_BASES = {
    "estudos": COMMON_REVIEW_BASE,
    "evidencias": COMMON_REVIEW_BASE,
    "doencas": COMMON_REVIEW_BASE,
    "operacional": COMMON_REVIEW_BASE,
    "documentos_markdown": MARKDOWN_REVIEW_BASE,
}

JSON_FRONTS = {
    "estudos": ("estudos", "estudos/metadados.json"),
    "evidencias": ("evidencias", "evidencias/metadados.json"),
    "doencas_especializadas": ("doencas", "doencas/metadados.json"),
    "casos_clinicos": ("operacional", "casos-clinicos/metadados.json"),
    "checklists": ("operacional", "checklists/metadados.json"),
    "material_paciente": ("operacional", "material-paciente/metadados.json"),
    "trilhas": ("operacional", "trilhas/metadados.json"),
    "triagem_sintomas": ("operacional", "triagem-sintomas/metadados.json"),
}
EXPECTED_FRONT_COUNTS = {
    "documentos": 89,
    "estudos": 181,
    "evidencias": 174,
    "doencas_especializadas": 161,
    "casos_clinicos": 28,
    "checklists": 50,
    "material_paciente": 15,
    "trilhas": 24,
    "triagem_sintomas": 3,
}
EXPECTED_TOTAL = 725
OPERATIONAL_INTEGRITY_ONLY: dict[str, set[str]] = {}
EXPECTED_DELETED_STUDY_ALIASES = {
    "advor-acetazolamida-diuretico-ic-aguda-descompensada",
    "clorotic-hidroclorotiazida-associada-a-diuretico-de-alca-na-ic-aguda",
    "deliver-dapagliflozina-icfep",
    "finearts-hf-finerenona-na-icfem-e-icfep",
    "paragon-hf-sacubitril-valsartana-na-icfep",
    "peitho-fibrinolise-em-tep-de-risco-intermediario",
    "select-lincoff-semaglutida-24mg-mace-obesidade-sem-diabetes",
    "summit-tirzepatida-icfep-com-obesidade",
}
TARGETED_LEGACY_STUDIES = {
    "attribute-cm-acoramidis-na-amiloidose-cardiaca-por-transtirretina": "38197816",
    "helios-b-vutrisirana-na-amiloidose-cardiaca-por-transtirretina": "39213194",
    "storm-pe-trombectomia-mecanica-versus-anticoagulacao-isolada-no-tep-de-risco-intermediario-alto": "41183181",
}
PENDING_REVIEW_PATTERNS = (
    re.compile(r"\bainda\s+n[aã]o\s+revisad", re.IGNORECASE),
    re.compile(r"\baguardando\s+revis[aã]o", re.IGNORECASE),
    re.compile(
        r"\brevis[aã]o\s+"
        r"(?:(?:editorial|cl[ií]nica|metodol[oó]gica)\s+)*"
        r"(?:independente\s+)?pendent",
        re.IGNORECASE,
    ),
    re.compile(
        r"\brevis[aã]o\s+"
        r"(?:(?:editorial|cl[ií]nica|metodol[oó]gica)\s+)*"
        r"(?:independente\s+)?obrigat",
        re.IGNORECASE,
    ),
    re.compile(r"\b(?:artigo|texto)\s+integral\b[^.]{0,120}\bpendent", re.IGNORECASE),
    re.compile(
        r"^(?!.*\brevis[aã]o\b[^.]{0,200}\b"
        r"(?:conclu[ií]d|verificad[ao]s?\s+em\s+\d{4}))"
        r"(?=.*\b(?:abstract|resumo|xml)\b)"
        r"(?=.*\bartigo\s+integral\s+n[aã]o\s+conferid)",
        re.IGNORECASE | re.DOTALL,
    ),
    re.compile(r"\bsem\s+(?:aval|avalia[cç][aã]o|aprova[cç][aã]o)\b", re.IGNORECASE),
    re.compile(
        r"\bainda\s+n[aã]o\b[^.]{0,100}\b"
        r"(?:aval|avaliad[oa]s?|avalia[cç][aã]o|aprova[cç][aã]o)\b",
        re.IGNORECASE,
    ),
)


def git(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.stdout


def load_tree_json(commit: str, path: str) -> list[dict[str, Any]]:
    payload = json.loads(git("show", f"{commit}:{path}"))
    assert isinstance(payload, list), f"{commit}:{path} não contém uma lista JSON"
    assert all(isinstance(item, dict) for item in payload), f"objetos inválidos em {path}"
    return payload


def by_slug(records: list[dict[str, Any]], source: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for record in records:
        slug = record.get("slug")
        assert isinstance(slug, str) and slug.strip(), f"slug vazio em {source}"
        assert slug not in result, f"slug duplicado em {source}: {slug}"
        result[slug] = record
    return result


def assert_reviewed_and_published(record: dict[str, Any], source: str) -> None:
    status = record.get("review_status")
    if status is None and record.get("revisao") == "revisado":
        status = "revisado"
    assert status == "revisado", f"{source} não está revisado"
    assert record.get("published") is True, f"{source} não está published:true"


def has_review_note(record: dict[str, Any]) -> bool:
    notes = [
        value.strip()
        for field in ("review_note", "revisao")
        if isinstance((value := record.get(field)), str) and value.strip()
    ]
    return bool(notes) and not any(
        pattern.search(note) for note in notes for pattern in PENDING_REVIEW_PATTERNS
    )


def changed_json_slugs(front: str, review_key: str, path: str) -> list[str]:
    base = by_slug(load_tree_json(REVIEW_DIFF_BASES[review_key], path), f"base:{path}")
    head = by_slug(load_tree_json(REVIEW_HEADS[review_key], path), f"head:{path}")
    changed = {slug for slug, record in head.items() if base.get(slug) != record}

    if front == "estudos":
        deleted = set(base) - set(head)
        assert deleted == EXPECTED_DELETED_STUDY_ALIASES, (
            f"aliases deduplicados divergentes: {sorted(deleted)}"
        )
        assert set(TARGETED_LEGACY_STUDIES) <= changed, (
            "os três estudos legados alvo não estão integralmente no delta"
        )
        for slug, pmid in TARGETED_LEGACY_STUDIES.items():
            assert head[slug].get("pmid") == pmid, f"PMID divergente em estudos:{slug}"
    elif front != "triagem_sintomas":
        assert not (set(base) - set(head)), f"remoção inesperada em {front}"

    excluded = OPERATIONAL_INTEGRITY_ONLY.get(front, set())
    assert excluded <= changed, f"exclusão histórica não aparece no delta de {front}"
    selected = changed - excluded
    if front == "estudos":
        release_base = by_slug(load_tree_json(BASE, path), f"release-base:{path}")
        new_slugs = set(head) - set(release_base)
        assert len(new_slugs) == 170 and new_slugs <= selected, (
            f"lote novo de estudos divergente: {len(new_slugs)}"
        )
        canonical_deduplications = selected - new_slugs - set(TARGETED_LEGACY_STUDIES)
        assert len(canonical_deduplications) == 8, (
            f"canônicos deduplicados divergentes: {sorted(canonical_deduplications)}"
        )
    missing_notes = sorted(slug for slug in selected if not has_review_note(head[slug]))
    assert not missing_notes, (
        f"bloqueio: {front} sem nota concluída ou com linguagem de pendência: {missing_notes}"
    )
    for slug in selected:
        assert_reviewed_and_published(head[slug], f"{front}:{slug}")

    # Nada é filtrado implicitamente: toda mudança não aprovada deve estar na
    # pequena lista nominal de correções históricas fora do lote.
    not_publishable = {
        slug
        for slug in changed
        if head[slug].get("review_status") != "revisado"
        or head[slug].get("published") is not True
    }
    assert not_publishable == excluded, (
        f"delta não publicável inesperado em {front}: {sorted(not_publishable)}"
    )
    return sorted(selected)


def frontmatter_value(text: str, key: str, path: str, *, required: bool = True) -> str:
    match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", text, re.DOTALL)
    assert match, f"frontmatter ausente em {path}"
    value = re.search(rf"^{re.escape(key)}:\s*(.*?)\s*$", match.group(1), re.MULTILINE)
    if not value:
        assert not required, f"{key} ausente em {path}"
        return ""
    return value.group(1).strip().strip("\"'")


def changed_markdown_slugs() -> list[str]:
    base = REVIEW_DIFF_BASES["documentos_markdown"]
    head = REVIEW_HEADS["documentos_markdown"]
    paths = [
        path
        for path in git(
            "diff", "--name-only", "--diff-filter=AM", base, head, "--", "content"
        ).splitlines()
        if path.endswith(".md")
    ]
    assert len(paths) == EXPECTED_FRONT_COUNTS["documentos"], (
        f"delta Markdown inesperado: {len(paths)} arquivos"
    )

    slugs: list[str] = []
    not_reviewed: list[str] = []
    not_published: list[str] = []
    missing_notes: list[str] = []
    for path in paths:
        text = git("show", f"{head}:{path}")
        slug = frontmatter_value(text, "slug", path)
        if frontmatter_value(text, "review_status", path, required=False) != "revisado":
            not_reviewed.append(slug)
        if frontmatter_value(text, "published", path, required=False).lower() != "true":
            not_published.append(slug)
        note = frontmatter_value(text, "review_note", path, required=False)
        if not has_review_note({"review_note": note}):
            missing_notes.append(slug)
        slugs.append(slug)
    assert not not_reviewed, f"documentos não revisados: {sorted(not_reviewed)}"
    assert not not_published, f"documentos sem published:true: {sorted(not_published)}"
    assert not missing_notes, (
        "bloqueio: documentos sem nota concluída ou com linguagem de pendência: "
        f"{sorted(missing_notes)}"
    )
    assert len(slugs) == len(set(slugs)), "slugs duplicados no delta Markdown"
    return sorted(slugs)


def build_manifest() -> dict[str, Any]:
    fronts: dict[str, list[str]] = {"documentos": changed_markdown_slugs()}
    for front, (review_key, path) in JSON_FRONTS.items():
        fronts[front] = changed_json_slugs(front, review_key, path)

    assert set(fronts) == set(EXPECTED_FRONT_COUNTS), "frentes canônicas divergentes"
    counts = {front: len(slugs) for front, slugs in fronts.items()}
    assert counts == EXPECTED_FRONT_COUNTS, f"contagens divergentes: {counts}"
    assert sum(counts.values()) == EXPECTED_TOTAL
    for front, slugs in fronts.items():
        assert slugs and all(slug.strip() for slug in slugs), f"frente vazia: {front}"
        assert len(slugs) == len(set(slugs)), f"duplicata na frente {front}"

    return {
        "batch": "science-release-20260901",
        "base": BASE,
        "pr_head": PR_HEAD,
        "decision": "approved_for_publication",
        "approval_basis": (
            "Instrução explícita do responsável pelo repositório em 01/09/2026 para "
            "revisar, corrigir e publicar todo o lote científico no mesmo release, após "
            "revisão científica independente, consolidação das duplicatas e passagem dos "
            "gates finais de integridade científica, segurança de carga e release."
        ),
        "review_heads": REVIEW_HEADS,
        "review_diff_bases": REVIEW_DIFF_BASES,
        "review_scope": {
            "estudos": {
                "novos": 170,
                "canonicos_deduplicados": 8,
                "legados_alvo": 3,
                "total": 181,
            },
            "evidencias": 174,
            "doencas_especializadas": 161,
            "operacional": 120,
            "documentos_markdown": 89,
        },
        "counts": {"total": EXPECTED_TOTAL, "fronts": counts},
        "fronts": fronts,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--write",
        action="store_true",
        help=f"grava {OUTPUT.relative_to(ROOT)}; sem a opção, valida o arquivo existente",
    )
    args = parser.parse_args()
    expected = build_manifest()
    if args.write:
        OUTPUT.write_text(
            json.dumps(expected, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    else:
        actual = json.loads(OUTPUT.read_text(encoding="utf-8"))
        assert actual == expected, "manifesto difere da geração determinística"
    print(json.dumps(expected["counts"], ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
