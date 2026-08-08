"""Calculadora de mortalidade cirúrgica geral no perioperatório.

Fonte de produção: ChatGPT.
O S-MPM não é um escore de MACE/MICA; seu endpoint é mortalidade por todas as
causas em 30 dias após cirurgia não cardíaca.
"""

from __future__ import annotations

from app.services.calculators import Calculator, Field

SOURCE_PRODUCTION = "chatgpt"


_SMPM_ASA = {1: 0, 2: 2, 3: 4, 4: 5, 5: 6}
_SMPM_PROCEDURE = {"baixo": 0, "intermediario": 1, "alto": 2}


def _smpm(d: dict) -> dict:
    asa = int(d["asa"])
    if asa not in _SMPM_ASA:
        raise ValueError("Classe ASA inválida para S-MPM.")
    procedimento = d["risco_procedimento"]
    if procedimento not in _SMPM_PROCEDURE:
        raise ValueError("Classe de risco do procedimento inválida para S-MPM.")

    score = _SMPM_ASA[asa] + _SMPM_PROCEDURE[procedimento]
    score += 1 if d.get("emergencia") else 0

    if score <= 4:
        classe = "I"
        mortalidade = "<0,5%"
    elif score <= 6:
        classe = "II"
        mortalidade = "1,5–4,0%"
    else:
        classe = "III"
        mortalidade = ">10%"

    return {
        "score": score,
        "max": 9,
        "classe": classe,
        "mortalidade_30d": mortalidade,
        "endpoint": "mortalidade por todas as causas em 30 dias",
    }


def _smpm_txt(r: dict) -> str:
    return (
        f"S-MPM {r['score']}/9 — Classe {r['classe']}; mortalidade estimada em 30 dias "
        f"{r['mortalidade_30d']} na classificação original. Este é um escore de mortalidade "
        "cirúrgica global, não um escore específico de IAM/parada cardíaca. A classe de risco "
        "do procedimento deve ser atribuída de forma consistente com a metodologia adotada; "
        "a categorização empírica original do S-MPM não é idêntica a todas as tabelas ESC/AHA."
    )


MORTALITY_PERIOPERATIVE_REGISTRY: dict[str, Calculator] = {
    "s-mpm": Calculator(
        slug="s-mpm",
        name="S-MPM — Surgical Mortality Probability Model",
        theme="Perioperatório",
        purpose="Estimar mortalidade por todas as causas em 30 dias após cirurgia não cardíaca.",
        fields=[
            Field("asa", "Classe ASA", "select", options=[
                {"value": 1, "label": "ASA I — 0 ponto"},
                {"value": 2, "label": "ASA II — 2 pontos"},
                {"value": 3, "label": "ASA III — 4 pontos"},
                {"value": 4, "label": "ASA IV — 5 pontos"},
                {"value": 5, "label": "ASA V — 6 pontos"},
            ]),
            Field("risco_procedimento", "Classe de risco do procedimento no S-MPM", "select", options=[
                {"value": "baixo", "label": "Baixo risco — 0 ponto"},
                {"value": "intermediario", "label": "Risco intermediário — 1 ponto"},
                {"value": "alto", "label": "Alto risco — 2 pontos"},
            ], help="A classificação empírica original do S-MPM pode divergir de classificações ESC/AHA contemporâneas."),
            Field("emergencia", "Cirurgia de emergência — +1 ponto", "boolean"),
        ],
        reference=(
            "Glance LG, Lustik SJ, Hannan EL, et al. The Surgical Mortality Probability Model: "
            "derivation and validation of a simple risk prediction rule for noncardiac surgery. "
            "Ann Surg. 2012;255(4):696-702. PMID: 22418007. "
            "DOI: 10.1097/SLA.0b013e31824b45af."
        ),
        compute=_smpm,
        interpret=_smpm_txt,
        limitations=[
            "Endpoint: mortalidade por todas as causas em 30 dias; não confundir com risco cardíaco específico.",
            "A classificação do risco do procedimento no estudo foi empiricamente derivada e pode não coincidir com classificações ESC/AHA.",
            "Não substitui modelos cirúrgicos contemporâneos mais granulares quando estes estão disponíveis.",
        ],
    ),
}
