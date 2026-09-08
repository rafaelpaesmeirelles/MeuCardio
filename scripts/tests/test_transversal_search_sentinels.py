"""Pure search contracts; no claim of PostgreSQL or public-runtime coverage."""
import ast
import importlib
import json
from pathlib import Path
import re
import sys
import unicodedata
import unittest

ROOT = Path(__file__).resolve().parents[2]
SERVICE = ROOT / "backend/app/services/catalog_search.py"


def load_search_functions():
    sys.path.insert(0, str(ROOT / "backend"))
    try:
        calc = importlib.import_module("app.services.calculators")
    finally:
        sys.path.pop(0)
    tree = ast.parse(SERVICE.read_text(encoding="utf-8"))
    names = {"normalizar", "literal_like", "calculadoras_encontradas"}
    selected = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
    assert len(selected) == len(names)
    namespace = {"re": re, "unicodedata": unicodedata, "calc": calc}
    exec(compile(ast.Module(body=selected, type_ignores=[]), str(SERVICE), "exec"), namespace)
    return namespace


FUNCTIONS = load_search_functions()


class TransversalSearchSentinels(unittest.TestCase):
    def test_required_human_queries_normalize_without_slug_knowledge(self):
        examples = {
            "Holter": "holter", "Holter 24h": "holter 24h",
            "fibrilação atrial": "fibrilacao atrial", "CHA2DS2-VASc": "cha2ds2 vasc",
            "HAS-BLED": "has bled", "estenose aórtica": "estenose aortica",
            "choque cardiogênico": "choque cardiogenico",
            "hipertensão resistente": "hipertensao resistente",
        }
        for query, expected in examples.items():
            with self.subTest(query=query):
                self.assertEqual(FUNCTIONS["normalizar"](query), expected)

    def test_real_calculator_registry_finds_unicode_and_ascii_scores(self):
        for query, slug in (("CHA2DS2-VASc", "cha2ds2-vasc"), ("CHA₂DS₂-VASc", "cha2ds2-vasc"), ("HAS-BLED", "has-bled")):
            with self.subTest(query=query):
                found = FUNCTIONS["calculadoras_encontradas"](query)
                self.assertTrue(found)
                self.assertEqual(found[0]["slug"], slug)

    def test_literal_search_escapes_user_wildcards(self):
        self.assertEqual(FUNCTIONS["literal_like"]("Á_%!₂"), "a!_!%!!2")

    def test_holter_has_unique_reviewed_canonical_endpoint_and_slug_search(self):
        exams = json.loads((ROOT / "exames/metadados.json").read_text(encoding="utf-8"))
        matches = [item for item in exams if item["slug"] == "holter-24h"]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["review_status"], "revisado")
        self.assertEqual(FUNCTIONS["normalizar"](matches[0]["slug"]), "holter 24h")
        tree = ast.parse(SERVICE.read_text(encoding="utf-8"))
        assignment = next(n for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "FULL_TEXT_MATCH" for t in n.targets))
        self.assertIn("to_tsvector('simple', coalesce(slug, ''))", ast.literal_eval(assignment.value))


if __name__ == "__main__":
    unittest.main()
