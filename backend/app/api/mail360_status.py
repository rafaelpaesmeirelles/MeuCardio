from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.core.security import current_user, require_admin
from app.models.email_account import EmailAccount
from app.models.user import User
from app.services import mail360
from app.services.mail360 import Mail360Error

router = APIRouter(prefix="/api/mail360-status", tags=["caixa de e-mail"])


@router.get("")
def status(
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    conta = db.query(EmailAccount).filter(EmailAccount.user_id == user.id).first()
    return {
        "configured": settings.mail360_configurado,
        "domain": settings.mail360_dominio,
        "account_provisioned": conta is not None,
        "account_status": conta.status if conta else None,
        "ready_for_activation": settings.mail360_configurado,
    }


@router.post("/admin/probe")
def probe(_: User = Depends(require_admin)):
    if not settings.mail360_configurado:
        return {
            "configured": False,
            "connected": False,
            "checked_at": datetime.now(timezone.utc),
            "error_code": "missing_environment_variables",
        }
    try:
        # A função obtém e valida um access token real. O token nunca sai deste
        # processo, não é retornado e não é escrito em log.
        mail360._obter_access_token()  # noqa: SLF001 — diagnóstico interno do mesmo pacote
        return {
            "configured": True,
            "connected": True,
            "checked_at": datetime.now(timezone.utc),
            "error_code": None,
        }
    except Mail360Error:
        return {
            "configured": True,
            "connected": False,
            "checked_at": datetime.now(timezone.utc),
            "error_code": "provider_rejected_credentials",
        }
    except Exception:
        return {
            "configured": True,
            "connected": False,
            "checked_at": datetime.now(timezone.utc),
            "error_code": "provider_unreachable",
        }
