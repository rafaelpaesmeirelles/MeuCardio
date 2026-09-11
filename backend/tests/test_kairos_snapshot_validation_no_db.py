"""Run directly: pure provider/data contracts, with no app/DB/conftest.

The direct runner also executes the 13 pre-existing K@iros contracts against
their explicit historical fixture. --benchmark measures synthetic expansion,
never catalogue publication or real prescriptions.
"""
import ast
from copy import deepcopy
from decimal import Decimal
import json
from pathlib import Path
import runpy
import sys
import tempfile
from time import perf_counter
from types import SimpleNamespace
import unittest


ROOT = Path(__file__).resolve().parents[2]
MATCHING = runpy.run_path(str(Path(__file__).with_name("test_kairos_matching_no_db.py")))
PROVIDER = MATCHING["load_provider"]()
BASELINE = json.loads(MATCHING["SNAPSHOT_FIXTURE"].read_text(encoding="utf-8"))


class KairosSnapshotValidationTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="corvia-kairos-contract-")
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "snapshot.json"
        self.data = deepcopy(BASELINE)

    def load(self, data=None):
        self.path.write_text(json.dumps(self.data if data is None else data), encoding="utf-8")
        return PROVIDER["load_snapshot"](self.path)

    def test_all_historical_cells_remain_literal_and_api_json_has_no_index_keys(self):
        snapshot = self.load()
        self.assertEqual(snapshot, BASELINE)
        self.assertEqual(json.loads(json.dumps(snapshot)), BASELINE)
        self.assertEqual(len(snapshot["records"]), 13)
        self.assertEqual(sum(len(r["presentations"]) for r in snapshot["records"]), 52)
        self.assertEqual(PROVIDER["_decimal_br"]("1.234,56"), Decimal("1234.56"))
        self.assertEqual(PROVIDER["_decimal_br"]("1234,56"), Decimal("1234.56"))

    def test_monetary_numbers_ambiguous_formats_and_nonpositive_values_fail_closed(self):
        invalid = [12.34, 12, True, False, float("nan"), float("inf"),
                   "NaN", "Infinity", "-1,00", "0,00", "00,50", "1.234",
                   "12.34", "12,3", "1,234.56", "1.23,45", " 1,00", "1,00 ",
                   "1e2", "1_000,00", [], {}]
        for value in invalid:
            with self.subTest(value=repr(value)):
                self.data["records"][0]["presentations"][0]["pmc20"] = value
                with self.assertRaises(ValueError):
                    self.load()

    def test_all_eight_price_columns_are_validated_not_just_pmc(self):
        for field in PROVIDER["PRICE_FIELDS"]:
            with self.subTest(field=field):
                data = deepcopy(BASELINE)
                data["records"][0]["presentations"][0][field] = 20.50
                with self.assertRaises(ValueError):
                    self.load(data)

    def test_missing_cells_and_substance_never_become_fabricated_pmc(self):
        record = self.data["records"][0]
        record["substance"] = None
        record["presentations"] = [
            {"presentation": "Synthetic PF-only package", "pf20": "10,00", "pmc20": None},
            {"presentation": "Synthetic unpriced package", "pmc20": ""},
        ]
        self.data["records"] = [record]
        snapshot = self.load()
        drug = SimpleNamespace(id=-1, generic_name="", brand_names=[record["product"]])
        self.assertEqual(PROVIDER["prescription_options_for"](drug, snapshot=snapshot)["opcoes"], [])
        observations = PROVIDER["KairosProvider"](SimpleNamespace(get=lambda *_: drug), self.path).observations_for(-1)
        self.assertEqual([(o.price_type, o.price) for o in observations], [("pf", Decimal("10.00"))])
        del record["substance"]
        self.load()

    def test_required_container_metadata_and_licence_validation(self):
        mutations = [("schema_version", True), ("schema_version", 2), ("issue", 0),
                     ("issue", True), ("competence", "2026-13"), ("competence", None),
                     ("licensed_use", "true"), ("source_type", "retail"),
                     ("source", ""), ("regulatory_authority", None),
                     ("regulatory_note", " "), ("records", {})]
        for key, value in mutations:
            with self.subTest(key=key, value=value):
                data = deepcopy(BASELINE)
                data[key] = value
                with self.assertRaises(ValueError):
                    self.load(data)
        with self.assertRaises(ValueError):
            self.load([])

    def test_required_record_and_presentation_shape(self):
        mutations = [("product", " "), ("laboratory", None), ("substance", []),
                     ("substance", ""), ("page", True), ("page", 0),
                     ("presentations", []), ("presentations", {}),
                     ("presentations", [None]), ("presentations", [{"presentation": ""}])]
        for key, value in mutations:
            with self.subTest(key=key):
                data = deepcopy(BASELINE)
                data["records"][0][key] = value
                with self.assertRaises(ValueError):
                    self.load(data)
        self.data["records"][0] = None
        with self.assertRaises(ValueError):
            self.load()

    def test_duplicate_json_keys_do_not_silently_overwrite_price_or_identity(self):
        serialized = json.dumps(BASELINE)
        self.path.write_text(serialized.replace('"pf20": "22,57"', '"pf20": "1,00", "pf20": "22,57"', 1), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "chave JSON duplicada"):
            PROVIDER["load_snapshot"](self.path)

    def test_duplicate_presentation_conflicting_price_or_substance_is_rejected(self):
        for conflict in ("price", "substance"):
            with self.subTest(conflict=conflict):
                data = deepcopy(BASELINE)
                duplicate = deepcopy(data["records"][0])
                duplicate["page"] += 1
                if conflict == "price":
                    duplicate["presentations"][0]["pmc20"] = "99,99"
                else:
                    duplicate["substance"] = "SYNTHETIC DIFFERENT INGREDIENT"
                data["records"].append(duplicate)
                with self.assertRaisesRegex(ValueError, "duplicada conflitante"):
                    self.load(data)

    def test_third_duplicate_is_checked_against_prior_complementary_cells(self):
        record = self.data["records"][0]
        record["presentations"] = [{"presentation": "Synthetic same package", "pf20": "10,00"}]
        second = deepcopy(record)
        second["presentations"][0] = {"presentation": "Synthetic same package", "pmc20": "20,00"}
        third = deepcopy(second)
        third["presentations"][0]["pmc20"] = "30,00"
        self.data["records"] = [record, second, third]
        with self.assertRaisesRegex(ValueError, "duplicada conflitante"):
            self.load()

    def test_identical_duplicates_metadata_and_distinct_presentations_are_preserved(self):
        record = self.data["records"][0]
        record["presentations"][0].update(source_side="left", source_line=12, bbox=[1, 2, 3, 4])
        self.data["records"].append(deepcopy(record))
        distinct = deepcopy(record)
        distinct["presentations"][0]["presentation"] += " SYNTHETIC DIFFERENT PACKAGE"
        distinct["presentations"][0]["pmc20"] = "99,99"
        self.data["records"].append(distinct)
        self.assertEqual(self.load(), self.data)

    def test_unreviewed_price_columns_fail_instead_of_being_silently_ignored(self):
        for column in ("pmc19", "pf0", "PMC20", "pf_20"):
            with self.subTest(column=column):
                data = deepcopy(BASELINE)
                data["records"][0]["presentations"][0][column] = "12,00"
                with self.assertRaisesRegex(ValueError, "coluna de preço não suportada"):
                    self.load(data)

    def test_reload_same_custom_path_reads_changed_file_without_stale_index(self):
        first = self.load()
        self.data["records"][0]["product"] = "SYNTHETIC CHANGED BRAND"
        self.data["records"][0]["presentations"][0]["pmc20"] = "40,00"
        second = self.load()
        drug = SimpleNamespace(id=-1, generic_name="", brand_names=["SYNTHETIC CHANGED BRAND"])
        self.assertEqual(PROVIDER["records_for_drug"](drug, snapshot=first)[1], [])
        self.assertEqual(len(PROVIDER["records_for_drug"](drug, snapshot=second)[1]), 1)
        self.assertEqual(second["records"][0]["presentations"][0]["pmc20"], "40,00")
        self.path.write_text("{}", encoding="utf-8")
        with self.assertRaises(ValueError):
            PROVIDER["load_snapshot"](self.path)

    def test_index_matches_unchanged_matcher_in_order_for_catalogue_and_adversarial_inputs(self):
        extra = deepcopy(self.data["records"][0])
        extra["product"] = "SYNTHETIC NULL SUBSTANCE"
        extra["substance"] = None
        self.data["records"].append(extra)
        snapshot = self.load()
        rows = json.loads((ROOT / "medicamentos/metadados.json").read_text(encoding="utf-8"))
        drugs = [SimpleNamespace(generic_name=r["generic_name"], brand_names=r.get("brand_names")) for r in rows]
        drugs += [SimpleNamespace(generic_name=name, brand_names=brands) for name, brands in (
            ("", ["ACERTANLO", "SYNTHETIC NULL SUBSTANCE"]),
            ("Anlodipino", []), ("Sacubitril", []), ("Valsartana", []),
            ("Valsartana + Sacubitril", ["ACERTALIX"]),
            ("ARGININA + ANLODIPINO", []), ("", []), (None, None),
        )]
        for drug in drugs:
            expected = [r for r in snapshot["records"] if PROVIDER["_record_matches"](drug, r)]
            actual = PROVIDER["records_for_drug"](drug, snapshot=snapshot)[1]
            self.assertEqual(actual, expected)
            self.assertEqual([id(r) for r in actual], [id(r) for r in expected])

    def test_plain_caller_snapshot_keeps_linear_compatibility_and_no_hidden_keys(self):
        plain = deepcopy(BASELINE)
        drug = SimpleNamespace(generic_name="", brand_names=["SYNTHETIC CHANGED BRAND"])
        self.assertEqual(PROVIDER["records_for_drug"](drug, snapshot=plain)[1], [])
        plain["records"][0]["product"] = drug.brand_names[0]
        self.assertEqual(len(PROVIDER["records_for_drug"](drug, snapshot=plain)[1]), 1)
        self.assertEqual(set(plain), set(BASELINE))


