from pathlib import Path
import json

from app.services.knowledge_relation_policy import validar_relacao_clinica

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = [
    "tudo_com_tudo_exact_61_100_curated_20260907.json",
    "tudo_com_tudo_exact_101_130_curated_20260907.json",
    "tudo_com_tudo_exact_131_160_curated_20260907.json",
    "tudo_com_tudo_exact_161_200_curated_20260907.json",
    "tudo_com_tudo_exact_201_250_curated_20260907.json",
    "tudo_com_tudo_exact_251_500_curated_20260907.json",
]


def _fixture_rows():
    rows = []
    for name in FIXTURES:
        rows.extend(json.loads((ROOT / "scripts/fixtures" / name).read_text(encoding="utf-8")))
    return rows


def _manifest():
    return json.loads((ROOT / "doencas/relacoes-explicitas.json").read_text(encoding="utf-8"))

def test_coorte_paralela_61_500_tem_dimensao_e_chaves_unicas():
    rows = _fixture_rows()
    keys = {
        (x["source_disease_slug"], x["target_type"], x["target_slug"], x["relation_type"])
        for x in rows
    }
    assert len(rows) == 2199
    assert len(keys) == 2199
    assert len({x["source_disease_slug"] for x in rows}) == 12


def test_coorte_paralela_61_500_esta_integralmente_no_manifesto():
    rows = _fixture_rows()
    manifest = _manifest()
    indexed = {
        (x["source_disease_slug"], x["target_type"], x["target_slug"], x["relation_type"]): x
        for x in manifest
    }
    for row in rows:
        key = (row["source_disease_slug"], row["target_type"], row["target_slug"], row["relation_type"])
        assert key in indexed
        relation = indexed[key]
        assert relation["review_status"] == "revisado"
        assert relation["provenance_type"] == "editorial"
        assert relation["confidence"] == "explicit"

def test_politica_clinica_aceita_toda_a_coorte_paralela():
    for row in _fixture_rows():
        validar_relacao_clinica(
            source_type="doenca",
            relation_type=row["relation_type"],
            target_type=row["target_type"],
            relevance_score=1.0,
            provenance_type="editorial",
            confidence="explicit",
            review_status="revisado",
            evidence_source="auditoria-paralela-61-500",
            extra={"review_note": "identidade clínica exata revisada"},
        )


def test_civ_adquirida_e_fallot_nao_sao_promovidos_para_civ_congenita():
    manifest = _manifest()
    targets = {
        (x["target_type"], x["target_slug"])
        for x in manifest
        if x["source_disease_slug"] == "comunicacao-interventricular"
    }
    assert ("documento", "comunicacao-interventricular-pos-infarto-diagnostico-e-decisao") not in targets
    assert ("galeria", "atresia-pulmonar-com-civ-tetralogia-de-fallot-extrema-diagrama-cdc") not in targets
