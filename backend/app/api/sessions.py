from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user
from app.models.user import User

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/encerrar-todas-sessoes")
def encerrar_todas_sessoes(
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> dict[str, str]:
    """Invalida todos os JWTs de aplicação emitidos até este instante.

    A própria requisição termina normalmente, mas o token usado nela deixa de
    funcionar em qualquer chamada posterior. A caixa CorvIA Mail usa escopo e
    credencial separados e não é afetada por esta ação.
    """
    user.sessions_valid_after = datetime.now(timezone.utc)
    db.commit()
    return {"nota": "Todas as sessões da conta foram encerradas."}
