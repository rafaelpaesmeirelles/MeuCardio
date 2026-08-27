"""Calculadoras operacionais para Cardiologia Intensiva e Unidade Coronariana.

O primeiro instrumento deste módulo calcula peso corporal predito e parâmetros
de ventilação protetora. Ele deliberadamente não sugere modo ventilatório nem
prescreve PEEP: essas decisões dependem da fisiologia e da avaliação à beira
leito.
"""

from __future__ import annotations

from .calculators import Calculator, Field


FONTE_PRODUCAO = "chatgpt"

REFERENCIAS_VENTILACAO = (
    "ARDS Network. Ventilation with lower tidal volumes as compared with traditional tidal "
    "volumes for acute lung injury and ARDS. N Engl J Med. 2000;342:1301-1308. "
    "doi:10.1056/NEJM200005043421801; Fan E et al. ATS/ESICM/SCCM Clinical Practice "
    "Guideline: Mechanical Ventilation in Adult Patients with ARDS. Am J Respir Crit Care "
    "Med. 2017;195:1253-1263. PMID:28459336; Qadir N et al. An Update on Management of "
    "Adult Patients with ARDS: An Official ATS Clinical Practice Guideline. Am J Respir Crit "
    "Care Med. 2024;209:24-36. doi:10.1164/rccm.202311-2011ST; Goodfellow LT et al. "
    "AARC Clinical Practice Guideline: Patient-Ventilator Assessment. Respir Care. "
    "2024;69:1042-1054. PMID:39048148; Ferreira JC et al. Brazilian guidelines for "
    "mechanical ventilation 2024. Crit Care Sci. 2025;37:e20250242en. "
    "doi:10.62675/2965-2774.20250242-en."
)


def _ventilacao_protetora(dados: dict) -> dict:
    sexo = dados["sexo_biologico"]
    altura_cm = float(dados["altura_cm"])
    volume_corrente_ml = float(dados["volume_corrente_ml"])
    pressao_plato = float(dados["pressao_plato_cmh2o"])
    peep_total = float(dados["peep_total_cmh2o"])

    if sexo not in {"masculino", "feminino"}:
        raise ValueError("Selecione o sexo biológico usado na equação de peso predito.")
    if not 120 <= altura_cm <= 220:
        raise ValueError("Informe altura entre 120 e 220 cm.")
    if volume_corrente_ml <= 0 or pressao_plato < 0 or peep_total < 0:
        raise ValueError("Volume corrente deve ser positivo; pressões não podem ser negativas.")
    if pressao_plato < peep_total:
        raise ValueError("Pressão de platô não pode ser menor que a PEEP total.")

    constante = 50.0 if sexo == "masculino" else 45.5
    peso_predito = constante + 0.91 * (altura_cm - 152.4)
    volume_por_kg = volume_corrente_ml / peso_predito
    pressao_distensao = pressao_plato - peep_total
    volume_abaixo = volume_por_kg < 4
    volume_acima = volume_por_kg > 8
    plato_elevada = pressao_plato >= 30

    if volume_abaixo:
        alerta_volume = "abaixo de 4 mL/kg de peso predito — revisar indicação e medidas"
    elif volume_acima:
        alerta_volume = "acima de 8 mL/kg de peso predito — revisar estratégia protetora"
    else:
        alerta_volume = "dentro da faixa protetora de referência de 4–8 mL/kg"

    alerta_plato = (
        "pressão de platô ≥30 cmH2O — reavaliar estratégia e qualidade da medida"
        if plato_elevada
        else "pressão de platô abaixo de 30 cmH2O"
    )

    return {
        "peso_predito_kg": round(peso_predito, 2),
        "vt_referencia_6_ml_kg": round(peso_predito * 6, 1),
        "faixa_vt_4_a_8_ml_kg": f"{peso_predito * 4:.1f}–{peso_predito * 8:.1f} mL",
        "vt_atual_ml_kg": round(volume_por_kg, 2),
        "pressao_distensao_cmh2o": round(pressao_distensao, 1),
        "alerta_volume": alerta_volume,
        "alerta_plato": alerta_plato,
        "fora_da_faixa": volume_abaixo or volume_acima or plato_elevada,
    }


def _interpretar_ventilacao(resultado: dict) -> str:
    return (
        f"Peso corporal predito {resultado['peso_predito_kg']} kg; volume de referência a "
        f"6 mL/kg = {resultado['vt_referencia_6_ml_kg']} mL e faixa 4–8 mL/kg = "
        f"{resultado['faixa_vt_4_a_8_ml_kg']}. O volume informado corresponde a "
        f"{resultado['vt_atual_ml_kg']} mL/kg. Pressão de distensão calculada = "
        f"{resultado['pressao_distensao_cmh2o']} cmH2O. {resultado['alerta_volume']}; "
        f"{resultado['alerta_plato']}."
    )


_VENTILACAO_PROTETORA = Calculator(
    slug="ventilacao-protetora-uco",
    name="Ventilação protetora — peso predito, volume corrente e pressões",
    theme="Terapia intensiva",
    purpose=(
        "Calcula peso corporal predito, faixa de volume corrente protetor, volume entregue "
        "por kg e pressão de distensão para apoiar a reavaliação ventilatória do adulto."
    ),
    fields=[
        Field(
            "sexo_biologico",
            "Sexo biológico usado na equação",
            "select",
            options=[
                {"value": "masculino", "label": "Masculino"},
                {"value": "feminino", "label": "Feminino"},
            ],
            help="A equação histórica de peso corporal predito usa constantes distintas por sexo biológico.",
        ),
        Field("altura_cm", "Altura", "number", "cm", min=120, max=220),
        Field(
            "volume_corrente_ml",
            "Volume corrente entregue",
            "number",
            "mL",
            min=50,
            max=2000,
            help="Use o volume efetivamente entregue e reavalie após mudanças de modo ou mecânica.",
        ),
        Field(
            "pressao_plato_cmh2o",
            "Pressão de platô",
            "number",
            "cmH₂O",
            min=0,
            max=80,
            help="Medir com pausa inspiratória e sem esforço respiratório que invalide a medida.",
        ),
        Field(
            "peep_total_cmh2o",
            "PEEP total",
            "number",
            "cmH₂O",
            min=0,
            max=50,
            help="Inclua PEEP intrínseca quando presente; a diferença para o platô estima pressão de distensão.",
        ),
    ],
    compute=_ventilacao_protetora,
    interpret=_interpretar_ventilacao,
    reference=REFERENCIAS_VENTILACAO,
    kind="dose",
    limitations=[
        "Ferramenta educacional e de conferência; não seleciona modo ventilatório, frequência, FiO₂ ou PEEP e não substitui avaliação à beira leito.",
        "A recomendação forte de 4–8 mL/kg de peso predito e platô <30 cmH₂O provém de pacientes com SDRA; em outros fenótipos, individualizar sem abandonar a prevenção de lesão pulmonar.",
        "Pressão de distensão é exibida para avaliação. A diretriz AARC 2024 recomenda sua aferição apenas condicionalmente, com baixa certeza; por isso a calculadora não impõe um limiar terapêutico.",
        "Pressão de platô exige pausa inspiratória adequada e ausência de esforço; assincronia, vazamento e medida inadequada podem invalidar o resultado.",
        "PEEP deve ser individualizada em instabilidade hemodinâmica, disfunção de ventrículo direito e fisiologia obstrutiva.",
    ],
)


INTENSIVE_CARE_CALCULATOR_REGISTRY: dict[str, Calculator] = {
    _VENTILACAO_PROTETORA.slug: _VENTILACAO_PROTETORA,
}
