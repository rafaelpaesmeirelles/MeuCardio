from dataclasses import asdict

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

router = APIRouter(prefix="/api/calculators", tags=["calculadoras"])


@router.get("")
def list_calculators(_=Depends(current_user)):
    return [
        {"slug": c.slug, "name": c.name, "theme": c.theme, "purpose": c.purpose,
         "status": c.status, "kind": c.kind}
        for c in sorted(calc.REGISTRY.values(), key=lambda c: c.name)
    ]


@router.get("/{slug}")
def get_calculator(slug: str, _=Depends(current_user)):
    c = calc.REGISTRY.get(slug)
    if not c:
        raise HTTPException(status_code=404, detail="Calculadora não encontrada.")
    return {
        "slug": c.slug, "name": c.name, "theme": c.theme, "purpose": c.purpose,
        "status": c.status, "kind": c.kind, "reference": c.reference,
        "limitations": c.limitations, "fields": [asdict(f) for f in c.fields],
    }


@router.post("/{slug}/run")
def run_calculator(slug: str, payload: dict, _=Depends(current_user)):
    try:
        return calc.run(slug, payload)
    except KeyError:
        raise HTTPException(status_code=404, detail="Calculadora não encontrada.")
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except (TypeError, ZeroDivisionError):
        raise HTTPException(status_code=422, detail="Revise os valores informados.")


class GerarDocumentoIn(BaseModel):
    patient_id: int | None = None
    patient_name: str | None = None
    contexto_clinico: str | None = None
    conduta_recomendada: str | None = None
    endereco: str | None = None
    payload: dict


@router.post("/{slug}/gerar-documento", status_code=201)
def gerar_documento(
    slug: str, dados: GerarDocumentoIn, db: Session = Depends(get_db), user=Depends(current_user),
):
    """Laudo genérico para qualquer calculadora; resultado recalculado no servidor."""
    c = calc.REGISTRY.get(slug)
    if not c:
        raise HTTPException(status_code=404, detail="Calculadora não encontrada.")
    if dados.patient_id is not None:
        p = db.get(Patient, dados.patient_id)
        if not p or p.created_by != user.id:
            raise HTTPException(status_code=404, detail="Paciente não encontrado.")
    if dados.endereco not in (None, "residencial", "profissional"):
        raise HTTPException(status_code=422, detail="endereco precisa ser 'residencial', 'profissional' ou omitido.")
    try:
        r = calc.run(slug, dados.payload)
    except KeyError:
        raise HTTPException(status_code=404, detail="Calculadora não encontrada.")
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except (TypeError, ZeroDivisionError):
        raise HTTPException(status_code=422, detail="Revise os valores informados antes de gerar o documento.")

    resultado, interpretacao = r["result"], r.get("interpretation")
    linhas: list[str] = [c.name.upper(), ""]
    if dados.contexto_clinico:
        linhas.extend([f"Contexto clínico / procedimento: {dados.contexto_clinico}", ""])
    if interpretacao:
        linhas.extend([interpretacao, ""])
    resumo = ", ".join(f"{k.replace('_', ' ')}: {v}" for k, v in resultado.items() if k != "fora_da_faixa")
    linhas.extend([f"Resultado: {resumo}", ""])
    if dados.conduta_recomendada:
        linhas.extend(["Conduta e recomendações do médico responsável:", dados.conduta_recomendada, ""])
    linhas.append(f"Referência: {c.reference}")
    if c.limitations:
        linhas.append("Limitações:")
        linhas.extend(f"- {l}" for l in c.limitations)
        linhas.append("")
    linhas.append("Este documento é uma ferramenta de apoio à decisão clínica, com o resultado recalculado no servidor a partir dos dados informados. Não substitui o julgamento clínico do médico responsável.")
    corpo = "\n".join(linhas)

    gerado = GeneratedDocument(
        patient_id=dados.patient_id, template_id=None, created_by=user.id,
        doc_type="calculadora_clinica", title=c.name, rendered_body=corpo,
        endereco_exibido=dados.endereco,
        variables={
            "slug": slug, "payload": dados.payload,
            "contexto_clinico": dados.contexto_clinico or "",
            "conduta_recomendada": dados.conduta_recomendada or "",
            "fonte_producao_extensao": "chatgpt" if slug in {"gscri", "sort", "s-mpm"} else "",
        },
    )
    db.add(gerado); db.flush()
    nome_paciente = (dados.patient_name or "").strip()
    if nome_paciente:
        gerado.patient_name_cifrado = cofre.cifrar_campo(nome_paciente, gerado.id)
    db.add(AuditLog(user_id=user.id, action="gerar_documento_calculadora",
                    entity="generated_document", entity_id=str(gerado.id), detail={"calculadora": slug}))
    db.commit(); db.refresh(gerado)
    return {
        "id": gerado.id, "title": gerado.title, "doc_type": gerado.doc_type,
        "rendered_body": gerado.rendered_body, "created_at": gerado.created_at,
        "patient_name": nome_paciente or None, "medico": document_identity(user),
        "result": resultado, "interpretation": interpretacao,
    }