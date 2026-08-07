"""Vasoativos no choque cardiogênico conforme ACC Concise Clinical Guidance 2025.

A Tabela 2 do documento fornece faixas de dose contemporâneas. Este módulo
mantém essas faixas separadas da calculadora genérica legada, evitando mudar
silenciosamente cálculos já existentes no sistema.

Fonte de produção: ChatGPT.
"""

from __future__ import annotations

from .calculators import Calculator, Field

FONTE_PRODUCAO = "chatgpt"

ACC_CS_2025 = (
    "Sinha SS, Morrow DA, Kapur NK, Kataria R, Roswell RO. 2025 Concise Clinical Guidance: "
    "An ACC Expert Consensus Statement on the Evaluation and Management of Cardiogenic Shock. "
    "J Am Coll Cardiol. 2025;85(16):1618-1641. doi:10.1016/j.jacc.2025.02.018. Table 2."
)

AGENTES = {
    "norepinefrina": {
        "nome": "Norepinefrina",
        "unidade": "mcg/kg/min",
        "min": 0.05,
        "max": 1.0,
        "classe": "inopressor",
    },
    "epinefrina": {
        "nome": "Epinefrina",
        "unidade": "mcg/kg/min",
        "min": 0.01,
        "max": 0.5,
        "classe": "inopressor",
    },
    "dopamina": {
        "nome": "Dopamina",
        "unidade": "mcg/kg/min",
        "min": 2.0,
        "max": 20.0,
        "classe": "inopressor/cronotrópico",
    },
    "dobutamina": {
        "nome": "Dobutamina",
        "unidade": "mcg/kg/min",
        "min": 2.0,
        "max": 10.0,
        "classe": "inodilatador",
    },
    "milrinona": {
        "nome": "Milrinona",
        "unidade": "mcg/kg/min",
        "min": 0.125,
        "max": 0.5,
        "classe": "inodilatador",
    },
    "fenilefrina": {
        "nome": "Fenilefrina",
        "unidade": "mcg/kg/min",
        "min": 0.1,
        "max": 10.0,
        "classe": "vasopressor puro",
    },
    "vasopressina": {
        "nome": "Vasopressina",
        "unidade": "U/min",
        "min": 0.01,
        "max": 0.04,
        "classe": "vasopressor",
    },
    "nitroprussiato": {
        "nome": "Nitroprussiato",
        "unidade": "mcg/kg/min",
        "min": 0.3,
        "max": 10.0,
        "classe": "vasodilatador",
    },
    "nitroglicerina": {
        "nome": "Nitroglicerina",
        "unidade": "mcg/min",
        "min": 25.0,
        "max": 200.0,
        "classe": "vasodilatador",
    },
    "isoproterenol": {
        "nome": "Isoproterenol",
        "unidade": "mcg/min",
        "min": 2.0,
        "max": 20.0,
        "classe": "cronotrópico",
    },
}


def _vasoativo_cs(d: dict) -> dict:
    chave = d["agente"]
    peso = float(d["peso"])
    alvo = float(d["dose_alvo"])
    quantidade = float(d["quantidade_soluto"])
    volume = float(d["volume_ml"])
    hipotensao = bool(d.get("hipotensao"))
    piora_renal = bool(d.get("piora_renal"))
    if peso <= 0 or alvo <= 0 or quantidade <= 0 or volume <= 0:
        raise ValueError("Peso, dose-alvo, quantidade e volume precisam ser maiores que zero.")

    a = AGENTES[chave]
    fora = alvo < a["min"] or alvo > a["max"]

    # quantidade_soluto deve ser informada em mg para drogas mcg e em U para vasopressina.
    if a["unidade"] == "U/min":
        concentracao_u_ml = quantidade / volume
        ml_h = alvo * 60 / concentracao_u_ml
        concentracao = f"{round(concentracao_u_ml, 4)} U/mL"
    else:
        concentracao_mcg_ml = quantidade * 1000 / volume
        if a["unidade"] == "mcg/kg/min":
            ml_h = alvo * peso * 60 / concentracao_mcg_ml
        else:
            ml_h = alvo * 60 / concentracao_mcg_ml
        concentracao = f"{round(concentracao_mcg_ml, 2)} mcg/mL"

    alertas = []
    if chave == "norepinefrina" and hipotensao:
        alertas.append("ACC 2025 considera norepinefrina uma escolha inicial razoável para a maioria dos pacientes com choque cardiogênico hipotensivo")
    if chave == "fenilefrina":
        alertas.append("ACC 2025 desencoraja fortemente fenilefrina como única infusão IV de primeira linha no choque cardiogênico por risco de reduzir débito cardíaco/reflexo bradicárdico")
    if chave == "milrinona" and piora_renal:
        alertas.append("milrinona tem meia-vida relativamente longa e eliminação renal; usar com cautela na piora da função renal")
    if chave in {"dobutamina", "milrinona", "nitroprussiato"} and hipotensao:
        alertas.append("agente com efeito inodilatador/vasodilatador pode agravar hipotensão; integrar hemodinâmica antes do uso")

    return {
        "agente": a["nome"],
        "classe": a["classe"],
        "dose_alvo": alvo,
        "unidade_dose": a["unidade"],
        "faixa_acc_2025": f"{a['min']}-{a['max']} {a['unidade']}",
        "fora_da_faixa": fora,
        "concentracao": concentracao,
        "ml_h": round(ml_h, 2),
        "alertas": alertas,
    }


