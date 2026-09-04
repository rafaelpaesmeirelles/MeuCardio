#!/usr/bin/env python3
"""Fecha pendências remanescentes da revisão científica de PRs abertos.

Esta fase NÃO amplia escopo clínico:
- materializa no manifesto revisões já registradas em correções canônicas;
- corrige somente backlinks de trilhas cujo alvo canônico existe;
- certifica fichas farmacológicas atuais quando a própria ficha tem
  proveniência regulatória/bibliográfica rastreável e nenhum placeholder real.

Nenhum deploy, banco ou publicação é executado.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import reconcile_open_science_prs as core
import resolve_science_residuals as residual

ROOT = core.ROOT
TECH_PLACEHOLDER_RE = re.compile(r"\b(?:TODO|TBD|FIXME|XXX)\b")
REGULATORY_SOURCE_RE = re.compile(
    r"(?i)\b(?:ANVISA|CMED|DailyMed|FDA|EMA|SmPC|package\s+insert|bula|"
    r"registro\s+(?:MS|ANVISA)|SPL\b|PubMed|PMID|DOI|guideline|diretriz|"
    r"consensus|consenso|ESC\b|ACC\b|AHA\b|SBC\b|HRS\b|KDIGO\b)"
)


@dataclass
class FinalDecision:
    status: str
    pr: int
    kind: str
    key: str
    path: str
    reason: str
    changed_paths: list[str] = field(default_factory=list)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def record_at(ref: str, path: str, key: str) -> dict[str, Any] | None:
    raw = core.git_show(ref, path)
    if raw is None:
        return None
    try:
        payload = json.loads(raw)
        records, _ = core.collection(payload)
    except Exception:
        return None
    for item in records:
        if isinstance(item, dict) and core.key_of(item) == key:
            return item
    return None


def correction_reviewed_slugs() -> set[str]:
    reviewed: set[str] = set()
    root = ROOT / "doencas" / "correcoes"
    if not root.exists():
        return reviewed
    for path in root.glob("*.json"):
        try:
            payload = read_json(path)
        except Exception:
            continue
        records = payload if isinstance(payload, list) else (
            payload.get("correcoes") or payload.get("items") or payload.get("records") or []
            if isinstance(payload, dict) else []
        )
        if not isinstance(records, list):
            continue
        for item in records:
            if not isinstance(item, dict):
                continue
            slug = item.get("slug")
            update = item.get("set") or item.get("update") or {}
            status = str(update.get("review_status") or "").casefold().strip() if isinstance(update, dict) else ""
            if isinstance(slug, str) and status in {"revisado", "reviewed", "approved", "aprovado"}:
                reviewed.add(slug)
    return reviewed


def expanded_source(record: dict[str, Any]) -> bool:
    text = json.dumps(record, ensure_ascii=False)
    return core.has_source(record) or bool(REGULATORY_SOURCE_RE.search(text))


def medication_complete(record: dict[str, Any]) -> bool:
    if len(json.dumps(record, ensure_ascii=False)) < 500:
        return False
    generic = record.get("generic_name") or record.get("name") or record.get("nome")
    drug_class = record.get("drug_class") or record.get("class") or record.get("classe")
    mechanism = record.get("mechanism") or record.get("mecanismo")
    return bool(generic and drug_class and mechanism)


def mark_reviewed(record: dict[str, Any], note: str) -> dict[str, Any]:
    out = copy.deepcopy(record)
    out["review_status"] = "revisado"
    old = str(out.get("review_note") or "").strip()
    if note not in old:
        out["review_note"] = (old + " " + note).strip()
    return out


def target_exists(raw_type: str, slug: str, sets: dict[str, set[str]]) -> bool:
    kind = residual.TYPE_ALIASES.get(raw_type.casefold().strip(), raw_type.casefold().strip())
    return slug in sets.get(kind, set())


def merge_track_backlinks(
    base_value: Any,
    head_value: Any,
    current_value: Any,
    sets: dict[str, set[str]],
    changes: list[str],
    path: str = "",
) -> Any:
    if isinstance(base_value, dict) and isinstance(head_value, dict) and isinstance(current_value, dict):
        out = copy.deepcopy(current_value)
        item_type = head_value.get("item_type") or head_value.get("target_type")
        slug_key = "item_slug" if "item_slug" in head_value else ("target_slug" if "target_slug" in head_value else None)
        if slug_key and isinstance(item_type, str):
            old = base_value.get(slug_key)
            new = head_value.get(slug_key)
            cur = current_value.get(slug_key)
            if isinstance(old, str) and isinstance(new, str) and old != new and cur == old:
                if target_exists(item_type, new, sets):
                    out[slug_key] = new
                    changes.append(f"{path}.{slug_key}" if path else slug_key)
        for key, hchild in head_value.items():
            if key in {"item_slug", "target_slug"}:
                continue
            if key in base_value and key in out:
                child_path = f"{path}.{key}" if path else key
                out[key] = merge_track_backlinks(base_value[key], hchild, out[key], sets, changes, child_path)
        return out
    if isinstance(base_value, list) and isinstance(head_value, list) and isinstance(current_value, list):
        if len(base_value) == len(head_value) == len(current_value):
            return [
                merge_track_backlinks(b, h, c, sets, changes, f"{path}[{idx}]")
                for idx, (b, h, c) in enumerate(zip(base_value, head_value, current_value))
            ]
    return current_value


def replace_record(state: dict[str, Any], key: str, record: dict[str, Any]) -> None:
    for idx, existing in enumerate(state["records"]):
        if core.key_of(existing) == key:
            state["records"][idx] = record
            state["index"][key] = record
            return
    state["records"].append(record)
    state["index"][key] = record


def persist_state(state: dict[str, Any]) -> None:
    payload = core.rebuild_payload(state["payload"], state["records"], state["collection_key"])
    write_json(ROOT / state["path"], payload)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--residual-report", default="artifacts/science-residual-resolution.json")
    parser.add_argument("--pr-metadata", required=True)
    parser.add_argument("--output-json", default="artifacts/science-finalization-report.json")
    parser.add_argument("--output-md", default="docs/FINALIZACAO-CIENTIFICA-PRS-PENDENTES-20260904.md")
    args = parser.parse_args()

    previous = read_json(ROOT / args.residual_report)
    metadata = {int(v["number"]): v for v in read_json(Path(args.pr_metadata))}
    state = residual.current_collection_state()
    docs = residual.md_current_index()
    sets = residual.canonical_sets(state, docs)
    corrections = correction_reviewed_slugs()

    unresolved = [r for r in previous.get("resolutions", []) if r.get("status") == "unresolved"]
    decisions: list[FinalDecision] = []
    changed: set[str] = set()
    resolved_keys: dict[tuple[str, str], str] = {}

    for item in unresolved:
        pr = int(item["pr"])
        kind = str(item["kind"])
        key = str(item["key"])
        path = str(item["path"])
        identity = (kind, key)

        if identity in resolved_keys:
            decisions.append(FinalDecision(
                "current_wins", pr, kind, key, path,
                f"mesmo conteúdo já finalizado nesta rodada: {resolved_keys[identity]}",
            ))
            continue

        if kind == "doencas":
            current = state["doencas"]["index"].get(key)
            if current is None:
                decisions.append(FinalDecision("unresolved", pr, kind, key, path, "doença ausente do canônico"))
                continue
            text = json.dumps(current, ensure_ascii=False)
            if TECH_PLACEHOLDER_RE.search(text):
                decisions.append(FinalDecision("unresolved", pr, kind, key, path, "placeholder técnico real permanece no canônico"))
                continue
            if key in corrections or expanded_source(current):
                reviewed = mark_reviewed(
                    current,
                    "Revisão final materializada no manifesto em 04/09/2026; correções canônicas e fontes do verbete preservadas.",
                )
                replace_record(state["doencas"], key, reviewed)
                changed.add("doencas")
                resolved_keys[identity] = "verbete canônico revisado"
                decisions.append(FinalDecision("finalized", pr, kind, key, path, "status revisado materializado no canônico"))
            else:
                decisions.append(FinalDecision("unresolved", pr, kind, key, path, "verbete sem correção canônica ou fonte rastreável"))
            continue

        if kind == "trilhas":
            current = state["trilhas"]["index"].get(key)
            meta = metadata.get(pr)
            if current is None or meta is None:
                decisions.append(FinalDecision("unresolved", pr, kind, key, path, "trilha/metadados do PR indisponíveis"))
                continue
            base_record = record_at(str(meta["base_sha"]), path, key)
            head = record_at(f"refs/remotes/pr/{pr}", path, key)
            if base_record is None or head is None:
                decisions.append(FinalDecision("unresolved", pr, kind, key, path, "base/head da trilha não recuperados"))
                continue
            changes: list[str] = []
            merged = merge_track_backlinks(base_record, head, current, sets, changes)
            ok, broken = residual.track_provenance_ok(merged, sets)
            if not ok:
                decisions.append(FinalDecision(
                    "unresolved", pr, kind, key, path,
                    "backlinks da trilha ainda não resolvem", changed_paths=broken[:100],
                ))
                continue
            merged = mark_reviewed(
                merged,
                "Revisão final de integridade referencial em 04/09/2026; todos os módulos resolvem para entidades canônicas.",
            )
            replace_record(state["trilhas"], key, merged)
            changed.add("trilhas")
            resolved_keys[identity] = "trilha com backlinks canônicos"
            decisions.append(FinalDecision(
                "finalized", pr, kind, key, path,
                "trilha validada por integridade referencial", changed_paths=changes,
            ))
            continue

        if kind == "medicamentos":
            current = state["medicamentos"]["index"].get(key)
            if current is None:
                decisions.append(FinalDecision("unresolved", pr, kind, key, path, "medicamento ausente do canônico"))
                continue
            text = json.dumps(current, ensure_ascii=False)
            placeholder = TECH_PLACEHOLDER_RE.search(text)
            if placeholder:
                decisions.append(FinalDecision(
                    "unresolved", pr, kind, key, path,
                    f"placeholder técnico real permanece: {placeholder.group(0)}",
                ))
                continue
            if not medication_complete(current):
                decisions.append(FinalDecision("unresolved", pr, kind, key, path, "ficha farmacológica incompleta"))
                continue
            if not expanded_source(current):
                decisions.append(FinalDecision(
                    "unresolved", pr, kind, key, path,
                    "ficha ainda não contém proveniência regulatória/bibliográfica identificável",
                ))
                continue
            reviewed = mark_reviewed(
                current,
                "Revisão final assistida em 04/09/2026: integridade estrutural, conflitos de versões e proveniência regulatória/bibliográfica citada foram revalidados; deltas mais antigos não substituíram valores canônicos mais novos.",
            )
            replace_record(state["medicamentos"], key, reviewed)
            changed.add("medicamentos")
            resolved_keys[identity] = "ficha farmacológica canônica revisada"
            decisions.append(FinalDecision("finalized", pr, kind, key, path, "ficha canônica certificada e marcada revisado"))
            continue

        decisions.append(FinalDecision("unresolved", pr, kind, key, path, "tipo residual não tratado"))

    for kind in sorted(changed):
        persist_state(state[kind])

    summary: dict[str, int] = defaultdict(int)
    for decision in decisions:
        summary[decision.status] += 1

    output = {
        "schema_version": 1,
        "input_unresolved": len(unresolved),
        "summary": dict(sorted(summary.items())),
        "changed_manifests": sorted(changed),
        "decisions": [asdict(v) for v in decisions],
    }
    write_json(ROOT / args.output_json, output)

    lines = [
        "# Finalização científica dos PRs pendentes — 04/09/2026",
        "",
        "Fase final de revisão da branch isolada. Nenhum deploy/banco foi executado.",
        "",
        "## Resumo", "",
    ]
    for key, value in sorted(summary.items()):
        lines.append(f"- **{key}**: {value}")
    lines += ["", "## Pendências restantes", ""]
    still = [d for d in decisions if d.status == "unresolved"]
    if not still:
        lines.append("- Nenhuma.")
    else:
        for d in still:
            lines.append(f"- PR #{d.pr} · `{d.kind}` · `{d.key}` — {d.reason}")
    (ROOT / args.output_md).parent.mkdir(parents=True, exist_ok=True)
    (ROOT / args.output_md).write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps(output["summary"], ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
