"""Contrato editorial e relacional do lote Tudo com Tudo sobre isquemia
mesentérica aguda de origem cardioembólica.
"""

from __future__ import annotations

import json
from pathlib import Path

from app.services.clinical_rule_engine import evaluate_rules, validate_answers


ROOT = Path(__file__).resolve().parents[2]
DOCUMENTO = "isquemia-mesenterica-aguda-origem-cardioembolica-reconhecimento-e-primeira-hora"
FLUXOGRAMA = "fluxograma-suspeita-de-isquemia-mesenterica-aguda-primeira-hora"
CRONICA = "isquemia-mesenterica-cronica-diagnostico-e-tratamento-svs-2021"


def _por_slug(relative_path: str) -> dict[str, dict]:
    payload = json.loads((ROOT / relative_path).read_text(encoding="utf-8"))
    return {item["slug"]: item for item in payload}


def test_lote_ima_preserva_revisao_humana_e_atribuicao():
    manifests = {
        "triagem-sintomas/metadados.json": {"dor-abdominal-aguda-desproporcional-ao-exame"},
        "doencas/metadados.json": {"isquemia-mesenterica-aguda-cardioembolica"},
        "checklists/metadados.json": {"primeira-hora-na-suspeita-de-isquemia-mesenterica-aguda"},
        "material-paciente/metadados.json": {
            "dor-abdominal-subita-e-intensa-quando-procurar-a-emergencia"
        },
        "evidencias/metadados.json": {
            "ima-dor-abdominal-desproporcional-assumir-ima-ate-provar-o-contrario-wses-2022",
            "ima-angiotomografia-urgente-independente-da-funcao-renal-esvs-2025",
            "ima-revascularizacao-endovascular-primeira-linha-oclusao-arterial-esvs-2025",
        },
        "trilhas/metadados.json": {
            "trilha-suspeita-de-isquemia-mesenterica-aguda-do-reconhecimento-a-decisao-de-revascularizacao"
        },
    }

    for path, slugs in manifests.items():
        items = _por_slug(path)
        for slug in slugs:
            assert items[slug]["review_status"] == "pendente_revisao"
            assert items[slug]["fonte_producao"] == "claude"
            assert items[slug].get("published") is not True

    for name in (f"{DOCUMENTO}.md", f"{FLUXOGRAMA}.md"):
        text = (
            ROOT / "content/Aorta_e_doença_arterial_periférica" / name
        ).read_text(encoding="utf-8")
        assert "review_status: pendente_revisao" in text
        assert "fonte_producao: claude" in text


def test_lote_ima_fecha_relacoes_diretas_sem_fuzzy_matching():
    triagem = _por_slug("triagem-sintomas/metadados.json")[
        "dor-abdominal-aguda-desproporcional-ao-exame"
    ]
    doenca = _por_slug("doencas/metadados.json")["isquemia-mesenterica-aguda-cardioembolica"]
    checklist = _por_slug("checklists/metadados.json")[
        "primeira-hora-na-suspeita-de-isquemia-mesenterica-aguda"
    ]
    material = _por_slug("material-paciente/metadados.json")[
        "dor-abdominal-subita-e-intensa-quando-procurar-a-emergencia"
    ]
    evidencias = _por_slug("evidencias/metadados.json")
    trilha = _por_slug("trilhas/metadados.json")[
        "trilha-suspeita-de-isquemia-mesenterica-aguda-do-reconhecimento-a-decisao-de-revascularizacao"
    ]

    assert doenca["name"] == "Isquemia mesentérica aguda de origem cardioembólica"
    assert triagem["differentials"].count(doenca["name"]) == 1
    assert set(doenca["related_document_slugs"]) == {DOCUMENTO, FLUXOGRAMA}
    assert doenca["patient_material_slug"] == material["slug"]
    assert material["documento_slug"] == DOCUMENTO
    assert checklist["documento_origem"] == DOCUMENTO
    assert doenca["area"] == "cardiogeriatria"

    evidence_targets = {
        item["document_slug"]
        for item in evidencias.values()
        if item["slug"].startswith("ima-") and item.get("fonte_producao") == "claude"
    }
    assert evidence_targets == {DOCUMENTO, FLUXOGRAMA}

    etapas = {(step["item_type"], step["item_slug"]) for step in trilha["etapas"]}
    assert {
        ("documento", DOCUMENTO),
        ("documento", FLUXOGRAMA),
        ("checklist", checklist["slug"]),
        ("medicamento", "heparina-nao-fracionada"),
        ("documento", CRONICA),
    } <= etapas

    # A prevenção primária de embolia (anticoagulação crônica na FA) e a
    # investigação etiológica pós-evento não são etapas do reconhecimento
    # agudo; proximidade temática não vira aresta clínica.
    assert not any(
        step["item_type"] in {"calculadora", "caso_clinico"} for step in trilha["etapas"]
    )


def test_lote_ima_usa_recomendacoes_primarias_com_classe_e_nivel_exatos():
    evidencias = _por_slug("evidencias/metadados.json")
    dor = evidencias["ima-dor-abdominal-desproporcional-assumir-ima-ate-provar-o-contrario-wses-2022"]
    cta = evidencias["ima-angiotomografia-urgente-independente-da-funcao-renal-esvs-2025"]
    revasc = evidencias["ima-revascularizacao-endovascular-primeira-linha-oclusao-arterial-esvs-2025"]

    assert dor["recommendation_class"] == "Recomendação forte"
    assert dor["evidence_level"] == "1C (evidência de baixa qualidade)"
    assert "10.1186/s13017-022-00443-x" in dor["reference"]

    assert cta["recommendation_class"] == "Classe I"
    assert cta["evidence_level"] == "Nível B"
    assert "10.1016/j.ejvs.2025.06.010" in cta["reference"]

    assert revasc["recommendation_class"] == "Classe IIa"
    assert revasc["evidence_level"] == "Nível B"
    assert "10.1016/j.ejvs.2025.06.010" in revasc["reference"]


def test_triagem_ima_aciona_emergencia_por_peritonite_mesmo_sem_dor_confirmada():
    triagem = _por_slug("triagem-sintomas/metadados.json")[
        "dor-abdominal-aguda-desproporcional-ao-exame"
    ]
    answers = {
        "pain_disproportionate_to_exam": False,
        "cardioembolic_risk_factor": True,
        "peritonitis_signs": True,
        "critically_ill_on_vasopressor": False,
        "cta_requested": False,
    }

    result = evaluate_rules(
        questions=triagem["questions"],
        rules=triagem["rules"],
        answers=answers,
        base_ambulatory_flow=triagem["ambulatory_flow"],
        base_emergency_flow=triagem["emergency_flow"],
        context="ambulatorio",
    )

    assert result["risk"] == "emergencia"
    assert {
        "peritonite-cirurgia-sem-esperar-exame",
        "fator-de-risco-cardioembolico",
        "exame-nao-solicitado",
    } <= set(result["matched_rules"])
    assert result["invalid_fields"] == []
    assert validate_answers(triagem["questions"], answers) == ([], [])
