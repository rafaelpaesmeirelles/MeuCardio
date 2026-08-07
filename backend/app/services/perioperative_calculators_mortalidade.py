"""S-MPM: mortalidade global em 30 dias. Fonte de produção: ChatGPT."""
from __future__ import annotations
from app.services.calculators import Calculator, Field

_SMPM_ASA = {1: 0, 2: 2, 3: 4, 4: 5, 5: 6}
_SMPM_PROCEDURE = {"baixo": 0, "intermediario": 1, "alto": 2}


def _smpm(d: dict) -> dict:
    asa, proc = int(d["asa"]), d["risco_procedimento"]
    if asa not in _SMPM_ASA or proc not in _SMPM_PROCEDURE:
        raise ValueError("Dados categóricos inválidos para S-MPM.")
    score = _SMPM_ASA[asa] + _SMPM_PROCEDURE[proc] + (1 if d.get("emergencia") else 0)
    if score <= 4: classe, mortalidade = "I", "<0,5%"
    elif score <= 6: classe, mortalidade = "II", "1,5–4,0%"
    else: classe, mortalidade = "III", ">10%"
    return {"score": score, "max": 9, "classe": classe, "mortalidade_30d": mortalidade, "endpoint": "mortalidade por todas as causas em 30 dias"}


def _smpm_txt(r: dict) -> str:
    return f"S-MPM {r['score']}/9 — Classe {r['classe']}; mortalidade em 30 dias {r['mortalidade_30d']}. É mortalidade cirúrgica global, não risco cardíaco específico."


MORTALITY_PERIOPERATIVE_REGISTRY = {
    "s-mpm": Calculator(
        slug="s-mpm", name="S-MPM — Surgical Mortality Probability Model", theme="Perioperatório",
        purpose="Mortalidade por todas as causas em 30 dias após cirurgia não cardíaca.",
        fields=[
            Field("asa", "Classe ASA", "select", options=[{"value": 1, "label": "ASA I — 0"}, {"value": 2, "label": "ASA II — 2"}, {"value": 3, "label": "ASA III — 4"}, {"value": 4, "label": "ASA IV — 5"}, {"value": 5, "label": "ASA V — 6"}]),
            Field("risco_procedimento", "Classe de risco do procedimento no S-MPM", "select", options=[{"value": "baixo", "label": "Baixo — 0"}, {"value": "intermediario", "label": "Intermediário — 1"}, {"value": "alto", "label": "Alto — 2"}], help="A taxonomia original do S-MPM não é idêntica às categorias ESC/AHA."),
            Field("emergencia", "Cirurgia de emergência — +1", "boolean"),
        ],
        reference="Glance LG, Lustik SJ, Hannan EL, et al. Ann Surg. 2012;255(4):696-702. PMID: 22418007. DOI: 10.1097/SLA.0b013e31824b45af.",
        compute=_smpm, interpret=_smpm_txt,
        limitations=["Endpoint: mortalidade global em 30 dias.", "A categoria de risco do procedimento é específica da metodologia original; em dúvida: VERIFICAÇÃO HUMANA NECESSÁRIA."],
    )
}