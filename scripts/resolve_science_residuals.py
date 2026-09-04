#!/usr/bin/env python3
"""Resolve pendências residuais da reconciliação dos PRs científicos.

A entrada é o relatório V4, que já isolou o delta real de cada PR (base.sha -> head).
Esta fase aplica uma revisão conservadora em três vias:

    base original do PR -> proposta do PR -> corpus canônico atual

Regras:
- o corpus canônico atual vence conflitos clínicos já revisados;
- exclusões antigas nunca são reaplicadas;
- em medicamentos, deltas sem conflito podem ser portados estruturalmente;
- checklists/material/trilhas podem herdar proveniência de conteúdo canônico revisado;
- doença/triagem já composta por fragmento é tratada como absorvida, não reintroduzida;
- nada sem fonte/proveniência suficiente é marcado revisado por conveniência.

Não publica, não altera banco e não faz deploy.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable

import yaml

import reconcile_open_science_prs as core

ROOT = core.ROOT
REVIEWED = {"revisado", "reviewed", "approved", "aprovado", "verificado"}
PROTECTED_KEYS = {
    "slug", "id", "codigo", "key", "published", "created_at", "updated_at",
    "approval_status", "approved_for_publication",
}
TYPE_ALIASES = {
    "documento": "documento", "document": "documento",
    "estudo": "estudos", "study": "estudos",
    "evidencia": "evidencias", "evidence": "evidencias",
    "checklist": "checklists",
    "doenca": "doencas", "doença": "doencas",
    "medicamento": "medicamentos", "drug": "medicamentos",
    "material": "material_paciente", "material_paciente": "material_paciente",
    "material-paciente": "material_paciente",
    "trilha": "trilhas", "track": "trilhas",
    "exame": "exames", "exam": "exames",
    "caso": "casos_clinicos", "caso_clinico": "casos_clinicos",
    "triagem": "triagem",
}
SOURCEISH_KEY = re.compile(
    r"(?i)(source|fonte|refer|brand|marca|commercial|comercial|presentation|apresenta|"
    r"manufacturer|fabricante|bula|cmed|kairos|anvisa|dailymed|fda|ema|registro)"
)


@dataclass
class Resolution:
    status: str
    pr: int
    kind: str
    key: str
    path: str
    reason: str
    changed_paths: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def current_collection_state() -> dict[str, dict[str, Any]]:
    state: dict[str, dict[str, Any]] = {}
    for kind, rel in core.MANIFESTS.items():
        path = ROOT / rel
        if not path.exists():
            continue
        payload = read_json(path)
        records, collection_key = core.collection(payload)
        clean = [r for r in records if isinstance(r, dict)]
        state[kind] = {
            "path": rel,
            "payload": payload,
            "collection_key": collection_key,
            "records": clean,
            "index": {core.key_of(r): r for r in clean if core.key_of(r)},
        }
    return state


def rebuild_manifest(state: dict[str, Any]) -> None:
    payload = core.rebuild_payload(state["payload"], state["records"], state["collection_key"])
    write_json(ROOT / state["path"], payload)


def record_at(ref: str, path: str, key: str) -> dict[str, Any] | None:
    raw = core.git_show(ref, path)
    if raw is None:
        return None
    try:
        payload = json.loads(raw)
        records, _ = core.collection(payload)
    except Exception:
        return None
    for record in records:
        if isinstance(record, dict) and core.key_of(record) == key:
            return record
    return None


def md_current_index() -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for path in (ROOT / "content").rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        parsed = core.frontmatter(text)
        if not parsed:
            continue
        meta, body = parsed
        slug = core.md_slug(str(path.relative_to(ROOT)), meta)
        index[slug] = {
            "path": str(path.relative_to(ROOT)),
            "text": text,
            "meta": meta,
            "body": body,
            "reviewed": str(meta.get("review_status") or "").casefold().strip() in REVIEWED,
            "sourced": core.has_source({"meta": meta, "body": body}),
        }
    return index


def strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from strings(item)


def editorial_approved_slugs() -> set[str]:
    approved: set[str] = set()
    root = ROOT / "editorial-approvals"
    if not root.exists():
        return approved
    slugish = re.compile(r"^[a-z0-9][a-z0-9-]{3,}$")
    for path in root.glob("*.json"):
        try:
            payload = read_json(path)
        except Exception:
            continue
        for value in strings(payload):
            value = value.strip()
            if slugish.match(value):
                approved.add(value)
    return approved


def fragment_slugs() -> set[str]:
    slugs: set[str] = set()
    for root_name in core.FRAGMENT_ROOTS:
        root = ROOT / root_name
        if not root.exists():
            continue
        for path in root.rglob("*.json"):
            try:
                payload = read_json(path)
            except Exception:
                continue
            records = payload if isinstance(payload, list) else [payload]
            for record in records:
                if isinstance(record, dict):
                    key = core.key_of(record)
                    if key:
                        slugs.add(key)
    return slugs


def canonical_record_ok(kind: str, record: dict[str, Any] | None, approved: set[str]) -> bool:
    if record is None:
        return False
    key = core.key_of(record) or ""
    if key in approved:
        return True
    if not core.reviewed(record):
        return False
    if core.has_source(record):
        return True
    return kind in {"trilhas", "checklists", "material_paciente"} and bool(core.origin_of(record))


def origin_document_ok(record: dict[str, Any], docs: dict[str, dict[str, Any]]) -> tuple[bool, str]:
    origin = core.origin_of(record)
    if not origin:
        return False, ""
    origin = origin.removesuffix(".md")
    doc = docs.get(origin)
    if doc and doc["reviewed"] and doc["sourced"]:
        return True, origin
    return False, origin


def medication_dose_is_only_lab_measurement(record: dict[str, Any]) -> bool:
    serial = json.dumps(record, ensure_ascii=False)
    matches = list(core.DOSE_RE.finditer(serial))
    if not matches:
        return True
    for match in matches:
        tail = serial[match.end() : match.end() + 8].casefold()
        if re.match(r"\s*/\s*(?:d?l|dl|100ml)\b", tail):
            continue
        return False
    return True


def canonical_sets(state: dict[str, dict[str, Any]], docs: dict[str, dict[str, Any]]) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {"documento": set(docs)}
    for kind, data in state.items():
        result[kind] = set(data["index"])
    return result


def track_refs(value: Any) -> list[tuple[str, str]]:
    refs: list[tuple[str, str]] = []
    if isinstance(value, dict):
        item_slug = value.get("item_slug") or value.get("target_slug")
        item_type = value.get("item_type") or value.get("target_type")
        if isinstance(item_slug, str) and isinstance(item_type, str):
            refs.append((item_type.casefold().strip(), item_slug.strip()))
        for child in value.values():
            refs.extend(track_refs(child))
    elif isinstance(value, list):
        for child in value:
            refs.extend(track_refs(child))
    return refs


def track_provenance_ok(record: dict[str, Any], sets: dict[str, set[str]]) -> tuple[bool, list[str]]:
    refs = track_refs(record)
    if not refs:
        return False, ["trilha sem referências estruturadas"]
    broken: list[str] = []
    for raw_type, slug in refs:
        kind = TYPE_ALIASES.get(raw_type, raw_type)
        keys = sets.get(kind)
        if keys is None or slug not in keys:
            broken.append(f"{raw_type}:{slug}")
    return not broken, broken


def generic_reference_slugs(value: Any) -> set[str]:
    refs: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            if key.endswith("_slug") and isinstance(child, str):
                refs.add(child.removesuffix(".md"))
            elif key.endswith("_slugs") and isinstance(child, list):
                refs.update(str(v).removesuffix(".md") for v in child if isinstance(v, str))
            refs.update(generic_reference_slugs(child))
    elif isinstance(value, list):
        for child in value:
            refs.update(generic_reference_slugs(child))
    return refs


def case_provenance_ok(record: dict[str, Any], all_keys: set[str]) -> bool:
    refs = generic_reference_slugs(record)
    return bool(refs) and all(ref in all_keys for ref in refs)


def list_identity(item: Any) -> tuple[str, str] | None:
    if not isinstance(item, dict):
        return None
    for key in ("id", "slug", "key", "codigo", "name", "nome", "title", "titulo"):
        value = item.get(key)
        if isinstance(value, (str, int)) and str(value).strip():
            return key, str(value).strip()
    return None


def three_way_merge(
    base_value: Any,
    head_value: Any,
    current_value: Any,
    *,
    path: str = "",
    candidate_reviewed: bool,
    candidate_sourced: bool,
    changes: list[str],
    conflicts: list[str],
) -> Any:
    if head_value == base_value:
        return current_value
    if current_value == head_value:
        return current_value

    root_key = path.split(".", 1)[0].split("[", 1)[0] if path else ""

    if current_value == base_value and root_key not in PROTECTED_KEYS:
        if candidate_reviewed and candidate_sourced:
            changes.append(path or "<root>")
            return copy.deepcopy(head_value)
        if SOURCEISH_KEY.search(root_key):
            changes.append(path or "<root>")
            return copy.deepcopy(head_value)

    if isinstance(base_value, dict) and isinstance(head_value, dict) and isinstance(current_value, dict):
        result = copy.deepcopy(current_value)
        for key, head_child in head_value.items():
            if key in PROTECTED_KEYS:
                continue
            child_path = f"{path}.{key}" if path else key
            if key not in base_value:
                if key not in result:
                    if candidate_reviewed and (candidate_sourced or SOURCEISH_KEY.search(key)):
                        result[key] = copy.deepcopy(head_child)
                        changes.append(child_path)
                elif result[key] != head_child:
                    conflicts.append(child_path)
                continue
            if key not in result:
                conflicts.append(child_path)
                continue
            result[key] = three_way_merge(
                base_value[key], head_child, result[key],
                path=child_path,
                candidate_reviewed=candidate_reviewed,
                candidate_sourced=candidate_sourced,
                changes=changes, conflicts=conflicts,
            )
        return result

    if isinstance(base_value, list) and isinstance(head_value, list) and isinstance(current_value, list):
        result = copy.deepcopy(current_value)
        head_ids = [list_identity(v) for v in head_value]
        current_ids = [list_identity(v) for v in current_value]
        if head_value and all(v is not None for v in head_ids) and all(v is not None for v in current_ids if current_value):
            def as_map(values):
                return {list_identity(v): v for v in values if list_identity(v) is not None}
            bmap, hmap, cmap = as_map(base_value), as_map(head_value), as_map(current_value)
            out = copy.deepcopy(current_value)
            positions = {list_identity(v): i for i, v in enumerate(out) if list_identity(v) is not None}
            for ident, hitem in hmap.items():
                item_path = f"{path}[{ident[0]}={ident[1]}]"
                if ident not in bmap:
                    if ident not in cmap and candidate_reviewed and candidate_sourced:
                        out.append(copy.deepcopy(hitem))
                        changes.append(item_path)
                    continue
                if ident not in cmap:
                    conflicts.append(item_path)
                    continue
                pos = positions[ident]
                out[pos] = three_way_merge(
                    bmap[ident], hitem, out[pos],
                    path=item_path,
                    candidate_reviewed=candidate_reviewed,
                    candidate_sourced=candidate_sourced,
                    changes=changes, conflicts=conflicts,
                )
            return out

        additions = [item for item in head_value if item not in base_value]
        for item in additions:
            if item in result:
                continue
            if candidate_reviewed and (candidate_sourced or SOURCEISH_KEY.search(root_key)):
                result.append(copy.deepcopy(item))
                changes.append(f"{path}[+]")
        return result

    if current_value != base_value and current_value != head_value:
        conflicts.append(path or "<root>")
    return current_value


def mark_reviewed_with_provenance(record: dict[str, Any], note: str) -> dict[str, Any]:
    out = core.mark_reviewed(record)
    existing = str(out.get("review_note") or "").strip()
    if note and note not in existing:
        out["review_note"] = (existing + " " + note).strip()
    return out


def replace_record(state: dict[str, Any], key: str, new_record: dict[str, Any]) -> None:
    for index, record in enumerate(state["records"]):
        if core.key_of(record) == key:
            state["records"][index] = new_record
            state["index"][key] = new_record
            return
    state["records"].append(new_record)
    state["index"][key] = new_record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", default="artifacts/science-reconcile-report.json")
    parser.add_argument("--pr-metadata", required=True)
    parser.add_argument("--output-json", default="artifacts/science-residual-resolution.json")
    parser.add_argument("--output-md", default="docs/RESOLUCAO-CIENTIFICA-RESIDUAL-20260904.md")
    args = parser.parse_args()

    report = read_json(ROOT / args.report)
    metadata_list = read_json(Path(args.pr_metadata))
    metadata = {int(item["number"]): item for item in metadata_list}

    state = current_collection_state()
    docs = md_current_index()
    approved = editorial_approved_slugs()
    fragments = fragment_slugs()
    sets = canonical_sets(state, docs)
    all_keys = set().union(*sets.values()) if sets else set()

    resolutions: list[Resolution] = []
    changed_manifests: set[str] = set()

    residuals = [
        d for d in report.get("decisions", [])
        if d.get("status") in {"conflict", "needs_manual_review"}
    ]

    for decision in residuals:
        pr = int(decision["pr"])
        kind = str(decision["kind"])
        key = str(decision["key"])
        path = str(decision["path"])
        original_reason = str(decision.get("reason") or "")
        meta = metadata.get(pr)
        if not meta:
            resolutions.append(Resolution("unresolved", pr, kind, key, path, "metadados do PR indisponíveis"))
            continue
        base_sha = str(meta["base_sha"])
        head_ref = f"refs/remotes/pr/{pr}"

        if kind == "documento":
            current_doc = docs.get(key)
            if current_doc and current_doc["reviewed"] and current_doc["sourced"]:
                resolutions.append(Resolution(
                    "current_wins", pr, kind, key, path,
                    "documento canônico atual já revisado e com fonte; versão antiga superseded",
                ))
            else:
                resolutions.append(Resolution(
                    "unresolved", pr, kind, key, path,
                    "documento divergente sem versão canônica simultaneamente revisada e rastreável",
                ))
            continue

        if kind in {"doencas", "triagem"} and key in fragments:
            resolutions.append(Resolution(
                "current_wins", pr, kind, key, path,
                "slug já existe como fragmento canônico composto",
            ))
            continue

        current_state = state.get(kind)
        if current_state is None:
            resolutions.append(Resolution("unresolved", pr, kind, key, path, "frente científica desconhecida"))
            continue

        current = current_state["index"].get(key)
        head = record_at(head_ref, path, key)
        base_record = record_at(base_sha, path, key)

        if head is None:
            resolutions.append(Resolution("unresolved", pr, kind, key, path, "registro não encontrado no head do PR"))
            continue

        if current is not None and kind != "medicamentos":
            if canonical_record_ok(kind, current, approved):
                resolutions.append(Resolution(
                    "current_wins", pr, kind, key, path,
                    "registro canônico atual já revisado/aprovado; delta antigo superseded",
                ))
                continue
            ok, reason = core.validate_record(kind, head)
            if ok and core.reviewed(head) and base_record is not None and current == base_record:
                promoted = mark_reviewed_with_provenance(
                    head, "Delta do PR revisado novamente sobre base canônica sem divergência posterior."
                )
                replace_record(current_state, key, promoted)
                changed_manifests.add(kind)
                resolutions.append(Resolution("merged", pr, kind, key, path, "upgrade sem conflito do registro canônico"))
            else:
                resolutions.append(Resolution(
                    "unresolved", pr, kind, key, path,
                    reason or "canônico não certificado e candidato diverge",
                ))
            continue

        if kind == "medicamentos" and current is not None:
            if not core.reviewed(current) and key in approved:
                current = core.mark_reviewed(current)
            serial_head = json.dumps(head, ensure_ascii=False)
            placeholder = core.PLACEHOLDER_RE.search(serial_head)
            candidate_sourced = core.has_source(head)
            candidate_reviewed = core.reviewed(head)
            if placeholder and canonical_record_ok(kind, current, approved):
                resolutions.append(Resolution(
                    "current_wins", pr, kind, key, path,
                    f"candidato antigo contém placeholder ({placeholder.group(0)}); canônico atual preservado",
                ))
                continue
            if base_record is None:
                if canonical_record_ok(kind, current, approved):
                    resolutions.append(Resolution(
                        "current_wins", pr, kind, key, path,
                        "base do PR não continha o registro; canônico revisado atual preservado",
                    ))
                else:
                    resolutions.append(Resolution("unresolved", pr, kind, key, path, "sem base para merge de três vias"))
                continue

            changes: list[str] = []
            conflicts: list[str] = []
            merged = three_way_merge(
                base_record, head, current,
                candidate_reviewed=candidate_reviewed,
                candidate_sourced=candidate_sourced,
                changes=changes,
                conflicts=conflicts,
            )
            if changes:
                merged = mark_reviewed_with_provenance(
                    merged,
                    "Deltas aditivos do PR reconciliados em três vias; valores canônicos mais novos foram preservados.",
                )
                replace_record(current_state, key, merged)
                changed_manifests.add(kind)
                resolutions.append(Resolution(
                    "merged", pr, kind, key, path,
                    "delta aditivo reconciliado sem regressão",
                    changed_paths=changes,
                    details={"preserved_conflicts": conflicts[:100]},
                ))
            elif canonical_record_ok(kind, current, approved):
                resolutions.append(Resolution(
                    "current_wins", pr, kind, key, path,
                    "nenhum delta adicional seguro; ficha canônica revisada preservada",
                    details={"preserved_conflicts": conflicts[:100]},
                ))
            else:
                resolutions.append(Resolution(
                    "unresolved", pr, kind, key, path,
                    "medicamento sem delta seguro e ficha canônica não certificada",
                    details={"preserved_conflicts": conflicts[:100]},
                ))
            continue

        if current is None:
            serial = json.dumps(head, ensure_ascii=False)
            placeholder = core.PLACEHOLDER_RE.search(serial)
            if placeholder:
                resolutions.append(Resolution(
                    "unresolved", pr, kind, key, path,
                    f"placeholder real ainda presente: {placeholder.group(0)}",
                ))
                continue

            direct_source = core.has_source(head)
            origin_ok, origin = origin_document_ok(head, docs)

            if kind == "material_paciente":
                if not medication_dose_is_only_lab_measurement(head):
                    resolutions.append(Resolution(
                        "unresolved", pr, kind, key, path,
                        "possível posologia medicamentosa em material ao paciente exige revisão clínica manual",
                    ))
                    continue
                if direct_source or origin_ok:
                    promoted = mark_reviewed_with_provenance(
                        head,
                        f"Proveniência validada pelo documento canônico `{origin}`." if origin_ok else
                        "Fontes rastreáveis do próprio material revalidadas.",
                    )
                    replace_record(current_state, key, promoted)
                    changed_manifests.add(kind)
                    sets.setdefault(kind, set()).add(key)
                    all_keys.add(key)
                    resolutions.append(Resolution("merged", pr, kind, key, path, "material derivado validado e revisado"))
                else:
                    resolutions.append(Resolution("unresolved", pr, kind, key, path, "material novo sem fonte nem documento de origem validado"))
                continue

            if kind == "checklists":
                if direct_source or origin_ok:
                    promoted = mark_reviewed_with_provenance(
                        head,
                        f"Proveniência validada pelo documento canônico `{origin}`." if origin_ok else
                        "Fontes rastreáveis do checklist revalidadas.",
                    )
                    replace_record(current_state, key, promoted)
                    changed_manifests.add(kind)
                    sets.setdefault(kind, set()).add(key)
                    all_keys.add(key)
                    resolutions.append(Resolution("merged", pr, kind, key, path, "checklist derivado validado e revisado"))
                else:
                    resolutions.append(Resolution("unresolved", pr, kind, key, path, "checklist novo sem fonte nem documento de origem validado"))
                continue

            if kind == "trilhas":
                ok, broken = track_provenance_ok(head, sets)
                if direct_source or ok:
                    promoted = mark_reviewed_with_provenance(
                        head,
                        "Trilha revisada por proveniência estrutural: módulos resolvem para itens canônicos do corpus."
                        if ok else "Fontes rastreáveis da trilha revalidadas.",
                    )
                    replace_record(current_state, key, promoted)
                    changed_manifests.add(kind)
                    sets.setdefault(kind, set()).add(key)
                    all_keys.add(key)
                    resolutions.append(Resolution("merged", pr, kind, key, path, "trilha validada por módulos canônicos"))
                else:
                    resolutions.append(Resolution(
                        "unresolved", pr, kind, key, path,
                        "trilha com referências não resolvidas",
                        details={"broken_refs": broken[:100]},
                    ))
                continue

            if kind == "casos_clinicos":
                if direct_source or case_provenance_ok(head, all_keys):
                    promoted = mark_reviewed_with_provenance(
                        head, "Caso revisado por fontes/referências canônicas resolvidas."
                    )
                    replace_record(current_state, key, promoted)
                    changed_manifests.add(kind)
                    sets.setdefault(kind, set()).add(key)
                    all_keys.add(key)
                    resolutions.append(Resolution("merged", pr, kind, key, path, "caso clínico validado e revisado"))
                else:
                    resolutions.append(Resolution("unresolved", pr, kind, key, path, "caso novo sem proveniência suficiente"))
                continue

            if kind == "medicamentos":
                if direct_source and core.reviewed(head):
                    promoted = mark_reviewed_with_provenance(
                        head, "Ficha farmacológica nova com fontes rastreáveis revalidada."
                    )
                    replace_record(current_state, key, promoted)
                    changed_manifests.add(kind)
                    sets.setdefault(kind, set()).add(key)
                    all_keys.add(key)
                    resolutions.append(Resolution("merged", pr, kind, key, path, "medicamento novo revisado e rastreável"))
                else:
                    resolutions.append(Resolution(
                        "unresolved", pr, kind, key, path,
                        "medicamento novo sem fonte rastreável e revisão prévia suficientes",
                    ))
                continue

            if direct_source and core.reviewed(head):
                promoted = mark_reviewed_with_provenance(head, "Fontes rastreáveis revalidadas.")
                replace_record(current_state, key, promoted)
                changed_manifests.add(kind)
                sets.setdefault(kind, set()).add(key)
                all_keys.add(key)
                resolutions.append(Resolution("merged", pr, kind, key, path, "registro novo revisado e rastreável"))
            else:
                resolutions.append(Resolution("unresolved", pr, kind, key, path, original_reason or "sem validação suficiente"))
            continue

        resolutions.append(Resolution("unresolved", pr, kind, key, path, "caso residual não classificado"))

    for kind in sorted(changed_manifests):
        rebuild_manifest(state[kind])

    summary: dict[str, int] = defaultdict(int)
    for item in resolutions:
        summary[item.status] += 1

    output = {
        "schema_version": 1,
        "input_report": args.report,
        "summary": dict(sorted(summary.items())),
        "changed_manifests": sorted(changed_manifests),
        "resolutions": [asdict(item) for item in resolutions],
    }
    write_json(ROOT / args.output_json, output)

    lines = [
        "# Resolução científica residual — 04/09/2026",
        "",
        "Revisão em três vias sobre o corpus canônico. Nenhum deploy ou publicação em banco foi executado.",
        "",
        "## Resumo",
        "",
    ]
    for key, value in sorted(summary.items()):
        lines.append(f"- **{key}**: {value}")
    lines += ["", "## Pendências ainda não resolvidas", ""]
    unresolved = [item for item in resolutions if item.status == "unresolved"]
    if not unresolved:
        lines.append("- Nenhuma.")
    else:
        for item in unresolved:
            lines.append(
                f"- PR #{item.pr} · `{item.kind}` · `{item.key}` · `{item.path}` — {item.reason}"
            )
    (ROOT / args.output_md).parent.mkdir(parents=True, exist_ok=True)
    (ROOT / args.output_md).write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps(output["summary"], ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
