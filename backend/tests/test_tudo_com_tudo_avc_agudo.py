"""Contrato editorial e relacional do lote Tudo com Tudo sobre AVC agudo."""

from __future__ import annotations

import json
from pathlib import Path

from app.services.clinical_rule_engine import evaluate_rules, validate_answers
from app.services.carregar_doencas_especializadas import AREAS as DISEASE_AREAS
from app.services.carregar_emergencia import _documento_pode_ser_referenciado


ROOT = Path(__file__).resolve().parents[2]
DOCUMENTO = "deficit-neurologico-focal-subito-reconhecimento-e-primeira-hora-do-avc"
FLUXOGRAMA = "fluxograma-suspeita-de-avc-agudo-primeira-hora"


def _por_slug(relative_path: str) -> dict[str, dict]:
    payload = json.loads((ROOT / relative_path).read_text(encoding="utf-8"))
    return {item["slug"]: item for item in payload}


def test_lote_avc_esta_revisado_sem_publicacao_antecipada():
    manifests = {
        "triagem-sintomas/metadados.json": {"deficit-neurologico-focal-subito"},
        "doencas/metadados.json": {"acidente-vascular-cerebral-agudo"},
        "emergencia/metadados.json": {"suspeita-de-avc-agudo"},
        "checklists/metadados.json": {"primeira-hora-na-suspeita-de-avc-agudo"},
        "material-paciente/metadados.json": {"sinais-de-avc-como-agir-sem-perder-tempo"},
        "evidencias/metadados.json": {
            "primeiros-socorros-suspeita-avc-acionar-emergencia-imediatamente-aha-2024",
            "primeiros-socorros-avc-usar-fast-ou-cincinnati-aha-2024",
            "primeiros-socorros-avc-glicemia-sem-atrasar-emergencia-aha-2024",
        },
        "trilhas/metadados.json": {
            "trilha-suspeita-de-avc-da-identificacao-a-decisao-de-reperfusao"
        },
    }

    for path, slugs in manifests.items():
        items = _por_slug(path)
        for slug in slugs:
            assert items[slug]["review_status"] == "revisado"
            assert items[slug]["fonte_producao"] == "chatgpt"
            assert items[slug].get("published") is not True

    for name in (f"{DOCUMENTO}.md", f"{FLUXOGRAMA}.md"):
        text = (ROOT / "content/Geral" / name).read_text(encoding="utf-8")
        assert "review_status: revisado" in text
        assert "fonte_producao: chatgpt" in text

    assert "geral" in DISEASE_AREAS


def test_loader_de_emergencia_aceita_par_pendente_sem_relaxar_publicacao():
    # Documento revisado pode sustentar protocolo revisado mesmo antes do flag
    # de publicação persistido; a reconciliação é quem controla published.
    assert _documento_pode_ser_referenciado(
        published=False,
        document_status="revisado",
        protocol_status="revisado",
    )
    # Par ainda pendente pode existir no corpus sem vazar para publicação.
    assert _documento_pode_ser_referenciado(
        published=False,
        document_status="pendente_revisao",
        protocol_status="pendente_revisao",
    )
    # Protocolo já revisado não pode depender de documento ainda pendente.
    assert not _documento_pode_ser_referenciado(
        published=False,
        document_status="pendente_revisao",
        protocol_status="revisado",
    )


