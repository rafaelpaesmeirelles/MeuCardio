"""Calculadoras de enoxaparina para SCA/ICP a partir da bula brasileira Clexane.

Fonte efetivamente consultada: bula Sanofi Medley Farmacêutica Ltda., registro
MS 1.8326.0336, aprovada pela Anvisa em 10/06/2019. A indicação estendida em
câncer foi posteriormente aprovada em 2025, mas não altera os esquemas de SCA
aqui modelados.

Fonte de produção: ChatGPT.
"""

from __future__ import annotations

from .calculators import Calculator, Field

FONTE_PRODUCAO = "chatgpt"

CLEXANE_BR = (
    "Clexane® (enoxaparina sódica). Bula Sanofi Medley Farmacêutica Ltda., "
    "MS 1.8326.0336, IB100619; aprovada pela Anvisa em 10/06/2019."
)


def _enoxaparina_sca(d: dict) -> dict:
    indicacao = d["indicacao"]
    idade = float(d["idade"])
    peso = float(d["peso"])
    clcr = float(d["clcr"])
    if idade <= 0 or peso <= 0 or clcr < 0:
        raise ValueError("Revise idade, peso e clearance de creatinina.")

    renal_severa = clcr < 30

    if indicacao == "ua_nstemi":
        intervalo = "a cada 24 h" if renal_severa else "a cada 12 h"
        dose = peso * 1.0
        return {
            "farmaco": "Enoxaparina",
            "indicacao": "Angina instável/IAM sem supra de ST",
            "dose_sc_mg": round(dose, 1),
            "dose_por_peso": "1 mg/kg SC",
            "intervalo": intervalo,
            "renal_severa": renal_severa,
        }

    # STEMI
    if idade < 75:
        bolus_iv_mg = 30.0
        dose_sc = min(peso * 1.0, 100.0)
        if renal_severa:
            intervalo = "a cada 24 h"
            regra_teto = "primeira dose SC máximo 100 mg; doses subsequentes 1 mg/kg"
        else:
            intervalo = "a cada 12 h"
            regra_teto = "duas primeiras doses SC máximo 100 mg cada; depois 1 mg/kg"
        return {
            "farmaco": "Enoxaparina",
            "indicacao": "IAM com supra de ST — idade <75 anos",
            "bolus_iv_mg": bolus_iv_mg,
            "dose_sc_inicial_mg": round(dose_sc, 1),
            "dose_por_peso": "1 mg/kg SC",
            "intervalo": intervalo,
            "regra_teto": regra_teto,
            "renal_severa": renal_severa,
        }

    # >=75 anos: sem bolus IV inicial
    if renal_severa:
        dose_sc = min(peso * 1.0, 100.0)
        return {
            "farmaco": "Enoxaparina",
            "indicacao": "IAM com supra de ST — idade ≥75 anos + ClCr <30 mL/min",
            "bolus_iv_mg": 0,
            "dose_sc_inicial_mg": round(dose_sc, 1),
            "dose_por_peso": "1 mg/kg SC",
            "intervalo": "a cada 24 h",
            "regra_teto": "primeira dose SC máximo 100 mg; sem bolus IV inicial",
            "renal_severa": True,
        }

    dose_sc = min(peso * 0.75, 75.0)
    return {
        "farmaco": "Enoxaparina",
        "indicacao": "IAM com supra de ST — idade ≥75 anos",
        "bolus_iv_mg": 0,
        "dose_sc_inicial_mg": round(dose_sc, 1),
        "dose_por_peso": "0,75 mg/kg SC",
        "intervalo": "a cada 12 h",
        "regra_teto": "duas primeiras doses SC máximo 75 mg cada; depois 0,75 mg/kg; sem bolus IV inicial",
        "renal_severa": False,
    }


def _enoxaparina_sca_txt(r: dict) -> str:
    if r["indicacao"] == "Angina instável/IAM sem supra de ST":
        return (
            f"Enoxaparina {r['dose_sc_mg']} mg SC ({r['dose_por_peso']}) {r['intervalo']}. "
            "Na bula, usar concomitantemente AAS oral 100-325 mg/dia; duração usual 2-8 dias."
        )
    bolus = "sem bolus IV inicial" if r["bolus_iv_mg"] == 0 else f"bolus IV inicial {r['bolus_iv_mg']} mg"
    return (
        f"{r['indicacao']}: {bolus} + {r['dose_sc_inicial_mg']} mg SC agora "
        f"({r['dose_por_peso']}), depois {r['intervalo']}. {r['regra_teto']}."
    )


