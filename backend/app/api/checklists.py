"""Checklist de alta pós-evento cardiovascular.

O modelo é conteúdo curado; a aplicação registra o trabalho concreto do médico.
A busca do catálogo inclui nome, resumo, tema e texto dos itens, sem alterar o
snapshot das aplicações já iniciadas.
"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import Text, cast, or_
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user
from app.models.checklist import DischargeChecklist, DischargeChecklistRun
from app.models.user import User
from app.services.clinical_text import (
    clinical_text_without_internal_overrides,
    structured_clinical_updates,
)

router = APIRouter(prefix="/api/checklists", tags=["checklists de alta"])

ESCOPO_VALIDO = {"doenca", "procedimento"}


def _dump(checklist: DischargeChecklist, db: Session | None = None) -> dict:
    payload = {
        "slug": checklist.slug,
        "condicao": checklist.condicao,
        "resumo": clinical_text_without_internal_overrides(checklist.resumo),
        "theme": checklist.theme,
        "scope_type": checklist.scope_type or "doenca",
        "documento_origem": checklist.documento_origem,
        "itens": checklist.itens or [],
        "source_refs": checklist.source_refs or [],
        "review_status": checklist.review_status,
        "total_itens": len(checklist.itens or []),
        "obrigatorios": len([
            item for item in (checklist.itens or []) if item.get("obrigatorio")
        ]),
    }
    if db is not None:
        payload["clinical_updates"] = structured_clinical_updates(
            db, "checklist", checklist.id,
        )
    return payload


def _pendencias(itens: list, marcados: list) -> dict:
    ids_marcados = set(marcados or [])
    faltando = [item for item in itens if item.get("id") not in ids_marcados]
    ids_validos = {item.get("id") for item in itens}
    return {
        "faltando": [
            {
                "id": item["id"],
                "texto": item["texto"],
                "categoria": item.get("categoria"),
                "obrigatorio": bool(item.get("obrigatorio")),
            }
            for item in faltando
        ],
        "faltando_obrigatorios": len([
            item for item in faltando if item.get("obrigatorio")
        ]),
        "marcados": len(ids_marcados & ids_validos),
        "total": len(itens),
    }


@router.get("")
def listar(
    scope_type: str | None = Query(None, max_length=20),
    q: str | None = Query(None, max_length=160),
    limit: int = Query(60, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    _: User = Depends(current_user),
):
    if scope_type and scope_type not in ESCOPO_VALIDO:
        raise HTTPException(
            status_code=422,
            detail="scope_type precisa ser 'doenca' ou 'procedimento'.",
        )

    query = db.query(DischargeChecklist).filter(
        DischargeChecklist.published.is_(True)
    )
    if scope_type:
        query = query.filter(DischargeChecklist.scope_type == scope_type)
    if q and q.strip():
        termo = f"%{q.strip()}%"
        query = query.filter(or_(
            DischargeChecklist.condicao.ilike(termo),
            DischargeChecklist.resumo.ilike(termo),
            DischargeChecklist.theme.ilike(termo),
            cast(DischargeChecklist.itens, Text).ilike(termo),
        ))

    total = query.count()
    checklists = query.order_by(
        DischargeChecklist.scope_type,
        DischargeChecklist.condicao,
    ).offset(offset).limit(limit).all()
    items = [
        {chave: valor for chave, valor in _dump(checklist).items() if chave != "itens"}
        for checklist in checklists
    ]
    return {
        "total": total, "limit": limit, "offset": offset,
        "next_offset": offset + len(items) if offset + len(items) < total else None,
        "has_more": offset + len(items) < total,
        "items": items,
    }


@router.get("/{slug}")
def detalhe(
    slug: str,
    db: Session = Depends(get_db),
    _: User = Depends(current_user),
):
    checklist = db.query(DischargeChecklist).filter(
        DischargeChecklist.slug == slug,
        DischargeChecklist.published.is_(True),
    ).first()
    if checklist is None:
        raise HTTPException(status_code=404, detail="Checklist não encontrado.")
    return _dump(checklist, db)


class NovaAplicacao(BaseModel):
    checklist_slug: str
    patient_id: int | None = None
    identificacao_livre: str | None = None


@router.post("/aplicacoes", status_code=201)
def iniciar(
    dados: NovaAplicacao,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    checklist = db.query(DischargeChecklist).filter(
        DischargeChecklist.slug == dados.checklist_slug,
        DischargeChecklist.published.is_(True),
    ).first()
    if checklist is None:
        raise HTTPException(status_code=404, detail="Checklist não encontrado.")

    run = DischargeChecklistRun(
        checklist_id=checklist.id,
        user_id=user.id,
        patient_id=dados.patient_id,
        identificacao_livre=(dados.identificacao_livre or "").strip()[:200] or None,
        marcados=[],
        itens_no_momento=checklist.itens or [],
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return {
        "id": run.id,
        "checklist": checklist.slug,
        "condicao": checklist.condicao,
        "scope_type": checklist.scope_type or "doenca",
        "itens": run.itens_no_momento,
        **_pendencias(run.itens_no_momento, []),
    }


class Marcacao(BaseModel):
    marcados: list[str]
    observacoes: str | None = None
    finalizar: bool = False


@router.patch("/aplicacoes/{run_id}")
def marcar(
    run_id: int,
    dados: Marcacao,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    run = db.query(DischargeChecklistRun).filter(
        DischargeChecklistRun.id == run_id,
        DischargeChecklistRun.user_id == user.id,
    ).first()
    if run is None:
        raise HTTPException(status_code=404, detail="Aplicação não encontrada.")
    if run.finalizado_em is not None:
        raise HTTPException(status_code=409, detail="Esta alta já foi finalizada.")

    validos = {item.get("id") for item in (run.itens_no_momento or [])}
    desconhecidos = [marcado for marcado in dados.marcados if marcado not in validos]
    if desconhecidos:
        raise HTTPException(
            status_code=422,
            detail=f"Itens que não pertencem a este checklist: {desconhecidos}",
        )

    run.marcados = sorted(set(dados.marcados))
    if dados.observacoes is not None:
        run.observacoes = dados.observacoes.strip() or None

    pendencias = _pendencias(run.itens_no_momento or [], run.marcados)
    if dados.finalizar:
        if pendencias["faltando_obrigatorios"] > 0 and not run.observacoes:
            raise HTTPException(
                status_code=422,
                detail=(
                    f"Faltam {pendencias['faltando_obrigatorios']} item(ns) obrigatório(s). "
                    "Para finalizar assim, registre em observações o motivo."
                ),
            )
        run.finalizado_em = datetime.now(timezone.utc)
    db.commit()
    return {
        "id": run.id,
        "finalizado": run.finalizado_em is not None,
        "observacoes": run.observacoes,
        **pendencias,
    }


@router.get("/aplicacoes/minhas")
def minhas(
    finalizadas: bool | None = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    query = db.query(DischargeChecklistRun).filter(
        DischargeChecklistRun.user_id == user.id
    )
    if finalizadas is True:
        query = query.filter(DischargeChecklistRun.finalizado_em.isnot(None))
    elif finalizadas is False:
        query = query.filter(DischargeChecklistRun.finalizado_em.is_(None))

    saida = []
    for run in query.order_by(DischargeChecklistRun.created_at.desc()).limit(100).all():
        checklist = db.query(DischargeChecklist).filter(
            DischargeChecklist.id == run.checklist_id
        ).first()
        pendencias = _pendencias(run.itens_no_momento or [], run.marcados or [])
        saida.append({
            "id": run.id,
            "condicao": checklist.condicao if checklist else "—",
            "scope_type": (checklist.scope_type or "doenca") if checklist else None,
            "checklist": checklist.slug if checklist else None,
            "identificacao": run.identificacao_livre,
            "patient_id": run.patient_id,
            "finalizado_em": run.finalizado_em,
            "criado_em": run.created_at,
            "marcados": pendencias["marcados"],
            "total": pendencias["total"],
            "faltando_obrigatorios": pendencias["faltando_obrigatorios"],
        })
    return saida


@router.get("/aplicacoes/{run_id}")
def ver_aplicacao(
    run_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    run = db.query(DischargeChecklistRun).filter(
        DischargeChecklistRun.id == run_id,
        DischargeChecklistRun.user_id == user.id,
    ).first()
    if run is None:
        raise HTTPException(status_code=404, detail="Aplicação não encontrada.")
    checklist = db.query(DischargeChecklist).filter(
        DischargeChecklist.id == run.checklist_id
    ).first()
    return {
        "id": run.id,
        "checklist": checklist.slug if checklist else None,
        "condicao": checklist.condicao if checklist else "—",
        "theme": checklist.theme if checklist else None,
        "scope_type": (checklist.scope_type or "doenca") if checklist else None,
        "documento_origem": checklist.documento_origem if checklist else None,
        "identificacao": run.identificacao_livre,
        "itens": run.itens_no_momento,
        "marcados": run.marcados or [],
        "observacoes": run.observacoes,
        "finalizado_em": run.finalizado_em,
        **_pendencias(run.itens_no_momento or [], run.marcados or []),
    }
