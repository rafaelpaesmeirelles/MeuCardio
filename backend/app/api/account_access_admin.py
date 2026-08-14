"""Controles administrativos de acesso e e-mail transacional.

Este router é registrado ANTES de ``admin.router`` para substituir, sem quebrar
o frontend legado, apenas a rota de decisão de cadastro. A regra editorial/
administrativa original continua sendo chamada; acrescentamos a obrigação de
notificar a aprovação pelo canal seguro.
"""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from app.api import admin as admin_api
from app.core.config import settings
from app.core.db import get_db
from app.core.security import require_admin
from app.models.email_log import EmailLog
from app.models.user import User
from app.services import account_recovery

router = APIRouter(prefix="/api/admin", tags=["administração-acesso"])


@router.post("/users/{user_id}/decidir")
def decidir_solicitacao_com_notificacao(
    user_id: int,
    dados: admin_api.DecisaoAcesso,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Mantém a decisão canônica e adiciona e-mail de acesso aprovado."""
    resultado = admin_api.decidir_solicitacao(user_id, dados, db, admin)
    if dados.aprovar:
        background_tasks.add_task(account_recovery.enviar_acesso_aprovado, user_id)
    return resultado


class DestinatarioProbe(BaseModel):
    email: str

    @field_validator("email")
    @classmethod
    def _email(cls, value: str) -> str:
        try:
            return account_recovery.validar_email_basico(value)
        except ValueError as exc:
            raise ValueError(str(exc)) from exc


class RecoveryEmailPayload(BaseModel):
    recovery_email: str

    @field_validator("recovery_email")
    @classmethod
    def _email(cls, value: str) -> str:
        try:
            return account_recovery.validar_email_basico(value)
        except ValueError as exc:
            raise ValueError(str(exc)) from exc


@router.get("/users/{user_id}/recovery-email")
def admin_obter_recovery_email(
    user_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    return {
        "user_id": user.id,
        "login_email": user.email,
        "recovery_email": account_recovery.obter_email_recuperacao(db, user.id),
    }


@router.put("/users/{user_id}/recovery-email")
def admin_definir_recovery_email(
    user_id: int,
    dados: RecoveryEmailPayload,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    if user.investidor:
        raise HTTPException(
            status_code=409,
            detail="Conta Investidor é demonstração global e não deve receber dados pessoais de recuperação.",
        )
    try:
        registro = account_recovery.definir_email_recuperacao(db, user, dados.recovery_email)
        db.commit()
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    background_tasks.add_task(account_recovery.enviar_confirmacao_canal_recuperacao, user.id)
    return {
        "user_id": user.id,
        "login_email": user.email,
        "recovery_email": registro.email,
    }


@router.get("/account-access/email-status")
def email_status(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    """Diagnóstico sem segredo: configuração + últimos resultados de envio."""
    ultimos = (
        db.query(EmailLog)
        .order_by(EmailLog.created_at.desc())
        .limit(20)
        .all()
    )
    return {
        "smtp_configurado": bool(settings.smtp_configurado),
        "smtp_from_canonico": "contato@corvia.med.br" in (settings.smtp_from or "").lower(),
        "smtp_user_canonico": (settings.smtp_user or "").strip().lower() == "contato@corvia.med.br",
        "smtp_host_configurado": bool((settings.smtp_host or "").strip()),
        "ultimos_envios": [
            {
                "tipo": item.tipo,
                "sucesso": bool(item.sucesso),
                "erro": item.erro,
                "created_at": item.created_at,
                # endereço mascarado para o painel de diagnóstico não virar
                # lista desnecessária de PII.
                "destino_dominio": item.destinatario.rsplit("@", 1)[-1].lower()
                if "@" in item.destinatario else "invalido",
            }
            for item in ultimos
        ],
    }


@router.post("/account-access/email-probe")
def email_probe(
    dados: DestinatarioProbe,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Smoke SMTP real e síncrono; retorna falha em vez de falso sucesso."""
    if not settings.smtp_configurado:
        raise HTTPException(status_code=503, detail="SMTP transacional não configurado.")
    ok = account_recovery.enviar_teste_transacional(dados.email, admin.id)
    if not ok:
        raise HTTPException(
            status_code=502,
            detail="O servidor SMTP não confirmou o envio. Consulte email-status/logs.",
        )
    return {"ok": True, "remetente": "contato@corvia.med.br"}


@router.post("/users/{user_id}/enviar-recuperacao")
def admin_enviar_recuperacao(
    user_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    """Dispara reset para o segundo canal de uma conta já bloqueada."""
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    if user.investidor:
        raise HTTPException(status_code=409, detail="Investidor não possui recuperação pessoal.")
    if not user.is_active:
        raise HTTPException(status_code=409, detail="A conta está desativada; reative antes do reset.")
    if account_recovery.obter_email_recuperacao(db, user.id) is None:
        raise HTTPException(
            status_code=409,
            detail="Cadastre primeiro o segundo e-mail de recuperação deste usuário.",
        )
    ok = account_recovery.enviar_recuperacao_senha(user.id)
    if not ok:
        raise HTTPException(status_code=502, detail="Falha ao enviar o e-mail de recuperação.")
    return {"ok": True}


@router.post("/users/{user_id}/reenviar-acesso")
def admin_reenviar_acesso(
    user_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    """Reenvia boas-vindas/liberação sem expor ou alterar senha."""
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    if user.investidor:
        raise HTTPException(status_code=409, detail="Investidor usa a credencial global de demonstração.")
    if not user.is_active or user.status != "aprovado":
        raise HTTPException(status_code=409, detail="O acesso ainda não está aprovado/ativo.")
    ok = account_recovery.enviar_acesso_aprovado(user.id)
    if not ok:
        raise HTTPException(status_code=502, detail="Falha ao enviar a mensagem de acesso.")
    return {"ok": True}
