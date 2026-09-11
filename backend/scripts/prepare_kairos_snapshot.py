"""Prepare, never activate, the reviewed K@iros 453 expansion (stdlib only).

Without --output this is a dry run. An explicit output and audit destination
are required to write; existing files additionally require --replace.
Minimums select one original row, never a vector assembled from several rows.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import unicodedata


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BASELINE = ROOT / "backend/tests/fixtures/kairos-453-2026-08-cardiovascular.json"
SOURCE_SHA256 = "32e4dff5205f7387040900df9820a65b78825e12028db698aa11c482297bc142"
APPROVED_CANDIDATE_SHA256 = "278b4370c5478a4fc931b1be2537b2b4a637e232a90ce9a33e3302e1849b3998"
BASELINE_CANONICAL_SHA256 = "8fb583d03e3ceedaf7539206c1a14261bd87b091b7dbbca8ea70a0987debef48"
PRICE_FIELDS = ("pf20", "pmc20", "pf18", "pmc18", "pf17", "pmc17", "pf12", "pmc12")
EXCLUSIONS = {
    ("micardis", "boehringer", 50): "published_composition_conflicts_with_catalogue",
    ("mirugell", "cristalia", 51): "ambiguous_source_annotation",
    ("triplixam", "servier", 72): "incomplete_published_ingredient_heading",
    ("repatha", "amgen", 63): "catalogue_groups_distinct_active_ingredients",
}


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def identity(value: str) -> str:
    # Preserve punctuation and word boundaries: 1.5, 15, XR, package counts,
    # and combinations must not collapse to the same presentation identity.
    return " ".join(unicodedata.normalize("NFKC", value).casefold().split())


def exclusion_name(value: str) -> str:
    return unicodedata.normalize("NFKD", identity(value)).encode("ascii", "ignore").decode()


def money(value: object) -> Decimal:
    if not isinstance(value, str) or len(value) > 64 or not re.fullmatch(
        r"(?:0|[1-9][0-9]*|[1-9][0-9]{0,2}(?:\.[0-9]{3})+),[0-9]{2}", value
    ):
        raise ValueError("Price must be a literal pt-BR monetary string")
    number = Decimal(value.replace(".", "").replace(",", "."))
    if not number.is_finite() or number <= 0:
        raise ValueError("Price must be finite and positive")
    return number


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_keys)


def row_key(record: dict, presentation: dict) -> tuple[str, str, str]:
    return identity(record["product"]), identity(record["laboratory"]), identity(presentation["presentation"])


def price_vector(presentation: dict) -> dict:
    return {field: presentation[field] for field in PRICE_FIELDS if field in presentation}


def source_order(row: dict) -> tuple:
    coords = row["source"]
    return (coords["page"], 0 if coords["side"] == "left" else 1,
            coords["line"], row["record_index"], row["presentation_index"])


def audit_variant(row: dict) -> dict:
    return {
        "record_index": row["record_index"], "presentation_index": row["presentation_index"],
        "product": row["record"]["product"], "laboratory": row["record"]["laboratory"],
        "substance": row["record"].get("substance"),
        "presentation": row["presentation"]["presentation"],
        "prices": price_vector(row["presentation"]), "source": deepcopy(row["source"]),
    }


def _rows(raw: dict) -> list[dict]:
    if not isinstance(raw.get("records"), list):
        raise ValueError("Raw records must be a list")
    rows = []
    for record_index, record in enumerate(raw["records"]):
        if not isinstance(record, dict):
            raise ValueError("Invalid raw record")
        for key in ("product", "laboratory"):
            if not isinstance(record.get(key), str) or not record[key].strip():
                raise ValueError(f"Invalid {key} in record {record_index}")
        if record.get("substance") is not None and (
            not isinstance(record["substance"], str) or not record["substance"].strip()
        ):
            raise ValueError(f"Invalid substance in record {record_index}")
        if type(record.get("page")) is not int or not 8 <= record["page"] <= 78:
            raise ValueError("Raw row is outside the reviewed source pages")
        if not isinstance(record.get("presentations"), list) or not record["presentations"]:
            raise ValueError("Raw presentations must be a nonempty list")
        for presentation_index, presentation in enumerate(record["presentations"]):
            if not isinstance(presentation, dict) or not isinstance(presentation.get("presentation"), str) or not presentation["presentation"].strip():
                raise ValueError("Invalid presentation")
            for field, value in presentation.items():
                if field.lower().startswith(("pf", "pmc")) and field not in PRICE_FIELDS:
                    raise ValueError(f"Unreviewed price field: {field}")
                if field in PRICE_FIELDS and value is not None and value != "":
                    money(value)
            page = presentation.get("source_page", record["page"])
            side, line = presentation.get("source_side"), presentation.get("source_line")
            if page != record["page"] or side not in ("left", "right") or type(line) is not int or line <= 0:
                raise ValueError("Missing or inconsistent raw source coordinates")
            rows.append({
                "record": record, "presentation": presentation,
                "record_index": record_index, "presentation_index": presentation_index,
                "source": {"page": page, "side": side, "line": line,
                           "bbox": deepcopy(presentation.get("bbox")),
                           "description_lines": deepcopy(presentation.get("source_description_lines", []))},
            })
    return rows


def choose_row(rows: list[dict]) -> tuple[dict, str]:
    """PMC first. A lower PF never wins over an available consumer price."""
    for prefix, reason in (("pmc", "minimum_positive_pmc_original_row"),
                           ("pf", "minimum_positive_pf_only_original_row")):
        candidates = []
        for row in rows:
            amounts = [money(value) for field, value in price_vector(row["presentation"]).items()
                       if field.startswith(prefix) and value is not None and value != ""]
            if amounts:
                candidates.append((min(amounts), source_order(row), row))
        if candidates:
            return min(candidates, key=lambda entry: entry[:2])[2], reason
    return min(rows, key=source_order), "no_published_price_source_order"


def prepare_snapshot(raw: dict, baseline: dict) -> tuple[dict, dict]:
    """Return a non-active snapshot and its complete row-decision audit."""
    if canonical_sha256(baseline) != BASELINE_CANONICAL_SHA256:
        raise ValueError("Historical baseline differs from the reviewed 13/52 fixture")
    if not isinstance(raw, dict) or any(raw.get(key) != baseline[key] for key in (
        "schema_version", "issue", "competence", "source_type",
    )) or raw.get("licensed_use") is not True:
        raise ValueError("Raw source edition/classification does not match the reviewed baseline")
    if raw.get("parse_evidence", {}).get("source_sha256") != SOURCE_SHA256:
        raise ValueError("Raw source PDF digest is not the reviewed edition")

    rows = _rows(raw)
    baseline_by_key = {row_key(record, presentation): (record, presentation)
                       for record in baseline["records"] for presentation in record["presentations"]}
    if len(baseline["records"]) != 13 or len(baseline_by_key) != 52:
        raise ValueError("Unexpected baseline cardinality")
    groups: dict[tuple, list[dict]] = {}
    decisions = []
    for row in rows:
        record = row["record"]
        excluded = EXCLUSIONS.get((exclusion_name(record["product"]), exclusion_name(record["laboratory"]), record["page"]))
        if excluded:
            decisions.append({"action": "quarantine", "reason": excluded,
                              "selected": None, "variants": [audit_variant(row)]})
        else:
            groups.setdefault(row_key(record, row["presentation"]), []).append(row)

    selected_rows = []
    baseline_seen = set()
    for key, variants in groups.items():
        ordered = sorted(variants, key=source_order)
        if key in baseline_by_key:
            record, presentation = baseline_by_key[key]
            corroborating = [row for row in variants if all(
                row["presentation"].get(field) == presentation.get(field) for field in PRICE_FIELDS
            )]
            if not corroborating:
                raise ValueError(f"Raw source no longer corroborates baseline prices: {record['product']}")
            baseline_seen.add(key)
            decisions.append({
                "action": "preserve_baseline", "reason": "reviewed_baseline_precedence_not_reparsed_literal",
                "selected": {"product": record["product"], "laboratory": record["laboratory"],
                             "substance": record.get("substance"), "page": record["page"],
                             "presentation": presentation["presentation"], "prices": price_vector(presentation)},
                "variants": [audit_variant(row) for row in ordered],
            })
            continue
        substances = {identity(row["record"]["substance"]) if row["record"].get("substance") is not None else None for row in variants}
        if len(substances) > 1:
            decisions.append({"action": "quarantine", "reason": "duplicate_composition_headings_disagree",
                              "selected": None, "variants": [audit_variant(row) for row in ordered]})
            continue
        chosen, reason = choose_row(variants)
        selected_rows.append(chosen)
        decisions.append({"action": "select_original_row", "reason": reason,
                          "selected": audit_variant(chosen), "variants": [audit_variant(row) for row in ordered]})
    if baseline_seen != set(baseline_by_key):
        raise ValueError("Raw source is missing one or more of the 52 baseline presentations")

    output = deepcopy(baseline)
    for record in output["records"]:
        record["curation_provenance"] = {
            "kind": "reviewed_cardiovascular_baseline",
            "baseline_canonical_sha256": BASELINE_CANONICAL_SHA256,
            "note": "Preserved prior reviewed labels, substance and prices; not a claim of verbatim PDF transcription.",
        }
    record_groups = {}
    for row in sorted(selected_rows, key=source_order):
        index = row["record_index"]
        if index not in record_groups:
            original = row["record"]
            record_groups[index] = {key: original.get(key) for key in ("product", "laboratory", "substance", "page")}
            record_groups[index]["presentations"] = []
            record_groups[index]["source_origin"] = "pdf_literal_selected_original_row"
            output["records"].append(record_groups[index])
        record_groups[index]["presentations"].append({
            "presentation": row["presentation"]["presentation"], **price_vector(row["presentation"]),
            "source_page": row["source"]["page"], "source_side": row["source"]["side"], "source_line": row["source"]["line"],
        })

    row_actions = Counter()
    for decision in decisions:
        row_actions[decision["action"]] += len(decision["variants"])
    counts = {
        "input_records": len(raw["records"]), "input_presentations": len(rows),
        "input_price_cells": sum(sum(v is not None and v != "" for v in price_vector(row["presentation"]).values()) for row in rows),
        "baseline_records_preserved": 13, "baseline_presentations_preserved": 52,
        "baseline_raw_occurrences": row_actions["preserve_baseline"],
        "quarantined_presentations": row_actions["quarantine"],
        "new_selected_presentations": len(selected_rows),
        "duplicate_rows_not_selected": row_actions["select_original_row"] - len(selected_rows),
        "output_records": len(output["records"]),
        "output_product_laboratory_pairs": len({(identity(r["product"]), identity(r["laboratory"])) for r in output["records"]}),
        "output_presentations": 52 + len(selected_rows),
        "output_price_cells": sum(sum(v is not None and v != "" for v in price_vector(p).values()) for r in output["records"] for p in r["presentations"]),
        "output_presentations_with_pmc": sum(any(p.get(f) not in (None, "") for f in PRICE_FIELDS if f.startswith("pmc")) for r in output["records"] for p in r["presentations"]),
    }
    provenance = {
        "status": "prepared_not_active", "source_file": raw["parse_evidence"].get("source_file"),
        "source_sha256": SOURCE_SHA256, "source_citation": baseline["source"],
        "source_page_count": 80, "extracted_physical_pages": [8, 78],
        "raw_candidate_canonical_sha256": canonical_sha256(raw),
        "baseline_canonical_sha256": BASELINE_CANONICAL_SHA256,
        "selection_policy": "One original row with lowest positive PMC for the same edition/product/laboratory/presentation; source-order ties. PF-only is never PMC.",
        "baseline_policy": "Preserve the prior 13 records/52 presentations verbatim in their existing order; takes precedence over new minimum selection.",
        "geographic_policy": "Comparison across literal published ICMS columns, not an inferred UF or pharmacy price.",
        "counters": counts,
    }
    output["preparation_evidence"] = provenance
    audit = {"provenance": deepcopy(provenance), "reason_groups": dict(Counter(d["reason"] for d in decisions)), "decisions": decisions}
    return output, audit


def write_result(path: Path, value: dict, *, replace: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, prefix=".kairos-prepared-", delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(value, stream, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
            stream.write("\n")
        if replace:
            os.replace(temporary, path)
        else:
            os.link(temporary, path)  # Atomic refusal if the target appeared meanwhile.
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--source-pdf", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--audit-output", type=Path)
    parser.add_argument("--replace", action="store_true")
    args = parser.parse_args(argv)
    if bool(args.output) != bool(args.audit_output):
        parser.error("--output and --audit-output must be supplied together")
    inputs = {p.resolve() for p in (args.candidate, args.source_pdf, args.baseline)}
    protected = inputs | {
        # Preserve both the immutable corpus sidecar and operational assets.
        (ROOT / "medicamentos/kairos-453-2026-08.json").resolve(),
        Path("/medicamentos/kairos-453-2026-08.json").resolve(),
        Path("/opt/meucardio/medicamentos/kairos-453-2026-08.json").resolve(),
    }
    for filename in ("kairos-453-2026-08.json", "kairos-453-2026-08-curation-audit.json"):
        protected.update({
            (ROOT / "backend/app/data/pricing" / filename).resolve(),
            (Path("/app/app/data/pricing") / filename).resolve(),
            (Path("/opt/meucardio/backend/app/data/pricing") / filename).resolve(),
        })
    targets = [p.resolve() for p in (args.output, args.audit_output) if p is not None]
    if len(targets) != len(set(targets)) or any(p in protected for p in targets):
        parser.error("Outputs must be distinct and must not overwrite inputs, historical evidence or operational assets")
    if not args.replace and any(p.exists() for p in targets):
        parser.error("Output already exists; inspect it and explicitly pass --replace if intended")
    try:
        if hashlib.sha256(args.source_pdf.read_bytes()).hexdigest() != SOURCE_SHA256:
            raise ValueError("PDF digest does not match the reviewed source")
        raw_bytes = args.candidate.read_bytes()
        raw_sha = hashlib.sha256(raw_bytes).hexdigest()
        if raw_sha != APPROVED_CANDIDATE_SHA256:
            raise ValueError("Raw candidate digest does not match the approved V3 extraction")
        raw = json.loads(raw_bytes.decode("utf-8"), object_pairs_hook=unique_keys)
        output, audit = prepare_snapshot(raw, read_json(args.baseline))
        output["preparation_evidence"]["raw_candidate_file_sha256"] = raw_sha
        audit["provenance"]["raw_candidate_file_sha256"] = raw_sha
        if args.output:
            write_result(args.audit_output, audit, replace=args.replace)
            write_result(args.output, output, replace=args.replace)
        print(json.dumps({"dry_run": args.output is None, "status": "prepared_not_active", **output["preparation_evidence"]["counters"]}, ensure_ascii=False))
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
