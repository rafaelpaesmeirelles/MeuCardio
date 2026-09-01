#!/usr/bin/env python3
"""Auditoria reprodutível das relações do corpus Tudo com Tudo.

Lê os itens versionados, valida referências por slug e mede a cobertura
taxonômica sem acessar dados de paciente nem alterar banco/conteúdo.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import re
import sys
import unicodedata
from typing import Any
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.services.disease_manifest import load_disease_records  # noqa: E402
from app.services.triage_manifest import load_triage_records  # noqa: E402

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
VALID_REVIEW_STATUSES = EXPLICIT_REVIEW_STATUSES | {"lacuna_declarada"}
APPROVAL_FRONT_BY_KIND = {
    "documento_markdown": "documentos",
    "galeria": "galeria",
    "exame": "exames",
    "evidencia": "evidencias",
    "estudo": "estudos",
    "medicamento": "medicamentos",
    "checklist": "checklists",
    "caso_clinico": "casos_clinicos",
    "trilha": "trilhas",
    "material_paciente": "material_paciente",
    "protocolo_emergencia": "emergencia",
    "doenca": "doencas_especializadas",
    "triagem_sintoma": "triagem_sintomas",
}
PENDING_REVIEW_PATTERNS = (
    re.compile(r"\bainda\s+n[aã]o\s+revisad", re.IGNORECASE),
    re.compile(r"\baguardando\s+revis[aã]o", re.IGNORECASE),
    re.compile(r"\brevis[aã]o\s+(?:editorial\s+)?independente\s+pendent", re.IGNORECASE),
    re.compile(r"\brevis[aã]o\s+(?:editorial\s+)?pendent", re.IGNORECASE),
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
    re.compile(r"\bsem\s+(?:aval|aprova[cç][aã]o)\b", re.IGNORECASE),
    re.compile(
        r"\bainda\s+n[aã]o\b[^.]{0,100}\b(?:aval|aprova[cç][aã]o)\b",
        re.IGNORECASE,
    ),
)


def _frontmatter(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}, text
    _start, header, body = text.split("---", 2)
    metadata: dict[str, Any] = {}
    for field in (
        "slug", "title", "theme", "kind", "review_status", "review_note",
    ):
        match = re.search(rf'(?m)^{field}:\s*["\']?(.*?)["\']?\s*$', header)
        if match:
            metadata[field] = match.group(1).strip()
    published = re.search(r'(?mi)^published:\s*["\']?([^"\'\n]+?)["\']?\s*$', header)
    if published:
        raw_published = published.group(1).strip()
        if raw_published.casefold() in {"true", "false"}:
            metadata["published"] = raw_published.casefold() == "true"
        else:
            # Preserva o valor inválido para que o gate o identifique; tratá-lo
            # como campo ausente esconderia uma possível publicação insegura.
            metadata["published"] = raw_published
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
    if name == "doencas":
        return load_disease_records(ROOT / "doencas" / "metadados.json")
    if name == "triagem-sintomas":
        return load_triage_records(ROOT / "triagem-sintomas" / "metadados.json")
    payload = json.loads((ROOT / name / "metadados.json").read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"{name}/metadados.json não é uma lista")
    return payload


def _reference_issue(
    *,
    field: str,
    source: str,
    target: str,
    allowed: tuple[str, ...],
    slugs: dict[str, set[str]],
) -> dict[str, Any] | None:
    """Distingue alvo ausente de alvo existente com tipo incompatível."""
    actual_types = sorted(kind for kind, values in slugs.items() if target in values)
    if any(kind in actual_types for kind in allowed):
        return None
    reason = "wrong_target_type" if actual_types else "missing_target"
    return {
        "field": field,
        "source": source,
        "target": target,
        "reason": reason,
        "allowed_types": list(allowed),
        "actual_types": actual_types,
    }


def _normalized_pmid(value: Any) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip()
    return normalized or None


def _evidence_study_issue(
    evidence: dict[str, Any],
    *,
    slugs: dict[str, set[str]],
    studies_by_slug: dict[str, list[dict[str, Any]]],
) -> dict[str, Any] | None:
    """Valida alvo tipado, unicidade e identidade bibliográfica do estudo."""
    target = evidence.get("study_slug")
    issue = _reference_issue(
        field="EvidenceRecord.study_slug",
        source=str(evidence.get("slug") or ""),
        target=target,
        allowed=("estudo",),
        slugs=slugs,
    )
    if issue is not None:
        return issue

    matches = studies_by_slug.get(target, [])
    if len(matches) != 1:
        return {
            "field": "EvidenceRecord.study_slug",
            "source": str(evidence.get("slug") or ""),
            "target": target,
            "reason": "ambiguous_target",
            "allowed_types": ["estudo"],
            "actual_types": ["estudo"],
            "matching_studies": len(matches),
        }

    study = matches[0]
    if study.get("published") is not True:
        return {
            "field": "EvidenceRecord.study_slug",
            "source": str(evidence.get("slug") or ""),
            "target": target,
            "reason": "target_not_published",
            "allowed_types": ["estudo"],
            "actual_types": ["estudo"],
        }
    if study.get("review_status") != "revisado":
        return {
            "field": "EvidenceRecord.study_slug",
            "source": str(evidence.get("slug") or ""),
            "target": target,
            "reason": "target_not_reviewed",
            "allowed_types": ["estudo"],
            "actual_types": ["estudo"],
        }

    source_pmid = _normalized_pmid(evidence.get("pmid"))
    target_pmid = _normalized_pmid(study.get("pmid"))
    if source_pmid is not None and target_pmid is None:
        return {
            "field": "EvidenceRecord.study_slug",
            "source": str(evidence.get("slug") or ""),
            "target": target,
            "reason": "target_pmid_missing",
            "allowed_types": ["estudo"],
            "actual_types": ["estudo"],
            "source_pmid": source_pmid,
            "target_pmid": target_pmid,
        }
    if source_pmid is not None and source_pmid != target_pmid:
        return {
            "field": "EvidenceRecord.study_slug",
            "source": str(evidence.get("slug") or ""),
            "target": target,
            "reason": "pmid_mismatch",
            "allowed_types": ["estudo"],
            "actual_types": ["estudo"],
            "source_pmid": source_pmid,
            "target_pmid": target_pmid,
        }
    return None


def _load_editorial_approvals(root: Path = ROOT) -> dict[str, set[str]]:
    """Lê aprovações versionadas sem alterar status nem flags do corpus."""
    kind_by_front = {front: kind for kind, front in APPROVAL_FRONT_BY_KIND.items()}
    approvals = {kind: set() for kind in APPROVAL_FRONT_BY_KIND}
    directory = root / "editorial-approvals"
    if not directory.exists():
        return approvals

    for path in sorted(directory.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError(f"Aprovação editorial inválida: {path.name}")
        if payload.get("decision") != "approved_for_publication":
            continue
        fronts = payload.get("fronts") or {}
        if not isinstance(fronts, dict):
            raise ValueError(f"Frentes editoriais inválidas: {path.name}")
        unknown = sorted(set(fronts) - set(kind_by_front))
        if unknown:
            raise ValueError(
                f"Aprovação editorial {path.name} contém frentes desconhecidas: {unknown}"
            )
        for front, slugs in fronts.items():
            if not isinstance(slugs, list) or not all(
                isinstance(slug, str) and slug.strip() for slug in slugs
            ):
                raise ValueError(
                    f"Aprovação editorial {path.name}/{front} deve listar slugs válidos"
                )
            approvals[kind_by_front[front]].update(slugs)
    return approvals


def _editorial_issues(
    kind: str,
    records: list[dict[str, Any]],
    *,
    approved: set[str] | None = None,
) -> list[dict[str, Any]]:
    """Aplica invariantes editoriais sem promover nem publicar conteúdo."""
    approved = approved or set()
    issues: list[dict[str, Any]] = []
    for index, record in enumerate(records):
        identifier = str(
            record.get("slug") or record.get("title") or record.get("titulo") or index
        )
        status = record.get("review_status")
        published = record.get("published")
        note = "\n".join(
            str(record[field])
            for field in ("review_note", "revisao")
            if record.get(field)
        )

        if not isinstance(status, str) or status not in VALID_REVIEW_STATUSES:
            issues.append({
                "kind": kind,
                "identifier": identifier,
                "reason": "invalid_review_status",
                "review_status": status,
                "published": published,
            })
        if "published" in record and not isinstance(published, bool):
            issues.append({
                "kind": kind,
                "identifier": identifier,
                "reason": "invalid_published_flag",
                "review_status": status,
                "published": published,
            })
        if published is True and status != "revisado":
            issues.append({
                "kind": kind,
                "identifier": identifier,
                "reason": "published_without_review",
                "review_status": status,
                "published": published,
            })
        if published is True and identifier not in approved:
            issues.append({
                "kind": kind,
                "identifier": identifier,
                "reason": "published_without_approval",
                "review_status": status,
                "published": published,
            })
        if status == "revisado" and any(pattern.search(note) for pattern in PENDING_REVIEW_PATTERNS):
            issues.append({
                "kind": kind,
                "identifier": identifier,
                "reason": "reviewed_with_pending_review_note",
                "review_status": status,
                "published": published,
            })
    return issues


def _approval_target_issues(
    approvals: dict[str, set[str]],
    records_by_kind: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    """Valida todos os manifests que o reconciliador aceita por união.

    Uma aprovação pode legitimamente manter um item retido (`published:false`),
    mas nunca pode apontar para alvo inexistente, de outra frente ou ambíguo.
    A prontidão de todo item efetivamente público é verificada separadamente por
    `_editorial_issues`, exigindo cumulativamente revisão e aprovação.
    """

    grouped: dict[str, dict[str, list[dict[str, Any]]]] = {}
    locations: dict[str, set[str]] = defaultdict(set)
    for kind, records in records_by_kind.items():
        by_slug: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for record in records:
            slug = record.get("slug")
            if isinstance(slug, str) and slug.strip():
                normalized = slug.strip()
                by_slug[normalized].append(record)
                locations[normalized].add(kind)
        grouped[kind] = by_slug

    issues: list[dict[str, Any]] = []
    for kind, approved_slugs in approvals.items():
        for slug in sorted(approved_slugs):
            matches = grouped.get(kind, {}).get(slug, [])
            if len(matches) == 1:
                continue
            actual_kinds = sorted(locations.get(slug, set()))
            if not matches:
                reason = (
                    "approval_target_wrong_type"
                    if actual_kinds else "approval_target_not_found"
                )
            else:
                reason = "approval_target_ambiguous"
            issues.append({
                "kind": kind,
                "identifier": slug,
                "reason": reason,
                "actual_kinds": actual_kinds,
                "matching_records": len(matches),
            })
    return issues


def _editorial_quarantine(
    kind: str, records: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Conta conteúdo retido sem convertê-lo em falso bloqueio editorial."""
    quarantined: list[dict[str, Any]] = []
    for index, record in enumerate(records):
        status = record.get("review_status")
        if status == "revisado" or record.get("published") is True:
            continue
        quarantined.append({
            "kind": kind,
            "identifier": str(
                record.get("slug") or record.get("title") or record.get("titulo") or index
            ),
            "review_status": status,
            "published": record.get("published") if "published" in record else "missing",
        })
    return quarantined


