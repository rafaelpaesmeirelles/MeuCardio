"""Avaliação Cardiológica Pré-Operatória de Risco Cirúrgico.

Reúne calculadoras perioperatórias validadas num documento clínico pronto para
impressão, assinatura digital e envio ao paciente. Os resultados são sempre
recalculados no servidor a partir dos campos brutos.

Fonte: ChatGPT nas extensões perioperatórias produzidas em 07/08/2026.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user
from app.models.audit import AuditLog
from app.models.clinical_docs import GeneratedDocument
from app.models.round import Patient
from app.services import calculators as calc
from app.services import cofre
from app.services.perioperative_calculators import PERIOPERATIVE_REGISTRY
from app.services.perioperative_calculators_geriatria import GERIATRIC_PERIOPERATIVE_REGISTRY
from app.services.perioperative_calculators_mortalidade import MORTALITY_PERIOPERATIVE_REGISTRY
from app.services.perioperative_calculators_sort import SORT_PERIOPERATIVE_REGISTRY
from app.services.professional_profile import document_identity

calc.REGISTRY.update(PERIOPERATIVE_REGISTRY)
calc.REGISTRY.update(GERIATRIC_PERIOPERATIVE_REGISTRY)
calc.REGISTRY.update(MORTALITY_PERIOPERATIVE_REGISTRY)
calc.REGISTRY.update(SORT_PERIOPERATIVE_REGISTRY)

router = APIRouter(prefix="/api/avaliacao-preoperatoria", tags=["avaliacao-preoperatoria"])
DOC_TYPE = "avaliacao_preoperatoria"
TITULO_DOCUMENTO = "Avaliação Cardiológica Pré-Operatória de Risco Cirúrgico"


class GerarIn(BaseModel):
    patient_id: int | None = None
    patient_name: str | None = None
    idade: int | None = None
    procedimento_planejado: str
    indicacao_cirurgica: str | None = None
    capacidade_funcional: str | None = None
    rcri: dict | None = None
    gupta: dict | None = None
    dasi: dict | None = None
    aub_has2: dict | None = None
    vsg_cri: dict | None = None
    gscri: dict | None = None
    sort: dict | None = None
    s_mpm: dict | None = None
    conduta_recomendada: str | None = None
    endereco: str | None = None


def _resultado_calculadora(slug: str, payload: dict | None) -> tuple[dict, str] | None:
    if not payload:
        return None
    try:
        r = calc.run(slug, payload)
    except (KeyError, ValueError, TypeError, ZeroDivisionError) as e:
        raise HTTPException(status_code=422, detail=f"Dados inválidos para {slug}: {e}") from e
    return r["result"], r["interpretation"]


def _montar_corpo(dados: GerarIn, resultados: list[tuple[str, tuple[dict, str] | None]]) -> str:
    linhas: list[str] = ["AVALIAÇÃO CARDIOLÓGICA PRÉ-OPERATÓRIA DE RISCO CIRÚRGICO", ""]
    if dados.idade is not None:
        linhas.append(f"Idade do paciente: {dados.idade} anos")
    linhas.append(f"Procedimento planejado: {dados.procedimento_planejado}")
    if dados.indicacao_cirurgica:
        linhas.append(f"Indicação cirúrgica: {dados.indicacao_cirurgica}")
    if dados.capacidade_funcional:
        linhas.append(f"Capacidade funcional (descrição clínica): {dados.capacidade_funcional}")
    linhas.append("")

    for nome, item in resultados:
        if not item:
            continue
        resultado, interpretacao = item
        if nome == "RCRI":
            linhas.append(f"RCRI: {resultado['pontos']} ponto(s) — Classe {resultado['classe']}.")
        elif nome == "Gupta MICA":
            linhas.append(f"Gupta MICA — risco de IAM/parada cardíaca: {resultado['risco_pct']}%.")
        elif nome == "DASI":
            linhas.append(f"DASI: {resultado['score']}/58,2 — capacidade funcional {resultado['capacidade_funcional'].replace('_', ' ')}.")
        elif nome == "AUB-HAS2":
            linhas.append(f"AUB-HAS2: {resultado['score']}/6 — risco {resultado['categoria']}.")
        elif nome == "VSG-CRI":
            linhas.append(f"VSG-CRI (cirurgia vascular): {resultado['score']} ponto(s) — risco {resultado['categoria']}.")
        elif nome == "GSCRI":
            linhas.append(f"GSCRI (≥65 anos) — risco de IAM/parada cardíaca: {resultado['risco_pct']}%.")
        elif nome == "SORT":
            linhas.append(f"SORT — mortalidade por todas as causas em 30 dias: {resultado['risco_pct']}%.")
        elif nome == "S-MPM":
            linhas.append(f"S-MPM — mortalidade por todas as causas em 30 dias: {resultado['score']}/9, Classe {resultado['classe']}, {resultado['mortalidade_30d']}.")
        if interpretacao:
            linhas.append(interpretacao)
        linhas.append("")

    linhas.extend([
        "INTEGRAÇÃO DOS MÉTODOS",
        "Os escores estimam desfechos diferentes e não devem ser somados ou promediados. RCRI, Gupta MICA, AUB-HAS2, VSG-CRI e GSCRI focam risco cardiovascular com endpoints próprios; SORT e S-MPM estimam mortalidade cirúrgica global; DASI mede capacidade funcional. A decisão final integra doença cardiovascular ativa, risco do procedimento, fragilidade, capacidade funcional e a possibilidade de que investigação adicional modifique o manejo.",
        "",
    ])
    if dados.conduta_recomendada:
        linhas.extend(["Conduta e recomendações do médico responsável:", dados.conduta_recomendada, ""])
    linhas.append("Ferramenta de apoio à decisão clínica; não substitui julgamento médico nem avaliação anestésica. Árvores de decisão e referências completas: Biblioteca Corvia > Perioperatório.")
    return "\n".join(linhas)


@router.post("/gerar", status_code=201)
def gerar(dados: GerarIn, db: Session = Depends(get_db), user=Depends(current_user)):
    if not dados.procedimento_planejado.strip():
        raise HTTPException(status_code=422, detail="Informe o procedimento planejado.")
    if dados.patient_id is not None:
        p = db.get(Patient, dados.patient_id)
        if not p or p.created_by != user.id:
            raise HTTPException(status_code=404, detail="Paciente não encontrado.")
    if dados.endereco not in (None, "residencial", "profissional"):
        raise HTTPException(status_code=422, detail="endereco precisa ser 'residencial', 'profissional' ou omitido.")

    payloads = {
        "rcri": dados.rcri, "gupta-mica": dados.gupta, "dasi": dados.dasi,
        "aub-has2": dados.aub_has2, "vsg-cri": dados.vsg_cri, "gscri": dados.gscri,
        "sort": dados.sort, "s-mpm": dados.s_mpm,
    }
    if all(v is None for v in payloads.values()):
        raise HTTPException(status_code=422, detail="Calcule ao menos um método antes de gerar o documento.")

    calculados = {slug: _resultado_calculadora(slug, payload) for slug, payload in payloads.items()}
    resultados = [
        ("RCRI", calculados["rcri"]), ("Gupta MICA", calculados["gupta-mica"]),
        ("DASI", calculados["dasi"]), ("AUB-HAS2", calculados["aub-has2"]),
        ("VSG-CRI", calculados["vsg-cri"]), ("GSCRI", calculados["gscri"]),
        ("SORT", calculados["sort"]), ("S-MPM", calculados["s-mpm"]),
    ]
    corpo = _montar_corpo(dados, resultados)

    variaveis = {
        "idade": str(dados.idade) if dados.idade is not None else "",
        "procedimento_planejado": dados.procedimento_planejado,
        "indicacao_cirurgica": dados.indicacao_cirurgica or "",
        "capacidade_funcional": dados.capacidade_funcional or "",
        "conduta_recomendada": dados.conduta_recomendada or "",
        **{slug.replace('-', '_'): payload or {} for slug, payload in payloads.items()},
        "fonte_producao_extensoes": "chatgpt",
    }

    gerado = GeneratedDocument(patient_id=dados.patient_id, template_id=None, created_by=user.id, doc_type=DOC_TYPE,
        title=TITULO_DOCUMENTO, rendered_body=corpo, endereco_exibido=dados.endereco, variables=variaveis)
    db.add(gerado); db.flush()
    nome_paciente = (dados.patient_name or "").strip()
    if nome_paciente:
        gerado.patient_name_cifrado = cofre.cifrar_campo(nome_paciente, gerado.id)
    db.add(AuditLog(user_id=user.id, action="gerar_avaliacao_preoperatoria", entity="generated_document",
        entity_id=str(gerado.id), detail={f"tem_{slug.replace('-', '_')}": calculados[slug] is not None for slug in calculados}))
    db.commit(); db.refresh(gerado)
    return {
        "id": gerado.id, "title": gerado.title, "doc_type": gerado.doc_type,
        "rendered_body": gerado.rendered_body, "created_at": gerado.created_at,
        "patient_name": nome_paciente or None, "medico": document_identity(user),
        **{slug.replace('-', '_'): calculados[slug][0] if calculados[slug] else None for slug in calculados},
    }