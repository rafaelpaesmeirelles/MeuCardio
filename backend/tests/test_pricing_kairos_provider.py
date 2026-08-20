from types import SimpleNamespace

from app.services.pricing.kairos_provider import (
    KairosProvider,
    load_snapshot,
    prescription_options_for,
    records_for_drug,
)


class FakeDb:
    def __init__(self, drug):
        self.drug = drug

    def get(self, _model, drug_id):
        return self.drug if self.drug.id == drug_id else None


def drug(drug_id: int, generic_name: str, brands=None):
    return SimpleNamespace(id=drug_id, generic_name=generic_name, brand_names=brands or [])


def test_snapshot_is_explicitly_licensed_market_intelligence():
    snapshot = load_snapshot()
    assert snapshot["issue"] == 453
    assert snapshot["competence"] == "2026-08"
    assert snapshot["licensed_use"] is True
    assert snapshot["source_type"] == "market_intelligence"
    assert snapshot["regulatory_authority"] == "CMED/ANVISA"


def test_matches_sacubitril_valsartana_without_confusing_source_layer():
    d = drug(1, "Sacubitril/Valsartana", ["Neparvis"])
    snapshot, records = records_for_drug(d)
    assert snapshot["issue"] == 453
    assert [record["product"] for record in records] == ["NEPARVIS"]

    observations = KairosProvider(FakeDb(d)).observations_for(d.id)
    assert observations
    assert {item.source for item in observations} == {"kairos"}
    assert {item.source_type for item in observations} == {"market_intelligence"}
    assert any(item.price_type == "pmc" and item.region == "ICMS 20%" and str(item.price) == "158.67" for item in observations)
    assert all(item.confidence == "high" for item in observations)
    assert all(item.metadata["licensed_use"] is True for item in observations)


def test_generic_substance_match_is_conservative_and_exact_by_tokens():
    d = drug(2, "Espironolactona")
    _, records = records_for_drug(d)
    assert [record["product"] for record in records] == ["ALDACTONE"]

    unrelated = drug(3, "Amoxicilina")
    _, records = records_for_drug(unrelated)
    assert records == []


def test_brand_name_can_match_when_publication_substance_label_is_not_canonical():
    d = drug(4, "Perindopril + Anlodipino", ["Acertanlo"])
    _, records = records_for_drug(d)
    assert [record["product"] for record in records] == ["ACERTANLO"]


def test_hospital_only_rows_without_pmc_do_not_generate_fabricated_values():
    d = drug(5, "Fondaparinux", ["Arixtra"])
    observations = KairosProvider(FakeDb(d)).observations_for(d.id)
    assert observations
    assert all(item.price > 0 for item in observations)
    # Every observation comes from a literal cell present in the licensed snapshot.
    assert not any(item.metadata.get("estimated") for item in observations)


def test_prescription_options_keep_kairos_separate_and_expose_literal_pmc_range():
    d = drug(6, "Sacubitril/Valsartana", ["Neparvis"])

    result = prescription_options_for(d)

    assert result["fonte"] == "K@iros"
    assert result["tipo_fonte"] == "inteligencia_de_mercado"
    assert result["edicao"] == 453
    assert result["competencia"] == "2026-08"
    assert result["opcoes"]
    assert all(option["preco_minimo"] <= option["preco_maximo"] for option in result["opcoes"])
    assert all(option["precos_por_icms"] for option in result["opcoes"])
    assert not any("uf" in option for option in result["opcoes"])
