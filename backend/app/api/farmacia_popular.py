"""Carga do elenco do Programa Farmácia Popular do Brasil (PFPB).

Gap encontrado por sessão externa (Claude chat), 29/08/2026 — ver CLAUDE.md
e `app/services/farmacia_popular.py`. Diferente de `app/api/cmed.py`, não há
hoje um caminho automatizado de download verificado (ver docstring do
serviço) — esta rota só recarrega o manifesto local versionado
(`app/data/farmacia_popular_manifesto.json`).
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import require_admin
from app.models.farmacia_popular import FarmaciaPopularVersao
from app.services import farmacia_popular

router = APIRouter(prefix="/api/admin/farmacia-popular", tags=["administração"])


@router.post("/carregar")
def carregar(db: Session = Depends(get_db), _=Depends(require_admin)):
    return farmacia_popular.carregar_manifesto(db)


@router.get("/status")
def status(db: Session = Depends(get_db), _=Depends(require_admin)):
    versao = db.query(FarmaciaPopularVersao).order_by(FarmaciaPopularVersao.id.desc()).first()
    if not versao:
        return {"importado": False}
    return {
        "importado": True, "conferido_em": versao.conferido_em,
        "criado_em": versao.criado_em, "itens": versao.itens,
    }
