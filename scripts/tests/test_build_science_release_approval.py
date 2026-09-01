from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "build_science_release_approval.py"
SPEC = importlib.util.spec_from_file_location("science_release_approval", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ReviewNoteGateTests(unittest.TestCase):
    def test_accepts_completed_review_note(self) -> None:
        self.assertTrue(
            MODULE.has_review_note(
                {
                    "review_note": (
                        "Revisão científica independente concluída em 2026-09-01; "
                        "fontes e limites conferidos."
                    )
                }
            )
        )

    def test_accepts_non_presumption_without_pending_review(self) -> None:
        self.assertTrue(
            MODULE.has_review_note(
                {
                    "revisao": (
                        "A atestação clínica individual não foi presumida; a aprovação "
                        "editorial está registrada. Revisão independente concluída."
                    )
                }
            )
        )

    def test_rejects_empty_or_missing_note(self) -> None:
        self.assertFalse(MODULE.has_review_note({}))
        self.assertFalse(MODULE.has_review_note({"review_note": "  "}))

    def test_rejects_pending_review_language(self) -> None:
        pending_notes = (
            "Este conteúdo ainda não revisado não pode ser publicado.",
            "Aguardando revisão independente.",
            "Revisão pendente.",
            "Revisão editorial independente pendente.",
            "Revisão clínica independente pendente.",
            "Revisão metodológica independente obrigatória.",
            "Artigo integral e revisão independente pendentes.",
            "Sem avaliação clínica independente.",
            "Ainda não avaliado pela equipe editorial.",
            "Este item ainda não carrega aval clínico individual.",
        )
        for note in pending_notes:
            with self.subTest(note=note):
                self.assertFalse(MODULE.has_review_note({"review_note": note}))

    def test_pending_legacy_field_is_not_hidden_by_completed_new_field(self) -> None:
        self.assertFalse(
            MODULE.has_review_note(
                {
                    "review_note": "Revisão estrutural concluída.",
                    "revisao": "Aguardando revisão editorial independente.",
                }
            )
        )


if __name__ == "__main__":
    unittest.main()
