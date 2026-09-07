from pathlib import Path
import json

from app.services.disease_manifest import load_disease_records
from app.services.knowledge_relation_policy import validar_relacao_clinica

ROOT = Path(__file__).resolve().parents[2]
DOENCAS = ROOT / "doencas/metadados.json"
RELACOES = ROOT / "doencas/relacoes-explicitas.json"

TERATOMA_DOCS = {
    "tumores-cardiacos-fetais-rabdomioma-e-diagnostico-diferencial-de-massa-cardiaca-intrautero",
    "massas-cardiacas-e-pericardicas-caracterizacao-por-tc-e-ressonancia-sbc-2024",
}
CONTRASTE_EVIDENCIAS = {
    "scc25-t32-contraste-isosmolar-ou-hiposmolar-na-profilaxia-eletiva",
    "scc25-t33-hidrocortisona-500mg-iv-na-emergencia",
    "scc25-t33-difenidramina-na-emergencia",
    "scc25-t33-fexofenadina-na-emergencia",
}
def test_teratoma_fetal_nao_fica_restrito_a_exames_sinteticos():
    diseases = {item["slug"]: item for item in load_disease_records(DOENCAS)}
    item = diseases["teratoma-cardiaco-pericardico-fetal"]
    assert TERATOMA_DOCS <= set(item.get("related_document_slugs") or [])
    assert item.get("patient_material_slug") == "tumores-cardiacos-fetais"

    assert (ROOT / "content/Cardiologia_pediátrica/tumores-cardiacos-fetais-rabdomioma-e-diagnostico-diferencial-de-massa-cardiaca-intrautero.md").exists()
    assert (ROOT / "content/Cardiomiopatias/massas-cardiacas-e-pericardicas-caracterizacao-por-tc-e-ressonancia-sbc-2024.md").exists()
    materials = json.loads((ROOT / "material-paciente/metadados.json").read_text(encoding="utf-8"))
    assert "tumores-cardiacos-fetais" in {x["slug"] for x in materials}


def test_reacao_a_contraste_recebe_evidencias_especificas_curadas():
    relations = json.loads(RELACOES.read_text(encoding="utf-8"))
    selected = [x for x in relations if x["source_disease_slug"] == "reacao-anafilactoide-a-contraste-iodado" and x["target_type"] == "evidencia"]
    assert CONTRASTE_EVIDENCIAS == {x["target_slug"] for x in selected}
    assert all(x["relation_type"] == "supported_by" for x in selected)
    assert all(x["review_status"] == "revisado" for x in selected)
    assert all(x["provenance_type"] == "editorial" and x["confidence"] == "explicit" for x in selected)

    evidence_slugs = {
        x["slug"] for x in json.loads((ROOT / "evidencias/metadados.json").read_text(encoding="utf-8"))
    }
    assert CONTRASTE_EVIDENCIAS <= evidence_slugs


def test_politica_clinica_aceita_doenca_sustentada_por_evidencia_curada():
    validar_relacao_clinica(
        source_type="doenca", relation_type="supported_by", target_type="evidencia",
        relevance_score=1.0, provenance_type="editorial", confidence="explicit",
        review_status="revisado", evidence_source="doencas/relacoes-explicitas.json#sentinela",
        extra={"review_note": "sentinela de política clínica"},
    )

EXACT_LOW_DENSITY_LINKS = {
    ("beriberi-cardiaco", "caso_clinico", "beriberi-cardiaco-pos-cirurgia-bariatrica-ic-alto-debito-reversivel-com-tiamina", "used_in_case"),
    ("distrofia-miotonica-tipo-1", "caso_clinico", "distrofia-miotonica-tipo-1-conducao-cardiaca-estudo-eletrofisiologico", "used_in_case"),
    ("fibroelastoma-papilar-cardiaco", "checklist", "fibroelastoma-papilar-cardiaco-decisao-ressecao-vs-vigilancia", "associated_with"),
}


def test_candidatos_exatos_de_baixa_densidade_nao_ficam_desconectados():
    relations = json.loads(RELACOES.read_text(encoding="utf-8"))
    actual = {
        (x["source_disease_slug"], x["target_type"], x["target_slug"], x["relation_type"])
        for x in relations
    }
    assert EXACT_LOW_DENSITY_LINKS <= actual

    cases = json.loads((ROOT / "casos-clinicos/metadados.json").read_text(encoding="utf-8"))
    checklists = json.loads((ROOT / "checklists/metadados.json").read_text(encoding="utf-8"))
    case_slugs = {x["slug"] for x in cases}
    checklist_slugs = {x["slug"] for x in checklists}
    assert {x[2] for x in EXACT_LOW_DENSITY_LINKS if x[1] == "caso_clinico"} <= case_slugs
    assert {x[2] for x in EXACT_LOW_DENSITY_LINKS if x[1] == "checklist"} <= checklist_slugs


def test_coorte_exact_single_curada_esta_inteira_no_manifesto():
    fixture = json.loads(
        (ROOT / "scripts/fixtures/tudo_com_tudo_exact_single_candidates_20260907.json").read_text(encoding="utf-8")
    )
    assert len(fixture) == 31
    relations = json.loads(RELACOES.read_text(encoding="utf-8"))
    by_key = {
        (x["source_disease_slug"], x["target_type"], x["target_slug"]): x
        for x in relations
    }
    for expected in fixture:
        key = (
            expected["source_disease_slug"], expected["target_type"], expected["target_slug"],
        )
        assert key in by_key
        relation = by_key[key]
        assert relation["relation_type"] == "associated_with"
        assert relation["review_status"] == "revisado"
        assert relation["provenance_type"] == "editorial"
        assert relation["confidence"] == "explicit"
        assert relation["relevance_score"] == 1.0


def test_coorte_exact_single_respeita_matriz_clinica_tipificada():
    fixture = json.loads(
        (ROOT / "scripts/fixtures/tudo_com_tudo_exact_single_candidates_20260907.json").read_text(encoding="utf-8")
    )
    for item in fixture:
        validar_relacao_clinica(
            source_type="doenca",
            relation_type="associated_with",
            target_type=item["target_type"],
            relevance_score=1.0,
            provenance_type="editorial",
            confidence="explicit",
            review_status="revisado",
            evidence_source="doencas/relacoes-explicitas.json#exact-single-sentinela",
            extra={"review_note": "coorte exact-single revisada"},
        )
