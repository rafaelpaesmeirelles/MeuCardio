"""Read-only tests of explicit unavailable-reference dispositions."""
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))
from app.services import clinical_link_availability as availability
from app.services.clinical_markdown_links import parse_clinical_markdown_target


class LinkAvailabilityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        snapshot = json.loads((ROOT / "editorial-approvals/scoped-corpus-release-20260910.json").read_text())
        cls.quarantine = set(snapshot["quarantined"]["documentos"])
        cls.canonical = cls.quarantine | set(snapshot["approved"]["documentos"])

    def validate(self, url, **overrides):
        args = {"repository_root": ROOT, "canonical_document_slugs": self.canonical,
                "quarantined_document_slugs": self.quarantine,
                "source_path": availability.UNAVAILABLE_REFERENCES[url]["source_paths"][0]}
        args.update(overrides)
        return availability.validate_unavailable_clinical_reference(url, **args)

    def test_all_seventeen_have_exact_proof_and_no_graph_target(self):
        self.assertEqual(len(availability.UNAVAILABLE_REFERENCES), 17)
        reasons = []
        for url in availability.UNAVAILABLE_REFERENCES:
            with self.subTest(url=url):
                result = self.validate(url)
                reasons.append(result["reason"])
                self.assertEqual(result["presentation"], "label_without_href")
                self.assertIsNone(parse_clinical_markdown_target(url))
                label = availability.unavailable_clinical_link_label("Texto clínico preservado", url)
                self.assertEqual(label, "Texto clínico preservado (conteúdo indisponível nesta versão)")
                self.assertNotIn("href", label)
        self.assertEqual(reasons.count("target_quarantined"), 10)
        self.assertEqual(reasons.count("no_integral_approved_equivalent"), 7)

    def test_unknown_destination_is_not_exempted(self):
        url = "/biblioteca/unknown-clinical-destination"
        self.assertIsNone(availability.unavailable_clinical_link_reason(url))
        self.assertIsNone(availability.unavailable_clinical_link_label("Unknown", url))
        self.assertIsNotNone(parse_clinical_markdown_target(url))
        self.assertIsNone(availability.validate_unavailable_clinical_reference(
            url, repository_root=ROOT, canonical_document_slugs=set(),
            quarantined_document_slugs=set(), source_path="unknown"))

    def test_published_target_makes_quarantine_disposition_stale(self):
        url = next(k for k, v in availability.UNAVAILABLE_REFERENCES.items()
                   if v["reason"] == "target_quarantined")
        with self.assertRaisesRegex(RuntimeError, "quarantine"):
            self.validate(url, quarantined_document_slugs=set())

    def test_newly_existing_target_makes_missing_disposition_stale(self):
        url = next(k for k, v in availability.UNAVAILABLE_REFERENCES.items()
                   if v["reason"] == "no_integral_approved_equivalent")
        with self.assertRaisesRegex(RuntimeError, "bibliographic gap"):
            self.validate(url, canonical_document_slugs=self.canonical | {url.rsplit("/", 1)[1]})

    def test_changed_proof_cannot_hide_a_reference(self):
        url = next(iter(availability.UNAVAILABLE_REFERENCES))
        changed = {**availability.UNAVAILABLE_REFERENCES[url], "evidence_sha256": "f" * 64}
        with patch.dict(availability.UNAVAILABLE_REFERENCES, {url: changed}):
            with self.assertRaisesRegex(RuntimeError, "evidence changed"):
                self.validate(url)

    def test_new_source_requires_recorded_review(self):
        url = next(iter(availability.UNAVAILABLE_REFERENCES))
        with self.assertRaisesRegex(RuntimeError, "recorded source"):
            self.validate(url, source_path="content/new-unreviewed-reference.md")

    def test_relative_markdown_and_fragments_use_same_disposition(self):
        url = next(iter(availability.UNAVAILABLE_REFERENCES))
        slug = url.rsplit("/", 1)[1]
        for destination in (url + "#secao", "../Tema/" + slug + ".md?view=1#secao"):
            self.assertEqual(availability.unavailable_clinical_link_reason(destination),
                             availability.unavailable_clinical_link_reason(url))
            self.assertIsNone(parse_clinical_markdown_target(destination))
        self.assertIsNone(availability.unavailable_clinical_link_reason("https://example.test" + url))


if __name__ == "__main__":
    unittest.main()
