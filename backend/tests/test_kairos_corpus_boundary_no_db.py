"""Historical proof stays frozen when operational K@iros prices are replaced.

Run directly with Python; only stdlib, repository files and the genuine pure
authorization helper are loaded. No application, database or conftest import.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
HISTORICAL = "medicamentos/kairos-453-2026-08.json"
HISTORICAL_SHA = "7a7ac549bead518f3566dce41e64702090448545c35d7b56e3316d79ef896e9e"
OPERATIONAL = "backend/app/data/pricing/kairos-453-2026-08.json"
OPERATIONAL_SHA = "ff070fdf46b257253d9e618de56bfb63f3e2b33333bab332e734537d05ec8363"
AUDIT = "backend/app/data/pricing/kairos-453-2026-08-curation-audit.json"
AUDIT_SHA = "593aa4d944c6e65f40c1ea0048363cc75ccf91b372a500ed5ef1c1d3b101860a"
SPEC = importlib.util.spec_from_file_location(
    "corpus_release_authorization", ROOT / "backend/app/services/corpus_release_authorization.py")
AUTH = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUTH)


class KairosCorpusBoundaryTest(unittest.TestCase):
    def test_historical_bytes_and_fixture_remain_unchanged(self):
        historical = (ROOT / HISTORICAL).read_bytes()
        fixture = (ROOT / "backend/tests/fixtures/kairos-453-2026-08-cardiovascular.json").read_bytes()
        self.assertEqual(hashlib.sha256(historical).hexdigest(), HISTORICAL_SHA)
        self.assertEqual(hashlib.sha256(fixture).hexdigest(), "d6f3c17ff04643188b96f56a9dfa1da2312cc99373015f678e7b0e4f8b024ad6")
        self.assertEqual(json.loads(historical), json.loads(fixture))

    def test_original_reference_still_validates_and_rejects_the_operational_hash(self):
        evidence = json.loads((ROOT / "docs/scoped-corpus-release-evidence-20260910.json").read_text())
        references = [ref for ref in evidence["references"] if ref["path"] == HISTORICAL]
        self.assertEqual(references, [{"path": HISTORICAL, "basis": "baseline_unchanged", "sha256": HISTORICAL_SHA}])
        self.assertEqual(AUTH._evidence_file(ROOT, HISTORICAL, HISTORICAL_SHA), (ROOT / HISTORICAL).resolve())
        with self.assertRaisesRegex(RuntimeError, "Hash da evidência divergente"):
            AUTH._evidence_file(ROOT, HISTORICAL, OPERATIONAL_SHA)
        self.assertFalse(any(ref["path"] in {OPERATIONAL, AUDIT} for ref in evidence["references"]))

    def test_operational_asset_and_curation_audit_are_literal_relocations(self):
        self.assertEqual(hashlib.sha256((ROOT / OPERATIONAL).read_bytes()).hexdigest(), OPERATIONAL_SHA)
        self.assertEqual(hashlib.sha256((ROOT / AUDIT).read_bytes()).hexdigest(), AUDIT_SHA)
        self.assertEqual(json.loads((ROOT / AUDIT).read_text())["candidate_sha256"], OPERATIONAL_SHA)
        self.assertFalse((ROOT / "medicamentos/kairos-453-2026-08-curation-audit.json").exists())


if __name__ == "__main__":
    unittest.main()
