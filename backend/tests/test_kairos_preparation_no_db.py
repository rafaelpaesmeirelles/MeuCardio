"""Pure preparation tests; execute directly, never through app/conftest/DB."""
from copy import deepcopy
from contextlib import redirect_stderr, redirect_stdout
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import runpy
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "backend/scripts/prepare_kairos_snapshot.py"
SPEC = importlib.util.spec_from_file_location("kairos_preparation", SOURCE)
PREPARER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PREPARER)
BASELINE = json.loads(PREPARER.DEFAULT_BASELINE.read_text(encoding="utf-8"))
PROVIDER = runpy.run_path(str(Path(__file__).with_name("test_kairos_matching_no_db.py")))["load_provider"]()


def raw_baseline():
    data = deepcopy(BASELINE)
    data["parse_evidence"] = {"source_sha256": PREPARER.SOURCE_SHA256, "source_file": "reviewed.pdf"}
    for record in data["records"]:
        for i, presentation in enumerate(record["presentations"], start=1):
            presentation.update(source_page=record["page"], source_side="left", source_line=i)
    return data


def record(*presentations, product="SYNTHETIC BRAND", laboratory="SYNTHETIC LAB", substance="SYNTHETIC INGREDIENT", page=20):
    return {"product": product, "laboratory": laboratory, "substance": substance, "page": page,
            "presentations": [{"presentation": "5mg Comp. x 30", "source_page": page,
                               "source_side": "left", "source_line": i, **p}
                              for i, p in enumerate(presentations, start=1)]}


