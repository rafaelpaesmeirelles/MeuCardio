from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user, limpar_cookie_sessao
from app.models.user import User
from app.services.access_security import end_session

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/encerrar-todas-sessoes")
def encerrar_todas_sessoes(
    response: Response,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> dict[str, str]:
    """Invalida todos os JWTs de aplicação emitidos até este instante."""
    user.sessions_valid_after = datetime.now(timezone.utc)
    end_session(
        db, user_id=user.id, surface="corvia_os",
        session_id=user.active_session_id, reason="revogada_pelo_usuario",
    )
    user.active_session_id = None
    db.commit()
    limpar_cookie_sessao(response)
    return {"nota": "Todas as sessões da conta foram encerradas."}