def existing_contract_suite():
    """Execute genuine six historical functions without importing app or pytest."""
    source = Path(__file__).with_name("test_pricing_kairos_provider.py")
    tree = ast.parse(source.read_text(encoding="utf-8"))
    tree.body = [node for node in tree.body if not (
        isinstance(node, ast.ImportFrom) and node.module == "app.services.pricing.kairos_provider"
    )]
    namespace = {"__file__": str(source), **{key: PROVIDER[key] for key in (
        "KairosProvider", "load_snapshot", "prescription_options_for", "records_for_drug",
    )}}
    exec(compile(tree, str(source), "exec"), namespace)
    suite = unittest.TestSuite(unittest.FunctionTestCase(value) for name, value in namespace.items() if name.startswith("test_"))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(MATCHING["KairosMatchingTest"]))
    return suite


def benchmark():
    rows = json.loads((ROOT / "medicamentos/metadados.json").read_text(encoding="utf-8"))
    drugs = [SimpleNamespace(**{key: row.get(key) for key in ("generic_name", "brand_names", "slug", "review_status")})
             for row in rows if row.get("review_status") == "revisado"][:176]
    expanded = {**BASELINE, "records": [dict(BASELINE["records"][i % len(BASELINE["records"])], product=f"BENCH PRODUCT {i}") for i in range(6000)]}
    started = perf_counter()
    expected = [PROVIDER["records_for_drug"](drug, snapshot=expanded)[1] for drug in drugs]
    linear_seconds = perf_counter() - started
    started = perf_counter()
    PROVIDER["_validate_snapshot"](expanded)
    indexed = PROVIDER["_IndexedSnapshot"](expanded)
    preparation_seconds = perf_counter() - started
    started = perf_counter()
    actual = [PROVIDER["records_for_drug"](drug, snapshot=indexed)[1] for drug in drugs]
    indexed_seconds = perf_counter() - started
    assert actual == expected, "Index changed matching semantics/order"
    print(json.dumps({"records": 6000, "catalogue_drugs": len(drugs), "matches": sum(map(len, actual)),
                      "linear_seconds": round(linear_seconds, 4), "validation_and_index_seconds": round(preparation_seconds, 4),
                      "indexed_matching_seconds": round(indexed_seconds, 4), "note": "synthetic records, not DB publication"}))


if __name__ == "__main__":
    if sys.argv[1:] == ["--benchmark"]:
        benchmark()
    else:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(KairosSnapshotValidationTest)
        suite.addTests(existing_contract_suite())
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        raise SystemExit(not result.wasSuccessful())
