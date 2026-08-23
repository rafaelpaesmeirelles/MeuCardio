"""Normaliza com segurança uma conta existente como sócio operacional.

O comando não cria, revela nem altera senhas e não aceita o termo LGPD do
CorVIA Mail em nome do titular. Sem ``--apply`` ele é somente leitura.
"""
from __future__ import annotations

import argparse

from sqlalchemy import func

from app.core.db import SessionLocal
from app.models.audit import AuditLog
from app.models.email_account import EmailAccount
from app.models.kyc_waiver import KycRequirementWaiver
from app.models.subscription import PLANO_COMPLETO
from app.models.user import User


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Configura conta existente como sócio com acesso integral.")
    p.add_argument("--email", required=True)
    p.add_argument("--apply", action="store_true", help="Aplica a alteração; sem esta opção faz apenas diagnóstico.")
    return p


def main() -> None:
    args = parser().parse_args()
    email = args.email.strip().lower()
    db = SessionLocal()
    try:
        user = db.query(User).filter(func.lower(User.email) == email).first()
        if user is None:
            raise SystemExit(f"Conta não encontrada: {email}")

        conta_mail = db.query(EmailAccount).filter(EmailAccount.user_id == user.id).first()
        print(
            "Estado atual: "
            f"id={user.id} role={user.role} ativo={user.is_active} status={user.status} "
            f"convidado={user.convidado} investidor={user.investidor} "
            f"perfil_pendente={user.profile_completion_required} "
            f"tour_concluido={user.onboarding_visto} "
            f"corvia_mail={conta_mail.email_address if conta_mail else 'a ativar pelo titular'}"
        )
        if not args.apply:
            print("Diagnóstico concluído. Execute novamente com --apply para promover a conta.")
            return

        antes = {
            "role": user.role,
            "is_active": user.is_active,
            "status": user.status,
            "convidado": user.convidado,
            "investidor": user.investidor,
            "profile_completion_required": user.profile_completion_required,
            "onboarding_visto": user.onboarding_visto,
        }
        user.role = "admin"
        user.is_active = True
        user.status = "aprovado"
        user.convidado = True
        user.investidor = False
        user.convidado_plano_preferido = PLANO_COMPLETO
        user.profile_completion_required = False
        user.onboarding_visto = False

        waiver = db.get(KycRequirementWaiver, user.id)
        if waiver is None:
            waiver = KycRequirementWaiver(owner_id=user.id)
            db.add(waiver)
        # Só a selfie permanece obrigatória; nenhum documento é solicitado.
        waiver.professional_front = True
        waiver.professional_back = True
        waiver.personal_front = True
        waiver.personal_back = True
        waiver.personal_digital = True
        waiver.selfie = False

        db.add(AuditLog(
            user_id=None,
            action="configure_partner_user",
            entity="user",
            entity_id=str(user.id),
            detail={
                "email": user.email,
                "antes": antes,
                "depois": {
                    "role": "admin",
                    "is_active": True,
                    "status": "aprovado",
                    "convidado": True,
                    "investidor": False,
                    "tipo_acesso": "socio",
                    "profile_completion_required": False,
                    "onboarding_visto": False,
                    "kyc": "somente_selfie_aprovacao_automatica",
                    "plano": PLANO_COMPLETO,
                },
            },
        ))
        db.commit()
        print(
            "Conta configurada como sócio: acesso administrativo e clínico integral, "
            "plano completo/CorVIA Mail, perfil opcional, KYC somente com selfie "
            "e tour pendente. A senha não foi alterada."
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()