class KairosPreparationTest(unittest.TestCase):
    def prepare(self, *extra):
        raw = raw_baseline()
        raw["records"].extend(deepcopy(extra))
        output, audit = PREPARER.prepare_snapshot(raw, BASELINE)
        # Genuine production validation, compiled unchanged except ORM imports.
        PROVIDER["_validate_snapshot"](output)
        return output, audit

    def test_baseline_13_records_52_presentations_remains_literal_in_original_order(self):
        output, audit = self.prepare()
        self.assertEqual(len(output["records"]), 13)
        for original, preserved in zip(BASELINE["records"], output["records"]):
            self.assertEqual({key: preserved[key] for key in original}, original)
            self.assertEqual(preserved["curation_provenance"]["kind"], "reviewed_cardiovascular_baseline")
        self.assertEqual(output["preparation_evidence"]["status"], "prepared_not_active")
        self.assertEqual(audit["provenance"]["counters"]["baseline_presentations_preserved"], 52)

    def test_lower_pmc_wins_even_when_its_pf_is_higher(self):
        output, audit = self.prepare(record({"pf20": "1,00", "pmc20": "50,00"}, {"pf20": "90,00", "pmc20": "40,00"}))
        chosen = output["records"][-1]["presentations"][0]
        self.assertEqual((chosen["pf20"], chosen["pmc20"]), ("90,00", "40,00"))
        decision = audit["decisions"][-1]
        self.assertEqual(len(decision["variants"]), 2)
        self.assertEqual(decision["reason"], "minimum_positive_pmc_original_row")

    def test_lower_pmc_across_published_icms_keeps_the_whole_original_vector(self):
        output, _ = self.prepare(record(
            {"pmc20": "30,00", "pmc18": "15,00", "pf20": "4,00"},
            {"pmc20": "14,00", "pmc18": "25,00", "pf20": "9,00"}))
        selected = output["records"][-1]["presentations"][0]
        self.assertEqual(PREPARER.price_vector(selected), {"pf20": "9,00", "pmc20": "14,00", "pmc18": "25,00"})
        self.assertNotIn("uf", selected)
        self.assertNotIn("retail", json.dumps(selected))

    def test_pmc_ties_use_source_order_not_pf_or_input_order(self):
        output, _ = self.prepare(record(
            {"pmc20": "20,00", "pf20": "1,00", "source_line": 12},
            {"pmc20": "20,00", "pf20": "15,00", "source_line": 3}))
        chosen = output["records"][-1]["presentations"][0]
        self.assertEqual(chosen["source_line"], 3)
        self.assertEqual(chosen["pf20"], "15,00")

    def test_pf_only_uses_pf_and_never_creates_a_consumer_price(self):
        output, audit = self.prepare(record({"pf20": "3,00"}, {"pf20": "2,00", "pf18": "2,50"}))
        chosen = output["records"][-1]["presentations"][0]
        self.assertEqual(chosen["pf20"], "2,00")
        self.assertFalse(any(key.startswith("pmc") for key in chosen))
        self.assertEqual(audit["decisions"][-1]["reason"], "minimum_positive_pf_only_original_row")
        self.assertEqual(audit["provenance"]["counters"]["output_presentations_with_pmc"], 52)

    def test_available_pmc_has_priority_over_a_lower_pf_only_row(self):
        output, _ = self.prepare(record({"pf20": "1,00"}, {"pf20": "90,00", "pmc20": "100,00"}))
        self.assertEqual(output["records"][-1]["presentations"][0]["pmc20"], "100,00")

    def test_dose_decimal_punctuation_package_and_release_variants_are_not_merged(self):
        descriptions = ["1.5mg Comp. x 30", "15mg Comp. x 30", "1,5mg Comp. x 30",
                        "1.5mg Comp. x 60", "1.5mg Comp. XR x 30", "1 5mg Comp. x 30"]
        output, _ = self.prepare(record(*[{"presentation": text, "pmc20": "10,00"} for text in descriptions]))
        self.assertEqual([p["presentation"] for p in output["records"][-1]["presentations"]], descriptions)

    def test_same_presentation_different_brand_or_laboratory_is_not_merged(self):
        output, _ = self.prepare(record({"pmc20": "10,00"}),
                                 record({"pmc20": "8,00"}, product="OTHER BRAND"),
                                 record({"pmc20": "6,00"}, laboratory="OTHER LAB"))
        self.assertEqual(output["preparation_evidence"]["counters"]["new_selected_presentations"], 3)

    def test_four_known_composition_groups_are_quarantined_with_all_values(self):
        extras = [record({"pf20": "1,00", "pmc20": "2,00"}, product=product, laboratory=lab, page=page)
                  for product, lab, page in PREPARER.EXCLUSIONS]
        output, audit = self.prepare(*extras)
        self.assertEqual(len(output["records"]), 13)
        quarantined = [d for d in audit["decisions"] if d["action"] == "quarantine"]
        self.assertEqual(len(quarantined), 4)
        self.assertEqual({d["reason"] for d in quarantined}, set(PREPARER.EXCLUSIONS.values()))
        self.assertTrue(all(d["variants"][0]["prices"]["pmc20"] == "2,00" for d in quarantined))

    def test_duplicate_conflicting_substances_are_not_resolved_by_price(self):
        output, audit = self.prepare(record({"pmc20": "10,00"}, substance="INGREDIENT A"),
                                    record({"pmc20": "1,00"}, substance="INGREDIENT A + INGREDIENT B"))
        self.assertEqual(len(output["records"]), 13)
        self.assertEqual(audit["decisions"][-1]["reason"], "duplicate_composition_headings_disagree")
        self.assertEqual(len(audit["decisions"][-1]["variants"]), 2)

    def test_missing_substance_and_price_remain_missing(self):
        output, audit = self.prepare(record({}, substance=None))
        self.assertIsNone(output["records"][-1]["substance"])
        self.assertEqual(PREPARER.price_vector(output["records"][-1]["presentations"][0]), {})
        self.assertEqual(audit["decisions"][-1]["reason"], "no_published_price_source_order")

    def test_baseline_precedence_is_explicit_even_if_raw_duplicate_has_lower_price(self):
        raw = raw_baseline()
        other = deepcopy(raw["records"][0])
        other["presentations"] = [deepcopy(other["presentations"][0])]
        other["presentations"][0]["pmc20"] = "1,00"
        raw["records"].append(other)
        output, audit = PREPARER.prepare_snapshot(raw, BASELINE)
        self.assertEqual(output["records"][0]["presentations"], BASELINE["records"][0]["presentations"])
        decision = next(d for d in audit["decisions"] if len(d["variants"]) == 2)
        self.assertEqual(decision["reason"], "reviewed_baseline_precedence_not_reparsed_literal")
        self.assertEqual(decision["variants"][-1]["prices"]["pmc20"], "1,00")

    def test_missing_or_changed_baseline_prices_prevent_preparation(self):
        raw = raw_baseline()
        raw["records"][0]["presentations"][0]["pmc20"] = "1,00"
        with self.assertRaisesRegex(ValueError, "corroborates baseline"):
            PREPARER.prepare_snapshot(raw, BASELINE)
        raw = raw_baseline()
        raw["records"].pop(0)
        with self.assertRaisesRegex(ValueError, "missing one or more"):
            PREPARER.prepare_snapshot(raw, BASELINE)

    def test_bad_source_edition_or_changed_baseline_cannot_be_used(self):
        for key, value in (("issue", 454), ("competence", "2026-09"), ("licensed_use", "true")):
            with self.subTest(key=key):
                raw = raw_baseline()
                raw[key] = value
                with self.assertRaises(ValueError):
                    PREPARER.prepare_snapshot(raw, BASELINE)
        raw = raw_baseline()
        raw["parse_evidence"]["source_sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            PREPARER.prepare_snapshot(raw, BASELINE)
        baseline = deepcopy(BASELINE)
        baseline["records"][0]["substance"] = "CHANGED"
        with self.assertRaisesRegex(ValueError, "Historical baseline differs"):
            PREPARER.prepare_snapshot(raw_baseline(), baseline)

    def test_invalid_prices_and_unreviewed_rates_fail_without_silent_dropping(self):
        for value in (1.50, True, "0,00", "-1,00", "NaN", "1.50"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.prepare(record({"pmc20": value}))
        with self.assertRaises(ValueError):
            self.prepare(record({"pmc19": "10,00"}))

    def test_compact_output_removes_glyphs_but_audit_preserves_values_and_coordinates(self):
        row = record({"pmc20": "10,00", "source_price_glyphs": [{"raw": "10,00"}],
                      "bbox": [1, 2, 3, 4], "source_description_lines": [{"text": "5mg", "bbox": [5, 6, 7, 8]}]})
        output, audit = self.prepare(row)
        self.assertNotIn("glyph", json.dumps(output))
        self.assertNotIn("bbox", json.dumps(output))
        original = audit["decisions"][-1]["variants"][0]
        self.assertEqual(original["prices"], {"pmc20": "10,00"})
        self.assertEqual(original["source"]["bbox"], [1, 2, 3, 4])
        self.assertEqual(original["source"]["description_lines"][0]["text"], "5mg")

    def test_all_raw_rows_are_accounted_for_in_the_audit(self):
        output, audit = self.prepare(record({"pmc20": "10,00"}, {"pmc20": "8,00"}),
                                    record({}, product="UNPRICED"),
                                    record({"pmc20": "5,00"}, product="MICARDIS", laboratory="BOEHRINGER", page=50))
        count = output["preparation_evidence"]["counters"]
        self.assertEqual(sum(len(d["variants"]) for d in audit["decisions"]), count["input_presentations"])
        self.assertEqual(count["input_presentations"], count["baseline_raw_occurrences"] + count["quarantined_presentations"] + count["new_selected_presentations"] + count["duplicate_rows_not_selected"])

    def test_cli_dry_run_and_explicit_outputs_refuse_overwrite_and_input_alias(self):
        with tempfile.TemporaryDirectory(prefix="corvia-kairos-prepare-test-") as folder:
            directory = Path(folder)
            pdf, raw_file = directory / "source.pdf", directory / "raw.json"
            pdf.write_bytes(b"synthetic test PDF digest only")
            source_hash = hashlib.sha256(pdf.read_bytes()).hexdigest()
            with patch.object(PREPARER, "SOURCE_SHA256", source_hash):
                raw_file.write_text(json.dumps(raw_baseline()), encoding="utf-8")
                approved_patch = patch.object(PREPARER, "APPROVED_CANDIDATE_SHA256", hashlib.sha256(raw_file.read_bytes()).hexdigest())
                approved_patch.start()
                self.addCleanup(approved_patch.stop)
                args = [str(raw_file), "--source-pdf", str(pdf)]
                with redirect_stdout(io.StringIO()) as capture:
                    self.assertEqual(PREPARER.main(args), 0)
                self.assertTrue(json.loads(capture.getvalue())["dry_run"])
                self.assertEqual({p.name for p in directory.iterdir()}, {"source.pdf", "raw.json"})
                output, audit = directory / "prepared.json", directory / "audit.json"
                write_args = args + ["--output", str(output), "--audit-output", str(audit)]
                with redirect_stdout(io.StringIO()):
                    PREPARER.main(write_args)
                original = output.read_bytes()
                with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                    PREPARER.main(write_args)
                self.assertEqual(output.read_bytes(), original)
                with redirect_stdout(io.StringIO()):
                    PREPARER.main(write_args + ["--replace"])
                with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                    PREPARER.main(args + ["--output", str(raw_file), "--audit-output", str(audit), "--replace"])

    def test_cli_cannot_overwrite_historical_or_operational_assets_even_with_replace(self):
        protected = [
            ROOT / "medicamentos/kairos-453-2026-08.json",
            Path("/medicamentos/kairos-453-2026-08.json"),
            Path("/opt/meucardio/medicamentos/kairos-453-2026-08.json"),
        ]
        for folder in (ROOT / "backend/app/data/pricing", Path("/app/app/data/pricing"),
                       Path("/opt/meucardio/backend/app/data/pricing")):
            protected.extend(folder / name for name in (
                "kairos-453-2026-08.json", "kairos-453-2026-08-curation-audit.json"))
        with tempfile.TemporaryDirectory(prefix="corvia-kairos-protected-") as folder:
            directory = Path(folder)
            args = [str(directory / "input.json"), "--source-pdf", str(directory / "source.pdf"), "--replace"]
            for target in protected:
                for option, other in (("--output", "--audit-output"), ("--audit-output", "--output")):
                    with self.subTest(target=str(target), option=option), \
                         patch.object(PREPARER, "prepare_snapshot") as prepare, \
                         patch.object(PREPARER, "write_result") as write, \
                         redirect_stderr(io.StringIO()) as error, self.assertRaises(SystemExit):
                        PREPARER.main(args + [option, str(target), other, str(directory / "other.json")])
                    self.assertIn("historical evidence or operational assets", error.getvalue())
                    prepare.assert_not_called()
                    write.assert_not_called()

    def test_cli_rejects_changed_new_price_with_valid_pdf_before_preparation_or_writing(self):
        with tempfile.TemporaryDirectory(prefix="corvia-kairos-tamper-test-") as folder:
            directory = Path(folder)
            pdf, raw_file = directory / "source.pdf", directory / "raw.json"
            output, audit = directory / "prepared.json", directory / "audit.json"
            pdf.write_bytes(b"synthetic valid PDF digest")
            source_hash = hashlib.sha256(pdf.read_bytes()).hexdigest()
            raw = raw_baseline()
            raw["parse_evidence"]["source_sha256"] = source_hash
            raw["records"].append(record({"pmc20": "10,00"}))
            approved_bytes = json.dumps(raw).encode()
            approved_sha = hashlib.sha256(approved_bytes).hexdigest()
            raw["records"][-1]["presentations"][0]["pmc20"] = "1,00"
            raw_file.write_text(json.dumps(raw), encoding="utf-8")
            with patch.object(PREPARER, "SOURCE_SHA256", source_hash), \
                 patch.object(PREPARER, "APPROVED_CANDIDATE_SHA256", approved_sha), \
                 patch.object(PREPARER, "prepare_snapshot") as prepare, \
                 redirect_stderr(io.StringIO()) as error, self.assertRaises(SystemExit):
                PREPARER.main([str(raw_file), "--source-pdf", str(pdf),
                               "--output", str(output), "--audit-output", str(audit)])
            self.assertIn("approved V3 extraction", error.getvalue())
            prepare.assert_not_called()
            self.assertFalse(output.exists())
            self.assertFalse(audit.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