def _vasoativo_cs_txt(r: dict) -> str:
    aviso = " ⚠️ Dose-alvo fora da faixa da Tabela 2 ACC 2025." if r["fora_da_faixa"] else ""
    texto = (
        f"{r['agente']} ({r['classe']}): {r['dose_alvo']} {r['unidade_dose']} = "
        f"{r['ml_h']} mL/h na concentração informada ({r['concentracao']}). "
        f"Faixa ACC 2025: {r['faixa_acc_2025']}.{aviso}"
    )
    if r["alertas"]:
        texto += " " + " | ".join(r["alertas"]) + "."
    return texto


_VASOATIVO_CS = Calculator(
    slug="vasoativos-choque-cardiogenico-acc-2025",
    name="Choque cardiogênico — vasoativos e conversão para mL/h (ACC 2025)",
    theme="Doses — Choque Cardiogênico",
    purpose="Converte dose-alvo em mL/h usando as faixas contemporâneas da Tabela 2 ACC 2025 e emite alertas por fenótipo.",
    fields=[
        Field("agente", "Agente", "select", options=[
            {"value": k, "label": f"{v['nome']} — {v['min']}-{v['max']} {v['unidade']}"}
            for k, v in AGENTES.items()
        ]),
        Field("peso", "Peso", "number", "kg", min=20, max=300,
              help="Usado apenas nos agentes expressos por kg; mantenha o peso real documentado."),
        Field("dose_alvo", "Dose-alvo", "number", help="Use a unidade mostrada no nome do agente."),
        Field("quantidade_soluto", "Quantidade total do fármaco na solução", "number",
              help="Informe mg para agentes em mcg; para vasopressina, informe unidades (U)."),
        Field("volume_ml", "Volume total preparado", "number", "mL", min=1),
        Field("hipotensao", "Choque com hipotensão relevante", "boolean"),
        Field("piora_renal", "Função renal em piora", "boolean"),
    ],
    compute=_vasoativo_cs,
    interpret=_vasoativo_cs_txt,
    reference=ACC_CS_2025,
    kind="dose",
    limitations=[
        "Usar vasoativos na menor dose capaz de sustentar perfusão e pelo menor tempo possível, conforme o consenso ACC 2025.",
        "Não há um vasoativo com superioridade de mortalidade estabelecida para todos os fenótipos; a seleção deve ser hemodinâmica.",
        "Norepinefrina é considerada escolha inicial razoável para a maioria dos pacientes hipotensivos.",
        "Inodilatadores/vasodilatadores podem ser considerados em choque normotensivo, especialmente com resistência vascular sistêmica elevada.",
        "Fenilefrina isolada como primeira infusão é fortemente desencorajada no choque cardiogênico.",
        "Milrinona exige cautela na piora renal.",
        "Levosimendana aparece na tabela ACC 2025, mas não foi incluída aqui porque não é aprovada pelo FDA e a disponibilidade/regulação brasileira exigiria verificação própria.",
    ],
)


CHOQUE_CARDIOGENICO_2025_DOSE_REGISTRY: dict[str, Calculator] = {_VASOATIVO_CS.slug: _VASOATIVO_CS}
