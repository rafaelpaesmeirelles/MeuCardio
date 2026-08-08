"""Calculadoras de fibrinolíticos para STEMI.

Tenecteplase:
- dose nominal e volume: bula profissional brasileira Metalyse/Boehringer;
- meia-dose em idosos: evidência STREAM descrita na própria bula e orientação
  da SBC em cardiogeriatria, SEM substituir silenciosamente a tabela de posologia.

Alteplase:
- esquema acelerado de 90 min conforme ACC/AHA ACS 2025.

Estes regimes são EXCLUSIVOS para infarto com supra de ST; não reutilizar em
AVC isquêmico ou tromboembolismo pulmonar.

Fonte de produção: ChatGPT.
"""

from __future__ import annotations

from .calculators import Calculator, Field

FONTE_PRODUCAO = "chatgpt"

METALYSE_BR = (
    "Metalyse® (tenecteplase). Bula profissional Boehringer Ingelheim, "
    "código 07-5773227/07-5775310/P23-02; tabela de posologia por peso. "
    "A própria bula descreve a redução pela metade em pacientes ≥75 anos no estudo STREAM."
)

SBC_IDOSO = (
    "Atualização das Diretrizes em Cardiogeriatria da Sociedade Brasileira de Cardiologia - 2019. "
    "Arq Bras Cardiol. 2019. Recomendação: se utilizar tenecteplase em idosos >75 anos, aplicar metade da dose."
)

ACC_AHA_ACS_2025 = (
    "Rao SV, O'Donoghue ML, Ruel M, et al. 2025 ACC/AHA/ACEP/NAEMSP/SCAI Guideline for the "
    "Management of Patients With Acute Coronary Syndromes. J Am Coll Cardiol. 2025. "
    "doi:10.1016/j.jacc.2024.11.009."
)


def _tnk_nominal(peso: float) -> tuple[float, float, int]:
    if peso < 60:
        return 30.0, 6.0, 6000
    if peso < 70:
        return 35.0, 7.0, 7000
    if peso < 80:
        return 40.0, 8.0, 8000
    if peso < 90:
        return 45.0, 9.0, 9000
    return 50.0, 10.0, 10000


def _tenecteplase_stemi(d: dict) -> dict:
    peso = float(d["peso"])
    idade = float(d["idade"])
    usar_meia_dose = bool(d.get("usar_meia_dose_idoso"))
    if peso <= 0 or idade <= 0:
        raise ValueError("Peso e idade precisam ser maiores que zero.")

    dose_nominal, volume_nominal, unidades = _tnk_nominal(peso)
    elegivel_meia_stream = idade >= 75

    if usar_meia_dose and not elegivel_meia_stream:
        raise ValueError(
            "Meia-dose do protocolo de idoso não deve ser selecionada automaticamente em paciente <75 anos."
        )

    dose_final = dose_nominal / 2 if usar_meia_dose else dose_nominal
    volume_final = volume_nominal / 2 if usar_meia_dose else volume_nominal
    unidades_final = unidades // 2 if usar_meia_dose else unidades

    return {
        "farmaco": "Tenecteplase (Metalyse)",
        "peso_kg": peso,
        "idade_anos": idade,
        "dose_nominal_bula_mg": dose_nominal,
        "volume_nominal_bula_ml": volume_nominal,
        "unidades_nominais": unidades,
        "idoso_ge_75_stream": elegivel_meia_stream,
        "meia_dose_selecionada": usar_meia_dose,
        "dose_a_administrar_mg": round(dose_final, 1),
        "volume_a_administrar_ml": round(volume_final, 1),
        "unidades_a_administrar": unidades_final,
        "administracao": "bolus IV único em aproximadamente 5-10 s",
    }


def _tenecteplase_stemi_txt(r: dict) -> str:
    if r["meia_dose_selecionada"]:
        return (
            f"Tenecteplase: {r['dose_a_administrar_mg']} mg ({r['volume_a_administrar_ml']} mL da solução "
            f"reconstituída; {r['unidades_a_administrar']} U) em bolus IV único em 5-10 s. "
            f"Dose nominal da bula para este peso: {r['dose_nominal_bula_mg']} mg. A meia-dose foi "
            "selecionada deliberadamente para paciente idoso conforme estratégia STREAM/SBC; a tabela "
            "de posologia da bula brasileira permanece expressa na dose nominal por peso."
        )
    alerta = (
        " ⚠️ Paciente ≥75 anos: a própria bula descreve que o STREAM reduziu a tenecteplase pela metade "
        "neste subgrupo após sinal de hemorragia intracraniana; a SBC também orienta meia-dose em idosos. "
        "Revise se o protocolo institucional indica selecionar a opção de meia-dose."
        if r["idoso_ge_75_stream"] else ""
    )
    return (
        f"Tenecteplase: dose nominal de bula {r['dose_a_administrar_mg']} mg "
        f"({r['volume_a_administrar_ml']} mL; {r['unidades_a_administrar']} U) em bolus IV único "
        f"em aproximadamente 5-10 s.{alerta}"
    )


