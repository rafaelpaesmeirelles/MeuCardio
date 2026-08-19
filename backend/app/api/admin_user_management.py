from __future__ import annotations

import logging
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy import delete, inspect, text, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import require_admin
from app.models.audit import AuditLog
from app.models.email_account import EmailAccount
from app.models.subscription import Subscription, TIPO_EMAIL, TIPO_MEUCARDIO
from app.models.user import User
from app.services import mail360
from app.services.mail360 import Mail360Error
from app.services.professional_profile import normalize_council, normalize_professional_title

log = logging.getLogger("meucardio.admin-user-management")
router = APIRouter(prefix="/api/admin/user-management", tags=["administração de usuários"])


class AtualizarUsuario(BaseModel):
    full_name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    role: str
    birth_date: date | None = None
    cpf: str | None = Field(default=None, max_length=14)
    profession: str | None = Field(default=None, max_length=80)
    council_name: str | None = Field(default=None, max_length=20)
    council_number: str | None = Field(default=None, max_length=30)
    council_state: str | None = Field(default=None, max_length=2)
    specialty: str | None = Field(default=None, max_length=120)
    rqe: str | None = Field(default=None, max_length=40)
    professional_title: str | None = Field(default=None, max_length=30)
    workplace_name: str | None = Field(default=None, max_length=180)
    workplace_department: str | None = Field(default=None, max_length=180)
    workplace_role: str | None = Field(default=None, max_length=180)
    workplace_notes: str | None = Field(default=None, max_length=500)
    is_active: bool
    tipo_acesso: str

    @field_validator("role")
    @classmethod
    def _role(cls, value: str) -> str:
        value = value.strip().lower()
        if value not in {"medico", "residente", "leitor"}:
            raise ValueError("Perfil inválido para conta gerenciada. Administrador não pode ser definido aqui.")
        return value

    @field_validator("tipo_acesso")
    @classmethod
    def _tipo(cls, value: str) -> str:
        value = value.strip().lower()
        if value not in {"normal", "convidado", "investidor"}:
            raise ValueError("Tipo de acesso inválido.")
        return value

    @field_validator("professional_title")
    @classmethod
    def _titulo(cls, value: str | None) -> str | None:
        return normalize_professional_title(value)

    @field_validator("council_name")
    @classmethod
    def _conselho(cls, value: str | None) -> str | None:
        return normalize_council(value)

    @field_validator("council_state")
    @classmethod
    def _uf(cls, value: str | None) -> str | None:
        value = (value or "").strip().upper()
        if value and (len(value) != 2 or not value.isalpha()):
            raise ValueError("UF inválida.")
        return value or None


class ExcluirUsuario(BaseModel):
    confirmar_email: EmailStr
    excluir_corvia_mail: bool = True


_STATUS_PAGOS_RELEVANTES = {"ativo", "teste", "pendente", "inadimplente", "suspenso", "pausado"}


def _assinaturas_pagas(db: Session, user_id: int) -> list[Subscription]:
    return db.query(Subscription).filter(
        Subscription.user_id == user_id,
        Subscription.kind.in_([TIPO_MEUCARDIO, TIPO_EMAIL]),
        Subscription.status.in_(_STATUS_PAGOS_RELEVANTES),
        (Subscription.stripe_subscription_id.is_not(None) | Subscription.stripe_customer_id.is_not(None)),
    ).all()


def _pode_excluir(db: Session, alvo: User, admin: User) -> tuple[bool, str | None]:
    if alvo.id == admin.id:
        return False, "A própria conta administrativa não pode ser excluída por esta tela."
    if alvo.role == "admin":
        return False, "Contas administrativas não podem ser excluídas por esta rotina."
    if _assinaturas_pagas(db, alvo.id):
        return False, "Existe assinatura/cobrança vinculada. Cancele e trate o vínculo financeiro antes da exclusão definitiva."
    return True, None


def _tipo_acesso(alvo: User) -> str:
    if alvo.investidor:
        return "investidor"
    if alvo.convidado:
        return "convidado"
    return "normal"


