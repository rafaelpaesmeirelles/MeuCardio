"""Atualização da lista de preços da CMED (Tarefa A, CLAUDE.md).

Um só caminho de código: esta rota e o cron diário (`infra/cmed_cron.sh`)
chamam a mesma função `cmed_precos.atualizar()`. Só baixa de novo se o
timestamp da lista mudou — ver docstring de `atualizar()`.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import require_admin
from app.models.cmed import CmedVersao
from app.services import cmed_precos

router = APIRouter(prefix="/api/admin/cmed", tags=["administração"])


@router.post("/atualizar")
def atualizar(forcar: bool = False, db: Session = Depends(get_db), _=Depends(require_admin)):
    return cmed_precos.atualizar(db, forcar=forcar)


@router.get("/status")
def status(db: Session = Depends(get_db), _=Depends(require_admin)):
    versao = db.query(CmedVersao).order_by(CmedVersao.id.desc()).first()
    if not versao:
        return {"importado": False}
    return {
        "importado": True, "publicado_em": versao.publicado_em,
        "baixado_em": versao.baixado_em, "linhas": versao.linhas,
    }
