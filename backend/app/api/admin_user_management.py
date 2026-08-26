from __future__ import annotations

import logging
from datetime import date, datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import delete, inspect, text, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import hash_password, is_owner_admin, require_admin, require_owner_admin
from app.models.audit import AuditLog
from app.models.email_account import EmailAccount
from app.models.subscription import Subscription
from app.models.user import User
from app.models.user_access import UserAccess
from app.services import mail360
from app.services.mail360 import Mail360Error
from app.services.professional_profile import normalize_council, normalize_professional_title

log = logging.getLogger("meucardio.admin-user-management")
router = APIRouter(prefix="/api/admin/user-management", tags=["administração de usuários"])


def _email_valido(value: str) -> str:
    value = (value or "").strip().lower()
    if not value or "@" not in value or value.startswith("@") or value.endswith("@"):
        raise ValueError("E-mail inválido.")
    local, dominio = value.rsplit("@", 1)
    if not local or "." not in dominio or dominio.startswith(".") or dominio.endswith("."):
        raise ValueError("E-mail inválido.")
    return value


class AtualizarUsuario(BaseModel):
    full_name: str = Field(min_length=2, max_length=255)
    email: str = Field(min_length=3, max_length=255)
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

    @field_validator("email")
    @classmethod
    def _email(cls, value: str) -> str:
        return _email_valido(value)

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


class SenhaAdministrativa(BaseModel):
    password: str = Field(min_length=8, max_length=256)


class ExcluirUsuario(BaseModel):
    confirmar_email: str = Field(min_length=3, max_length=255)
    excluir_corvia_mail: bool = True

    @field_validator("confirmar_email")
    @classmethod
    def _email(cls, value: str) -> str:
        return _email_valido(value)


_STATUS_PAGOS_RELEVANTES = {"ativo", "teste", "pendente", "inadimplente", "suspenso", "pausado"}


def _assinaturas_pagas(db: Session, user_id: int) -> list[Subscription]:
    # Qualquer vínculo Stripe relevante bloqueia exclusão, inclusive curso.
    # Não descartamos histórico financeiro só porque não é a assinatura principal.
    return db.query(Subscription).filter(
        Subscription.user_id == user_id,
        Subscription.status.in_(_STATUS_PAGOS_RELEVANTES),
        (Subscription.stripe_subscription_id.is_not(None) | Subscription.stripe_customer_id.is_not(None)),
    ).all()


def _pode_excluir(db: Session, alvo: User, admin: User) -> tuple[bool, str | None]:
    if alvo.id == admin.id:
        return False, "A própria conta administrativa não pode ser excluída por esta tela."
    if alvo.role == "admin":
        return False, "Contas administrativas não podem ser excluídas por esta rotina."
    if _assinaturas_pagas(db, alvo.id):
        return False, "Existe assinatura/cobrança Stripe vinculada. Cancele e trate o vínculo financeiro antes da exclusão definitiva."
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
        "pode_ver_historico_acessos": is_owner_admin(admin),
        "sessao_unica_ativa": True,
        "corvia_mail": None if not conta_email else {
            "id": conta_email.id,
            "email_address": conta_email.email_address,
            "status": conta_email.status,
        },
    }


def _acesso_json(item: UserAccess, alvo: User, conta_email: EmailAccount | None) -> dict:
    active_session_id = (
        alvo.active_session_id if item.surface == "corvia_os"
        else conta_email.active_session_id if conta_email else None
    )
    ativo = bool(
        item.successful and item.ended_at is None and item.session_id
        and active_session_id == item.session_id
    )
    local = ", ".join(
        value for value in (item.city, item.region, item.country_code) if value
    ) or "Localização não informada pelo provedor"
    reason_labels = {
        "invalid_credentials": "Credenciais incorretas",
        "account_pending": "Cadastro ainda pendente",
        "account_rejected": "Cadastro rejeitado",
        "account_inactive": "Conta desativada",
        "mail_suspended": "Caixa de e-mail suspensa",
        "substituida_por_novo_login": "Substituída por um novo login",
        "logout": "Logout normal",
        "revogada_pelo_usuario": "Revogada pelo usuário",
        "revogada_pelo_proprietario": "Revogada pelo proprietário",
    }
    return {
        "id": item.id,
        "surface": item.surface,
        "successful": item.successful,
        "started_at": item.started_at,
        "last_seen_at": item.last_seen_at,
        "ended_at": item.ended_at,
        "end_reason": item.end_reason,
        "end_reason_label": reason_labels.get(item.end_reason or "", item.end_reason),
        "active": ativo,
        "ip_address": item.ip_address or "Não informado",
        "city": item.city,
        "region": item.region,
        "country_code": item.country_code,
        "location": local,
        "operating_system": item.operating_system or "Não identificado",
        "browser": item.browser or "Não identificado",
        "device_type": item.device_type or "Não identificado",
        "risk_level": item.risk_level,
        "risk_reasons": item.risk_reasons or [],
    }


