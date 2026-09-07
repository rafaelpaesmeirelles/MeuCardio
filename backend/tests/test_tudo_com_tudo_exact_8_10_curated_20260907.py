from pathlib import Path
import json

from app.services.knowledge_relation_policy import validar_relacao_clinica

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "scripts/fixtures/tudo_com_tudo_exact_8_10_curated_20260907.json"
RELATIONS = ROOT / "doencas/relacoes-explicitas.json"
EXCLUDED = {
    ("comunicacao-interventricular", "documento", "comunicacao-interventricular-pos-infarto-diagnostico-e-decisao"),
    ("comunicacao-interventricular", "galeria", "atresia-pulmonar-com-civ-tetralogia-de-fallot-extrema-diagrama-cdc"),
}


def _fixture():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _relations():
    return json.loads(RELATIONS.read_text(encoding="utf-8"))


def test_fixture_exact_8_10_promove_16_e_exclui_2_limites():
    rows = _fixture()
    assert len(rows) == 16
    assert len({row["source_disease_slug"] for row in rows}) == 2
    promoted = {(x["source_disease_slug"], x["target_type"], x["target_slug"]) for x in rows}
    assert promoted.isdisjoint(EXCLUDED)


def test_fixture_exact_8_10_esta_persistida_e_revisada():
    relations = _relations()
    index = {
        (row["source_disease_slug"], row["target_type"], row["target_slug"], row["relation_type"]): row
        for row in relations
    }
    for item in _fixture():
        key = (
            item["source_disease_slug"], item["target_type"],
            item["target_slug"], item["relation_type"],
        )
        assert key in index
        relation = index[key]
        assert relation["review_status"] == "revisado"
        assert relation["provenance_type"] == "editorial"
        assert relation["confidence"] == "explicit"


def test_candidatos_limite_nao_foram_promovidos():
    relations = _relations()
    relation_keys = {
        (row["source_disease_slug"], row["target_type"], row["target_slug"])
        for row in relations
        if row.get("review_status") != "rejeitado"
    }
    assert relation_keys.isdisjoint(EXCLUDED)


def test_fixture_exact_8_10_respeita_politica_clinica():
    for item in _fixture():
        validar_relacao_clinica(
            source_type="doenca", relation_type=item["relation_type"],
            target_type=item["target_type"], relevance_score=1.0,
            provenance_type="editorial", confidence="explicit",
            review_status="revisado",
            evidence_source="scripts/fixtures/tudo_com_tudo_exact_8_10_curated_20260907.json",
            extra={"review_note": "coorte exact 8-10 curada"},
        )
