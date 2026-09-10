"""Unavailable-link guards use isolated evidence; live links follow current approval."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))
from app.services import clinical_link_availability as availability
from app.services.clinical_markdown_links import parse_clinical_markdown_target

LIVE_REFERENCES = deepcopy(availability.UNAVAILABLE_REFERENCES)


class LinkAvailabilityTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.quarantined_url = "/biblioteca/fixture-quarantined-document"
        self.missing_url = "/biblioteca/fixture-missing-document"
        self.source = "content/fixture-source.md"
        proofs = {
            "quarantine.json": {"quarantined": {"documentos": ["fixture-quarantined-document"]}},
            "gap.json": {"items": [{"old_url": self.missing_url,
                                    "status": "no_equivalent", "source_paths": [self.source]}]},
        }
        for filename, proof in proofs.items():
            (self.root / filename).write_text(json.dumps(proof))
        references = {}
        for url, reason, filename in [
            (self.quarantined_url, "target_quarantined", "quarantine.json"),
            (self.missing_url, "no_integral_approved_equivalent", "gap.json"),
        ]:
            references[url] = {
                "reason": reason, "evidence_path": filename,
                "evidence_sha256": sha256((self.root / filename).read_bytes()).hexdigest(),
                "source_paths": [self.source],
            }
        self.registry_patch = patch.dict(availability.UNAVAILABLE_REFERENCES, references, clear=True)
        self.registry_patch.start()
        self.addCleanup(self.registry_patch.stop)
        self.quarantine = {"fixture-quarantined-document"}
        self.canonical = set(self.quarantine)

    def validate(self, url, **overrides):
        args = {"repository_root": self.root, "canonical_document_slugs": self.canonical,
                "quarantined_document_slugs": self.quarantine,
                "source_path": availability.UNAVAILABLE_REFERENCES[url]["source_paths"][0]}
        args.update(overrides)
        return availability.validate_unavailable_clinical_reference(url, **args)

    def test_each_unavailable_reason_requires_exact_proof_and_no_graph_target(self):
        for url in (self.quarantined_url, self.missing_url):
            with self.subTest(url=url):
                result = self.validate(url)
                self.assertEqual(result["reason"], availability.UNAVAILABLE_REFERENCES[url]["reason"])
                self.assertEqual(result["presentation"], "label_without_href")
                self.assertIsNone(parse_clinical_markdown_target(url))
                label = availability.unavailable_clinical_link_label("Texto clínico preservado", url)
                self.assertEqual(label, "Texto clínico preservado (conteúdo indisponível nesta versão)")
                self.assertNotIn("href", label)

    def test_unknown_destination_is_not_exempted(self):
        url = "/biblioteca/unknown-clinical-destination"
        self.assertIsNone(availability.unavailable_clinical_link_reason(url))
        self.assertIsNone(availability.unavailable_clinical_link_label("Unknown", url))
        self.assertIsNotNone(parse_clinical_markdown_target(url))
        self.assertIsNone(availability.validate_unavailable_clinical_reference(
            url, repository_root=self.root, canonical_document_slugs=set(),
            quarantined_document_slugs=set(), source_path="unknown"))

    def test_published_target_makes_quarantine_disposition_stale(self):
        with self.assertRaisesRegex(RuntimeError, "quarantine"):
            self.validate(self.quarantined_url, quarantined_document_slugs=set())

    def test_newly_existing_target_makes_missing_disposition_stale(self):
        with self.assertRaisesRegex(RuntimeError, "bibliographic gap"):
            self.validate(self.missing_url, canonical_document_slugs=self.canonical | {"fixture-missing-document"})

    def test_changed_proof_cannot_hide_a_reference(self):
        changed = {**availability.UNAVAILABLE_REFERENCES[self.quarantined_url], "evidence_sha256": "f" * 64}
        with patch.dict(availability.UNAVAILABLE_REFERENCES, {self.quarantined_url: changed}):
            with self.assertRaisesRegex(RuntimeError, "evidence changed"):
                self.validate(self.quarantined_url)

    def test_changed_evidence_bytes_are_rejected(self):
        (self.root / "quarantine.json").write_text("{}")
        with self.assertRaisesRegex(RuntimeError, "evidence changed"):
            self.validate(self.quarantined_url)

    def test_new_source_requires_recorded_review(self):
        with self.assertRaisesRegex(RuntimeError, "recorded source"):
            self.validate(self.quarantined_url, source_path="content/new-unreviewed-reference.md")

    def test_relative_markdown_and_fragments_use_same_disposition(self):
        url = self.quarantined_url
        slug = url.rsplit("/", 1)[1]
        for destination in (url + "#secao", "../Tema/" + slug + ".md?view=1#secao"):
            self.assertEqual(availability.unavailable_clinical_link_reason(destination),
                             availability.unavailable_clinical_link_reason(url))
            self.assertIsNone(parse_clinical_markdown_target(destination))
        self.assertIsNone(availability.unavailable_clinical_link_reason("https://example.test" + url))

    def test_restored_exact_targets_follow_existing_approved_sources(self):
        payload = json.loads((ROOT / "backend/app/services/clinical_link_availability.json").read_text())
        restoration = payload["restoration"]
        snapshot_path = ROOT / restoration["approval_snapshot_path"]
        snapshot = json.loads(snapshot_path.read_bytes())
        self.assertEqual(len(restoration["references"]), 17)
        with patch.dict(availability.UNAVAILABLE_REFERENCES, LIVE_REFERENCES, clear=True):
            for url, record in restoration["references"].items():
                with self.subTest(url=url):
                    slug = url.rsplit("/", 1)[1]
                    self.assertIn(slug, snapshot["approved"]["documentos"])
                    self.assertNotIn(slug, snapshot["quarantined"]["documentos"])
                    proof = snapshot["provenance"]["documentos"][slug]
                    source = ROOT / record["restored_target_path"]
                    self.assertEqual(source.stem, slug)
                    # Current authorization is checked against actual bytes, not
                    # copied from a stale unavailability/quarantine snapshot.
                    self.assertEqual(sha256(source.read_bytes()).hexdigest(), proof["source_sha256"])
                    self.assertEqual(sha256((ROOT / proof["evidence_path"]).read_bytes()).hexdigest(),
                                     proof["evidence_sha256"])
                    self.assertNotIn(url, LIVE_REFERENCES)
                    self.assertIsNone(availability.unavailable_clinical_link_reason(url))
                    self.assertIsNone(availability.unavailable_clinical_link_label("Disponível", url))
                    target = parse_clinical_markdown_target(url)
                    self.assertIsNotNone(target)
                    self.assertIn("documento", target[0])
                    self.assertEqual(target[1], slug)


if __name__ == "__main__":
    unittest.main()