def test_lote_avc_fecha_relacoes_diretas_sem_fuzzy_matching():
    triagem = _por_slug("triagem-sintomas/metadados.json")[
        "deficit-neurologico-focal-subito"
    ]
    doenca = _por_slug("doencas/metadados.json")["acidente-vascular-cerebral-agudo"]
    emergencia = _por_slug("emergencia/metadados.json")["suspeita-de-avc-agudo"]
    checklist = _por_slug("checklists/metadados.json")[
        "primeira-hora-na-suspeita-de-avc-agudo"
    ]
    material = _por_slug("material-paciente/metadados.json")[
        "sinais-de-avc-como-agir-sem-perder-tempo"
    ]
    evidencias = _por_slug("evidencias/metadados.json")
    trilha = _por_slug("trilhas/metadados.json")[
        "trilha-suspeita-de-avc-da-identificacao-a-decisao-de-reperfusao"
    ]

    assert doenca["name"] == "Acidente vascular cerebral agudo"
    assert triagem["differentials"].count(doenca["name"]) == 1
    assert set(doenca["related_document_slugs"]) == {DOCUMENTO, FLUXOGRAMA}
    assert doenca["patient_material_slug"] == material["slug"]
    assert material["documento_slug"] == DOCUMENTO
    assert checklist["documento_origem"] == DOCUMENTO
    assert emergencia["documento_slug"] == DOCUMENTO
    assert emergencia["fluxograma_slug"] == FLUXOGRAMA

    evidence_targets = {
        item["document_slug"]
        for item in evidencias.values()
        if item.get("fonte_producao") == "chatgpt"
        and item["slug"].startswith("primeiros-socorros-")
    }
    assert evidence_targets == {DOCUMENTO, FLUXOGRAMA}

    etapas = {(step["item_type"], step["item_slug"]) for step in trilha["etapas"]}
    assert {
        ("documento", DOCUMENTO),
        ("documento", FLUXOGRAMA),
        ("estudo", "ecass-iii-alteplase-janela-estendida-avc-isquemico"),
        ("medicamento", "alteplase"),
        ("medicamento", "tenecteplase"),
        ("checklist", checklist["slug"]),
    } <= etapas

    # Escores de risco embólico e casos de prevenção secundária não são etapas
    # da triagem aguda; proximidade temática não vira aresta clínica.
    assert not any(step["item_type"] in {"calculadora", "caso_clinico"} for step in trilha["etapas"])
    assert emergencia["relacionados"] == []


def test_lote_avc_usa_recomendacoes_primarias_com_classe_e_nivel_exatos():
    evidencias = _por_slug("evidencias/metadados.json")
    assert (
        evidencias[
            "primeiros-socorros-suspeita-avc-acionar-emergencia-imediatamente-aha-2024"
        ]["recommendation_class"],
        evidencias[
            "primeiros-socorros-suspeita-avc-acionar-emergencia-imediatamente-aha-2024"
        ]["evidence_level"],
    ) == ("I", "B-NR")
    assert (
        evidencias["primeiros-socorros-avc-usar-fast-ou-cincinnati-aha-2024"][
            "recommendation_class"
        ],
        evidencias["primeiros-socorros-avc-usar-fast-ou-cincinnati-aha-2024"][
            "evidence_level"
        ],
    ) == ("I", "B-NR")
    assert (
        evidencias["primeiros-socorros-avc-glicemia-sem-atrasar-emergencia-aha-2024"][
            "recommendation_class"
        ],
        evidencias["primeiros-socorros-avc-glicemia-sem-atrasar-emergencia-aha-2024"][
            "evidence_level"
        ],
    ) == ("IIa", "C-EO")
    assert all(
        "10.1161/CIR.0000000000001281" in evidencias[slug]["reference"]
        for slug in (
            "primeiros-socorros-suspeita-avc-acionar-emergencia-imediatamente-aha-2024",
            "primeiros-socorros-avc-usar-fast-ou-cincinnati-aha-2024",
            "primeiros-socorros-avc-glicemia-sem-atrasar-emergencia-aha-2024",
        )
    )


def test_fluxograma_nao_exige_confirmacao_radiologica_precoce_de_isquemia():
    protocolo = (ROOT / "content/Geral" / f"{DOCUMENTO}.md").read_text(encoding="utf-8")
    fluxograma = (ROOT / "content/Geral" / f"{FLUXOGRAMA}.md").read_text(encoding="utf-8")

    assert "apresentações posteriores" not in protocolo
    assert "circulação posterior" in protocolo
    assert "AVC isquêmico confirmado" not in fluxograma
    assert "hipótese clínica" in fluxograma
    assert "não equivale a exigir confirmação radiológica" in fluxograma


def test_triagem_avc_aciona_emergencia_mesmo_se_sintomas_melhoraram():
    triagem = _por_slug("triagem-sintomas/metadados.json")[
        "deficit-neurologico-focal-subito"
    ]
    answers = {
        "new_face_arm_speech_deficit": True,
        "other_sudden_focal_deficit": False,
        "symptoms_resolved": True,
        "last_known_well_known": True,
        "glucose_low": False,
        "anticoagulant_or_bleeding": True,
        "emergency_activated": False,
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
        "fast-positivo",
        "ait-nao-e-alta",
        "anticoagulante-ou-sangramento",
        "socorro-nao-acionado",
    } <= set(result["matched_rules"])
    assert result["invalid_fields"] == []
    assert validate_answers(triagem["questions"], answers) == ([], [])
