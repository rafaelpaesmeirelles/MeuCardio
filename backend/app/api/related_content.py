"""`GET /api/relacionados` — "Tudo sobre este tema" do ecossistema Corvia.

Pedido do Rafael, 08/08/2026: a partir de 1 item, o usuário precisa visualizar
tudo que o ecossistema tem sobre aquele tópico e acessar o que quiser
imediatamente. A lógica de cruzamento em si (o que conta como "mesmo tema" em
cada uma das doze frentes) vive em `app.services.related_content` — este
arquivo é só a casca HTTP.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user
from app.services.related_content import buscar_relacionados

router = APIRouter(prefix="/api/relacionados", tags=["relacionados"])


@router.get("")
def relacionados(
    tema: str = Query(..., min_length=1, max_length=120),
    excluir_tipo: str | None = Query(
        None, description="Tipo do item de origem, para não aparecer na própria lista de relacionados."
    ),
    excluir_slug: str | None = Query(None, description="Slug do item de origem."),
    db: Session = Depends(get_db),
    _=Depends(current_user),
):
    return buscar_relacionados(db, tema, excluir_tipo=excluir_tipo, excluir_slug=excluir_slug)
