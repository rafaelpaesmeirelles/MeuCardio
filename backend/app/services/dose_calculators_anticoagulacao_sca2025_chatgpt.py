"""Anticoagulação parenteral na SCA — ACC/AHA 2025, Tabela 10.

Inclui HNF, bivalirudina e fondaparinux. Enoxaparina permanece em módulo
separado por ter lógica mais extensa de idade/ClCr/PCI e bula brasileira.

Fonte de produção: ChatGPT.
"""

from __future__ import annotations

from .calculators import Calculator, Field

FONTE_PRODUCAO = "chatgpt"

ACC_AHA_ACS_2025 = (
    "Rao SV, O'Donoghue ML, Ruel M, et al. 2025 ACC/AHA/ACEP/NAEMSP/SCAI Guideline for the "
    "Management of Patients With Acute Coronary Syndromes. J Am Coll Cardiol. 2025. "
    "doi:10.1016/j.jacc.2024.11.009. Table 10."
)


def _hnf_sca_2025(d: dict) -> dict:
    peso = float(d["peso"])
    cenario = d["cenario"]
    anticoagulante_previo = bool(d.get("anticoagulante_previo"))
    if peso <= 0:
        raise ValueError("Peso precisa ser maior que zero.")

    if cenario in {"terapia_inicial", "com_fibrinolitico"}:
        bolus = min(60 * peso, 4000)
        infusao = min(12 * peso, 1000)
        return {
            "farmaco": "Heparina não fracionada",
            "cenario": cenario,
            "bolus_ui": round(bolus),
            "infusao_ui_h": round(infusao),
            "alvo_aptt": "60-80 s",
        }

    # suporte da PCI
    if anticoagulante_previo:
        return {
            "farmaco": "Heparina não fracionada",
            "conduta": "titular_por_act",
            "alvo_act": "250-300 s",
            "motivo": "paciente já recebeu anticoagulante; ACC/AHA 2025 orienta HNF adicional conforme necessário para atingir ACT",
        }
    return {
        "farmaco": "Heparina não fracionada",
        "cenario": "PCI sem anticoagulação prévia",
        "bolus_min_ui": round(70 * peso),
        "bolus_max_ui": round(100 * peso),
        "dose_por_peso": "70-100 U/kg IV",
        "alvo_act": "250-300 s",
    }


def _hnf_sca_2025_txt(r: dict) -> str:
    if r.get("conduta") == "titular_por_act":
        return f"HNF: {r['motivo']}; alvo ACT {r['alvo_act']}."
    if "infusao_ui_h" in r:
        return (
            f"HNF: bolus {r['bolus_ui']} UI IV (60 UI/kg, máx 4.000 UI), seguido de "
            f"{r['infusao_ui_h']} UI/h (12 UI/kg/h, máx 1.000 UI/h), ajustar para aPTT {r['alvo_aptt']}."
        )
    return (
        f"HNF para PCI sem anticoagulante prévio: {r['bolus_min_ui']}-{r['bolus_max_ui']} UI IV "
        f"({r['dose_por_peso']}), visando ACT {r['alvo_act']}."
    )


_HNF_SCA_2025 = Calculator(
    slug="hnf-sca-pci-fibrinolise-acc-aha-2025",
    name="Heparina não fracionada — SCA, fibrinólise e PCI (ACC/AHA 2025)",
    theme="Doses — Hemodinâmica",
    purpose="Calcula bolus/infusão da HNF na SCA e o bolus para PCI sem anticoagulação prévia.",
    fields=[
        Field("peso", "Peso", "number", "kg", min=20, max=300),
        Field("cenario", "Cenário", "select", options=[
            {"value": "terapia_inicial", "label": "Terapia anticoagulante inicial da SCA"},
            {"value": "com_fibrinolitico", "label": "Associada à fibrinólise"},
            {"value": "pci", "label": "Suporte da PCI"},
        ]),
        Field("anticoagulante_previo", "Já recebeu anticoagulante antes da PCI", "boolean"),
    ],
    compute=_hnf_sca_2025,
    interpret=_hnf_sca_2025_txt,
    reference=ACC_AHA_ACS_2025,
    kind="dose",
    limitations=[
        "Na terapia inicial/fibrinólise: 60 UI/kg, máximo 4.000 UI, seguida de 12 UI/kg/h, máximo 1.000 UI/h, ajustada para aPTT 60-80 s.",
        "Na PCI sem anticoagulação prévia: 70-100 U/kg IV para ACT 250-300 s.",
        "Na PCI após anticoagulação prévia, a diretriz não fornece um bolus fixo universal; titular HNF adicional ao ACT.",
        "Protocolos institucionais podem usar alvos de ACT diferentes conforme uso de GP IIb/IIIa; não foram extrapolados nesta calculadora.",
    ],
)


def _bivalirudina_pci_2025(d: dict) -> dict:
    peso = float(d["peso"])
    clcr = float(d["clcr"])
    if peso <= 0 or clcr < 0:
        raise ValueError("Revise peso e ClCr.")
    bolus = 0.75 * peso
    taxa_mg_kg_h = 1.0 if clcr < 30 else 1.75
    taxa = taxa_mg_kg_h * peso
    return {
        "farmaco": "Bivalirudina",
        "bolus_mg": round(bolus, 1),
        "bolus_por_peso": "0,75 mg/kg IV",
        "infusao_mg_kg_h": taxa_mg_kg_h,
        "infusao_mg_h": round(taxa, 1),
        "duracao_pci": "durante a PCI",
        "pos_pci_ppci": "manter 2-4 h após PCI primária quando aplicável",
        "clcr_menor_30": clcr < 30,
    }


