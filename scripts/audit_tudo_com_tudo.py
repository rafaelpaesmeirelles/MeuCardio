#!/usr/bin/env python3
"""Auditoria reprodutível das relações do corpus Tudo com Tudo.

Lê os 9.452 itens versionados, valida referências por slug e mede a cobertura
taxonômica sem acessar dados de paciente nem alterar banco/conteúdo.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import json
from pathlib import Path
import re
import unicodedata
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)\s]+)\)")
CODE_BLOCK = re.compile(r"```.*?```|~~~.*?~~~", re.DOTALL)
INLINE_CODE = re.compile(r"`[^`\n]*`")
URL_SCHEME = re.compile(r"^[a-z][a-z0-9+.-]*:", re.IGNORECASE)
EXPLICIT_RELATION_TYPES = {
    "treats", "indicated_for", "contraindicated_in", "contraindicated_with",
    "interacts_with", "monitor_with", "diagnosed_by", "supported_by",
    "studied_in", "recommended_by", "associated_with", "causes", "may_cause",
    "alternative_to", "belongs_to_class", "used_in_case", "mentioned_in",
    "patient_education_for", "differential_for", "same_theme", "belongs_to_topic",
    "derived_from", "uses_flowchart", "contains",
}
EXPLICIT_PROVENANCE_TYPES = {
    "editorial", "structured_metadata", "imported", "derived",
    "ai_suggested", "clinical_context",
}
EXPLICIT_CONFIDENCE_LEVELS = {"explicit", "derived", "ai_suggested"}
EXPLICIT_REVIEW_STATUSES = {"revisado", "pendente_revisao", "rejeitado"}


def _frontmatter(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}, text
    _start, header, body = text.split("---", 2)
    metadata: dict[str, str] = {}
    for field in ("slug", "title", "theme", "kind", "review_status"):
        match = re.search(rf'(?m)^{field}:\s*["\']?(.*?)["\']?\s*$', header)
        if match:
            metadata[field] = match.group(1).strip()
    return metadata, body


def _norm(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value or "")
    return " ".join(
        "".join(c for c in decomposed if not unicodedata.combining(c))
        .casefold().split()
    )


def _link_slug(target: str) -> str | None:
    path = unquote(target).split("#", 1)[0].split("?", 1)[0].strip()
    if URL_SCHEME.match(path) or path.startswith("//"):
        return None
    if path.startswith("/biblioteca/"):
        return path.removeprefix("/biblioteca/").strip("/") or None
    if path.casefold().endswith(".md"):
        return path.rsplit("/", 1)[-1][:-3] or None
    return None


def _markdown_without_code(body: str) -> str:
    return INLINE_CODE.sub("", CODE_BLOCK.sub("", body))


def _load(name: str) -> list[dict]:
    payload = json.loads((ROOT / name / "metadados.json").read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"{name}/metadados.json não é uma lista")
    return payload


def audit() -> dict:
    documents: dict[str, dict] = {}
    for path in sorted((ROOT / "content").rglob("*.md")):
        meta, body = _frontmatter(path)
        slug = meta.get("slug") or path.stem
        if slug in documents:
            raise ValueError(f"Slug Markdown duplicado: {slug}")
        documents[slug] = {**meta, "body": body, "path": str(path.relative_to(ROOT))}

    manifests = {
        "galeria": _load("galeria"),
        "exame": _load("exames"),
        "evidencia": _load("evidencias"),
        "estudo": _load("estudos"),
        "medicamento": _load("medicamentos"),
        "checklist": _load("checklists"),
        "caso_clinico": _load("casos-clinicos"),
        "trilha": _load("trilhas"),
        "material_paciente": _load("material-paciente"),
        "protocolo_emergencia": _load("emergencia"),
        "doenca": _load("doencas"),
        "triagem_sintoma": _load("triagem-sintomas"),
    }
    slugs = {kind: {str(item["slug"]) for item in items} for kind, items in manifests.items()}
    for kind, items in manifests.items():
        if len(slugs[kind]) != len(items):
            raise ValueError(f"Slug duplicado no manifesto: {kind}")
    slugs["documento"] = set(documents)
    slugs["fluxograma"] = {
        slug for slug, item in documents.items() if item.get("kind") == "fluxograma"
    }

    # Calculadoras vivem em registro Python e não compõem os 9.452 itens.
    calculator_source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (
            ROOT / "backend/app/services/calculators.py",
            ROOT / "backend/app/services/dose_calculators.py",
        )
    )
    slugs["calculadora"] = set(re.findall(r'\bslug\s*=\s*["\']([^"\']+)', calculator_source))

    stats: dict[str, Counter] = defaultdict(Counter)
    broken: list[dict] = []

    def add(field: str, source: str, target: str, allowed: tuple[str, ...]) -> None:
        stats[field]["total"] += 1
        if any(target in slugs[kind] for kind in allowed):
            stats[field]["resolved"] += 1
        else:
            stats[field]["broken"] += 1
            broken.append({"field": field, "source": source, "target": target})

    explicit_relations = json.loads(
        (ROOT / "doencas/relacoes-explicitas.json").read_text(encoding="utf-8")
    )
    if not isinstance(explicit_relations, list):
        raise ValueError("doencas/relacoes-explicitas.json não é uma lista")
    explicit_keys: set[tuple[str, str, str, str]] = set()
    for index, relation in enumerate(explicit_relations):
        if not isinstance(relation, dict):
            raise ValueError(f"Relação explícita #{index} não é objeto")
        required = (
            "source_disease_slug", "target_type", "target_slug", "relation_type",
            "review_status", "provenance_type", "confidence",
        )
        missing = [
            field for field in required
            if not isinstance(relation.get(field), str) or not relation[field].strip()
        ]
        if missing:
            raise ValueError(f"Relação explícita #{index} inválida: {missing}")
        target_type = relation["target_type"]
        if target_type not in slugs or target_type in {"doenca", "documento"}:
            # Documento tem subtipagem documento/fluxograma; exigir o tipo
            # exato evita que um fluxograma seja declarado como documento.
            if target_type != "documento":
                raise ValueError(
                    f"Relação explícita #{index}: target_type inválido: {target_type}"
                )
        if relation["relation_type"] not in EXPLICIT_RELATION_TYPES:
            raise ValueError(f"Relação explícita #{index}: relation_type inválido")
        if relation["provenance_type"] not in EXPLICIT_PROVENANCE_TYPES:
            raise ValueError(f"Relação explícita #{index}: provenance_type inválido")
        if relation["confidence"] not in EXPLICIT_CONFIDENCE_LEVELS:
            raise ValueError(f"Relação explícita #{index}: confidence inválido")
        if relation["review_status"] not in EXPLICIT_REVIEW_STATUSES:
            raise ValueError(f"Relação explícita #{index}: review_status inválido")
        key = (
            relation["source_disease_slug"], target_type,
            relation["target_slug"], relation["relation_type"],
        )
        if key in explicit_keys:
            raise ValueError(f"Relação explícita duplicada: {key}")
        explicit_keys.add(key)
        add(
            "ExplicitDiseaseRelation.source_disease_slug",
            f"relacao-explicita:{index}",
            relation["source_disease_slug"],
            ("doenca",),
        )
        add(
            "ExplicitDiseaseRelation.target_slug",
            relation["source_disease_slug"],
            relation["target_slug"],
            (target_type,),
        )

    for slug, document in documents.items():
        for target in LINK.findall(_markdown_without_code(document["body"])):
            target_slug = _link_slug(target)
            if target_slug:
                add("Document.body_md.link", slug, target_slug, ("documento",))

    for item in manifests["evidencia"]:
        if item.get("document_slug"):
            add("EvidenceRecord.document_slug", item["slug"], item["document_slug"], ("documento",))
    for item in manifests["checklist"]:
        if item.get("documento_origem"):
            add("DischargeChecklist.documento_origem", item["slug"], item["documento_origem"], ("documento",))
    for item in manifests["material_paciente"]:
        if item.get("documento_slug"):
            add("PatientMaterial.documento_slug", item["slug"], item["documento_slug"], ("documento",))
    for item in manifests["protocolo_emergencia"]:
        add("EmergencyProtocol.documento_slug", item["slug"], item["documento_slug"], ("documento",))
        if item.get("fluxograma_slug"):
            add("EmergencyProtocol.fluxograma_slug", item["slug"], item["fluxograma_slug"], ("documento",))
        for target in item.get("relacionados") or []:
            add("EmergencyProtocol.relacionados", item["slug"], target, ("documento", "protocolo_emergencia"))
    track_types = {
        "documento": ("documento",), "estudo": ("estudo",),
        "medicamento": ("medicamento",), "checklist": ("checklist",),
        "caso_clinico": ("caso_clinico",), "evidencia": ("evidencia",),
        "calculadora": ("calculadora",),
    }
    for item in manifests["trilha"]:
        for step in item.get("etapas") or []:
            allowed = track_types.get(step.get("item_type"), ())
            add("StudyTrack.etapas", item["slug"], step.get("item_slug", ""), allowed)
    for item in manifests["doenca"]:
        for target in item.get("related_document_slugs") or []:
            add("SpecialtyDisease.related_document_slugs", item["slug"], target, ("documento",))
        if item.get("patient_material_slug"):
            add("SpecialtyDisease.patient_material_slug", item["slug"], item["patient_material_slug"], ("material_paciente",))

    interactions = json.loads((ROOT / "medicamentos/interacoes.json").read_text(encoding="utf-8"))
    for item in interactions:
        drugs = item.get("farmacos") or []
        if len(drugs) == 2 and item.get("review_status") == "revisado":
            add("DrugInteraction.farmacos[2]", item["slug"], drugs[0], ("medicamento",))
            add("DrugInteraction.farmacos[2]", item["slug"], drugs[1], ("medicamento",))

    disease_names: dict[str, set[str]] = defaultdict(set)
    for disease in manifests["doenca"]:
        for name in [disease.get("name", ""), *(disease.get("aliases") or [])]:
            disease_names[_norm(name)].add(disease["slug"])
    exact_differentials = 0
    for triage in manifests["triagem_sintoma"]:
        for raw in triage.get("differentials") or []:
            value = raw if isinstance(raw, str) else next(
                (raw.get(key) for key in ("name", "label", "text", "title") if raw.get(key)), ""
            )
            if len(disease_names.get(_norm(value), set())) == 1:
                exact_differentials += 1

    total = len(documents) + sum(len(items) for items in manifests.values())
    review_counts = Counter(
        item.get("review_status", "ausente")
        for items in manifests.values()
        for item in items
    )
    review_counts.update(item.get("review_status", "ausente") for item in documents.values())

    # Cobertura conservadora: frentes com tema próprio + emergência herdada +
    # medicamento em Farmacologia + doença/triagem somente via vínculo explícito.
    direct_topic = len(documents)
    for kind in ("galeria", "exame", "evidencia", "estudo", "checklist", "caso_clinico", "trilha", "material_paciente"):
        direct_topic += sum(bool(item.get("theme") or item.get("tema")) for item in manifests[kind])
    direct_topic += len(manifests["medicamento"]) + len(manifests["protocolo_emergencia"])
    valid_areas = {"geral", "cardiopediatria", "cardiogeriatria", "cardiooncologia", "gravidez"}
    diseases_with_topic = sum(item.get("area") in valid_areas for item in manifests["doenca"])
    triages_with_topic = sum(
        bool(set(triage.get("areas") or []) & valid_areas)
        for triage in manifests["triagem_sintoma"]
    )
    specialty_area_associations = diseases_with_topic + sum(
        len(set(triage.get("areas") or []) & valid_areas)
        for triage in manifests["triagem_sintoma"]
    )

    return {
        "total_items": total,
        "items_by_type": {"documento_markdown": len(documents), **{k: len(v) for k, v in manifests.items()}},
        "review_status": dict(review_counts),
        "references": {field: dict(counts) for field, counts in sorted(stats.items())},
        "broken_references": broken,
        "explicit_disease_relations": {
            "total": len(explicit_relations),
            "by_review_status": dict(Counter(
                relation["review_status"] for relation in explicit_relations
            )),
            "by_provenance_type": dict(Counter(
                relation["provenance_type"] for relation in explicit_relations
            )),
        },
        "exact_unambiguous_triage_differentials": exact_differentials,
        "topic_coverage": {
            "covered": direct_topic + diseases_with_topic + triages_with_topic,
            "total": total,
            "without_explicit_topic": total - direct_topic - diseases_with_topic - triages_with_topic,
            "specialty_area_associations": specialty_area_associations,
        },
    }


if __name__ == "__main__":
    print(json.dumps(audit(), ensure_ascii=False, indent=2, sort_keys=True))