def _publication_flags(records: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter(
        "true" if record.get("published") is True
        else "false" if record.get("published") is False
        else "missing" if "published" not in record
        else "invalid"
        for record in records
    )
    return {
        key: counts.get(key, 0)
        for key in ("true", "false", "missing", "invalid")
    }


def _strict_release_issues(
    kind: str, records: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Exige revisão e publicação explícitas para cada item do release final."""
    issues: list[dict[str, Any]] = []
    for index, record in enumerate(records):
        status = record.get("review_status")
        published = record.get("published")
        blockers = []
        if status != "revisado":
            blockers.append("not_reviewed")
        if published is not True:
            blockers.append("not_published")
        if not blockers:
            continue
        issues.append({
            "kind": kind,
            "identifier": str(
                record.get("slug") or record.get("title")
                or record.get("titulo") or index
            ),
            "reason": "release_item_not_ready",
            "blockers": blockers,
            "review_status": status,
            "published": published if "published" in record else "missing",
        })
    return issues


def _strict_release_manifest_issues(
    path: Path,
    records_by_kind: dict[str, list[dict[str, Any]]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Certifica apenas o lote explicitamente aprovado no manifesto do release."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Manifesto estrito de release deve ser um objeto JSON")
    if payload.get("decision") != "approved_for_publication":
        raise ValueError(
            "Manifesto estrito de release não contém decisão aprovada para publicação"
        )

    fronts = payload.get("fronts")
    if not isinstance(fronts, dict) or not fronts:
        raise ValueError("Manifesto estrito de release deve declarar frentes")
    kind_by_front = {
        front: kind for kind, front in APPROVAL_FRONT_BY_KIND.items()
    }
    unknown = sorted(set(fronts) - set(kind_by_front))
    if unknown:
        raise ValueError(
            f"Manifesto estrito de release contém frentes desconhecidas: {unknown}"
        )

    selected: list[tuple[str, str, str]] = []
    seen: set[str] = set()
    front_counts: dict[str, int] = {}
    for front, raw_slugs in fronts.items():
        if not isinstance(raw_slugs, list) or not all(
            isinstance(slug, str) and slug.strip() for slug in raw_slugs
        ):
            raise ValueError(
                f"Manifesto estrito de release/{front} deve listar slugs válidos"
            )
        front_counts[front] = len(raw_slugs)
        for raw_slug in raw_slugs:
            slug = raw_slug.strip()
            if slug in seen:
                raise ValueError(
                    f"Slug duplicado no manifesto estrito de release: {slug}"
                )
            seen.add(slug)
            selected.append((front, kind_by_front[front], slug))
    if not selected:
        raise ValueError("Manifesto estrito de release não seleciona nenhum item")

    records_by_slug: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for kind, records in records_by_kind.items():
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for record in records:
            slug = record.get("slug")
            if isinstance(slug, str) and slug:
                grouped[slug].append(record)
        records_by_slug[kind] = grouped

    issues: list[dict[str, Any]] = []
    for front, kind, slug in selected:
        matches = records_by_slug.get(kind, {}).get(slug, [])
        if not matches:
            actual_kinds = sorted(
                candidate_kind
                for candidate_kind, grouped in records_by_slug.items()
                if grouped.get(slug)
            )
            issues.append({
                "kind": kind,
                "front": front,
                "identifier": slug,
                "reason": (
                    "release_manifest_wrong_target_type"
                    if actual_kinds else "release_manifest_target_not_found"
                ),
                "blockers": [
                    "wrong_target_type" if actual_kinds else "missing_target"
                ],
                "actual_kinds": actual_kinds,
                "review_status": "missing",
                "published": "missing",
            })
            continue
        if len(matches) != 1:
            issues.append({
                "kind": kind,
                "front": front,
                "identifier": slug,
                "reason": "release_manifest_target_ambiguous",
                "blockers": ["ambiguous_target"],
                "matching_records": len(matches),
                "review_status": "ambiguous",
                "published": "ambiguous",
            })
            continue
        for issue in _strict_release_issues(kind, matches):
            issue["front"] = front
            issues.append(issue)

    return issues, {
        "path": str(path),
        "decision": payload["decision"],
        "item_count": len(selected),
        "fronts": front_counts,
    }


def _approval_manifest_issues(
    path: Path,
    records_by_kind: dict[str, list[dict[str, Any]]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Audita um manifest exatamente como autorização, sem forçar publicação.

    Aprovação e intenção de publicação são controles independentes no runtime.
    Por isso um item aprovado pode continuar retido, mas todo alvo precisa ser
    inequívoco e qualquer alvo já marcado `published:true` precisa estar
    revisado. O auditor genérico verifica também que todo item público aparece
    em ao menos uma dessas aprovações.
    """

    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Manifesto de aprovação deve ser um objeto JSON")
    if payload.get("decision") != "approved_for_publication":
        raise ValueError("Manifesto não contém decisão aprovada para publicação")
    fronts = payload.get("fronts")
    if not isinstance(fronts, dict) or not fronts:
        raise ValueError("Manifesto de aprovação deve declarar frentes")

    kind_by_front = {
        front: kind for kind, front in APPROVAL_FRONT_BY_KIND.items()
    }
    unknown = sorted(set(fronts) - set(kind_by_front))
    if unknown:
        raise ValueError(f"Manifesto contém frentes desconhecidas: {unknown}")

    grouped: dict[str, dict[str, list[dict[str, Any]]]] = {}
    locations: dict[str, set[str]] = defaultdict(set)
    for kind, records in records_by_kind.items():
        by_slug: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for record in records:
            slug = record.get("slug")
            if isinstance(slug, str) and slug.strip():
                normalized = slug.strip()
                by_slug[normalized].append(record)
                locations[normalized].add(kind)
        grouped[kind] = by_slug

    issues: list[dict[str, Any]] = []
    item_count = public_items = retained_items = 0
    front_counts: dict[str, int] = {}
    for front, raw_slugs in fronts.items():
        if not isinstance(raw_slugs, list) or not all(
            isinstance(slug, str) and slug.strip() for slug in raw_slugs
        ):
            raise ValueError(f"Manifesto/{front} deve listar slugs válidos")
        slugs = [slug.strip() for slug in raw_slugs]
        if len(slugs) != len(set(slugs)):
            raise ValueError(f"Manifesto/{front} contém slug duplicado")
        front_counts[front] = len(slugs)
        item_count += len(slugs)
        kind = kind_by_front[front]
        for slug in slugs:
            matches = grouped.get(kind, {}).get(slug, [])
            if len(matches) != 1:
                actual_kinds = sorted(locations.get(slug, set()))
                issues.append({
                    "kind": kind,
                    "front": front,
                    "identifier": slug,
                    "reason": (
                        "approval_target_ambiguous"
                        if matches else "approval_target_wrong_type"
                        if actual_kinds else "approval_target_not_found"
                    ),
                    "actual_kinds": actual_kinds,
                    "matching_records": len(matches),
                })
                continue
            record = matches[0]
            if record.get("published") is True:
                public_items += 1
                if record.get("review_status") != "revisado":
                    issues.append({
                        "kind": kind,
                        "front": front,
                        "identifier": slug,
                        "reason": "approved_publication_not_reviewed",
                        "review_status": record.get("review_status"),
                        "published": True,
                    })
            else:
                retained_items += 1

    return issues, {
        "path": str(path),
        "decision": payload["decision"],
        "item_count": item_count,
        "public_items": public_items,
        "retained_items": retained_items,
        "fronts": front_counts,
    }


def _gate_summary(
    result: dict[str, Any], *, strict_release: bool = False
) -> dict[str, Any]:
    reference_issues = result.get("broken_references") or []
    editorial_issues = result.get("editorial_issues") or []
    approval_manifest_issues = result.get("approval_manifest_issues") or []
    release_issues = (
        result.get("release_readiness_issues") or []
        if strict_release else []
    )
    reference_reasons = Counter(issue.get("reason", "unknown") for issue in reference_issues)
    editorial_reasons = Counter(issue.get("reason", "unknown") for issue in editorial_issues)
    blocker_count = (
        len(reference_issues)
        + len(editorial_issues)
        + len(approval_manifest_issues)
        + len(release_issues)
    )
    summary = {
        "passed": blocker_count == 0,
        "blocker_count": blocker_count,
        "reference_blockers": len(reference_issues),
        "editorial_blockers": len(editorial_issues),
        "approval_manifest_blockers": len(approval_manifest_issues),
        "broken_markdown_links": sum(
            issue.get("field") == "Document.body_md.link" for issue in reference_issues
        ),
        "reference_reasons": dict(sorted(reference_reasons.items())),
        "editorial_reasons": dict(sorted(editorial_reasons.items())),
        "approval_manifest_reasons": dict(sorted(Counter(
            issue.get("reason", "unknown") for issue in approval_manifest_issues
        ).items())),
    }
    if strict_release:
        release_reasons = Counter(
            blocker
            for issue in release_issues
            for blocker in issue.get("blockers", [])
        )
        summary.update({
            "strict_release": True,
            "release_blockers": len(release_issues),
            "release_reasons": dict(sorted(release_reasons.items())),
        })
    return summary


def audit(
    *,
    strict_release: bool = False,
    strict_release_manifest: Path | None = None,
    approval_manifest: Path | None = None,
) -> dict:
    selected_modes = sum((
        strict_release,
        strict_release_manifest is not None,
        approval_manifest is not None,
    ))
    if selected_modes > 1:
        raise ValueError(
            "Use apenas um modo: corpus completo, release ou manifesto de aprovação"
        )
    documents: dict[str, dict] = {}
    for path in sorted((ROOT / "content").rglob("*.md")):
        meta, body = _frontmatter(path)
        slug = meta.get("slug") or path.stem
        if slug in documents:
            raise ValueError(f"Slug Markdown duplicado: {slug}")
        documents[slug] = {
            **meta,
            "slug": slug,
            "body": body,
            "path": str(path.relative_to(ROOT)),
        }

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
    slugs["fluxograma"] = {
        slug for slug, item in documents.items() if item.get("kind") == "fluxograma"
    }
    slugs["documento"] = set(documents) - slugs["fluxograma"]
    studies_by_slug: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for study in manifests["estudo"]:
        studies_by_slug[str(study["slug"])].append(study)

    # Calculadoras vivem em registro Python e não compõem os itens do corpus.
    calculator_source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((ROOT / "backend/app/services").glob("*calculators*.py"))
    )
    slugs["calculadora"] = set(re.findall(r'\bslug\s*=\s*["\']([^"\']+)', calculator_source))

    stats: dict[str, Counter] = defaultdict(Counter)
    broken: list[dict[str, Any]] = []

    def add(field: str, source: str, target: str, allowed: tuple[str, ...]) -> None:
        stats[field]["total"] += 1
        issue = _reference_issue(
            field=field,
            source=source,
            target=target,
            allowed=allowed,
            slugs=slugs,
        )
        if issue is None:
            stats[field]["resolved"] += 1
        else:
            stats[field]["broken"] += 1
            broken.append(issue)

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
                add("Document.body_md.link", slug, target_slug, ("documento", "fluxograma"))

    for item in manifests["evidencia"]:
        if item.get("document_slug"):
            add("EvidenceRecord.document_slug", item["slug"], item["document_slug"], ("documento", "fluxograma"))
        if "study_slug" in item:
            field = "EvidenceRecord.study_slug"
            stats[field]["total"] += 1
            issue = _evidence_study_issue(
                item,
                slugs=slugs,
                studies_by_slug=studies_by_slug,
            )
            if issue is None:
                stats[field]["resolved"] += 1
            else:
                stats[field]["broken"] += 1
                broken.append(issue)
    for item in manifests["estudo"]:
        if item.get("document_slug"):
            add("ScientificStudy.document_slug", item["slug"], item["document_slug"], ("documento", "fluxograma"))
    for item in manifests["checklist"]:
        if item.get("documento_origem"):
            add("DischargeChecklist.documento_origem", item["slug"], item["documento_origem"], ("documento", "fluxograma"))
    for item in manifests["material_paciente"]:
        if item.get("documento_slug"):
            add("PatientMaterial.documento_slug", item["slug"], item["documento_slug"], ("documento", "fluxograma"))
    for item in manifests["protocolo_emergencia"]:
        add("EmergencyProtocol.documento_slug", item["slug"], item["documento_slug"], ("documento",))
        if item.get("fluxograma_slug"):
            add("EmergencyProtocol.fluxograma_slug", item["slug"], item["fluxograma_slug"], ("fluxograma",))
        for target in item.get("relacionados") or []:
            add("EmergencyProtocol.relacionados", item["slug"], target, ("documento", "protocolo_emergencia"))
    track_types = {
        "documento": ("documento", "fluxograma"), "estudo": ("estudo",),
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
            add("SpecialtyDisease.related_document_slugs", item["slug"], target, ("documento", "fluxograma"))
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
    approvals = _load_editorial_approvals()
    editorial_issues: list[dict[str, Any]] = []
    editorial_quarantine: list[dict[str, Any]] = []
    release_readiness_issues: list[dict[str, Any]] = []
    publication_flags: dict[str, dict[str, int]] = {}
    document_records = list(documents.values())
    records_by_kind = {**manifests, "documento_markdown": document_records}
    editorial_issues.extend(_approval_target_issues(approvals, records_by_kind))
    for kind, items in manifests.items():
        editorial_issues.extend(
            _editorial_issues(kind, items, approved=approvals.get(kind, set()))
        )
        editorial_quarantine.extend(_editorial_quarantine(kind, items))
        if strict_release:
            release_readiness_issues.extend(_strict_release_issues(kind, items))
        publication_flags[kind] = _publication_flags(items)
    editorial_issues.extend(_editorial_issues(
        "documento_markdown",
        document_records,
        approved=approvals.get("documento_markdown", set()),
    ))
    editorial_quarantine.extend(
        _editorial_quarantine("documento_markdown", document_records)
    )
    if strict_release:
        release_readiness_issues.extend(
            _strict_release_issues("documento_markdown", document_records)
        )
    publication_flags["documento_markdown"] = _publication_flags(document_records)
    release_manifest: dict[str, Any] | None = None
    if strict_release_manifest is not None:
        release_readiness_issues, release_manifest = (
            _strict_release_manifest_issues(
                strict_release_manifest,
                records_by_kind,
            )
        )
    approval_manifest_metadata: dict[str, Any] | None = None
    approval_manifest_issues: list[dict[str, Any]] = []
    if approval_manifest is not None:
        approval_manifest_issues, approval_manifest_metadata = (
            _approval_manifest_issues(approval_manifest, records_by_kind)
        )

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

    result = {
        "total_items": total,
        "items_by_type": {"documento_markdown": len(documents), **{k: len(v) for k, v in manifests.items()}},
        "review_status": dict(review_counts),
        "publication_flags": publication_flags,
        "editorial_quarantine": editorial_quarantine,
        "editorial_quarantine_count": len(editorial_quarantine),
        "references": {field: dict(counts) for field, counts in sorted(stats.items())},
        "broken_references": broken,
        "editorial_issues": editorial_issues,
        "approval_manifest_issues": approval_manifest_issues,
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
    release_strict = strict_release or strict_release_manifest is not None
    if release_strict:
        result["release_readiness_issues"] = release_readiness_issues
        result["release_readiness_issue_count"] = len(release_readiness_issues)
    if release_manifest is not None:
        result["release_manifest"] = release_manifest
    if approval_manifest_metadata is not None:
        result["approval_manifest"] = approval_manifest_metadata
    result["gate"] = _gate_summary(result, strict_release=release_strict)
    if release_manifest is not None:
        result["gate"]["strict_release_manifest"] = release_manifest["path"]
        result["gate"]["release_manifest_items"] = release_manifest["item_count"]
    if approval_manifest_metadata is not None:
        result["gate"]["approval_manifest"] = approval_manifest_metadata["path"]
        result["gate"]["approval_manifest_items"] = approval_manifest_metadata[
            "item_count"
        ]
    return result


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audita referências e estado editorial do corpus Tudo com Tudo."
    )
    strict_group = parser.add_mutually_exclusive_group()
    strict_group.add_argument(
        "--strict-release",
        action="store_true",
        help=(
            "falha se qualquer item não estiver explicitamente revisado e publicado; "
            "o modo genérico continua permitindo quarentena"
        ),
    )
    strict_group.add_argument(
        "--approval-manifest",
        type=Path,
        metavar="PATH",
        help=(
            "valida um manifesto aceito pelo runtime: alvos tipados/únicos e "
            "revisão obrigatória para itens já marcados como publicados"
        ),
    )
    strict_group.add_argument(
        "--strict-release-manifest",
        type=Path,
        metavar="PATH",
        help=(
            "falha se qualquer slug listado no manifesto aprovado estiver ausente, "
            "ambíguo, não revisado ou não publicado"
        ),
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args([] if argv is None else argv)
    try:
        if args.strict_release:
            result = audit(strict_release=True)
        elif args.strict_release_manifest is not None:
            result = audit(strict_release_manifest=args.strict_release_manifest)
        elif args.approval_manifest is not None:
            result = audit(approval_manifest=args.approval_manifest)
        else:
            result = audit()
    except Exception as exc:  # noqa: BLE001 - o gate deve falhar fechado
        print(json.dumps({
            "gate": {"passed": False, "blocker_count": 1},
            "error": {"type": type(exc).__name__, "detail": str(exc)},
        }, ensure_ascii=False, indent=2, sort_keys=True))
        return 2
    release_strict = args.strict_release or args.strict_release_manifest is not None
    result["gate"] = _gate_summary(result, strict_release=release_strict)
    if args.strict_release_manifest is not None:
        result["gate"]["strict_release_manifest"] = str(
            args.strict_release_manifest
        )
        result["gate"]["release_manifest_items"] = result.get(
            "release_manifest", {}
        ).get("item_count", 0)
    if args.approval_manifest is not None:
        result["gate"]["approval_manifest"] = str(args.approval_manifest)
        result["gate"]["approval_manifest_items"] = result.get(
            "approval_manifest", {}
        ).get("item_count", 0)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["gate"]["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
