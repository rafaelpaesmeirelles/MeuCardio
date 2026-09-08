"""Pure regression tests for canonical calculator Markdown references."""
import unittest
import ast
import re
from pathlib import Path
from types import SimpleNamespace
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))

from app.services.clinical_markdown_links import parse_clinical_markdown_target


class ClinicalMarkdownLinksTests(unittest.TestCase):
    def test_auditor_reads_assembled_registry_including_safety_tools(self):
        from app.services import calculators

        path = Path(__file__).resolve().parents[1] / "audit_tudo_com_tudo.py"
        tree = ast.parse(path.read_text(encoding="utf-8"))
        function = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                        and n.name == "audit")
        assignment = next(
            n for n in function.body if isinstance(n, ast.Assign)
            and any(isinstance(t, ast.Subscript) and isinstance(t.value, ast.Name)
                    and t.value.id == "slugs" and isinstance(t.slice, ast.Constant)
                    and t.slice.value == "calculadora" for t in n.targets)
        )
        unavailable = SimpleNamespace(slug="nao-publicavel", status="verificacao_humana_necessaria")
        env = {"slugs": {}, "calculator_service": SimpleNamespace(
            REGISTRY={**calculators.REGISTRY, "nao-publicavel": unavailable},
        )}
        exec(compile(ast.Module(body=[assignment], type_ignores=[]), str(path), "exec"), env)
        actual = env["slugs"]["calculadora"]
        self.assertIn("hipercalemia-seguranca-uco", actual)
        self.assertIn("brash-reconhecimento-padrao-uco", actual)
        self.assertNotIn("nao-publicavel", actual)
        self.assertEqual(actual, {c.slug for c in calculators.REGISTRY.values()
                                  if c.status == "implementada"})

    def test_actual_graph_document_loop_keeps_direction_and_canonical_types(self):
        graph_path = Path(__file__).resolve().parents[2] / "backend/app/services/knowledge_graph.py"
        tree = ast.parse(graph_path.read_text(encoding="utf-8"))
        function = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                        and n.name == "_registrar_referencias_explicitas")
        loop = next(n for n in function.body if isinstance(n, ast.For)
                    and isinstance(n.target, ast.Name) and n.target.id == "documento")
        calls = []
        env = {
            "documentos": [SimpleNamespace(
                slug="origem", kind="fluxograma",
                body_md="[KDIGO](/calculadoras/lesao-renal-aguda-kdigo-uco) "
                        "[externo](https://other.example/calculadoras/heart)",
            )],
            "parse_clinical_markdown_target": parse_clinical_markdown_target,
            "_LINK_MARKDOWN": re.compile(r"(?<!!)\[[^\]]+\]\(([^)\s]+)\)"),
            "_markdown_sem_codigo": lambda value: value,
            "_no": lambda types, slug: (types, slug),
            "_ligar": lambda *args, **kwargs: calls.append((args, kwargs)),
        }
        exec(compile(ast.Module(body=[loop], type_ignores=[]), str(graph_path), "exec"), env)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][0], (
            (("calculadora",), "lesao-renal-aguda-kdigo-uco"),
            (("fluxograma",), "origem"), "mentioned_in",
        ))
        self.assertEqual(calls[0][1]["extra"]["campo"], "Document.body_md.link")

    def test_calculator_uses_exact_typed_identity(self):
        for destination in (
            "/calculadoras/lesao-renal-aguda-kdigo-uco",
            "/calculadoras/lesao-renal-aguda-kdigo-uco/",
            "/calculadoras/lesao-renal-aguda-kdigo-uco?origem=texto#resultado",
            "/calculadoras/lesao%2Drenal-aguda-kdigo-uco",
        ):
            with self.subTest(destination=destination):
                self.assertEqual(parse_clinical_markdown_target(destination), (
                    ("calculadora",), "lesao-renal-aguda-kdigo-uco",
                ))

    def test_unrecognized_or_ambiguous_routes_are_not_guessed(self):
        for destination in (
            "https://other.example/calculadoras/heart", "//other.example/calculadoras/heart",
            "javascript:alert(1)", "/calculadoras/", "/calculadoras/../heart",
            "/calculadoras/heart/results", "/calculadoras/heart%2Fresults",
            "/calculadoras/heart with spaces", "/calculadoras?slug=heart", "/exames/heart",
        ):
            with self.subTest(destination=destination):
                self.assertIsNone(parse_clinical_markdown_target(destination))

    def test_legacy_library_references_remain_compatible(self):
        for destination in ("/biblioteca/fluxograma-ic#etapa", "../content/fluxograma-ic.md"):
            with self.subTest(destination=destination):
                self.assertEqual(parse_clinical_markdown_target(destination), (
                    ("documento", "fluxograma"), "fluxograma-ic",
                ))


if __name__ == "__main__":
    unittest.main()
