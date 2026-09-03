"""Orquestra a submissão KYC existente com a validação automática CFM.

Mantém o armazenamento cifrado e as regras já existentes de convidado/
outros conselhos. Para médico CRM normal, a decisão automática é aplicada
antes do commit da requisição: só aprovação inequívoca libera acesso; qualquer
reprovação ou incerteza fica bloqueada e entra na fila administrativa já
existente, com os documentos disponíveis no cofre para revisão manual.
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.audit import AuditLog
from app.models.kyc import KycVerification
from app.models.user import User
from app.services import notificar
from app.services.kyc import auto_validation, verificacao


def _eh_medico_cfm(user: User) -> bool:
    conselho = (user.council_name or "CRM").strip().upper()
    return conselho in {"", "CRM"}


def submeter_com_auto_validacao(
    db: Session,
    user: User,
    docs: verificacao.DocumentosSubmissao,
) -> KycVerification:
    """Submete documentos e, quando aplicável, decide o KYC automaticamente.

    A chamada a ``verificacao.submeter`` continua sendo a fonte da verdade
    para persistência cifrada, dispensas e compatibilidade. A etapa abaixo
    endurece o caminho CRM: não basta o conselho responder ativo; cadastro e
    documentos também precisam conferir para uma aprovação definitiva.
    """
    registro = verificacao.submeter(db, user, docs)

    # Convidados conservam a política administrativa já existente; demais
    # conselhos mantêm o fluxo atual, pois a base oficial do CFM não os cobre.
    if user.convidado or user.investidor or not _eh_medico_cfm(user):
        return registro

    resultado = auto_validation.validar_medico(user, docs)
    registro.conselho_check_status = resultado.conselho_status
    registro.conselho_check_detalhe = resultado.conselho_detalhe
    registro.conselho_check_em = resultado.verificado_em

    agora = datetime.now(timezone.utc)
    if resultado.decisao == "aprovado":
        registro.status = "aprovado"
        registro.liberado_em = agora
        registro.aprovado_em = agora
        registro.aprovado_por = None
        registro.nota_revisao = "Aprovação automática — CFM, cadastro e documentos conferem."
        action = "kyc_auto_aprovado"
    else:
        # "reprovado" é uma decisão automática negativa, mas não encerra o
        # caso: por pedido do responsável, todo negativo vai para revisão
        # humana. Usar a fila existente evita criar um estado terminal que
        # impediria o admin de aprovar os mesmos documentos.
        registro.status = "aguardando_revisao"
        registro.liberado_em = None
        registro.aprovado_em = None
        registro.aprovado_por = None
        prefixo = "Reprovação automática" if resultado.decisao == "reprovado" else "Validação automática inconclusiva"
        registro.nota_revisao = f"{prefixo}: {resultado.motivo}"
        action = "kyc_auto_reprovado" if resultado.decisao == "reprovado" else "kyc_auto_manual"
        notificar.notificar_admins_kyc_manual(
            db,
            nome=user.full_name,
            email=user.email,
            motivo=registro.nota_revisao,
        )

    db.add(AuditLog(
        user_id=user.id,
        action=action,
        entity="kyc_verifications",
        entity_id=str(registro.id),
        detail={
            "owner_id": user.id,
            "decisao": resultado.decisao,
            # Nunca persistir OCR/texto/documento; somente resultados booleanos.
            "checks": resultado.checks,
        },
    ))
    return registro
