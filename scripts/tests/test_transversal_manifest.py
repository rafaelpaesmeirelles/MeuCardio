from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))
from app.services.transversal_manifest import load_transversal_relations, resolve_transversal_relations


class TransversalManifestTests(unittest.TestCase):
    def setUp(self):
        self.record = dict(source_type="medicamento", source_slug="med",
            target_type="exame", target_slug="exam", relation_type="monitor_with",
            provenance_type="editorial", confidence="explicit", review_status="revisado",
            relevance_score=1.0, evidence_source="exames/metadados.json#exam",
            review_note="Monitorização explicitamente descrita na fonte.")

    def load(self, records):
        with patch.object(Path, "read_text", return_value=json.dumps(records)):
            return load_transversal_relations(Path("manifest.json"))

    def test_accepts_reviewed_pair_and_rejects_invalid_clinical_direction(self):
        self.assertEqual(self.load([self.record]), [self.record])
        self.record.update(source_type="estudo", target_type="calculadora", relation_type="treats")
        with self.assertRaises(ValueError):
            self.load([self.record])

    def test_fails_closed_for_duplicates_missing_provenance_pending_and_lexical(self):
        with self.assertRaises(ValueError):
            self.load([self.record, self.record])
        for field, value in (("evidence_source", ""), ("review_note", ""),
                             ("review_status", "pendente_revisao"),
                             ("confidence", "derived"), ("relevance_score", True)):
            record = {**self.record, field: value}
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.load([record])

    def test_old_active_node_cannot_substitute_current_publication(self):
        entities = {("medicamento", "med"): object(), ("exame", "exam"): object()}
        resolved, unresolved = resolve_transversal_relations([self.record], entities, set(entities))
        self.assertEqual(len(resolved), 1)
        self.assertEqual(unresolved, [])
        resolved, unresolved = resolve_transversal_relations([self.record], entities, {("medicamento", "med")})
        self.assertEqual(resolved, [])
        self.assertEqual(unresolved[0]["motivo"], "destino_nao_publicado")
        resolved, unresolved = resolve_transversal_relations([self.record], {}, set(entities))
        self.assertEqual(unresolved[0]["motivo"], "no_ativo_ausente")

    def test_real_manifest_satisfies_policy(self):
        records = load_transversal_relations(ROOT / "doencas/relacoes-transversais.json")
        self.assertTrue(records)


if __name__ == "__main__":
    unittest.main()