_TENECTEPLASE_STEMI = Calculator(
    slug="tenecteplase-stemi-peso-idoso",
    name="Tenecteplase (Metalyse) — STEMI por peso e meia-dose no idoso",
    theme="Doses — Cardiologia Geral",
    purpose="Calcula a dose nominal brasileira por peso e, quando selecionado, a meia-dose do idoso baseada no STREAM/SBC.",
    fields=[
        Field("peso", "Peso corporal", "number", "kg", min=20, max=300),
        Field("idade", "Idade", "number", "anos", min=18, max=120),
        Field(
            "usar_meia_dose_idoso",
            "Aplicar meia-dose do protocolo de idoso (somente se idade ≥75 anos)",
            "boolean",
            help=(
                "A tabela de posologia da bula brasileira mantém a dose nominal por peso. A própria bula "
                "descreve que no STREAM a dose foi reduzida pela metade em pacientes ≥75 anos após sinal "
                "de HIC; a SBC orienta meia-dose em idosos >75 anos. Selecione deliberadamente conforme "
                "protocolo institucional."
            ),
        ),
    ],
    compute=_tenecteplase_stemi,
    interpret=_tenecteplase_stemi_txt,
    reference=f"{METALYSE_BR} · {SBC_IDOSO} · {ACC_AHA_ACS_2025}",
    kind="dose",
    limitations=[
        "Uso aqui modelado exclusivamente para fibrinólise de STEMI; não usar este regime para AVC isquêmico ou TEP.",
        "A meia-dose em ≥75 anos aparece como estratégia de segurança/evidência e não substitui silenciosamente a tabela nominal da seção de posologia da bula brasileira.",
        "A SBC 2019 usa a redação >75 anos, enquanto o STREAM descrito na bula reduziu a dose em pacientes ≥75 anos; a calculadora permite o protocolo a partir de 75 e deixa a seleção explícita ao médico.",
        "Antes da fibrinólise, excluir contraindicações absolutas/relativas e confirmar que a estratégia fibrinolítica é apropriada frente ao tempo para ICP primária.",
        "A solução reconstituída do Metalyse contém 5 mg/mL segundo a bula consultada; incompatível com solução glicosada no mesmo acesso.",
    ],
)


def _alteplase_stemi(d: dict) -> dict:
    peso = float(d["peso"])
    if peso <= 0:
        raise ValueError("Peso precisa ser maior que zero.")

    bolus = 15.0
    if peso >= 67:
        # ACC/AHA 2025 explicita este ramo como esquema fixo.
        fase_30 = 50.0
        fase_60 = 35.0
    else:
        # A tabela usa dose peso-ajustada com os mesmos tetos de 50 e 35 mg.
        fase_30 = min(0.75 * peso, 50.0)
        fase_60 = min(0.50 * peso, 35.0)
    total = bolus + fase_30 + fase_60
    return {
        "farmaco": "Alteplase (tPA)",
        "peso_kg": peso,
        "bolus_iv_mg": bolus,
        "infusao_primeiros_30min_mg": round(fase_30, 1),
        "infusao_30_a_90min_mg": round(fase_60, 1),
        "dose_total_mg": round(total, 1),
        "peso_ge_67": peso >= 67,
    }


def _alteplase_stemi_txt(r: dict) -> str:
    return (
        f"Alteplase no STEMI: 15 mg IV em bolus, depois {r['infusao_primeiros_30min_mg']} mg nos "
        f"primeiros 30 min e {r['infusao_30_a_90min_mg']} mg nos 60 min seguintes. "
        f"Dose total: {r['dose_total_mg']} mg em 90 min."
    )


_ALTEPLASE_STEMI = Calculator(
    slug="alteplase-stemi-esquema-acelerado-90min-2025",
    name="Alteplase — STEMI, esquema acelerado de 90 minutos (ACC/AHA 2025)",
    theme="Doses — Cardiologia Geral",
    purpose="Calcula as três etapas do esquema acelerado de alteplase para fibrinólise do STEMI.",
    fields=[Field("peso", "Peso corporal", "number", "kg", min=20, max=300)],
    compute=_alteplase_stemi,
    interpret=_alteplase_stemi_txt,
    reference=ACC_AHA_ACS_2025,
    kind="dose",
    limitations=[
        "Uso exclusivo para fibrinólise de STEMI; não usar este regime para AVC isquêmico ou TEP.",
        "Em adultos ≥67 kg, o esquema é fixo e resulta em 100 mg totais: 15 mg bolus + 50 mg/30 min + 35 mg/60 min.",
        "Em adultos <67 kg, usar 15 mg bolus + 0,75 mg/kg (máx 50 mg) em 30 min + 0,5 mg/kg (máx 35 mg) nos 60 min seguintes.",
        "A calculadora não decide indicação de fibrinólise nem verifica contraindicações hemorrágicas.",
    ],
)


FIBRINOLITICOS_STEMI_DOSE_REGISTRY: dict[str, Calculator] = {
    c.slug: c for c in [_TENECTEPLASE_STEMI, _ALTEPLASE_STEMI]
}
