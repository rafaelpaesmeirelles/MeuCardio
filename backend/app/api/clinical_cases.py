"""Casos clínicos interativos (Tarefa 11a).

Um caso, uma pergunta, um conjunto de opções — e só depois de responder o
médico vê a conduta correta e a evidência que a sustenta. A resposta certa
nunca é omitida da carga (o front decide quando mostrar); o que fica gravado
por médico é o histórico de tentativas, para Indicadores agregar taxa de
acerto ao longo do tempo.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user
from app.models.clinical_case import ClinicalCase, ClinicalCaseAttempt
from app.models.user import User

router = APIRouter(prefix="/api/casos-clinicos", tags=["casos clínicos interativos"])


def _resumo_tentativas(db: Session, user_id: int, case_id: int) -> dict:
    tentativas = (
        db.query(ClinicalCaseAttempt)
        .filter(ClinicalCaseAttempt.user_id == user_id, ClinicalCaseAttempt.case_id == case_id)
        .order_by(ClinicalCaseAttempt.created_at.desc())
        .all()
    )
    return {
        "tentativas": len(tentativas),
        "acertou_na_ultima": tentativas[0].acertou if tentativas else None,
    }


@router.get("")
def listar(db: Session = Depends(get_db), user: User = Depends(current_user)):
    casos = (
        db.query(ClinicalCase)
        .filter(ClinicalCase.published.is_(True))
        .order_by(ClinicalCase.tema, ClinicalCase.titulo)
        .all()
    )
    return [
        {
            "slug": c.slug, "titulo": c.titulo, "tema": c.tema, "nivel": c.nivel,
            **_resumo_tentativas(db, user.id, c.id),
        }
        for c in casos
    ]


@router.get("/{slug}")
def detalhe(slug: str, db: Session = Depends(get_db), user: User = Depends(current_user)):
    c = db.query(ClinicalCase).filter(
        ClinicalCase.slug == slug, ClinicalCase.published.is_(True)
    ).first()
    if c is None:
        raise HTTPException(status_code=404, detail="Caso clínico não encontrado.")
    return {
        "slug": c.slug, "titulo": c.titulo, "tema": c.tema, "nivel": c.nivel,
        "enunciado": c.enunciado, "pergunta": c.pergunta, "opcoes": c.opcoes,
        "resposta_correta": c.resposta_correta, "explicacao": c.explicacao,
        "source_refs": c.source_refs,
        **_resumo_tentativas(db, user.id, c.id),
    }


class Resposta(BaseModel):
    opcao_escolhida: int


@router.post("/{slug}/responder")
def responder(slug: str, dados: Resposta,
              db: Session = Depends(get_db), user: User = Depends(current_user)):
    c = db.query(ClinicalCase).filter(
        ClinicalCase.slug == slug, ClinicalCase.published.is_(True)
    ).first()
    if c is None:
        raise HTTPException(status_code=404, detail="Caso clínico não encontrado.")
    if not (0 <= dados.opcao_escolhida < len(c.opcoes or [])):
        raise HTTPException(status_code=422, detail="Opção inválida.")

    acertou = dados.opcao_escolhida == c.resposta_correta
    db.add(ClinicalCaseAttempt(
        user_id=user.id, case_id=c.id,
        opcao_escolhida=dados.opcao_escolhida, acertou=acertou,
    ))
    db.commit()
    return {"acertou": acertou, "resposta_correta": c.resposta_correta, "explicacao": c.explicacao}


@router.get("/meus/resumo")
def meu_resumo(db: Session = Depends(get_db), user: User = Depends(current_user)):
    """Para Indicadores: quantos casos distintos já foram tentados e taxa de
    acerto agregada, contando a tentativa mais recente de cada caso — refazer
    um caso não deve contar duas vezes na taxa de acerto."""
    subq = (
        db.query(
            ClinicalCaseAttempt.case_id,
            func.max(ClinicalCaseAttempt.created_at).label("ultima"),
        )
        .filter(ClinicalCaseAttempt.user_id == user.id)
        .group_by(ClinicalCaseAttempt.case_id)
        .subquery()
    )
    ultimas = (
        db.query(ClinicalCaseAttempt)
        .join(subq, (ClinicalCaseAttempt.case_id == subq.c.case_id)
              & (ClinicalCaseAttempt.created_at == subq.c.ultima))
        .filter(ClinicalCaseAttempt.user_id == user.id)
        .all()
    )
    acertos = sum(1 for a in ultimas if a.acertou)
    return {
        "casos_tentados": len(ultimas),
        "acertos": acertos,
        "taxa_acerto": round(acertos / len(ultimas), 3) if ultimas else None,
    }
