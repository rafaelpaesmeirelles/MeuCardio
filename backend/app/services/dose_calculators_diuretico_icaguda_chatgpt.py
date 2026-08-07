"""Estratégia de diurético IV reproduzindo o protocolo do ensaio DOSE.

Esta calculadora NÃO define uma dose universal de furosemida na IC aguda.
Ela reproduz os braços do ensaio DOSE (NEJM 2011) em pacientes que já usavam
diurético de alça cronicamente: total IV igual a 1x ou 2,5x a dose oral diária
equivalente de furosemida, em bolus q12h ou infusão contínua.

Fonte de produção: ChatGPT.
"""

from __future__ import annotations

from .calculators import Calculator, Field

FONTE_PRODUCAO = "chatgpt"

DOSE_TRIAL = (
    "Felker GM, Lee KL, Bull DA, et al. Diuretic Strategies in Patients with Acute Decompensated "
    "Heart Failure. N Engl J Med. 2011;364:797-805. PMID: 21366472. "
    "doi:10.1056/NEJMoa1005419."
)

# Equivalências usadas no próprio DOSE: 20 mg torsemida ou 1 mg bumetanida = 40 mg furosemida.
FATOR_FUROSEMIDA = {
    "furosemida": 1.0,
    "torsemida": 2.0,
    "bumetanida": 40.0,
}


def _dose_trial_ic_aguda(d: dict) -> dict:
    farmaco_casa = d["farmaco_casa"]
    dose_oral_dia = float(d["dose_oral_dia"])
    estrategia = d["estrategia"]
    modo = d["modo"]
    if dose_oral_dia <= 0:
        raise ValueError("Dose oral diária precisa ser maior que zero.")

    eq_furo = dose_oral_dia * FATOR_FUROSEMIDA[farmaco_casa]
    multiplicador = 1.0 if estrategia == "baixa" else 2.5
    total_iv_dia = eq_furo * multiplicador

    result = {
        "farmaco": "Furosemida IV",
        "equivalente_furosemida_oral_mg_dia": round(eq_furo, 1),
        "estrategia": "1x dose oral equivalente" if estrategia == "baixa" else "2,5x dose oral equivalente",
        "total_iv_furosemida_mg_dia": round(total_iv_dia, 1),
        "dentro_populacao_dose_trial": 80 <= eq_furo <= 240,
    }
    if modo == "bolus_q12":
        result["bolus_mg_q12h"] = round(total_iv_dia / 2, 1)
        result["modo"] = "bolus IV a cada 12 h"
    else:
        result["infusao_mg_h"] = round(total_iv_dia / 24, 2)
        result["modo"] = "infusão IV contínua"
    return result


def _dose_trial_ic_aguda_txt(r: dict) -> str:
    if "bolus_mg_q12h" in r:
        esquema = f"{r['bolus_mg_q12h']} mg IV a cada 12 h"
    else:
        esquema = f"{r['infusao_mg_h']} mg/h em infusão contínua"
    alerta = (
        " ⚠️ A dose oral equivalente informada está fora de 80-240 mg/dia, faixa de elegibilidade do DOSE; "
        "a extrapolação quantitativa não reproduz diretamente a população do ensaio."
        if not r["dentro_populacao_dose_trial"] else ""
    )
    return (
        f"Estratégia DOSE: equivalente domiciliar {r['equivalente_furosemida_oral_mg_dia']} mg/dia de furosemida; "
        f"braço {r['estrategia']} = {r['total_iv_furosemida_mg_dia']} mg/dia IV, administrados como {esquema}."
        f"{alerta}"
    )


_DOSE_TRIAL_CALC = Calculator(
    slug="furosemida-iv-ic-aguda-estrategia-dose-trial",
    name="Furosemida IV na IC aguda — estratégias do ensaio DOSE",
    theme="Doses — Insuficiência Cardíaca",
    purpose="Reproduz 1x versus 2,5x a dose oral equivalente e bolus q12h versus infusão contínua do ensaio DOSE.",
    fields=[
        Field("farmaco_casa", "Diurético de alça oral domiciliar", "select", options=[
            {"value": "furosemida", "label": "Furosemida"},
            {"value": "torsemida", "label": "Torsemida"},
            {"value": "bumetanida", "label": "Bumetanida"},
        ]),
        Field("dose_oral_dia", "Dose oral total por dia", "number", "mg/dia", min=0.1, max=1000),
        Field("estrategia", "Braço de dose a reproduzir", "select", options=[
            {"value": "baixa", "label": "Baixa dose — total IV = 1x a dose oral equivalente"},
            {"value": "alta", "label": "Alta dose — total IV = 2,5x a dose oral equivalente"},
        ]),
        Field("modo", "Modo de administração", "select", options=[
            {"value": "bolus_q12", "label": "Bolus IV a cada 12 horas"},
            {"value": "continua", "label": "Infusão IV contínua"},
        ]),
    ],
    compute=_dose_trial_ic_aguda,
    interpret=_dose_trial_ic_aguda_txt,
    reference=DOSE_TRIAL,
    kind="dose",
    limitations=[
        "Esta é uma calculadora de METODOLOGIA DO ENSAIO, não uma recomendação de dose universal.",
        "O DOSE incluiu pacientes com IC aguda que já usavam diurético de alça por pelo menos 1 mês, equivalentes a 80-240 mg/dia de furosemida.",
        "Equivalências usadas no estudo: 20 mg de torsemida ou 1 mg de bumetanida = 40 mg de furosemida.",
        "Pacientes com PAS <90 mmHg, creatinina >3,0 mg/dL ou necessidade de vasodilatador/inotrópico IV foram excluídos do ensaio.",
        "Bolus versus infusão contínua não diferiu nos endpoints coprimários. A estratégia de 2,5x produziu maior diurese, mas maior proporção de aumento transitório da creatinina >0,3 mg/dL (23% vs 14%).",
        "A resposta clínica deve ser reavaliada por diurese, peso, congestão, eletrólitos, PA e função renal; resistência diurética exige estratégia clínica além desta fórmula.",
    ],
)


DIURETICO_IC_AGUDA_DOSE_REGISTRY: dict[str, Calculator] = {_DOSE_TRIAL_CALC.slug: _DOSE_TRIAL_CALC}