@router.get("/{user_id}/accesses")
def listar_acessos_usuario(
    user_id: int,
    offset: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=1000),
    db: Session = Depends(get_db),
    owner=Depends(require_owner_admin),
):
    alvo = db.get(User, user_id)
    if not alvo:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    query = db.query(UserAccess).filter(UserAccess.user_id == user_id)
    total = query.count()
    items = query.order_by(UserAccess.started_at.desc()).offset(offset).limit(limit).all()
    conta_email = db.query(EmailAccount).filter(EmailAccount.user_id == user_id).first()
    db.add(AuditLog(
        user_id=owner.id,
        action="admin_visualizar_historico_acessos",
        entity="user",
        entity_id=str(user_id),
        detail={"offset": offset, "limit": limit},
    ))
    db.commit()
    return {
        "items": [_acesso_json(item, alvo, conta_email) for item in items],
        "total": total,
        "offset": offset,
        "limit": limit,
        "single_session_enforced": True,
    }


@router.post("/{user_id}/revoke-session")
def revogar_sessao_usuario(
    user_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    owner=Depends(require_owner_admin),
):
    alvo = db.get(User, user_id)
    if not alvo:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    now = datetime.now(timezone.utc)
    ativos = db.query(UserAccess).filter(
        UserAccess.user_id == user_id,
        UserAccess.successful.is_(True),
        UserAccess.ended_at.is_(None),
    ).all()
    for access in ativos:
        access.ended_at = now
        access.end_reason = "revogada_pelo_proprietario"
    alvo.sessions_valid_after = now
    alvo.active_session_id = None
    conta = db.query(EmailAccount).filter(EmailAccount.user_id == user_id).first()
    if conta:
        conta.sessions_valid_after = now
        conta.active_session_id = None
    db.add(AuditLog(
        user_id=owner.id,
        action="admin_revogar_sessoes_usuario",
        entity="user",
        entity_id=str(user_id),
        detail={"sessoes_encerradas": len(ativos), "incluiu_corvia_mail": bool(conta)},
    ))
    db.commit()
    from app.api.chat import gerenciador
    background_tasks.add_task(gerenciador.encerrar_usuario, user_id)
    return {"revoked": True, "sessions_ended": len(ativos), "corvia_mail": bool(conta)}


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

    existente = db.query(User).filter(User.email == dados.email, User.id != alvo.id).first()
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
    alvo.email = dados.email
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


@router.post("/{user_id}/corvia-mail/senha")
def redefinir_senha_corvia_mail(
    user_id: int,
    dados: SenhaAdministrativa,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    alvo = db.get(User, user_id)
    if not alvo:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    if alvo.id == admin.id or alvo.role == "admin":
        raise HTTPException(status_code=409, detail="Use o fluxo próprio da conta administrativa.")
    conta = db.query(EmailAccount).filter(EmailAccount.user_id == user_id).first()
    if not conta:
        raise HTTPException(status_code=404, detail="Este usuário não possui uma caixa CorVIA Mail nativa.")

    conta.password_hash = hash_password(dados.password)
    db.add(AuditLog(
        user_id=admin.id,
        action="admin_redefinir_senha_corvia_mail",
        entity="email_account",
        entity_id=str(conta.id),
        detail={"user_id": user_id, "email_address": conta.email_address},
    ))
    db.commit()
    return {"user_id": user_id, "email_address": conta.email_address, "senha_redefinida": True}


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

    # Legados sem ON DELETE CASCADE. Só chegamos aqui depois de confirmar que
    # não existe vínculo Stripe relevante, portanto nenhum histórico financeiro
    # ativo é descartado silenciosamente.
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
    if dados.confirmar_email != alvo.email.strip().lower():
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
