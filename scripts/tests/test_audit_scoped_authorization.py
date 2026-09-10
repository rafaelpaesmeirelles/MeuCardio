"""Standalone audit policy regressions; no database, network or clinical edits."""
import importlib.util
import json
from hashlib import sha256
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))
spec = importlib.util.spec_from_file_location("scoped_audit", ROOT / "scripts/audit_tudo_com_tudo.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
from app.services import corpus_release_authorization as auth


class ScopedAuditTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        source = self.root / "content"
        source.mkdir()
        self.records = {"documentos": {}}
        for slug in ("approved", "excluded"):
            raw = f"Exact fixture {slug}".encode()
            (source / (slug + ".md")).write_bytes(raw)
            self.records["documentos"][slug] = {
                "metadata": {"slug": slug, "review_status": "revisado", "published": True},
                "source_sha256": sha256(raw).hexdigest(),
            }
        self.fingerprints = {"documentos": auth.build_front_fingerprint(
            source, {"approved", "excluded"}, {"approved": "revisado", "excluded": "revisado"})}
        reference = self.root / "reference.json"
        reference.write_text('{"authorization": "synthetic test only"}')
        approved_hash = self.records["documentos"]["approved"]["source_sha256"]
        evidence = {
            "schema_version": 1, "decision": "reconciled_publication_evidence",
            "approval_basis": "Synthetic test only",
            "approved_sources": {"documentos": {"approved": approved_hash}},
            "approved_bases": {"documentos": {"approved": "approved_package"}},
            "references": [{"path": "reference.json", "basis": "approved_package",
                            "sha256": sha256(reference.read_bytes()).hexdigest()}],
        }
        self.evidence = self.root / "evidence.json"
        self.evidence.write_text(json.dumps(evidence))
        self.manifest = {
            "schema_version": 2, "release": "synthetic", "decision": auth.SNAPSHOT_DECISION,
            "scope": auth.SNAPSHOT_SCOPE, "approval_basis": "Synthetic test only",
            "expected_total": 2, "inventory_sha256": auth.corpus_inventory_sha256(self.fingerprints),
            "fronts": self.fingerprints, "approved": {"documentos": ["approved"]},
            "quarantined": {"documentos": ["excluded"]},
            "provenance": {"documentos": {"approved": {
                "basis": "approved_package", "source_sha256": approved_hash,
                "evidence_path": "evidence.json",
                "evidence_sha256": sha256(self.evidence.read_bytes()).hexdigest(),
            }}},
        }
        self.path = self.root / "release.json"

    def load(self):
        self.path.write_text(json.dumps(self.manifest))
        with patch.object(audit, "_snapshot_inventory", return_value=(self.records, self.fingerprints)):
            return audit._load_scoped_approval(self.path, self.root)

    def test_exact_provenance_and_quarantine_override_raw_true(self):
        scoped = self.load()
        raw = [row["metadata"] for row in self.records["documentos"].values()]
        effective = audit._effective_editorial_records("documento_markdown", raw, scoped)
        self.assertEqual([r["published"] for r in raw], [True, True])
        self.assertEqual([r["published"] for r in effective], [True, False])
        self.assertFalse(audit._editorial_issues("documento_markdown", effective, approved={"approved"}))
        self.assertEqual(scoped["metadata"]["authorized_total"], 1)

    def test_changed_source_fails_closed(self):
        self.records["documentos"]["approved"]["source_sha256"] = "f" * 64
        with self.assertRaises(RuntimeError):
            self.load()

    def test_changed_evidence_fails_closed(self):
        self.evidence.write_text('{}')
        with self.assertRaises(RuntimeError):
            self.load()

    def test_promotion_without_item_provenance_fails_closed(self):
        self.manifest["approved"]["documentos"].append("excluded")
        self.manifest["quarantined"]["documentos"] = []
        with self.assertRaises(RuntimeError):
            self.load()

    def test_partition_overlap_fails_closed(self):
        self.manifest["quarantined"]["documentos"].append("approved")
        with self.assertRaises(RuntimeError):
            self.load()

    def test_disclosure_is_not_pending_only_with_verified_provenance(self):
        row = {"slug": "approved", "review_status": "revisado", "published": True,
               "review_note": "Revisão técnica assistida por IA; sem aprovação humana presumida."}
        self.assertTrue(audit._editorial_issues("documento_markdown", [row], approved={"approved"}))
        self.assertFalse(audit._editorial_issues("documento_markdown", [row], approved={"approved"},
                                                provenance_approved={"approved"}))
        row["review_note"] += " Aguardando revisão independente."
        self.assertTrue(audit._editorial_issues("documento_markdown", [row], approved={"approved"},
                                               provenance_approved={"approved"}))

    def test_quarantined_target_is_not_a_resolved_public_link(self):
        issue = audit._reference_issue(
            field="Document.body_md.link", source="approved", target="excluded",
            allowed=("documento", "fluxograma"), slugs={"documento": {"excluded"}},
            quarantined={"documento": {"excluded"}},
        )
        self.assertEqual(issue["reason"], "target_quarantined")

    def test_strict_v1_does_not_inherit_scoped_publication(self):
        row = {"slug": "approved", "review_status": "revisado", "published": False}
        self.assertEqual(audit._strict_release_issues("documento_markdown", [row])[0]["blockers"],
                         ["not_published"])
        self.path.write_text(json.dumps(self.manifest))
        with self.assertRaises(ValueError):
            audit._strict_release_manifest_issues(self.path, {"documento_markdown": [row]})


if __name__ == "__main__":
    unittest.main()
