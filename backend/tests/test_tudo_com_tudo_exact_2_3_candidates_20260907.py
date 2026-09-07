from pathlib import Path
import json

from app.services.knowledge_relation_policy import validar_relacao_clinica

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "scripts/fixtures/tudo_com_tudo_exact_2_3_candidates_20260907.json"
RELATIONS = ROOT / "doencas/relacoes-explicitas.json"


def _fixture():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _relations():
    return json.loads(RELATIONS.read_text(encoding="utf-8"))


def test_fixture_exact_2_3_tem_38_relacoes_em_16_doencas():
    rows = _fixture()
    assert len(rows) == 38
    assert len({row["source_disease_slug"] for row in rows}) == 16
    assert all(row["target_type"] and row["target_slug"] for row in rows)


def test_fixture_exact_2_3_esta_persistida_com_revisao_explicita():
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
        assert relation["relevance_score"] == 1.0


def test_fixture_exact_2_3_respeita_politica_clinica():
    for item in _fixture():
        validar_relacao_clinica(
            source_type="doenca", relation_type=item["relation_type"],
            target_type=item["target_type"], relevance_score=1.0,
            provenance_type="editorial", confidence="explicit",
            review_status="revisado",
            evidence_source="scripts/fixtures/tudo_com_tudo_exact_2_3_candidates_20260907.json",
            extra={"review_note": "coorte exact 2-3 revisada"},
        )


def test_manifesto_nao_tem_arestas_duplicadas():
    relations = _relations()
    keys = [
        (
            row["source_disease_slug"], row["target_type"],
            row["target_slug"], row["relation_type"],
        )
        for row in relations
    ]
    assert len(keys) == len(set(keys))