def _bivalirudina_pci_2025_txt(r: dict) -> str:
    renal = " ClCr <30 mL/min: infusão reduzida para 1 mg/kg/h." if r["clcr_menor_30"] else ""
    return (
        f"Bivalirudina: bolus {r['bolus_mg']} mg IV (0,75 mg/kg), seguido de "
        f"{r['infusao_mg_h']} mg/h ({r['infusao_mg_kg_h']} mg/kg/h) durante a PCI. "
        f"Na PCI primária, a Tabela 10 descreve manter a infusão por 2-4 h após o procedimento.{renal}"
    )


_BIVALIRUDINA_PCI_2025 = Calculator(
    slug="bivalirudina-pci-acc-aha-2025",
    name="Bivalirudina — PCI e ajuste renal (ACC/AHA 2025)",
    theme="Doses — Hemodinâmica",
    purpose="Calcula bolus e taxa de infusão da bivalirudina para suporte da PCI, com ajuste se ClCr <30.",
    fields=[
        Field("peso", "Peso", "number", "kg", min=20, max=300),
        Field("clcr", "Clearance de creatinina", "number", "mL/min", min=0, max=250),
    ],
    compute=_bivalirudina_pci_2025,
    interpret=_bivalirudina_pci_2025_txt,
    reference=ACC_AHA_ACS_2025,
    kind="dose",
    limitations=[
        "Bolus 0,75 mg/kg e infusão 1,75 mg/kg/h durante a PCI.",
        "ClCr <30 mL/min: reduzir a infusão para 1 mg/kg/h segundo a Tabela 10; o bolus permanece 0,75 mg/kg.",
        "Na PCI primária, a diretriz descreve infusão pós-PCI de 1,75 mg/kg/h por 2-4 h; em ClCr <30, preserve o ajuste renal e valide o protocolo institucional.",
    ],
)


def _fondaparinux_sca_2025(d: dict) -> dict:
    cenario = d["cenario"]
    clcr = float(d["clcr"])
    if clcr < 0:
        raise ValueError("ClCr não pode ser negativo.")
    if clcr < 30:
        return {
            "farmaco": "Fondaparinux",
            "conduta": "contraindicado_neste_esquema",
            "motivo": "ClCr <30 mL/min segundo a Tabela 10 ACC/AHA 2025",
        }
    if cenario == "pci":
        return {
            "farmaco": "Fondaparinux",
            "conduta": "nao_usar_isoladamente_para_suporte_da_pci",
            "motivo": "risco de trombose de cateter",
        }
    if cenario == "fibrinolise":
        return {
            "farmaco": "Fondaparinux",
            "inicial": "2,5 mg IV",
            "depois": "2,5 mg SC 1x/dia a partir do dia seguinte",
        }
    return {
        "farmaco": "Fondaparinux",
        "dose": "2,5 mg SC 1x/dia",
    }


def _fondaparinux_sca_2025_txt(r: dict) -> str:
    if r.get("conduta"):
        return f"Fondaparinux: não sugerir dose — {r['motivo']}."
    if r.get("inicial"):
        return f"Fondaparinux com fibrinólise: {r['inicial']}; depois {r['depois']}."
    return f"Fondaparinux: {r['dose']}."


_FONDAPARINUX_SCA_2025 = Calculator(
    slug="fondaparinux-sca-fibrinolise-pci-2025",
    name="Fondaparinux — SCA/fibrinólise e bloqueio na PCI (ACC/AHA 2025)",
    theme="Doses — Cardiologia Geral",
    purpose="Seleciona o esquema de fondaparinux e bloqueia ClCr <30 ou uso isolado para suporte da PCI.",
    fields=[
        Field("cenario", "Cenário", "select", options=[
            {"value": "inicial", "label": "Terapia inicial da SCA"},
            {"value": "fibrinolise", "label": "Associado à fibrinólise"},
            {"value": "pci", "label": "Suporte da PCI"},
        ]),
        Field("clcr", "Clearance de creatinina", "number", "mL/min", min=0, max=250),
    ],
    compute=_fondaparinux_sca_2025,
    interpret=_fondaparinux_sca_2025_txt,
    reference=ACC_AHA_ACS_2025,
    kind="dose",
    limitations=[
        "Terapia inicial: 2,5 mg SC 1x/dia.",
        "Com fibrinólise: 2,5 mg IV, depois 2,5 mg SC 1x/dia a partir do dia seguinte.",
        "Contraindicado se ClCr <30 mL/min na Tabela 10 consultada.",
        "Não usar fondaparinux isoladamente para suporte da PCI devido ao risco de trombose de cateter.",
    ],
)


ANTICOAGULACAO_SCA_2025_DOSE_REGISTRY: dict[str, Calculator] = {
    c.slug: c for c in [_HNF_SCA_2025, _BIVALIRUDINA_PCI_2025, _FONDAPARINUX_SCA_2025]
}
