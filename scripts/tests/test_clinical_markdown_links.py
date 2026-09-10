"""Pure regression tests for canonical calculator Markdown references."""
import unittest
import ast
import re
import json
from pathlib import Path
from types import SimpleNamespace
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))

from app.services.clinical_markdown_links import (
    parse_clinical_markdown_target, resolve_clinical_markdown_destination,
    rewrite_clinical_markdown_links,
)


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


class TypedApprovedLinksTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parents[2]
        report = json.loads((cls.root / "docs/tct-missing-link-destination-review-20260910.json").read_text())
        cls.aliases = [item for item in report["items"] if item["status"] == "approved_same_entity"]
        cls.excluded = [item for item in report["items"] if item["status"] != "approved_same_entity"]

    def test_exactly_seven_aliases_have_approved_typed_destinations(self):
        approval = json.loads((self.root / "editorial-approvals/scoped-corpus-release-20260910.json").read_text())
        self.assertEqual(len(self.aliases), 7)
        for item in self.aliases:
            with self.subTest(item=item["old_url"]):
                expected = ((item["new_type"],), item["new_slug"])
                self.assertIn(item["new_slug"], approval["approved"][item["approval_front"]])
                self.assertEqual(parse_clinical_markdown_target(item["old_url"]), expected)
                self.assertEqual(parse_clinical_markdown_target(item["new_url"]), expected)
                self.assertEqual(resolve_clinical_markdown_destination(item["old_url"]), item["new_url"])

    def test_renderer_preserves_labels_and_query_fragment(self):
        for item in self.aliases:
            source = f"[Rótulo original]({item['old_url']}?origem=tct#referencias)"
            expected = f"[Rótulo original]({item['new_url']}?origem=tct#referencias)"
            self.assertEqual(rewrite_clinical_markdown_links(source), expected)
            relative = "../content/" + item["old_url"].rsplit("/", 1)[-1] + ".md"
            self.assertEqual(resolve_clinical_markdown_destination(relative), item["new_url"])

    def test_partial_unknown_and_external_targets_are_never_aliased(self):
        for item in self.excluded:
            self.assertEqual(resolve_clinical_markdown_destination(item["old_url"]), item["old_url"])
        for destination in ["/biblioteca/ainda-nao-existe", "https://example.org" + self.aliases[0]["old_url"]]:
            self.assertEqual(resolve_clinical_markdown_destination(destination), destination)
        self.assertEqual(parse_clinical_markdown_target("/biblioteca/ainda-nao-existe"),
                         (("documento", "fluxograma"), "ainda-nao-existe"))

    def test_multiline_labels_match_graph_and_auditor_grammar(self):
        label = "Linha\nseguinte"
        alias = self.aliases[0]
        self.assertEqual(
            rewrite_clinical_markdown_links(f"[{label}]({alias['old_url']})"),
            f"[{label}]({alias['new_url']})",
        )
        unavailable = self.excluded[0]["old_url"]
        self.assertIsNone(parse_clinical_markdown_target(unavailable))
        rendered = rewrite_clinical_markdown_links(f"[{label}]({unavailable})")
        self.assertEqual(rendered, label + " (conteúdo indisponível nesta versão)")
        self.assertNotIn(unavailable, rendered)


    def test_code_samples_and_images_remain_unchanged(self):
        url = self.aliases[0]["old_url"]
        for body in [f"`[Exemplo]({url})`", f"```md\n[Exemplo]({url})\n```", f"![Imagem]({url})"]:
            self.assertEqual(rewrite_clinical_markdown_links(body), body)

    def test_actual_library_renderer_uses_the_shared_resolution(self):
        path = self.root / "backend/app/api/library.py"
        node = next(n for n in ast.parse(path.read_text()).body if isinstance(n, ast.FunctionDef)
                    and n.name == "_library_document_links")
        env = {"rewrite_clinical_markdown_links": rewrite_clinical_markdown_links}
        exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), "exec"), env)
        for item in self.aliases:
            self.assertEqual(env["_library_document_links"](f"[Título]({item['old_url']})"),
                             f"[Título]({item['new_url']})")

    def test_actual_graph_loop_records_real_type_and_no_strong_relation(self):
        path = self.root / "backend/app/services/knowledge_graph.py"
        tree = ast.parse(path.read_text())
        fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_registrar_referencias_explicitas")
        loop = next(n for n in fn.body if isinstance(n, ast.For) and isinstance(n.target, ast.Name) and n.target.id == "documento")
        calls = []
        body = "\n".join(f"[Referência]({item['old_url']})" for item in self.aliases + self.excluded)
        env = {"documentos": [SimpleNamespace(slug="origem", kind="documento", body_md=body)],
               "parse_clinical_markdown_target": parse_clinical_markdown_target,
               "_LINK_MARKDOWN": re.compile(r"(?<!!)\[[^\]]+\]\(([^)\s]+)\)"),
               "_markdown_sem_codigo": lambda value: value,
               "_no": lambda types, slug: (types, slug),
               "_ligar": lambda *args, **kwargs: calls.append((args, kwargs))}
        exec(compile(ast.Module(body=[loop], type_ignores=[]), str(path), "exec"), env)
        self.assertEqual(len(calls), 7)
        self.assertEqual({call[0][0] for call in calls},
                         {((item["new_type"],), item["new_slug"]) for item in self.aliases})
        self.assertTrue(all(call[0][1:] == ((("documento",), "origem"), "mentioned_in") for call in calls))


if __name__ == "__main__":
    unittest.main()
