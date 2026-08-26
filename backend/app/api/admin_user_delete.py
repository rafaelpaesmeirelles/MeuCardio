from __future__ import annotations

import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.admin_user_management import ExcluirUsuario, _pode_excluir
from app.core.db import get_db
from app.core.security import require_admin
from app.models.audit import AuditLog
from app.models.email_account import EmailAccount
from app.models.prontuario import PatientClinicalAISuggestion, PatientECGRecord
from app.models.user import User
from app.services import cofre, mail360
from app.services.mail360 import Mail360Error

log = logging.getLogger("meucardio.admin-user-delete")
router = APIRouter(prefix="/api/admin/user-management", tags=["administração de usuários"])


def _quote(db: Session, identifier: str) -> str:
    return db.get_bind().dialect.identifier_preparer.quote(identifier)


def _remover_referencias_usuario(db: Session, user_id: int) -> None:
    """Remove ou anonimiza todas as FKs que apontam para users.id.

    Exclusão definitiva de conta precisa funcionar para usuários reais, que já
    podem ter sessão, KYC, favoritos, agenda, documentos, chat e outros vínculos.
    O fluxo anterior conhecia apenas algumas tabelas e por isso passava no teste
    sintético, mas falhava em produção ao encontrar qualquer FK nova.

    Regra:
    - FK nullable: preserva a linha e anonimiza a referência (SET NULL);
    - FK NOT NULL: remove a linha dependente;
    - auto-referências da própria tabela users: somente SET NULL quando possível.

    Vínculos Stripe relevantes continuam bloqueados ANTES de chegar aqui pela
    regra canônica de _pode_excluir().
    """
    # A ordem da introspecção não garante a precedência exigida pelas FKs
    # clínicas: sugestões dependem do ECG, que por sua vez depende do perfil.
    # Remove explicitamente essa cadeia antes do tratamento genérico por user_id.
    db.query(PatientClinicalAISuggestion).filter(
        PatientClinicalAISuggestion.owner_id == user_id,
    ).delete(synchronize_session=False)
    db.query(PatientECGRecord).filter(
        PatientECGRecord.owner_id == user_id,
    ).delete(synchronize_session=False)

    inspector = inspect(db.get_bind())
    for table_name in inspector.get_table_names():
        columns = {col["name"]: col for col in inspector.get_columns(table_name)}
        for fk in inspector.get_foreign_keys(table_name):
            if fk.get("referred_table") != "users":
                continue
            referred = fk.get("referred_columns") or []
            constrained = fk.get("constrained_columns") or []
            if referred != ["id"] or len(constrained) != 1:
                continue

            column_name = constrained[0]
            column = columns.get(column_name)
            if not column:
                continue

            qtable = _quote(db, table_name)
            qcolumn = _quote(db, column_name)

            if table_name == "users":
                if column.get("nullable", True):
                    db.execute(
                        text(f"UPDATE {qtable} SET {qcolumn} = NULL WHERE {qcolumn} = :uid"),
                        {"uid": user_id},
                    )
                continue

            if column.get("nullable", False):
                db.execute(
                    text(f"UPDATE {qtable} SET {qcolumn} = NULL WHERE {qcolumn} = :uid"),
                    {"uid": user_id},
                )
            else:
                db.execute(
                    text(f"DELETE FROM {qtable} WHERE {qcolumn} = :uid"),
                    {"uid": user_id},
                )


def _validar_exclusao_local(db: Session, user_id: int) -> None:
    savepoint = db.begin_nested()
    try:
        _remover_referencias_usuario(db, user_id)
        db.execute(text("DELETE FROM users WHERE id = :uid"), {"uid": user_id})
        db.flush()
    except IntegrityError as exc:
        savepoint.rollback()
        log.warning("Exclusão de user_id=%s ainda bloqueada por FK: %s", user_id, exc)
        raise HTTPException(
            status_code=409,
            detail=(
                "A conta ainda possui uma dependência de banco não compatível com exclusão definitiva. "
                "Nada foi apagado."
            ),
        ) from exc
    else:
        savepoint.rollback()
        db.expire_all()


