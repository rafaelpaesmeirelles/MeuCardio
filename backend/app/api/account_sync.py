"""Sincronização manual robusta de uma conta externa.

Separada do router histórico da Agenda para poder evoluir sem duplicar a
semântica antiga de ``sync-all`` (que sempre tentava calendário primeiro e,
por isso, não servia para Yahoo mail-only).
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user
from app.models.agenda import CalendarIntegration
from app.models.audit import AuditLog
from app.models.user import User
from app.services.account_sync import sincronizar_conta
from app.services.agenda_integrada.connectors import ConnectorError

router = APIRouter(prefix="/api/agenda", tags=["sincronizacao-contas"])


@router.post("/integrations/{integration_id}/sync-live")
def sync_live(
    integration_id: int,
    full: bool = False,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    item = db.query(CalendarIntegration).filter(
        CalendarIntegration.id == integration_id,
        CalendarIntegration.owner_id == user.id,
    ).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Conta externa não encontrada.")
    try:
        resultado = sincronizar_conta(db, item, full=full)
    except ConnectorError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail={"code": exc.code, "message": str(exc)},
        ) from exc

    db.add(AuditLog(
        user_id=user.id,
        action="external_account_sync_live",
        entity="calendar_integration",
        entity_id=str(item.id),
        detail={
            "provider": item.provider,
            "ok": resultado.get("ok"),
            "reauth_required": resultado.get("reauth_required", False),
            "componentes": [
                {"componente": c.get("componente"), "ok": c.get("ok"), "codigo": c.get("codigo")}
                for c in resultado.get("componentes", [])
            ],
        },
    ))
    db.commit()
    return resultado
