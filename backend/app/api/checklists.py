"""Checklist de alta pós-evento cardiovascular (Tarefa 18).

O briefing pede três coisas que moldaram o desenho:

1. Os itens vêm do protocolo correspondente, não são escritos do zero — por
   isso cada item carrega a seção de origem, e o checklist aponta para o
   documento que o originou.
2. Cada condição tem checklist próprio, e deve dar para acrescentar um novo sem
   redesenhar nada — por isso condição e itens são dado versionado em JSON, como
   as demais frentes de conteúdo, e não código.
3. Não é lista estática de leitura: o médico marca item a item e vê o que falta.
   Daí a separação entre o modelo (conteúdo curado) e a aplicação (registro de
   trabalho de um médico numa alta concreta).
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user
from app.models.checklist import DischargeChecklist, DischargeChecklistRun
from app.models.user import User

router = APIRouter(prefix="/api/checklists", tags=["checklists de alta"])


def _dump(c: DischargeChecklist) -> dict:
    return {
        "slug": c.slug, "condicao": c.condicao, "resumo": c.resumo, "theme": c.theme,
        "documento_origem": c.documento_origem, "itens": c.itens or [],
        "source_refs": c.source_refs or [], "review_status": c.review_status,
        "total_itens": len(c.itens or []),
        "obrigatorios": len([i for i in (c.itens or []) if i.get("obrigatorio")]),
    }


def _pendencias(itens: list, marcados: list) -> dict:
    marcados = set(marcados or [])
    faltando = [i for i in itens if i.get("id") not in marcados]
    return {
        "faltando": [{"id": i["id"], "texto": i["texto"],
                      "categoria": i.get("categoria"), "obrigatorio": bool(i.get("obrigatorio"))}
                     for i in faltando],
        "faltando_obrigatorios": len([i for i in faltando if i.get("obrigatorio")]),
        "marcados": len(marcados & {i.get("id") for i in itens}),
        "total": len(itens),
    }


@router.get("")
def listar(db: Session = Depends(get_db), _: User = Depends(current_user)):
    cs = db.query(DischargeChecklist).filter(
        DischargeChecklist.published.is_(True)
    ).order_by(DischargeChecklist.condicao).all()
    return [{k: v for k, v in _dump(c).items() if k != "itens"} for c in cs]


@router.get("/{slug}")
def detalhe(slug: str, db: Session = Depends(get_db), _: User = Depends(current_user)):
    c = db.query(DischargeChecklist).filter(
        DischargeChecklist.slug == slug, DischargeChecklist.published.is_(True)
    ).first()
    if c is None:
        raise HTTPException(status_code=404, detail="Checklist não encontrado.")
    return _dump(c)


class NovaAplicacao(BaseModel):
    checklist_slug: str
    patient_id: int | None = None
    identificacao_livre: str | None = None


@router.post("/aplicacoes", status_code=201)
def iniciar(dados: NovaAplicacao, db: Session = Depends(get_db), user: User = Depends(current_user)):
    """Começa a usar um checklist numa alta.

    Copia os itens como estão agora. Se o conteúdo for revisado depois, esta
    alta continua descrevendo o que de fato foi conferido — sem isso, a revisão
    reescreveria retroativamente o registro e passaria a afirmar que alguém
    marcou um item que ainda não existia.
    """
    c = db.query(DischargeChecklist).filter(
        DischargeChecklist.slug == dados.checklist_slug,
        DischargeChecklist.published.is_(True),
    ).first()
    if c is None:
        raise HTTPException(status_code=404, detail="Checklist não encontrado.")

    run = DischargeChecklistRun(
        checklist_id=c.id, user_id=user.id, patient_id=dados.patient_id,
        identificacao_livre=(dados.identificacao_livre or "").strip()[:200] or None,
        marcados=[], itens_no_momento=c.itens or [],
    )
    db.add(run); db.commit(); db.refresh(run)
    return {"id": run.id, "checklist": c.slug, "condicao": c.condicao,
            "itens": run.itens_no_momento, **_pendencias(run.itens_no_momento, [])}


class Marcacao(BaseModel):
    marcados: list[str]
    observacoes: str | None = None
    finalizar: bool = False


@router.patch("/aplicacoes/{run_id}")
def marcar(run_id: int, dados: Marcacao,
           db: Session = Depends(get_db), user: User = Depends(current_user)):
    run = db.query(DischargeChecklistRun).filter(
        DischargeChecklistRun.id == run_id, DischargeChecklistRun.user_id == user.id
    ).first()
    if run is None:
        raise HTTPException(status_code=404, detail="Aplicação não encontrada.")
    if run.finalizado_em is not None:
        raise HTTPException(status_code=409, detail="Esta alta já foi finalizada.")

    validos = {i.get("id") for i in (run.itens_no_momento or [])}
    desconhecidos = [m for m in dados.marcados if m not in validos]
    if desconhecidos:
        raise HTTPException(status_code=422,
                            detail=f"Itens que não pertencem a este checklist: {desconhecidos}")

    run.marcados = sorted(set(dados.marcados))
    if dados.observacoes is not None:
        run.observacoes = dados.observacoes.strip() or None

    pend = _pendencias(run.itens_no_momento or [], run.marcados)
    if dados.finalizar:
        # Finalizar com obrigatório pendente é permitido, e de propósito: a
        # realidade clínica tem exceção justificada, e um sistema que trava a
        # alta vira sistema que o médico contorna. O que ele não pode é
        # finalizar sem saber — por isso a pendência exige observação escrita.
        if pend["faltando_obrigatorios"] > 0 and not run.observacoes:
            raise HTTPException(
                status_code=422,
                detail=f"Faltam {pend['faltando_obrigatorios']} item(ns) obrigatório(s). "
                       "Para finalizar assim, registre em observações o motivo.",
            )
        run.finalizado_em = datetime.now(timezone.utc)
    db.commit()
    return {"id": run.id, "finalizado": run.finalizado_em is not None,
            "observacoes": run.observacoes, **pend}


@router.get("/aplicacoes/minhas")
def minhas(
    finalizadas: bool | None = Query(None),
    db: Session = Depends(get_db), user: User = Depends(current_user),
):
    """Só as próprias aplicações — registro de trabalho não é de outro médico."""
    q = db.query(DischargeChecklistRun).filter(DischargeChecklistRun.user_id == user.id)
    if finalizadas is True:
        q = q.filter(DischargeChecklistRun.finalizado_em.isnot(None))
    elif finalizadas is False:
        q = q.filter(DischargeChecklistRun.finalizado_em.is_(None))

    saida = []
    for r in q.order_by(DischargeChecklistRun.created_at.desc()).limit(100).all():
        c = db.query(DischargeChecklist).filter(DischargeChecklist.id == r.checklist_id).first()
        pend = _pendencias(r.itens_no_momento or [], r.marcados or [])
        saida.append({
            "id": r.id, "condicao": c.condicao if c else "—",
            "checklist": c.slug if c else None,
            "identificacao": r.identificacao_livre, "patient_id": r.patient_id,
            "finalizado_em": r.finalizado_em, "criado_em": r.created_at,
            "marcados": pend["marcados"], "total": pend["total"],
            "faltando_obrigatorios": pend["faltando_obrigatorios"],
        })
    return saida


@router.get("/aplicacoes/{run_id}")
def ver_aplicacao(run_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    run = db.query(DischargeChecklistRun).filter(
        DischargeChecklistRun.id == run_id, DischargeChecklistRun.user_id == user.id
    ).first()
    if run is None:
        raise HTTPException(status_code=404, detail="Aplicação não encontrada.")
    c = db.query(DischargeChecklist).filter(DischargeChecklist.id == run.checklist_id).first()
    return {
        "id": run.id, "condicao": c.condicao if c else "—",
        "documento_origem": c.documento_origem if c else None,
        "identificacao": run.identificacao_livre,
        "itens": run.itens_no_momento, "marcados": run.marcados or [],
        "observacoes": run.observacoes, "finalizado_em": run.finalizado_em,
        **_pendencias(run.itens_no_momento or [], run.marcados or []),
    }
