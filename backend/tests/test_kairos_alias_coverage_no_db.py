"""Run directly with Python: genuine Káiros matcher, no app/DB/conftest.

Uses only the frozen, reviewed local catalogue and operational issue. This is
identity/price projection coverage, not a prescription, availability check or
clinical equivalence assessment.
"""
import copy
import hashlib
import json
from pathlib import Path
import runpy
from types import SimpleNamespace
import unittest


ROOT = Path(__file__).resolve().parents[2]
LOADER = Path(__file__).with_name("test_kairos_matching_no_db.py")


class KairosAliasCoverageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.provider = runpy.run_path(str(LOADER))["load_provider"]()
        cls.snapshot = cls.provider["load_snapshot"]()
        cls.catalogue = {
            item["slug"]: SimpleNamespace(**{"brand_names": [], **item})
            for item in json.loads((ROOT / "medicamentos/metadados.json").read_text())
        }

    def records(self, drug, snapshot=None):
        return self.provider["records_for_drug"](
            drug, snapshot=self.snapshot if snapshot is None else snapshot,
        )[1]

    def options(self, slug):
        return self.provider["prescription_options_for"](
            self.catalogue[slug], snapshot=self.snapshot,
        )["opcoes"]

    def test_every_alias_has_a_literal_reviewed_catalogue_name(self):
        normalize = self.provider["_normalize"]
        names = {normalize(drug.generic_name) for drug in self.catalogue.values()}
        for editorial, source in self.provider["SUBSTANCE_NAME_ALIASES"]:
            with self.subTest(editorial=editorial):
                self.assertIn(normalize(editorial), names)
                self.assertEqual(
                    self.provider["_substance_identity"](editorial),
                    self.provider["_substance_identity"](source),
                )

    def test_six_additional_catalogue_entries_have_literal_pmc_options(self):
        for slug, count in {
            "acido-acetilsalicilico-aas": 2,
            "epinefrina-adrenalina": 1,
            "sildenafila-citrato": 4,
            "paracetamol": 10,
            "azitromicina": 16,
            "salbutamol": 4,
        }.items():
            with self.subTest(slug=slug):
                self.assertEqual(len(self.options(slug)), count)

    def test_reviewed_salts_expand_brands_without_merging_packs(self):
        for slug, count in {
            "atorvastatina-calcica": 12,
            "clopidogrel-bissulfato": 3,
            "enalapril-maleato": 4,
            "losartana-potassica": 6,
            "rosuvastatina-calcica": 23,
            "losartana-potassica-hidroclorotiazida": 5,
            "rosuvastatina-calcica-ezetimiba": 6,
        }.items():
            with self.subTest(slug=slug):
                self.assertEqual(len(self.options(slug)), count)
        # Same brand/laboratory, three genuinely different strengths: retain
        # literal source descriptions, not an invented interchangeable pack.
        cozaar = [p["apresentacao"] for p in self.options("losartana-potassica")
                  if p["produto"] == "COZAAR"]
        self.assertEqual(cozaar, [
            "50mg Comp. cx c/1 bl x 15", "50mg Comp. cx c/2 bl x 15",
            "100mg Comp. cx c/2 bl x 15",
        ])

    def test_three_new_pf_only_matches_never_become_consumer_prices(self):
        for slug, product in {
            "milrinona": "PRIMACOR IV",
            "nitroglicerina-trinitrato-de-glicerila": "TRIDIL",
            "noradrenalina-norepinefrina": "UNIANORA",
        }.items():
            with self.subTest(slug=slug):
                self.assertEqual([r["product"] for r in self.records(self.catalogue[slug])], [product])
                self.assertEqual(self.options(slug), [])

    def test_qualifiers_are_not_erased_and_brands_are_not_prefix_matched(self):
        match = self.provider["_record_matches"]
        # Synthetic identity negatives, never clinical/source price fixtures.
        for name, brands, product, substance in [
            ("Minoxidil (via oral)", [], "MINOXIDIL TÓPICO", "MINOXIDIL"),
            ("Lidocaína (cloridrato de lidocaína, sem vasoconstritor, uso intravenoso)",
             ["Xylestesin"], "XYLESTESIN 10%", "LIDOCAÍNA"),
            ("Insulina humana isofana (NPH — Neutral Protamine Hagedorn)",
             ["Humulin N"], "INSULINA HUMANA HUMULIN", "INSULINA"),
            ("Metoprolol (succinato, liberação prolongada)", [], "TESTE", "METOPROLOL"),
            ("Metoprolol (tartarato)", [], "TESTE", "METOPROLOL"),
            ("Atorvastatina (cálcica) 10 mg", [], "TESTE", "ATORVASTATINA"),
            ("Paracetamol (acetaminofeno, via intravenosa)", [], "TESTE", "PARACETAMOL"),
        ]:
            with self.subTest(name=name):
                self.assertFalse(match(
                    SimpleNamespace(generic_name=name, brand_names=brands),
                    {"product": product, "substance": substance},
                ))
        for slug in ("minoxidil", "lidocaina-cloridrato", "metoprolol", "insulina-humana-nph"):
            self.assertEqual(self.records(self.catalogue[slug]), [])

    def test_aliases_preserve_every_component_and_unreviewed_qualifier(self):
        identity = self.provider["_substance_identity"]
        self.assertEqual(
            identity("Losartana potássica + Hidroclorotiazida"),
            identity("HIDROCLOROTIAZIDA + LOSARTANA"),
        )
        self.assertEqual(
            identity("Rosuvastatina (cálcica)/Ezetimiba"),
            identity("EZETIMIBA + ROSUVASTATINA"),
        )
        for combined, single in [
            ("Losartana potássica + Hidroclorotiazida", "Losartana"),
            ("Rosuvastatina (cálcica) + Ezetimiba", "Rosuvastatina"),
            ("Clopidogrel (bissulfato) + Ácido Acetilsalicílico (AAS)", "Clopidogrel"),
            ("Paracetamol (acetaminofeno) + Cafeína", "Paracetamol"),
            ("Epinefrina + adrenalina", "Epinefrina"),
            ("Losartana (potássica, uso experimental)", "Losartana"),
        ]:
            with self.subTest(combined=combined):
                self.assertNotEqual(identity(combined), identity(single))
        for slug in ("acido-bempedoico", "telmisartana",
                     "anlodipino-besilato-indapamida-perindopril-argininaerbumina"):
            self.assertEqual(self.records(self.catalogue[slug]), [])

    def test_index_and_final_match_agree_for_all_206_catalogue_entries(self):
        # Exercise the original plain-dict path as well as the production index.
        plain = dict(self.snapshot)
        for slug, drug in self.catalogue.items():
            with self.subTest(slug=slug):
                self.assertEqual(self.records(drug), self.records(drug, plain))

    def test_projection_keeps_source_prices_pages_and_snapshot_unchanged(self):
        original = copy.deepcopy(dict(self.snapshot))
        covered = factory_only = unmatched = 0
        for slug, drug in self.catalogue.items():
            records = self.records(drug)
            options = self.options(slug)
            covered += bool(options)
            factory_only += bool(records) and not options
            unmatched += not records
            expected = []
            for record in records:
                for presentation in record["presentations"]:
                    pmcs = {
                        region: float(self.provider["_decimal_br"](presentation[field]))
                        for field, (kind, region) in self.provider["PRICE_FIELDS"].items()
                        if kind == "pmc" and presentation.get(field)
                    }
                    if pmcs:
                        expected.append((record["product"], record["laboratory"],
                                         presentation["presentation"], record["page"], pmcs))
            self.assertEqual(len(options), len(expected))
            for option, (product, laboratory, presentation, page, pmcs) in zip(options, expected):
                self.assertEqual((option["produto"], option["laboratorio"], option["apresentacao"],
                                  option["pagina_fonte"], option["precos_por_icms"]),
                                 (product, laboratory, presentation, page, pmcs))
                self.assertEqual(option["preco_minimo"], min(pmcs.values()))
                self.assertEqual(option["preco_maximo"], max(pmcs.values()))
        self.assertEqual((covered, factory_only, unmatched), (90, 11, 105))
        self.assertEqual(dict(self.snapshot), original)
        self.assertEqual(hashlib.sha256(self.provider["SNAPSHOT_PATH"].read_bytes()).hexdigest(),
                         "ff070fdf46b257253d9e618de56bfb63f3e2b33333bab332e734537d05ec8363")


if __name__ == "__main__":
    unittest.main()
