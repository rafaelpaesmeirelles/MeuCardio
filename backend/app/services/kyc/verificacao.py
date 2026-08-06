"""Submissão e revisão da verificação de identidade — Trabalho 11.

Documentos ficam cifrados no cofre já existente (`services/cofre.py`),
volume próprio `settings.kyc_dir`, nunca montado no Caddy.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.kyc import KycVerification
from app.models.user import User
from app.services import cofre
from app.services.kyc import crm_check


class DocumentoPessoalIncompleto(ValueError):
    """Nem o par frente/verso nem o PDF digital foram enviados por completo."""


def _raiz() -> Path:
    return Path(settings.kyc_dir)


@dataclass
class DocumentosSubmissao:
    doc_profissional_frente: bytes
    doc_profissional_verso: bytes
    selfie: bytes
    doc_pessoal_frente: bytes | None = None
    doc_pessoal_verso: bytes | None = None
    doc_pessoal_digital: bytes | None = None


def submeter(db: Session, user: User, docs: DocumentosSubmissao) -> KycVerification:
    """Substitui uma submissão anterior do mesmo usuário, se houver — o
    médico pode reenviar se algo foi rejeitado. Falha alto se o documento
    pessoal não veio completo (nem o par frente/verso, nem o PDF digital) —
    nunca aceita uma submissão pela metade."""
    tem_par_fotos = docs.doc_pessoal_frente is not None and docs.doc_pessoal_verso is not None
    tem_digital = docs.doc_pessoal_digital is not None
    if not tem_par_fotos and not tem_digital:
        raise DocumentoPessoalIncompleto(
            "Envie a frente e o verso do documento pessoal, ou o PDF do documento digital (gov.br/CNH Digital)."
        )

    existente = db.query(KycVerification).filter(KycVerification.owner_id == user.id).first()
    arquivos_antigos = []
    if existente:
        arquivos_antigos = [
            existente.doc_profissional_frente, existente.doc_profissional_verso,
            existente.doc_pessoal_frente, existente.doc_pessoal_verso,
            existente.doc_pessoal_digital, existente.selfie,
        ]

    raiz = _raiz()
    nome_prof_frente = cofre.guardar(docs.doc_profissional_frente, user.id, raiz=raiz)
    nome_prof_verso = cofre.guardar(docs.doc_profissional_verso, user.id, raiz=raiz)
    nome_selfie = cofre.guardar(docs.selfie, user.id, raiz=raiz)
    nome_pessoal_frente = cofre.guardar(docs.doc_pessoal_frente, user.id, raiz=raiz) if docs.doc_pessoal_frente else None
    nome_pessoal_verso = cofre.guardar(docs.doc_pessoal_verso, user.id, raiz=raiz) if docs.doc_pessoal_verso else None
    nome_pessoal_digital = cofre.guardar(docs.doc_pessoal_digital, user.id, raiz=raiz) if docs.doc_pessoal_digital else None

    registro = existente or KycVerification(owner_id=user.id)
    registro.doc_profissional_frente = nome_prof_frente
    registro.doc_profissional_verso = nome_prof_verso
    registro.doc_pessoal_frente = nome_pessoal_frente
    registro.doc_pessoal_verso = nome_pessoal_verso
    registro.doc_pessoal_digital = nome_pessoal_digital
    registro.selfie = nome_selfie
    registro.status = "aguardando_revisao"
    registro.liberado_em = None
    registro.aprovado_em = None
    registro.aprovado_por = None
    registro.nota_revisao = None
    if not existente:
        db.add(registro)
    db.flush()

    # Checagem de CRM — melhor esforço, nunca bloqueia a submissão.
    resultado = crm_check.checar_crm(user.council_number or "", user.council_state or "")
    registro.crm_check_status = resultado.status
    registro.crm_check_detalhe = resultado.detalhe
    registro.crm_check_em = resultado.verificado_em
    if resultado.status == crm_check.STATUS_ATIVO_CONFIRMADO:
        registro.status = "liberado_crm_ok"
        registro.liberado_em = datetime.now(timezone.utc)

    for nome_antigo in arquivos_antigos:
        if nome_antigo:
            cofre.apagar(nome_antigo, raiz=raiz)

    return registro


def obter(db: Session, user: User) -> KycVerification | None:
    return db.query(KycVerification).filter(KycVerification.owner_id == user.id).first()


def liberado_para_uso(registro: KycVerification | None) -> bool:
    """Regra de acesso: liberado se a checagem automática confirmou OU se
    já passou pela revisão definitiva. "aguardando_revisao" sozinho NUNCA
    libera — é o caso em que a checagem de CRM falhou ou não confirmou."""
    return registro is not None and registro.status in ("liberado_crm_ok", "aprovado")


def listar_pendentes(db: Session) -> list[KycVerification]:
    """Fila do admin: tudo que ainda não recebeu aprovação DEFINITIVA —
    inclui tanto o que já está liberado por CRM (revisão ainda pendente)
    quanto o que está travado esperando revisão."""
    return (
        db.query(KycVerification)
        .filter(KycVerification.status.in_(["aguardando_revisao", "liberado_crm_ok"]))
        .order_by(KycVerification.criado_em.asc())
        .all()
    )


def ler_documento(registro: KycVerification, campo: str, owner_id: int) -> bytes:
    nome = getattr(registro, campo, None)
    if not nome:
        raise FileNotFoundError(campo)
    return cofre.ler(nome, owner_id, raiz=_raiz())


def aprovar(db: Session, registro: KycVerification, admin: User, nota: str | None) -> KycVerification:
    registro.status = "aprovado"
    registro.aprovado_em = datetime.now(timezone.utc)
    registro.aprovado_por = admin.id
    registro.nota_revisao = nota
    return registro


def rejeitar(db: Session, registro: KycVerification, admin: User, nota: str) -> KycVerification:
    registro.status = "rejeitado"
    registro.aprovado_em = None
    registro.aprovado_por = admin.id
    registro.nota_revisao = nota
    return registro