_ENOXAPARINA_SCA = Calculator(
    slug="enoxaparina-sca-idade-renal-bula-brasil",
    name="Enoxaparina — SCA por idade, peso e função renal (Clexane Brasil)",
    theme="Doses — Cardiologia Geral",
    purpose="Calcula o esquema de enoxaparina na SCA, incluindo os quatro ramos de STEMI por idade e ClCr.",
    fields=[
        Field("indicacao", "Cenário", "select", options=[
            {"value": "ua_nstemi", "label": "Angina instável / IAM sem supra de ST"},
            {"value": "stemi", "label": "IAM com supra de ST"},
        ]),
        Field("idade", "Idade", "number", "anos", min=18, max=120),
        Field("peso", "Peso", "number", "kg", min=20, max=300),
        Field("clcr", "Clearance de creatinina", "number", "mL/min", min=0, max=250),
    ],
    compute=_enoxaparina_sca,
    interpret=_enoxaparina_sca_txt,
    reference=CLEXANE_BR,
    kind="dose",
    limitations=[
        "No STEMI <75 anos: bolus IV 30 mg + 1 mg/kg SC; com ClCr ≥30, q12h e teto 100 mg nas duas primeiras doses SC; com ClCr <30, q24h e teto 100 mg na primeira dose SC.",
        "No STEMI ≥75 anos: NÃO administrar bolus IV inicial. Com ClCr ≥30, 0,75 mg/kg q12h, teto 75 mg nas duas primeiras doses; com ClCr <30, 1 mg/kg q24h, teto 100 mg na primeira dose.",
        "Na angina instável/IAM sem supra: 1 mg/kg q12h; se ClCr <30, 1 mg/kg q24h.",
        "ClCr 30-50 mL/min não exige ajuste na bula consultada, mas requer monitorização clínica cuidadosa.",
        "A calculadora não substitui avaliação de sangramento, peso extremo, trombocitopenia/HIT, anestesia neuraxial ou estratégia de reperfusão.",
    ],
)


def _enoxaparina_pci_stemi(d: dict) -> dict:
    peso = float(d["peso"])
    horas = float(d["horas_desde_ultima_sc"])
    if peso <= 0 or horas < 0:
        raise ValueError("Revise peso e intervalo desde a última dose SC.")
    if horas < 8:
        return {
            "conduta": "sem_dose_adicional",
            "motivo": "última dose SC administrada há menos de 8 horas antes da insuflação do balão",
        }
    if horas == 8:
        return {
            "conduta": "VERIFICAÇÃO HUMANA NECESSÁRIA",
            "motivo": "a bula consultada explicita <8 h sem dose e >8 h com dose adicional; não explicita exatamente 8 h",
        }
    return {
        "farmaco": "Enoxaparina",
        "conduta": "bolus_iv_adicional",
        "dose_mg": round(peso * 0.3, 1),
        "dose_por_peso": "0,3 mg/kg IV",
    }


def _enoxaparina_pci_stemi_txt(r: dict) -> str:
    if r["conduta"] == "sem_dose_adicional":
        return f"Não administrar dose adicional de enoxaparina na ICP: {r['motivo']}."
    if r["conduta"] == "VERIFICAÇÃO HUMANA NECESSÁRIA":
        return f"VERIFICAÇÃO HUMANA NECESSÁRIA — {r['motivo']}."
    return f"Administrar enoxaparina {r['dose_mg']} mg IV ({r['dose_por_peso']}) antes da ICP."


_ENOXAPARINA_PCI_STEMI = Calculator(
    slug="enoxaparina-stemi-dose-adicional-icp",
    name="Enoxaparina — dose IV adicional na ICP após STEMI",
    theme="Doses — Hemodinâmica",
    purpose="Decide e calcula a dose IV adicional de 0,3 mg/kg conforme o intervalo desde a última dose SC.",
    fields=[
        Field("peso", "Peso", "number", "kg", min=20, max=300),
        Field("horas_desde_ultima_sc", "Horas desde a última dose subcutânea de enoxaparina", "number", "h", min=0, max=48),
    ],
    compute=_enoxaparina_pci_stemi,
    interpret=_enoxaparina_pci_stemi_txt,
    reference=CLEXANE_BR,
    kind="dose",
    limitations=[
        "Se a última dose SC foi administrada há menos de 8 h antes da insuflação do balão, a bula não recomenda dose adicional.",
        "Se foi há mais de 8 h, administrar 0,3 mg/kg IV.",
        "Exatamente 8 h não é explicitado no texto consultado e por isso retorna VERIFICAÇÃO HUMANA NECESSÁRIA, em vez de interpolar a regra.",
    ],
)


ENOXAPARINA_SCA_DOSE_REGISTRY: dict[str, Calculator] = {
    c.slug: c for c in [_ENOXAPARINA_SCA, _ENOXAPARINA_PCI_STEMI]
}
