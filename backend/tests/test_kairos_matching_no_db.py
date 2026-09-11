"""Focused K@iros matching contracts: run directly, with no app/DB/conftest.

Compile the genuine provider unchanged except its ORM/type-only imports.
Prices come from the unchanged historical cardiovascular extract, pinned as an
explicit fixture so expanding the current issue cannot weaken these assertions.
These tests never open a database.
"""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest


ROOT = Path(__file__).resolve().parents[2]
PROVIDER = ROOT / "backend/app/services/pricing/kairos_provider.py"
SNAPSHOT_FIXTURE = Path(__file__).parent / "fixtures/kairos-453-2026-08-cardiovascular.json"


def load_provider():
    tree = ast.parse(PROVIDER.read_text(encoding="utf-8"))
    blocked_imports = {
        "sqlalchemy.orm", "app.models.drug", "app.services.pricing.base",
    }
    tree.body = [node for node in tree.body if not (
        isinstance(node, ast.ImportFrom) and node.module in blocked_imports
    )]
    namespace = {
        "__file__": str(PROVIDER), "Drug": object, "Session": object,
        "PriceObservation": SimpleNamespace,
    }
    exec(compile(tree, str(PROVIDER), "exec"), namespace)
    return namespace


class KairosMatchingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.provider = load_provider()
        cls.snapshot = cls.provider["load_snapshot"](SNAPSHOT_FIXTURE)

    def matches(self, name, brands=()):
        drug = SimpleNamespace(id=-1, generic_name=name, brand_names=list(brands))
        _, records = self.provider["records_for_drug"](drug, snapshot=self.snapshot)
        return [record["product"] for record in records]

    def test_repository_fallback_points_to_existing_reviewed_snapshot(self):
        fallback = ROOT / "medicamentos/kairos-453-2026-08.json"
        self.assertEqual(self.provider["REPOSITORY_FALLBACK"], fallback)
        self.assertTrue(fallback.is_file())
        self.assertEqual(self.snapshot["source_type"], "market_intelligence")
        self.assertTrue(self.snapshot["licensed_use"])

    def test_real_catalogue_salt_does_not_hide_trimetazidine(self):
        self.assertEqual(
            self.matches("Trimetazidina (dicloridrato)", ["Vastarel", "Vascor MR"]),
            ["VASTAREL CAPS LP"],
        )

    def test_single_ingredients_never_match_fixed_dose_combinations(self):
        for name in ("Valsartana", "Indapamida", "Sacubitril", "Anlodipino (besilato)"):
            with self.subTest(name=name):
                self.assertEqual(self.matches(name), [])
        self.assertEqual(self.matches("Perindopril (arginina/erbumina)"), ["ACERTIL"])

    def test_combination_order_and_reviewed_salts_keep_exact_ingredient_set(self):
        self.assertEqual(self.matches("Sacubitril/Valsartana"), ["NEPARVIS"])
        self.assertEqual(self.matches("Valsartana + Sacubitril"), ["NEPARVIS"])
        self.assertEqual(
            self.matches("Indapamida + Perindopril (arginina/erbumina)"),
            ["ACERTALIX"],
        )
        self.assertEqual(self.matches("Valsartana + Anlodipino"), [])
        self.assertEqual(self.matches("Perindopril + Indapamida + Anlodipino"), [])

    def test_audited_exact_brand_still_handles_abbreviated_source_heading(self):
        self.assertEqual(
            self.matches("Anlodipino (besilato) + Perindopril (arginina/erbumina)", ["ACERTANLO"]),
            ["ACERTANLO"],
        )

    def test_absent_product_and_other_brand_suffix_are_not_guessed(self):
        self.assertEqual(self.matches("ATEsto", ["ATEsto"]), [])
        self.assertEqual(self.matches("Amoxicilina", ["Vastarel"]), [])
        self.assertEqual(self.matches("", []), [])

    def test_newly_reached_options_are_literal_pmc_cells_not_cmed_or_ean(self):
        drug = SimpleNamespace(id=-1, generic_name="Trimetazidina (dicloridrato)", brand_names=["Vastarel"])
        payload = self.provider["prescription_options_for"](drug, snapshot=self.snapshot)
        record = next(r for r in self.snapshot["records"] if r["product"] == "VASTAREL CAPS LP")
        self.assertEqual(len(payload["opcoes"]), len(record["presentations"]))
        self.assertEqual(payload["tipo_fonte"], "inteligencia_de_mercado")
        self.assertEqual(payload["edicao"], self.snapshot["issue"])
        self.assertEqual(payload["competencia"], self.snapshot["competence"])
        for option, original in zip(payload["opcoes"], record["presentations"]):
            prices = [self.provider["_decimal_br"](str(original[key]))
                      for key, (kind, _) in self.provider["PRICE_FIELDS"].items()
                      if kind == "pmc" and original.get(key) not in (None, "")]
            self.assertEqual(option["preco_minimo"], float(min(prices)))
            self.assertEqual(option["preco_maximo"], float(max(prices)))
            self.assertEqual(option["apresentacao"], original["presentation"])
            self.assertEqual(option["pagina_fonte"], record["page"])
            self.assertFalse({"ean", "ggrem", "pmc_snapshot", "uf"} & option.keys())


if __name__ == "__main__":
    unittest.main()
