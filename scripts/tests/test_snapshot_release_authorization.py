"""No DB/provider: exact approval, provenance, quarantine and final identity gates."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))
from app.services.corpus_release_authorization import (
    build_front_fingerprint, corpus_inventory_sha256, resolve_publication_policy,
    validate_snapshot_authorization, validate_snapshot_publication,
)


class SnapshotAuthorizationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "sources.json"
        self.source.write_text('[{"slug":"approved"},{"slug":"excluded"},{"slug":"draft"}]')
        self.canonical = {"documents": {"approved", "excluded", "draft"}}
        self.statuses = {"documents": {"approved": "revisado", "excluded": "revisado", "draft": "pendente_revisao"}}
        self.sources = {"documents": {slug: hashlib.sha256(slug.encode()).hexdigest() for slug in self.canonical["documents"]}}
        self.fingerprints = {"documents": build_front_fingerprint(self.source, self.canonical["documents"], self.statuses["documents"])}
        self.reference = self.root / "approved-package.json"
        self.reference.write_text('{"authorization":"Explicit package publication authorization"}')
        evidence = {"schema_version": 1, "decision": "reconciled_publication_evidence",
                    "approval_basis": "Reconciled exact previously authorized sources; no human review attribution.",
                    "approved_sources": {"documents": {"approved": self.sources["documents"]["approved"]}},
                    "approved_bases": {"documents": {"approved": "approved_package"}},
                    "references": [{"path": self.reference.name, "sha256": hashlib.sha256(self.reference.read_bytes()).hexdigest(), "basis": "approved_package"}]}
        self.evidence = self.root / "evidence.json"
        self.evidence.write_text(json.dumps(evidence))
        claim = {"basis": "approved_package", "source_sha256": self.sources["documents"]["approved"],
                 "evidence_path": self.evidence.name, "evidence_sha256": hashlib.sha256(self.evidence.read_bytes()).hexdigest()}
        self.manifest = {"schema_version": 2, "release": "test-snapshot", "decision": "approved_snapshot_with_quarantine",
                         "scope": "exact_canonical_snapshot", "approval_basis": "Explicit limited release with exclusions.",
                         "expected_total": 3, "inventory_sha256": corpus_inventory_sha256(self.fingerprints),
                         "fronts": copy.deepcopy(self.fingerprints), "approved": {"documents": ["approved"]},
                         "quarantined": {"documents": ["excluded", "draft"]},
                         "provenance": {"documents": {"approved": claim}}}
        self.path = self.root / "release.json"

    def validate(self, manifest=None):
        self.path.write_text(json.dumps(manifest or self.manifest))
        return validate_snapshot_authorization(self.path, canonical_slugs=self.canonical,
            fingerprints=self.fingerprints, review_statuses=self.statuses,
            source_fingerprints=self.sources, repository_root=self.root)

    def test_valid_snapshot_preserves_reviewed_exclusion_and_pending_source(self):
        approved, meta = self.validate()
        self.assertEqual(approved, {"documents": {"approved"}})
        self.assertEqual(meta["canonical_total"], 3)
        self.assertEqual(meta["authorized_total"], 1)
        self.assertEqual(set(meta["quarantined"]["documents"]), {"excluded", "draft"})

    def test_partition_rejects_overlap_missing_duplicate_and_noncanonical(self):
        for approved, quarantined in [(["approved", "excluded"], ["excluded", "draft"]),
                (["approved"], ["draft"]), (["approved", "approved"], ["excluded", "draft"]),
                (["approved", "other"], ["excluded", "draft"])]:
            with self.subTest(approved=approved, quarantined=quarantined):
                m = copy.deepcopy(self.manifest); m["approved"]["documents"] = approved; m["quarantined"]["documents"] = quarantined
                with self.assertRaises(RuntimeError): self.validate(m)

    def test_reviewed_quarantine_cannot_be_promoted_with_borrowed_evidence(self):
        m = copy.deepcopy(self.manifest)
        m["approved"]["documents"].append("excluded"); m["quarantined"]["documents"].remove("excluded")
        claim = copy.deepcopy(m["provenance"]["documents"]["approved"])
        claim["source_sha256"] = self.sources["documents"]["excluded"]
        m["provenance"]["documents"]["excluded"] = claim
        with self.assertRaisesRegex(RuntimeError, "Evidência não autoriza"): self.validate(m)

    def test_basis_cannot_be_borrowed_from_another_reference(self):
        evidence = json.loads(self.evidence.read_text())
        evidence["references"].append({"path": self.reference.name,
            "sha256": hashlib.sha256(self.reference.read_bytes()).hexdigest(), "basis": "baseline_unchanged"})
        self.evidence.write_text(json.dumps(evidence))
        claim = self.manifest["provenance"]["documents"]["approved"]
        claim["evidence_sha256"] = hashlib.sha256(self.evidence.read_bytes()).hexdigest()
        claim["basis"] = "baseline_unchanged"
        with self.assertRaisesRegex(RuntimeError, "Evidência não autoriza"): self.validate()

    def test_explicit_theme_normalization_basis_is_evidence_bound(self):
        basis = "authorized_tct_theme_normalization"
        evidence = json.loads(self.evidence.read_text())
        evidence["approved_bases"]["documents"]["approved"] = basis
        evidence["references"][0]["basis"] = basis
        self.evidence.write_text(json.dumps(evidence))
        claim = self.manifest["provenance"]["documents"]["approved"]
        claim["basis"] = basis
        claim["evidence_sha256"] = hashlib.sha256(self.evidence.read_bytes()).hexdigest()
        approved, _ = self.validate()
        self.assertEqual(approved["documents"], {"approved"})
        claim["source_sha256"] = "c" * 64
        with self.assertRaisesRegex(RuntimeError, "Fonte aprovada foi alterada"): self.validate()

    def test_pending_status_never_approved(self):
        self.statuses["documents"]["approved"] = "pendente_revisao"
        self.fingerprints["documents"]["reviewed_count"] = 1
        self.manifest["fronts"] = copy.deepcopy(self.fingerprints)
        self.manifest["inventory_sha256"] = corpus_inventory_sha256(self.fingerprints)
        with self.assertRaisesRegex(RuntimeError, "não revisado"): self.validate()

    def test_same_slug_modified_source_fails_even_when_global_hash_recomputed(self):
        self.sources["documents"]["approved"] = "b" * 64
        self.source.write_text('changed')
        self.fingerprints["documents"] = build_front_fingerprint(self.source, self.canonical["documents"], self.statuses["documents"])
        self.manifest["fronts"] = copy.deepcopy(self.fingerprints)
        self.manifest["inventory_sha256"] = corpus_inventory_sha256(self.fingerprints)
        with self.assertRaisesRegex(RuntimeError, "Fonte aprovada foi alterada"): self.validate()

    def test_modified_evidence_and_reference_are_rejected(self):
        self.reference.write_text('changed approval')
        with self.assertRaisesRegex(RuntimeError, "Hash da evidência"): self.validate()
        self.evidence.write_text('{}')
        with self.assertRaisesRegex(RuntimeError, "Hash da evidência"): self.validate()

    def test_schema_unknown_fields_invalid_count_and_path_escape_fail(self):
        for key, value in [("schema_version", True), ("schema_version", 3), ("expected_total", True), ("scope", "full")]:
            with self.subTest(key=key, value=value):
                m = copy.deepcopy(self.manifest); m[key] = value
                with self.assertRaises(RuntimeError): self.validate(m)
        m = copy.deepcopy(self.manifest); m["wildcard"] = True
        with self.assertRaises(RuntimeError): self.validate(m)
        m = copy.deepcopy(self.manifest); m["provenance"]["documents"]["approved"]["evidence_path"] = "../outside"
        with self.assertRaises(RuntimeError): self.validate(m)

    def test_quarantine_revokes_old_and_generic_approvals_even_with_true_intent(self):
        approved, excluded = resolve_publication_policy({"approved", "excluded"},
            {"approved": True, "excluded": True}, {"approved", "excluded"}, {"approved", "excluded"},
            quarantined_slugs={"excluded"})
        self.assertEqual(approved, {"approved"}); self.assertEqual(excluded, {"excluded"})

    def test_final_gate_requires_exact_identities_not_counts(self):
        _, auth = self.validate()
        database = {"published_total": 1, "fronts": {"documents": {"published": 1, "published_slugs": ["approved"]}}}
        validate_snapshot_publication(database, auth)
        for replacement in [["excluded"], ["unknown"], ["approved", "approved"], []]:
            with self.subTest(replacement=replacement):
                database["fronts"]["documents"]["published_slugs"] = replacement
                with self.assertRaises(RuntimeError): validate_snapshot_publication(database, auth)


if __name__ == "__main__": unittest.main()
