"""Casos clínicos interativos (Tarefa 11a).

Um caso, uma pergunta, um conjunto de opções — e só depois de responder o
médico vê a conduta correta e a evidência que a sustenta. A resposta certa e a
explicação não fazem parte do GET inicial: escondê-las apenas no frontend
permitiria descobri-las no JSON antes da tentativa. O que fica gravado por
médico é o histórico de tentativas, para Indicadores agregar taxa de acerto.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func, or_
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


@router.get("/themes")
def temas(db: Session = Depends(get_db), _=Depends(current_user)):
    rows = (
        db.query(ClinicalCase.tema, func.count(ClinicalCase.id))
        .filter(ClinicalCase.published.is_(True))
        .group_by(ClinicalCase.tema)
        .order_by(ClinicalCase.tema)
        .all()
    )
    return [{"theme": theme or "Outros", "count": int(count)} for theme, count in rows]


@router.get("")
def listar(
    q: str | None = Query(None, max_length=160),
    theme: str | None = Query(None, max_length=120),
    limit: int = Query(60, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    query = db.query(ClinicalCase).filter(ClinicalCase.published.is_(True))
    if theme:
        query = query.filter(ClinicalCase.tema == theme)
    if q and q.strip():
        term = f"%{q.strip()}%"
        query = query.filter(or_(
            ClinicalCase.titulo.ilike(term),
            ClinicalCase.tema.ilike(term),
            ClinicalCase.enunciado.ilike(term),
            ClinicalCase.pergunta.ilike(term),
        ))
    total = query.count()
    casos = query.order_by(ClinicalCase.tema, ClinicalCase.titulo).offset(offset).limit(limit).all()

    def _pagina(items: list) -> dict:
        return {
            "total": total, "limit": limit, "offset": offset,
            "next_offset": offset + len(items) if offset + len(items) < total else None,
            "has_more": offset + len(items) < total,
            "items": items,
        }

    if not casos:
        return _pagina([])

    ids = [case.id for case in casos]
    contagens = dict(
        db.query(ClinicalCaseAttempt.case_id, func.count(ClinicalCaseAttempt.id))
        .filter(ClinicalCaseAttempt.user_id == user.id, ClinicalCaseAttempt.case_id.in_(ids))
        .group_by(ClinicalCaseAttempt.case_id)
        .all()
    )
    ultimas_subquery = (
        db.query(
            ClinicalCaseAttempt.case_id.label("case_id"),
            func.max(ClinicalCaseAttempt.created_at).label("created_at"),
        )
        .filter(ClinicalCaseAttempt.user_id == user.id, ClinicalCaseAttempt.case_id.in_(ids))
        .group_by(ClinicalCaseAttempt.case_id)
        .subquery()
    )
    ultimas = dict(
        db.query(ClinicalCaseAttempt.case_id, ClinicalCaseAttempt.acertou)
        .join(ultimas_subquery, (
            ClinicalCaseAttempt.case_id == ultimas_subquery.c.case_id
        ) & (
            ClinicalCaseAttempt.created_at == ultimas_subquery.c.created_at
        ))
        .filter(ClinicalCaseAttempt.user_id == user.id)
        .all()
    )
    return _pagina([
        {
            "slug": c.slug, "titulo": c.titulo, "tema": c.tema, "nivel": c.nivel,
            "tentativas": int(contagens.get(c.id, 0)),
            "acertou_na_ultima": ultimas.get(c.id),
        }
        for c in casos
    ])


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
