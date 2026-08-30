"""Contrato do registro NOVO de Triagem de Sintomas
"complicacao-local-pos-cateterismo-procedimento-vascular" (área geral/
cardiogeriatria), criado em 29/08/2026, adicionado ao FINAL de
triagem-sintomas/metadados.json.

Fontes usadas (as três mapeadas na missão, todas já `revisado` no corpus, e
uma quarta corroborante sem PMID próprio):
- content/Terapia_intensiva/oclusao-de-arteria-radial-pos-cateterismo-hemostasia-patente-e-tecnica-de-barbeau.md
  (PMIDs 18726956, 27712733, 26811162)
- content/Terapia_intensiva/acesso-vascular-large-bore-em-tmcs-prevencao-de-sangramento-isquemia-e-fechamento.md
  (sangramento retroperitoneal e isquemia de membro em acesso femoral)
- content/Dispositivos/marcapasso-temporario-transvenoso-indicacao-acesso-e-complicacoes-na-emergencia.md
  (PMIDs 30543806, 42132883)
- content/Terapia_intensiva/complicacoes-da-bomba-microaxial-hemolise-succao-sangramento-isquemia-e-anticoagulacao.md
  (seções 7-8, corrobora isquemia de membro/sangramento retroperitoneal)

Os 5 PMIDs centrais (18726956, 27712733, 26811162, 30543806, 42132883)
foram reconferidos via NCBI E-utilities (esummary) em 29/08/2026 antes de
persistir no `source_refs` deste registro.

Nota sobre review_status: este registro permanece "pendente_revisao" — não
foi revisado por humano. Por isso
test_canonical_content_review_status.py::
test_manifestos_canonicos_so_tem_pendencias_explicitamente_aprovadas_para_rc
FALHA para este slug (comportamento esperado e documentado no review_note
do próprio registro e em
docs/novo-sintoma-complicacao-local-pos-cateterismo-procedimento-vascular-2026-08-29.md
— não é bug e não deve ser contornado). Diferente do padrão de doenças, a
allowlist `PENDENTES_LOTES_TUDO_COM_TUDO` daquele teste não é reaproveitada
por nenhum outro teste de triagem-sintomas, então adicionar este slug a ela
não teria efeito prático — por isso NÃO foi adicionada.

Risco de colisão: outros agentes podem estar adicionando registros ao
mesmo triagem-sintomas/metadados.json em branches paralelas simultâneas.
Este registro foi adicionado ao FINAL do array JSON.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlparse

from app.services.clinical_rule_engine import (
    evaluate_rules,
    validate_question_definitions,
    validate_rule_definitions,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
TRIAGE_PATH = REPOSITORY_ROOT / "triagem-sintomas/metadados.json"
SLUG = "complicacao-local-pos-cateterismo-procedimento-vascular"

REQUIRED_ALIASES = {
    "dor no local da punção",
    "hematoma pós-cateterismo",
    "mão fria após exame",
    "sangramento na virilha após procedimento",
}

DOSE_PATTERNS = (
    r"\d+[\.,]?\d*\s*mg(?!/d[lL])\b",
    r"\d+[\.,]?\d*\s*mg/kg",
    r"\d+[\.,]?\d*\s*mcg",
    r"\d+[\.,]?\d*\s*µg",
    r"\d+[\.,]?\d*\s*UI\b",
    r"\d+[\.,]?\d*\s*U\/kg",
)

BASELINE_ANSWERS = {
    "access_site": "radial",
    "time_since_procedure": "lt_6h",
    "anticoagulant_or_antiplatelet": False,
    "hematoma_present": False,
    "hematoma_expanding_or_pulsatile": False,
    "active_bleeding_uncontrolled": False,
    "pain_disproportionate": False,
    "limb_pallor_or_coldness": False,
    "paresthesia_or_motor_weakness": False,
    "distal_pulse_absent_or_reduced": False,
    "capillary_refill_delayed": False,
    "hypotension_or_hypoperfusion": False,
    "abdominal_flank_or_back_pain": False,
    "pulsatile_mass_or_bruit": False,
}


def _load_records() -> list[dict]:
    data = json.loads(TRIAGE_PATH.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    return data


def _load_record() -> dict:
    records = _load_records()
    matches = [item for item in records if item.get("slug") == SLUG]
    assert len(matches) == 1, "registro deve existir exatamente uma vez"
    return matches[0]


def test_registro_existe_no_final_do_manifesto():
    records = _load_records()
    slugs = [item["slug"] for item in records]
    assert len(slugs) == len(set(slugs)), "nenhum slug duplicado no manifesto inteiro"
    assert slugs[-1] == SLUG, "registro deve estar ao final do array (risco de colisão com branches paralelas)"


def test_campos_obrigatorios_presentes_e_com_forma_esperada():
    item = _load_record()

    assert item["slug"] == SLUG
    assert item.get("name")
    assert REQUIRED_ALIASES <= set(item.get("aliases") or [])
    assert "geral" in (item.get("areas") or [])
    assert set(item.get("areas") or []) <= {
        "geral", "cardiopediatria", "cardiogeriatria", "cardiooncologia", "gravidez",
    }
    assert item.get("summary")
    assert item.get("questions")
    assert item.get("rules")
    assert item.get("default_tests")
    assert item.get("differentials")
    assert item.get("red_flags")
    assert item.get("ambulatory_flow")
    assert item.get("emergency_flow")
    assert item.get("tags")
    assert item.get("source_refs")
    assert item.get("review_status") == "pendente_revisao"
    assert item.get("review_note")
    assert item.get("version") == 1


def test_urls_sao_http_ou_https_com_host():
    item = _load_record()
    for url in item.get("source_urls") or []:
        parsed = urlparse(url)
        assert parsed.scheme in {"http", "https"}
        assert parsed.netloc


def test_pmids_centrais_estao_documentados_no_source_refs():
    item = _load_record()
    texto = json.dumps(item.get("source_refs"), ensure_ascii=False)
    for pmid in ("18726956", "27712733", "26811162", "30543806", "42132883"):
        assert pmid in texto, f"PMID {pmid} não encontrado em source_refs"


def test_nenhuma_dose_de_farmaco_em_nenhum_campo():
    item = _load_record()
    texto_completo = json.dumps(item, ensure_ascii=False)
    for pattern in DOSE_PATTERNS:
        achado = re.search(pattern, texto_completo, flags=re.IGNORECASE)
        assert achado is None, f"padrão de dose encontrado: {achado.group(0)!r} (padrão {pattern!r})"


def test_perguntas_e_regras_sao_validas_no_motor_de_regras():
    item = _load_record()
    question_errors, question_ids = validate_question_definitions(SLUG, item["questions"])
    assert question_errors == []
    assert set(BASELINE_ANSWERS) <= question_ids

    rule_errors = validate_rule_definitions(SLUG, item["rules"], question_ids)
    assert rule_errors == []


def test_perguntas_capturam_sitio_tempo_sinal_anticoagulante_e_sinais_vitais():
    item = _load_record()
    ids = {q["id"] for q in item["questions"]}
    campos_esperados = {
        "access_site",
        "time_since_procedure",
        "anticoagulant_or_antiplatelet",
        "hematoma_expanding_or_pulsatile",
        "active_bleeding_uncontrolled",
        "pain_disproportionate",
        "limb_pallor_or_coldness",
        "paresthesia_or_motor_weakness",
        "distal_pulse_absent_or_reduced",
        "hypotension_or_hypoperfusion",
    }
    assert campos_esperados <= ids

    labels = {q["id"]: q for q in item["questions"]}
    for question in labels.values():
        assert "label" in question
        assert "text" not in question


def _avaliar(item: dict, **overrides) -> dict:
    answers = dict(BASELINE_ANSWERS)
    answers.update(overrides)
    return evaluate_rules(
        questions=item["questions"],
        rules=item["rules"],
        answers=answers,
        base_ambulatory_flow=item["ambulatory_flow"],
        base_emergency_flow=item["emergency_flow"],
        context="ambulatorio",
    )


def test_isquemia_aguda_de_membro_palidez_frieza_pulso_ausente_e_emergencia():
    item = _load_record()
    resultado = _avaliar(
        item,
        limb_pallor_or_coldness=True,
        distal_pulse_absent_or_reduced=True,
    )
    assert resultado["invalid_fields"] == []
    assert resultado["risk"] == "emergencia"
    assert "isquemia-aguda-membro-palidez-frieza-pulso-ausente" in resultado["matched_rules"]
    assert resultado["emergency_flow"], "deve trazer conduta de emergência"


def test_deficit_neurologico_com_pulso_ausente_e_emergencia():
    item = _load_record()
    resultado = _avaliar(
        item,
        paresthesia_or_motor_weakness=True,
        distal_pulse_absent_or_reduced=True,
    )
    assert resultado["risk"] == "emergencia"
    assert "isquemia-aguda-deficit-neurologico-com-pulso-ausente" in resultado["matched_rules"]


def test_sangramento_retroperitoneal_suspeito_em_acesso_femoral_e_emergencia():
    item = _load_record()
    resultado = _avaliar(
        item,
        access_site="femoral",
        abdominal_flank_or_back_pain=True,
        hypotension_or_hypoperfusion=True,
    )
    assert resultado["risk"] == "emergencia"
    assert "sangramento-retroperitoneal-suspeito" in resultado["matched_rules"]


def test_retroperitoneal_nao_dispara_em_acesso_radial():
    item = _load_record()
    resultado = _avaliar(
        item,
        access_site="radial",
        abdominal_flank_or_back_pain=True,
        hypotension_or_hypoperfusion=True,
    )
    assert "sangramento-retroperitoneal-suspeito" not in resultado["matched_rules"]
    # hipotensão isolada ainda deve gerar alerta, só não o de retroperitônio
    assert resultado["risk"] == "urgente"


def test_hematoma_expansivo_ou_sangramento_ativo_e_red_flag_alto_urgente():
    item = _load_record()
    resultado = _avaliar(
        item,
        hematoma_present=True,
        hematoma_expanding_or_pulsatile=True,
    )
    assert resultado["risk"] == "urgente"
    assert "hematoma-expansivo-ou-sangramento-ativo-nao-controlado" in resultado["matched_rules"]
    assert resultado["risk"] != "emergencia"


def test_equimose_leve_estavel_sem_outros_sinais_e_risco_baixo():
    item = _load_record()
    resultado = _avaliar(item, hematoma_present=True)
    assert resultado["risk"] == "rotina"
    assert "equimose-leve-estavel-sem-outros-sinais" in resultado["matched_rules"]
    assert "isquemia-aguda-membro-palidez-frieza-pulso-ausente" not in resultado["matched_rules"]
    assert "sangramento-retroperitoneal-suspeito" not in resultado["matched_rules"]
    assert "hematoma-expansivo-ou-sangramento-ativo-nao-controlado" not in resultado["matched_rules"]


def test_cenario_totalmente_normal_e_informativo():
    item = _load_record()
    resultado = _avaliar(item)
    assert resultado["risk"] == "informativo"
    assert resultado["matched_rules"] == []
