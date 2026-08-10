"""`GET /api/grafo/relacionados` — leitura do Grafo de Conhecimento Clínico
Universal (issue #52, nova fase).

Casca HTTP fina — a lógica de registro/backfill/consulta vive em
`app.services.knowledge_graph`. Somente leitura nesta rota: o backfill/seed
do grafo é operação administrativa (`POST /api/admin/grafo/backfill`, em
`app.api.admin`), não algo que o assinante comum dispara.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user
from app.models.knowledge import TIPOS_ENTIDADE_PERMITIDOS
from app.services.knowledge_graph import relacionados_de

router = APIRouter(prefix="/api/grafo", tags=["grafo"])


@router.get("/relacionados")
def relacionados(
    entity_type: str = Query(..., min_length=1, max_length=40),
    slug: str = Query(..., min_length=1, max_length=255),
    limite_por_tipo: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
    _=Depends(current_user),
):
    if entity_type not in TIPOS_ENTIDADE_PERMITIDOS:
        raise HTTPException(status_code=422, detail="entity_type desconhecido.")
    resultado = relacionados_de(db, entity_type=entity_type, slug=slug, limite_por_tipo=limite_por_tipo)
    if resultado is None:
        return {"entity_type": entity_type, "slug": slug, "titulo": None, "grupos": [], "total": 0}
    return resultado