def _resumo(alvo: User, db: Session, admin: User) -> dict:
    conta_email = db.query(EmailAccount).filter(EmailAccount.user_id == alvo.id).first()
    pode, motivo = _pode_excluir(db, alvo, admin)
    return {
        "id": alvo.id,
        "full_name": alvo.full_name,
        "email": alvo.email,
        "role": alvo.role,
        "birth_date": alvo.birth_date,
        "cpf": alvo.cpf,
        "profession": alvo.profession,
        "council_name": alvo.council_name,
        "council_number": alvo.council_number,
        "council_state": alvo.council_state,
        "specialty": alvo.specialty,
        "rqe": alvo.rqe,
        "professional_title": alvo.professional_title,
        "workplace_name": alvo.workplace_name,
        "workplace_department": alvo.workplace_department,
        "workplace_role": alvo.workplace_role,
        "workplace_notes": alvo.workplace_notes,
        "is_active": alvo.is_active,
        "tipo_acesso": _tipo_acesso(alvo),
        "gratuito": bool(alvo.convidado or alvo.investidor or not _assinaturas_pagas(db, alvo.id)),
        "pode_excluir_definitivamente": pode,
        "bloqueio_exclusao": motivo,
        "corvia_mail": None if not conta_email else {
            "id": conta_email.id,
            "email_address": conta_email.email_address,
            "status": conta_email.status,
        },
    }