@router.delete("/{user_id}")
def excluir_usuario_definitivamente(
    user_id: int,
    dados: ExcluirUsuario,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    # Impede que um novo vínculo clínico/arquivo seja criado entre o inventário
    # abaixo e a exclusão definitiva, o que deixaria um blob fora da coleta.
    alvo = db.query(User).filter(User.id == user_id).with_for_update().one_or_none()
    if not alvo:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    pode, motivo = _pode_excluir(db, alvo, admin)
    if not pode:
        raise HTTPException(status_code=409, detail=motivo or "Exclusão não permitida.")

    email_login = alvo.email.strip().lower()
    if dados.confirmar_email != email_login:
        raise HTTPException(
            status_code=422,
            detail="Digite exatamente o e-mail de login da conta para confirmar a exclusão.",
        )

    conta_email = db.query(EmailAccount).filter(EmailAccount.user_id == user_id).first()
    if conta_email and not dados.excluir_corvia_mail:
        raise HTTPException(status_code=409, detail="A conta possui CorVIA Mail. Confirme também a remoção da caixa.")

    nome = alvo.full_name
    mail_address = conta_email.email_address if conta_email else None
    mail_key = conta_email.mail360_account_key if conta_email else None
    ecg_storage_keys = [
        key for (key,) in db.query(PatientECGRecord.storage_key)
        .filter(PatientECGRecord.owner_id == user_id)
        .all()
    ]

    _validar_exclusao_local(db, user_id)

    if conta_email and mail_key:
        try:
            mail360._chamar("DELETE", f"/accounts/{mail_key}")  # noqa: SLF001
        except Mail360Error as exc:
            raise HTTPException(
                status_code=502,
                detail="O Mail360 recusou a exclusão da caixa. A conta CorVIA não foi apagada; tente novamente.",
            ) from exc
    elif conta_email and not mail_key:
        raise HTTPException(
            status_code=409,
            detail=(
                "A caixa CorVIA Mail desta conta não possui account_key registrado. "
                "A exclusão foi bloqueada para não deixar uma caixa externa órfã."
            ),
        )

    try:
        _remover_referencias_usuario(db, user_id)
        resultado = db.execute(text("DELETE FROM users WHERE id = :uid"), {"uid": user_id})
        if resultado.rowcount != 1:
            db.rollback()
            raise HTTPException(status_code=409, detail="A conta mudou durante a exclusão; recarregue e tente novamente.")

        db.add(AuditLog(
            user_id=admin.id,
            action="admin_excluir_usuario_definitivamente",
            entity="user_excluido",
            entity_id=str(user_id),
            detail={
                "email": email_login,
                "nome": nome,
                "corvia_mail_excluido": bool(mail_address and mail_key),
                "corvia_mail_endereco": mail_address,
                "arquivos_ecg_programados_para_remocao": len(ecg_storage_keys),
            },
        ))
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        log.critical("Exclusão definitiva de user_id=%s falhou após dry-run: %s", user_id, exc)
        raise HTTPException(
            status_code=409,
            detail="A conta mudou durante a exclusão. Recarregue e tente novamente.",
        ) from exc

    arquivos_ecg_removidos = 0
    for storage_key in ecg_storage_keys:
        try:
            cofre.apagar(storage_key)
            arquivos_ecg_removidos += 1
        except OSError as exc:
            # O banco e a conta externa já foram removidos; expõe a falha
            # operacional sem registrar nome de paciente ou conteúdo clínico.
            log.critical(
                "Falha ao remover arquivo cifrado de ECG após excluir user_id=%s: %s",
                user_id,
                type(exc).__name__,
            )

    from app.api.chat import gerenciador
    background_tasks.add_task(gerenciador.encerrar_usuario, user_id)

    return {
        "excluido": True,
        "user_id": user_id,
        "email": email_login,
        "corvia_mail_excluido": bool(mail_address and mail_key),
        "corvia_mail_endereco": mail_address,
        "arquivos_ecg_removidos": arquivos_ecg_removidos,
        "arquivos_ecg_pendentes": len(ecg_storage_keys) - arquivos_ecg_removidos,
    }
