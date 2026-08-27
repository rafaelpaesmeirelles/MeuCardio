from pathlib import Path

import pytest

from app.services import calculators
from app.services.intensive_care_hyperkalemia_safety import INTENSIVE_CARE_HYPERKALEMIA_SAFETY_REGISTRY


CALC = INTENSIVE_CARE_HYPERKALEMIA_SAFETY_REGISTRY["hipercalemia-seguranca-uco"]
ROOT = Path(__file__).resolve().parents[2]


def data(**overrides):
    payload = {
        "potassio_mmol_l": 6.7,
        "qualidade_amostra": "desconhecida",
        "ecg_realizado": True,
        "alteracao_ecg_compativel": False,
        "instabilidade_ou_arritmia_grave": False,
        "parada_cardiorrespiratoria": False,
        "forte_suspeita_hipercalemia_na_parada": False,
        "lra_oliguria_ou_anuria": False,
        "insulina_glicose_administrada": False,
        "glicemia_seriada_programada": False,
        "potassio_seriado_programado": True,
        "suspeita_toxicidade_digitalica": False,
    }
    payload.update(overrides)
    return payload


def test_k_grave_com_hemolise_permanece_emergencia_em_paralelo_a_recoleta():
    result = CALC.compute(data(qualidade_amostra="hemolise_suspeita"))
    assert result["faixa"] == "hipercalemia grave (≥6,5 mmol/L)"
    assert result["nivel"] == "emergencia"
    assert "EMERGÊNCIA" in result["prioridade"]
    assert "repetir imediatamente" in result["conferencia_amostra"]
    assert "não rebaixar" in result["conferencia_amostra"]


def test_parada_com_k_leve_nao_abre_fluxo_especifico_sem_atribuicao():
    result = CALC.compute(data(
        potassio_mmol_l=5.5,
        parada_cardiorrespiratoria=True,
        forte_suspeita_hipercalemia_na_parada=False,
        potassio_seriado_programado=False,
    ))
    assert result["nivel"] == "emergencia"
    assert "ALS padrão" in result["prioridade"]
    assert "Não atribuir" in result["prioridade"]
    assert "abrir em paralelo o protocolo específico" not in result["prioridade"]


def test_parada_com_forte_suspeita_pode_abrir_causa_reversivel_em_paralelo():
    result = CALC.compute(data(
        parada_cardiorrespiratoria=True,
        forte_suspeita_hipercalemia_na_parada=True,
    ))
    assert "forte suspeita declarada" in result["prioridade"]
    assert "protocolo específico" in result["prioridade"]


def test_ecg_ausente_nunca_e_descrita_como_ecg_sem_alteracao():
    result = CALC.compute(data(
        ecg_realizado=False,
        parada_cardiorrespiratoria=True,
        forte_suspeita_hipercalemia_na_parada=False,
    ))
    assert "Não há ECG de 12 derivações documentado" in result["avaliacao_ecg"]
    assert "ECG sem alteração" not in result["avaliacao_ecg"]


def test_qualidade_da_amostra_inicia_como_desconhecida_no_select():
    field = next(field for field in CALC.fields if field.name == "qualidade_amostra")
    assert field.options[0]["value"] == "desconhecida"


def test_k_moderado_ou_grave_exige_potassio_seriado_mesmo_sem_insulina():
    result = CALC.compute(data(
        potassio_mmol_l=6.2,
        insulina_glicose_administrada=False,
        potassio_seriado_programado=False,
    ))
    alerts = " ".join(result["alertas_seguranca"])
    assert "Potássio seriado não está programado" in alerts
    assert "independentemente do uso de insulina/glicose" in alerts


def test_insulina_sem_glicemia_seriada_mantem_gate_de_hipoglicemia():
    result = CALC.compute(data(
        insulina_glicose_administrada=True,
        glicemia_seriada_programada=False,
        potassio_seriado_programado=False,
    ))
    alerts = " ".join(result["alertas_seguranca"])
    assert "glicemia seriada" in alerts.casefold()
    assert "potássio seriado" in alerts.casefold()


def test_instabilidade_com_k_abaixo_do_limiar_nao_e_atribuida_ao_potassio():
    result = CALC.compute(data(
        potassio_mmol_l=5.2,
        instabilidade_ou_arritmia_grave=True,
        potassio_seriado_programado=False,
    ))
    assert result["nivel"] == "informativo"
    assert "FORA DO ESCOPO" in result["prioridade"]
    assert "outras causas" in result["prioridade"]


def test_ecg_compativel_nao_pode_ser_marcado_sem_ecg_realizado():
    with pytest.raises(ValueError, match="sem ECG de 12 derivações realizado"):
        CALC.compute(data(ecg_realizado=False, alteracao_ecg_compativel=True))


def test_atribuicao_da_parada_nao_pode_existir_sem_parada():
    with pytest.raises(ValueError, match="só pode ser marcada"):
        CALC.compute(data(parada_cardiorrespiratoria=False, forte_suspeita_hipercalemia_na_parada=True))


def test_estacao_esta_no_registry_global_sem_posologia_embutida():
    global_calc = calculators.REGISTRY["hipercalemia-seguranca-uco"]
    assert global_calc.kind == "assessment"
    text = " ".join(global_calc.limitations).casefold()
    assert "não seleciona nem calcula tratamento" in text
    for forbidden in ("mg/kg", "mcg/kg", "meq/h", "mmol/h", "unidades/kg"):
        assert forbidden not in text


def test_cockpit_expoe_hipercalemia_e_brash_como_estacoes_rapidas():
    text = (ROOT / "frontend/src/pages/CardiologiaIntensiva.tsx").read_text(encoding="utf-8")
    assert '"hipercalemia-seguranca-uco"' in text
    assert '"brash-reconhecimento-padrao-uco"' in text
    assert 'to="/calculadoras/hipercalemia-seguranca-uco"' in text
    assert 'to="/calculadoras/brash-reconhecimento-padrao-uco"' in text


def test_protocolo_publicado_registra_os_gates_corrigidos():
    text = (ROOT / "content/Terapia_intensiva/hipercalemia-na-uco-gravidade-ecg-e-gates-de-seguranca.md").read_text(encoding="utf-8")
    assert "review_status: revisado" in text
    assert "Qualidade da amostra deve começar como **desconhecida**" in text
    assert "Um K discretamente aumentado" in text
    assert "independentemente de insulina/glicose" in text
    assert "ECG não realizado" in text
