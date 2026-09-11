"""Focused source-reference regressions; direct unittest, no app/DB/conftest."""
from collections import defaultdict
from copy import deepcopy
import json
from pathlib import Path
import runpy
import tempfile
from types import SimpleNamespace
import unittest


ROOT = Path(__file__).resolve().parents[2]
HELPERS = runpy.run_path(str(Path(__file__).with_name("test_kairos_matching_no_db.py")))
PROVIDER = HELPERS["load_provider"]()
BASELINE = json.loads(HELPERS["SNAPSHOT_FIXTURE"].read_text(encoding="utf-8"))


def curated_records():
    # Synthetic amounts/coordinates exercise actual collision shapes, not new
    # clinical pricing evidence. All eight tax cells belong to one row.
    def record(product, lab, page, descriptions, first_line):
        return {"product": product, "laboratory": lab, "substance": None, "page": page,
                "source_origin": "pdf_literal_selected_original_row",
                "presentations": [{"presentation": text, "source_page": page,
                                   "source_side": "left", "source_line": first_line + index,
                                   **{field: f"{index + 1},00" for field in PROVIDER["PRICE_FIELDS"]}}
                                  for index, text in enumerate(descriptions)]}
    return [record("HEPTRIS", "UNIÃO QUÍMICA", 41, ["40mg Sol. inj ct 10 ser vd tr pr x 0.4ml +sist seg"], 20),
            record("HEPTRIS", "VIATRIS", 41, ["40mg Sol. inj ct10 ser vd tr pre x 0.4ml"], 30),
            record("NIMEGON MET", "MSD", 53, ["50mg /850mg Comp. rev ct bl al al x 28", "50mg /1000mg Comp. rev ct bl al pla x 28"], 40),
            record("NIMEGON MET", "SUPERA RX", 53, ["50mg 1000mg Comp. rev x 28", "50mg 850mg Comp. rev x 28"], 50)]


class KairosPresentationReferenceTest(unittest.TestCase):
    def observations(self, snapshot, brands):
        with tempfile.TemporaryDirectory(prefix="corvia-kairos-ref-") as folder:
            path = Path(folder) / "snapshot.json"
            path.write_text(json.dumps(snapshot), encoding="utf-8")
            drug = SimpleNamespace(id=-1, generic_name="", brand_names=brands)
            db = SimpleNamespace(get=lambda *_: drug)
            return PROVIDER["KairosProvider"](db, path).observations_for(-1)

    @staticmethod
    def identity(observation):
        metadata = observation.metadata
        return metadata["product"], metadata["laboratory"], metadata["presentation"]

    def test_heptris_laboratories_and_nimegon_doses_have_distinct_references(self):
        data = {**BASELINE, "records": curated_records()}
        observations = self.observations(data, ["HEPTRIS", "NIMEGON MET"])
        refs = defaultdict(set)
        cells = defaultdict(list)
        for item in observations:
            refs[item.presentation_ref].add(self.identity(item))
            cells[item.presentation_ref].append((item.price_type, item.region))
        self.assertEqual(len(refs), 6)
        self.assertTrue(all(len(identities) == 1 for identities in refs.values()))
        self.assertTrue(all(len(values) == len(set(values)) == 8 for values in cells.values()))
        self.assertTrue(all(ref.startswith("kairos-453:source:") for ref in refs))

    def test_new_reference_does_not_depend_on_record_or_presentation_array_order(self):
        data = {**BASELINE, "records": curated_records()}
        before = {self.identity(item): item.presentation_ref for item in self.observations(data, ["HEPTRIS", "NIMEGON MET"])}
        reordered = deepcopy(data)
        reordered["records"].reverse()
        for record in reordered["records"]:
            record["presentations"].reverse()
        after = {self.identity(item): item.presentation_ref for item in self.observations(reordered, ["HEPTRIS", "NIMEGON MET"])}
        self.assertEqual(before, after)

    def test_historical_52_references_are_unchanged_with_or_without_curation_metadata(self):
        expected = {(record["product"], record["laboratory"], presentation["presentation"]):
                    f"kairos-{BASELINE['issue']}:{record['page']}:{PROVIDER['_normalize'](record['product']).replace(' ', '-')}:{index}"
                    for record in BASELINE["records"] for index, presentation in enumerate(record["presentations"], start=1)}
        brands = [record["product"] for record in BASELINE["records"]]
        for marked in (False, True):
            with self.subTest(curation_metadata=marked):
                data = deepcopy(BASELINE)
                if marked:
                    for record in data["records"]:
                        record["curation_provenance"] = {"kind": "reviewed_cardiovascular_baseline"}
                actual = {self.identity(item): item.presentation_ref for item in self.observations(data, brands)}
                self.assertEqual(len(actual), 52)
                self.assertEqual(actual, expected)

    def test_invalid_curated_source_coordinates_fail_instead_of_falling_back_to_index(self):
        cases = [("source_page", None), ("source_page", 40), ("source_page", True),
                 ("source_side", "center"), ("source_side", None),
                 ("source_line", 0), ("source_line", True), ("source_line", "20")]
        for field, value in cases:
            with self.subTest(field=field, value=value):
                record = curated_records()[0]
                record["presentations"][0][field] = value
                with self.assertRaisesRegex(ValueError, "coordenadas de origem"):
                    self.observations({**BASELINE, "records": [record]}, ["HEPTRIS"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
