"""`GET /api/relacionados` — "Tudo sobre este tema" do ecossistema Corvia.

Pedido do Rafael, 08/08/2026: a partir de 1 item, o usuário precisa visualizar
tudo que o ecossistema tem sobre aquele tópico e acessar o que quiser
imediatamente. A lógica de cruzamento em si vive em
`app.services.connected_content`: ela preserva as consultas por metadado
estruturado das doze frentes, canonicaliza aliases históricos e só admite
medicamentos em um tema clínico quando a indicação revisada do próprio verbete
sustenta explicitamente a relação.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user
from app.services.connected_content import (
    buscar_relacionados_contextuais,
    buscar_relacionados_do_medicamento,
)

router = APIRouter(prefix="/api/relacionados", tags=["relacionados"])


@router.get("/medicamento/{slug}")
def relacionados_medicamento(
    slug: str,
    db: Session = Depends(get_db),
    _=Depends(current_user),
):
    """All published ecosystem fronts safely connected to one medication.

    The traversal starts only from explicit clinical topics supported by the
    medication's structured indications. It never uses generic text similarity.
    """
    resultado = buscar_relacionados_do_medicamento(db, slug)
    if resultado is None:
        raise HTTPException(status_code=404, detail="Medicamento não encontrado.")
    return resultado


@router.get("")
def relacionados(
    tema: str = Query(..., min_length=1, max_length=120),
    assunto: str | None = Query(
        None, min_length=1, max_length=255,
        description="Slug/assunto específico do item de origem para filtrar relações por relevância.",
    ),
    excluir_tipo: str | None = Query(
        None, description="Tipo do item de origem, para não aparecer na própria lista de relacionados."
    ),
    excluir_slug: str | None = Query(None, description="Slug do item de origem."),
    db: Session = Depends(get_db),
    _=Depends(current_user),
):
    return buscar_relacionados_contextuais(
        db, tema, excluir_tipo=excluir_tipo, excluir_slug=excluir_slug, assunto=assunto
    )
