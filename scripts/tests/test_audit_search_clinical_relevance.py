"""Pure evaluator regressions; intentionally outside backend's DB conftest."""
from __future__ import annotations

from collections import Counter
from contextlib import redirect_stdout
from copy import deepcopy
from importlib.util import module_from_spec, spec_from_file_location
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
SPEC = spec_from_file_location("audit_search_clinical_relevance_tests",
                               ROOT / "scripts/audit_search_clinical_relevance.py")
assert SPEC is not None and SPEC.loader is not None
AUDITOR = module_from_spec(SPEC)
SPEC.loader.exec_module(AUDITOR)


class ClinicalSearchAuditTests(unittest.TestCase):
    def setUp(self):
        self.rows = [
            {"frente": "documento", "slug": "diagnostico-mitral", "title": "Diagnóstico",
             "clinical_role": "direct", "clinical_context": "Diagnóstico da estenose mitral."},
            {"frente": "medicamento", "slug": "varfarina-sodica", "title": "Varfarina",
             "clinical_role": "conditional", "clinical_context":
                 "FA com estenose mitral reumática; não é indicação universal."},
            {"frente": "evidencia", "slug": "excecao-doac", "title": "Exceção aos DOAC",
             "clinical_role": "comparison", "clinical_context":
                 "Exceção: a recomendação de DOAC não se aplica à estenose mitral moderada/grave."},
        ]
        self.gold = {
            "schema_version": 1, "query": "Estenose mitral", "aliases": ["Mitral stenosis"],
            "disease_slug": "estenose-mitral",
            "required": [
                {"frente": "documento", "slug": "diagnostico-mitral", "max_position": 2,
                 "expected_role": "direct"},
                {"frente": "medicamento", "slug": "varfarina-sodica", "max_position": 2,
                 "expected_role": "conditional"},
            ],
            "qualified": [
                {"frente": "medicamento", "slug": "varfarina-sodica", "role": "conditional",
                 "context_contains": ["FA", "reumática", "não é indicação universal"]},
                {"frente": "evidencia", "slug": "excecao-doac", "role": "comparison",
                 "context_contains": ["exceção", "moderada/grave"]},
            ],
            "cross_lesion_controls": [
                {"frente": "doenca", "slug": "estenose-aortica", "must_not_be_role": "direct"},
            ],
            "forbidden": [],
            "top_priorities": [
                {"frente": "documento", "slug": "diagnostico-mitral"},
                {"frente": "medicamento", "slug": "varfarina-sodica"},
            ],
            "top_20_clinical_review": [
                {"frente": row["frente"], "slug": row["slug"],
                 "expected_role": row["clinical_role"], "reason": "Julgamento independente de teste."}
                for row in self.rows
            ],
        }

    def fetch(self, query, limit, offset):
        rows = deepcopy(self.rows)
        page = rows[offset:offset + limit]
        return {
            "query": query, "count": len(page), "total": len(rows),
            "limit": limit, "offset": offset,
            "next_offset": offset + len(page) if offset + len(page) < len(rows) else None,
            "por_frente": dict(Counter(row["frente"] for row in rows)),
            "por_secao": dict(Counter(row["frente"] for row in rows)),
            "primary_disease": {"slug": "estenose-mitral"}, "primary_drug": None,
            "supplementary_groups": [], "results": page,
        }

    def codes(self, report):
        return {failure["code"] for failure in report["failures"]}

    def test_complete_audit_paginates_and_compares_aliases(self):
        calls = []

        def fetch(query, limit, offset):
            calls.append((query, offset))
            return self.fetch(query, limit, offset)

        report = AUDITOR.run_audit(fetch, self.gold, page_size=2)
        self.assertTrue(report["passed"])
        self.assertEqual(calls, [("Estenose mitral", 0), ("Estenose mitral", 2),
                                 ("Mitral stenosis", 0), ("Mitral stenosis", 2)])
        self.assertEqual(report["responses"][0]["count"], 3)
        self.assertTrue(report["alias_comparisons"][0]["same_order"])
        self.assertEqual(report["evaluations"][0]["required"][1]["position"], 2)

    def test_mutation_missing_required_fails(self):
        self.rows.pop(0)
        report = AUDITOR.run_audit(self.fetch, self.gold, page_size=2)
        self.assertFalse(report["passed"])
        self.assertIn("required_missing", self.codes(report))

    def test_mutation_wrong_context_fails_even_if_title_and_role_still_match(self):
        self.rows[1]["clinical_context"] = "FA reumática: indicação universal."
        self.rows[1]["match_reasons"] = [{"description": "não é indicação universal"}]
        report = AUDITOR.run_audit(self.fetch, self.gold, page_size=2)
        self.assertFalse(report["passed"])
        self.assertIn("qualified_context", self.codes(report))

    def test_mutation_duplicate_pagination_fails(self):
        def duplicate_page(query, limit, offset):
            page = self.fetch(query, limit, offset)
            if offset:
                page["results"][0] = deepcopy(self.rows[0])
            return page

        with self.assertRaisesRegex(AUDITOR.AuditContractError, "Duplicate paginated result"):
            AUDITOR.run_audit(duplicate_page, self.gold, page_size=2)

    def test_mutation_premature_end_fails(self):
        def truncated(query, limit, offset):
            page = self.fetch(query, limit, offset)
            page["next_offset"] = None
            return page

        with self.assertRaisesRegex(AUDITOR.AuditContractError, "omitted results"):
            AUDITOR.run_audit(truncated, self.gold, page_size=2)

    def test_mutation_total_changes_between_pages_fails(self):
        def inconsistent(query, limit, offset):
            page = self.fetch(query, limit, offset)
            if offset:
                page["total"] += 1
            return page

        with self.assertRaisesRegex(AUDITOR.AuditContractError, "changed total"):
            AUDITOR.run_audit(inconsistent, self.gold, page_size=2)

    def test_mutation_comparison_above_essential_fails(self):
        self.rows.insert(0, self.rows.pop())
        report = AUDITOR.run_audit(self.fetch, self.gold, page_size=2)
        self.assertIn("required_position", self.codes(report))
        self.assertIn("top_priority_after_context", self.codes(report))

    def test_real_cross_lesion_control_is_not_allowed_as_direct(self):
        self.rows.append({"frente": "doenca", "slug": "estenose-aortica",
                          "clinical_role": "direct", "clinical_context": "Outra lesão valvar."})
        report = AUDITOR.run_audit(self.fetch, self.gold, page_size=2)
        self.assertIn("cross_lesion_role", self.codes(report))

    def test_cross_lesion_control_can_be_qualified_without_claiming_a_judgment(self):
        self.rows.append({"frente": "doenca", "slug": "estenose-aortica",
                          "clinical_role": "comparison", "clinical_context": "Outra lesão valvar."})
        report = AUDITOR.run_audit(self.fetch, self.gold, page_size=2)
        self.assertTrue(report["passed"])
        review = report["evaluations"][0]["top_20"]
        self.assertFalse(review["clinical_review_complete"])
        self.assertEqual(review["judged_count"], 3)
        self.assertEqual(review["unjudged_keys"], ["doenca:estenose-aortica"])
        self.assertNotIn("precision_at_20", review)

    def test_mutation_qualified_comparison_cannot_silently_disappear(self):
        self.rows.pop()
        report = AUDITOR.run_audit(self.fetch, self.gold, page_size=2)
        self.assertIn("qualified_missing", self.codes(report))

    def test_alias_reordering_fails_even_when_required_positions_pass(self):
        def reordered(query, limit, offset):
            page = self.fetch(query, limit, offset)
            if query != self.gold["query"] and offset == 0:
                page["results"].reverse()
            return page

        report = AUDITOR.run_audit(reordered, self.gold, page_size=2)
        self.assertIn("alias_mismatch", self.codes(report))
        self.assertFalse(report["alias_comparisons"][0]["same_order"])

    def test_same_slug_in_different_fronts_is_not_a_pagination_duplicate(self):
        self.rows.append({"frente": "evidencia", "slug": "diagnostico-mitral",
                          "clinical_role": "direct", "clinical_context": "Outro registro publicado."})
        report = AUDITOR.run_audit(self.fetch, self.gold, page_size=2)
        self.assertTrue(report["passed"])
        self.assertEqual(report["responses"][0]["count"], 4)

    def test_empty_forbidden_does_not_claim_zero_irrelevant_results(self):
        report = AUDITOR.run_audit(self.fetch, self.gold)
        evaluation = report["evaluations"][0]
        self.assertEqual(evaluation["forbidden_tested_count"], 0)
        self.assertNotIn("irrelevant_result_count", evaluation)

    def test_baseline_comparison_uses_observed_positions_without_retroactive_role_gate(self):
        baseline = self.fetch(self.gold["query"], 100, 0)
        baseline["results"] = [baseline["results"][2]]
        baseline["total"] = 1
        baseline["results"][0].pop("clinical_role")
        report = AUDITOR.run_audit(self.fetch, self.gold, baseline=baseline)
        self.assertTrue(report["passed"])
        comparison = report["baseline_comparison"]
        self.assertEqual(comparison["added_keys"], ["documento:diagnostico-mitral",
                                                    "medicamento:varfarina-sodica"])
        self.assertIsNone(comparison["required_positions"][0]["before"])
        self.assertEqual(comparison["required_positions"][0]["after"], 1)

    def test_cli_returns_nonzero_json_for_failed_gold_without_importing_backend(self):
        with tempfile.TemporaryDirectory() as tmp:
            gold_path = Path(tmp) / "gold.json"
            gold_path.write_text(json.dumps(self.gold), encoding="utf-8")
            output = io.StringIO()
            with patch.object(AUDITOR, "audit_database", return_value={"passed": False, "failures": []}):
                with redirect_stdout(output):
                    exit_code = AUDITOR.main(["--gold", str(gold_path)])
            self.assertEqual(exit_code, 1)
            self.assertFalse(json.loads(output.getvalue())["passed"])


if __name__ == "__main__":
    unittest.main()
