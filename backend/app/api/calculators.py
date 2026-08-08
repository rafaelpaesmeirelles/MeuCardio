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
from app.services.professional_profile import document_identity

# Calculadoras perioperatórias produzidas pelo ChatGPT são registradas no mesmo
# catálogo usado pelo frontend genérico e pela avaliação pré-operatória.
# A atualização ocorre após `calculators` estar completamente importado, evitando
# duplicar as dataclasses/infraestrutura existentes.
calc.REGISTRY.update(PERIOPERATIVE_REGISTRY)

router = APIRouter(prefix="/api/calculators", tags=["calculadoras"])


def _fonte(c):
    return getattr(c, "fonte_producao", None)


@router.get("")
def list_calculators(_=Depends(current_user)):
    return [
        {
            "slug": c.slug,
            "name": c.name,
            "theme": c.theme,
            "purpose": c.purpose,
            "status": c.status,
            "kind": c.kind,
            "fonte_producao": _fonte(c),
        }
        for c in sorted(calc.REGISTRY.values(), key=lambda c: c.name)
    ]


@router.get("/{slug}")
def get_calculator(slug: str, _=Depends(current_user)):
    c = calc.REGISTRY.get(slug)
    if not c:
        raise HTTPException(status_code=404, detail="Calculadora não encontrada.")
    return {
        "slug": c.slug,
        "name": c.name,
        "theme": c.theme,
        "purpose": c.purpose,
        "status": c.status,
        "kind": c.kind,
        "fonte_producao": _fonte(c),
        "reference": c.reference,
        "limitations": c.limitations,
        "fields": [asdict(f) for f in c.fields],
    }


@router.post("/{slug}/run")
def run_calculator(slug: str, payload: dict, _=Depends(current_user)):
    try:
        result = calc.run(slug, payload)
        c = calc.REGISTRY.get(slug)
        result["fonte_producao"] = _fonte(c) if c else None
        return result
    except KeyError:
        raise HTTPException(status_code=404, detail="Calculadora não encontrada.")
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except (TypeError, ZeroDivisionError):
        raise HTTPException(status_code=422, detail="Revise os valores informados.")


class GerarDocumentoIn(BaseModel):
    patient_id: int | None = None
    patient_name: str | None = None
    # Texto livre — nem toda calculadora é sobre um procedimento cirúrgico
    # (CHA₂DS₂-VASc é sobre risco de AVC em FA, QTc é sobre segurança de
    # fármaco etc.), então o rótulo não presume cirurgia; quem preenche
    # escreve o que for pertinente (procedimento planejado, contexto da
    # avaliação, motivo da consulta).
    contexto_clinico: str | None = None
    conduta_recomendada: str | None = None
    endereco: str | None = None
    payload: dict


@router.post("/{slug}/gerar-documento", status_code=201)
def gerar_documento(
    slug: str, dados: GerarDocumentoIn, db: Session = Depends(get_db), user=Depends(current_user),
):
    """Laudo genérico de calculadora clínica — dados do paciente (opcionais,
    anonimizados como o resto do Round) + contexto clínico + resultado
    recalculado no servidor (nunca confia em número que o cliente diga ter
    obtido) + conduta do médico, pronto para assinar, imprimir e enviar.

    Reaproveita a mesma infraestrutura genérica de `GeneratedDocument` já
    usada por Atestado/Laudo/Avaliação Pré-Operatória: as rotas de
    `app/api/documents.py` (`/gerados/{id}/pdf`, `/assinatura-externa`,
    `/enviar-email`) servem este documento sem alteração nenhuma. Funciona
    para qualquer uma das calculadoras do catálogo, não só as de risco
    cirúrgico — pedido do Rafael em 07/08/2026 ("todas as calculadoras
    habilitadas para... gerar laudo completo do resultado").
    """
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
        linhas.append(f"Contexto clínico / procedimento: {dados.contexto_clinico}")
        linhas.append("")
    if interpretacao:
        linhas.append(interpretacao)
        linhas.append("")
    resumo = ", ".join(
        f"{k.replace('_', ' ')}: {v}" for k, v in resultado.items() if k != "fora_da_faixa"
    )
    linhas.append(f"Resultado: {resumo}")
    linhas.append("")
    if dados.conduta_recomendada:
        linhas.append("Conduta e recomendações do médico responsável:")
        linhas.append(dados.conduta_recomendada)
        linhas.append("")
    linhas.append(f"Referência: {c.reference}")
    if c.limitations:
        linhas.append("Limitações:")
        linhas.extend(f"- {l}" for l in c.limitations)
        linhas.append("")
    linhas.append(
        "Este documento é uma ferramenta de apoio à decisão clínica, com o resultado recalculado "
        "no servidor a partir dos dados informados. Não substitui o julgamento clínico do médico "
        "responsável."
    )
    corpo = "\n".join(linhas)

    gerado = GeneratedDocument(
        patient_id=dados.patient_id,
        template_id=None,
        created_by=user.id,
        doc_type="calculadora_clinica",
        title=c.name,
        rendered_body=corpo,
        endereco_exibido=dados.endereco,
        variables={
            "slug": slug,
            "payload": dados.payload,
            "contexto_clinico": dados.contexto_clinico or "",
            "conduta_recomendada": dados.conduta_recomendada or "",
        },
    )
    db.add(gerado)
    db.flush()
    nome_paciente = (dados.patient_name or "").strip()
    if nome_paciente:
        gerado.patient_name_cifrado = cofre.cifrar_campo(nome_paciente, gerado.id)

    db.add(
        AuditLog(
            user_id=user.id,
            action="gerar_documento_calculadora",
            entity="generated_document",
            entity_id=str(gerado.id),
            detail={"calculadora": slug},
        )
    )
    db.commit()
    db.refresh(gerado)
    return {
        "id": gerado.id,
        "title": gerado.title,
        "doc_type": gerado.doc_type,
        "rendered_body": gerado.rendered_body,
        "created_at": gerado.created_at,
        "patient_name": nome_paciente or None,
        "medico": document_identity(user),
        "result": resultado,
        "interpretation": interpretacao,
    }
