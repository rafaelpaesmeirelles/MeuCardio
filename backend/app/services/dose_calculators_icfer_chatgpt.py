"""Doses iniciais e alvo de fármacos usados na ICFER.

Fonte principal: Tabela 14 da diretriz AHA/ACC/HFSA 2022. Esta calculadora é
uma referência de dose de ensaio/diretriz — não decide elegibilidade clínica,
sequência, pressão mínima, função renal ou potássio para cada classe.

Fonte de produção: ChatGPT.
"""

from __future__ import annotations

from .calculators import Calculator, Field

FONTE_PRODUCAO = "chatgpt"

AHA_HF_2022 = (
    "Heidenreich PA, Bozkurt B, Aguilar D, et al. 2022 AHA/ACC/HFSA Guideline for the "
    "Management of Heart Failure. Circulation. 2022;145:e895-e1032. "
    "doi:10.1161/CIR.0000000000001063. Table 14."
)

DOSES_ICFER = {
    "sacubitril_valsartana": {
        "nome": "Sacubitril/valsartana",
        "inicial": "49/51 mg VO 2x/dia; pode iniciar 24/26 mg 2x/dia",
        "alvo": "97/103 mg VO 2x/dia",
        "nota": "Use a calculadora específica de Entresto/Brasil para seleção da dose inicial e bloqueios de segurança.",
    },
    "bisoprolol": {
        "nome": "Bisoprolol",
        "inicial": "1,25 mg VO 1x/dia",
        "alvo": "10 mg VO 1x/dia",
    },
    "carvedilol": {
        "nome": "Carvedilol",
        "inicial": "3,125 mg VO 2x/dia",
        "alvo": "25-50 mg VO 2x/dia",
    },
    "carvedilol_cr": {
        "nome": "Carvedilol CR",
        "inicial": "10 mg VO 1x/dia",
        "alvo": "80 mg VO 1x/dia",
    },
    "metoprolol_succinato": {
        "nome": "Metoprolol succinato de liberação prolongada",
        "inicial": "12,5-25 mg VO 1x/dia",
        "alvo": "200 mg VO 1x/dia",
    },
    "espironolactona": {
        "nome": "Espironolactona",
        "inicial": "12,5-25 mg VO 1x/dia",
        "alvo": "25-50 mg VO 1x/dia",
        "nota": "A diretriz contraindica iniciar MRA se eGFR <=30 mL/min/1,73 m² ou K >=5,0 mEq/L.",
    },
    "eplerenona": {
        "nome": "Eplerenona",
        "inicial": "25 mg VO 1x/dia",
        "alvo": "50 mg VO 1x/dia",
        "nota": "A diretriz contraindica iniciar MRA se eGFR <=30 mL/min/1,73 m² ou K >=5,0 mEq/L; eGFR 31-49 requer metade da dose de início/titulação descrita no texto de suporte.",
    },
    "dapagliflozina": {
        "nome": "Dapagliflozina",
        "inicial": "10 mg VO 1x/dia",
        "alvo": "10 mg VO 1x/dia",
    },
    "empagliflozina": {
        "nome": "Empagliflozina",
        "inicial": "10 mg VO 1x/dia",
        "alvo": "10 mg VO 1x/dia",
    },
    "hidralazina_isossorbida_fixa": {
        "nome": "Hidralazina/dinitrato de isossorbida — combinação fixa",
        "inicial": "37,5 mg hidralazina + 20 mg dinitrato de isossorbida, VO 3x/dia",
        "alvo": "75 mg hidralazina + 40 mg dinitrato de isossorbida, VO 3x/dia",
    },
    "ivabradina": {
        "nome": "Ivabradina",
        "inicial": "5 mg VO 2x/dia",
        "alvo": "7,5 mg VO 2x/dia",
        "nota": "A dose não define indicação; a elegibilidade depende de ritmo sinusal, FC, FEVE e terapia beta-bloqueadora conforme diretriz.",
    },
    "vericiguat": {
        "nome": "Vericiguat",
        "inicial": "2,5 mg VO 1x/dia",
        "alvo": "10 mg VO 1x/dia",
    },
    "digoxina": {
        "nome": "Digoxina",
        "inicial": "0,125-0,25 mg VO 1x/dia",
        "alvo": "individualizar para concentração sérica 0,5 a <0,9 ng/mL",
        "nota": "A dose deve ser individualizada por idade, função renal, massa corporal e interações; use calculadora específica quando disponível.",
    },
}


def _dose_icfer(d: dict) -> dict:
    chave = d["farmaco"]
    item = DOSES_ICFER.get(chave)
    if not item:
        raise ValueError("Selecione um fármaco válido.")
    return {
        "farmaco": item["nome"],
        "dose_inicial": item["inicial"],
        "dose_alvo": item["alvo"],
        "nota": item.get("nota"),
    }


def _dose_icfer_txt(r: dict) -> str:
    texto = f"{r['farmaco']}: dose inicial {r['dose_inicial']}; dose-alvo {r['dose_alvo']}."
    if r.get("nota"):
        texto += f" {r['nota']}"
    return texto


_DOSE_ICFER = Calculator(
    slug="icfer-doses-iniciais-e-alvo-aha-2022",
    name="ICFER — doses iniciais e alvo da terapia farmacológica",
    theme="Doses — Insuficiência Cardíaca",
    purpose="Consulta interativa das doses iniciais e alvo publicadas na Tabela 14 AHA/ACC/HFSA 2022.",
    fields=[
        Field("farmaco", "Fármaco", "select", options=[
            {"value": k, "label": v["nome"]} for k, v in DOSES_ICFER.items()
        ])
    ],
    compute=_dose_icfer,
    interpret=_dose_icfer_txt,
    reference=AHA_HF_2022,
    kind="dose",
    limitations=[
        "É uma tabela de doses de referência, não um prescritor automático.",
        "A diretriz recomenda iniciar em doses baixas e titular às doses-alvo dos ensaios conforme tolerância; não é necessário atingir a dose-alvo de uma classe antes de iniciar outra classe fundamental.",
        "Se a dose-alvo não for tolerada, usar a maior dose tolerada.",
        "Pressão arterial, frequência cardíaca, eletrólitos, função renal, congestão e sintomas precisam ser integrados antes de cada titulação.",
        "Para sacubitril/valsartana, use a calculadora específica da bula brasileira para definir 50 versus 100 mg 2x/dia e washout de IECA.",
    ],
)


ICFER_DOSE_REGISTRY: dict[str, Calculator] = {_DOSE_ICFER.slug: _DOSE_ICFER}