@router.get("/{user_id}")
def obter_usuario(user_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    alvo = db.get(User, user_id)
    if not alvo:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    return _resumo(alvo, db, admin)


@router.patch("/{user_id}")
def atualizar_usuario(
    user_id: int,
    dados: AtualizarUsuario,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    alvo = db.get(User, user_id)
    if not alvo:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    if alvo.id == admin.id or alvo.role == "admin":
        raise HTTPException(status_code=409, detail="Use o fluxo administrativo próprio para contas de administrador.")

    email = str(dados.email).strip().lower()
    existente = db.query(User).filter(User.email == email, User.id != alvo.id).first()
    if existente:
        raise HTTPException(status_code=409, detail="Já existe uma conta com este e-mail.")

    antes = {
        "email": alvo.email,
        "full_name": alvo.full_name,
        "role": alvo.role,
        "tipo_acesso": _tipo_acesso(alvo),
        "is_active": alvo.is_active,
    }

    alvo.full_name = dados.full_name.strip()
    alvo.email = email
    alvo.role = dados.role
    alvo.birth_date = dados.birth_date
    alvo.cpf = (dados.cpf or "").strip() or None
    alvo.profession = (dados.profession or "").strip() or None
    alvo.council_name = dados.council_name
    alvo.council_number = (dados.council_number or "").strip() or None
    alvo.council_state = dados.council_state
    alvo.specialty = (dados.specialty or "").strip() or None
    alvo.rqe = (dados.rqe or "").strip() or None
    alvo.professional_title = dados.professional_title
    alvo.workplace_name = (dados.workplace_name or "").strip() or None
    alvo.workplace_department = (dados.workplace_department or "").strip() or None
    alvo.workplace_role = (dados.workplace_role or "").strip() or None
    alvo.workplace_notes = (dados.workplace_notes or "").strip() or None
    alvo.is_active = dados.is_active
    alvo.convidado = dados.tipo_acesso == "convidado"
    alvo.investidor = dados.tipo_acesso == "investidor"
    if alvo.investidor:
        alvo.profile_completion_required = False

    db.add(AuditLog(
        user_id=admin.id,
        action="admin_editar_usuario",
        entity="user",
        entity_id=str(alvo.id),
        detail={
            "antes": antes,
            "depois": {
                "email": alvo.email,
                "full_name": alvo.full_name,
                "role": alvo.role,
                "tipo_acesso": _tipo_acesso(alvo),
                "is_active": alvo.is_active,
            },
        },
    ))
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Os dados informados conflitam com outro cadastro existente.") from exc
    db.refresh(alvo)
    return _resumo(alvo, db, admin)


def _preparar_referencias_para_exclusao(db: Session, user_id: int) -> None:
    # Histórico administrativo deve sobreviver; apenas solta a FK do ator.
    db.execute(update(AuditLog).where(AuditLog.user_id == user_id).values(user_id=None))
    db.execute(update(User).where(User.reviewed_by == user_id).values(reviewed_by=None))

    nomes = set(inspect(db.get_bind()).get_table_names())
    if "convidados_pre_autorizados" in nomes:
        db.execute(text("UPDATE convidados_pre_autorizados SET criado_por = NULL WHERE criado_por = :uid"), {"uid": user_id})
        db.execute(text("UPDATE convidados_pre_autorizados SET usado_por_user_id = NULL WHERE usado_por_user_id = :uid"), {"uid": user_id})
    if "google_test_user_requests" in nomes:
        db.execute(text("DELETE FROM google_test_user_requests WHERE user_id = :uid"), {"uid": user_id})

    # Legados sem ON DELETE CASCADE.
    db.execute(delete(Subscription).where(Subscription.user_id == user_id))
    db.execute(delete(EmailAccount).where(EmailAccount.user_id == user_id))


def _validar_exclusao_local(db: Session, user_id: int) -> None:
    # SAVEPOINT: prova que o banco aceita a remoção antes de tocar no Mail360.
    nested = db.begin_nested()
    try:
        _preparar_referencias_para_exclusao(db, user_id)
        alvo = db.get(User, user_id)
        if alvo:
            db.delete(alvo)
        db.flush()
    except IntegrityError as exc:
        nested.rollback()
        db.rollback()
        log.warning("Exclusão de user_id=%s bloqueada por dependência: %s", user_id, exc)
        raise HTTPException(
            status_code=409,
            detail="A conta possui dados vinculados que precisam ser tratados antes da exclusão definitiva. Nada foi apagado.",
        ) from exc
    else:
        nested.rollback()
        db.rollback()


@router.delete("/{user_id}")
def excluir_usuario(
    user_id: int,
    dados: ExcluirUsuario,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    alvo = db.get(User, user_id)
    if not alvo:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    pode, motivo = _pode_excluir(db, alvo, admin)
    if not pode:
        raise HTTPException(status_code=409, detail=motivo or "Exclusão não permitida.")
    if str(dados.confirmar_email).strip().lower() != alvo.email.strip().lower():
        raise HTTPException(status_code=422, detail="Digite exatamente o e-mail de login da conta para confirmar a exclusão.")

    conta_email = db.query(EmailAccount).filter(EmailAccount.user_id == alvo.id).first()
    if conta_email and not dados.excluir_corvia_mail:
        raise HTTPException(status_code=409, detail="A conta possui CorVIA Mail. Confirme também a remoção da caixa.")

    email_login = alvo.email
    nome = alvo.full_name
    mail_address = conta_email.email_address if conta_email else None
    mail_key = conta_email.mail360_account_key if conta_email else None

    _validar_exclusao_local(db, alvo.id)

    # Só depois do dry-run local: exclusão externa exata pela account_key persistida.
    if conta_email:
        try:
            mail360._chamar("DELETE", f"/accounts/{mail_key}")  # noqa: SLF001 — operação administrativa explícita
        except Mail360Error as exc:
            raise HTTPException(
                status_code=502,
                detail="O Mail360 recusou a exclusão da caixa. A conta CorVIA não foi apagada; tente novamente.",
            ) from exc

    _preparar_referencias_para_exclusao(db, user_id)
    alvo = db.get(User, user_id)
    if not alvo:
        raise HTTPException(status_code=409, detail="A conta mudou durante a exclusão; recarregue e tente novamente.")
    db.delete(alvo)
    db.add(AuditLog(
        user_id=admin.id,
        action="admin_excluir_usuario_definitivamente",
        entity="user_excluido",
        entity_id=str(user_id),
        detail={
            "email": email_login,
            "nome": nome,
            "corvia_mail_excluido": bool(mail_address),
            "corvia_mail_endereco": mail_address,
        },
    ))
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        log.critical("Corrida na exclusão definitiva de user_id=%s após Mail360: %s", user_id, exc)
        raise HTTPException(
            status_code=409,
            detail="A conta mudou durante a exclusão. O administrador deve revisar o estado antes de repetir.",
        ) from exc

    return {
        "excluido": True,
        "user_id": user_id,
        "email": email_login,
        "corvia_mail_excluido": bool(mail_address),
        "corvia_mail_endereco": mail_address,
    }
