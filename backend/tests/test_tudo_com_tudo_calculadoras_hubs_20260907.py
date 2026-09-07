from pathlib import Path
import json

from app.services.knowledge_relation_policy import validar_relacao_clinica

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "scripts/fixtures/tudo_com_tudo_calculadoras_hubs_20260907.json"
MANIFEST = ROOT / "doencas/relacoes-explicitas.json"
EXPECTED = {
    "fibrilacao-atrial": {"cha2ds2-vasc", "has-bled", "orbit"},
    "sindrome-coronariana-aguda": {"grace", "crusade", "timi-stemi", "timi-ua-nstemi"},
    "embolia-pulmonar-aguda": {"wells-tep", "geneva-revisado", "geneva-simplificado", "pesi", "spesi"},
    "tromboembolismo-venoso": {"wells-tvp"},
}


def _rows():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_calculadoras_criticas_estao_mapeadas_por_hub():
    rows = _rows()
    assert len(rows) == 13
    for disease, slugs in EXPECTED.items():
        found = {x["target_slug"] for x in rows if x["source_disease_slug"] == disease}
        assert found == slugs

def test_calculadoras_criticas_estao_persistidas_com_revisao_explicita():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    indexed = {
        (x["source_disease_slug"], x["target_slug"]): x
        for x in manifest
        if x["target_type"] == "calculadora"
    }
    for row in _rows():
        relation = indexed[(row["source_disease_slug"], row["target_slug"])]
        assert relation["relation_type"] == "associated_with"
        assert relation["review_status"] == "revisado"
        assert relation["provenance_type"] == "editorial"
        assert relation["confidence"] == "explicit"


def test_politica_clinica_aceita_os_13_vinculos_de_calculadora():
    for row in _rows():
        validar_relacao_clinica(
            source_type="doenca", relation_type="associated_with", target_type="calculadora",
            relevance_score=1.0, provenance_type="editorial", confidence="explicit",
            review_status="revisado", evidence_source="auditoria-calculadoras-hubs-20260907",
            extra={"review_note": "calculadora central do hub clínico"},
        )
