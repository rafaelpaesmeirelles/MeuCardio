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
from app.services.kyc import council_check


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

    # Checagem de conselho — melhor esforço, nunca bloqueia a submissão.
    resultado = council_check.checar_conselho(
        user.council_name, user.council_number or "", user.council_state or "",
    )
    registro.conselho_check_status = resultado.status
    registro.conselho_check_detalhe = resultado.detalhe
    registro.conselho_check_em = resultado.verificado_em
    if resultado.status == council_check.STATUS_ATIVO_CONFIRMADO:
        registro.status = "liberado_conselho_ok"
        registro.liberado_em = datetime.now(timezone.utc)
    elif resultado.status == council_check.STATUS_INDISPONIVEL_PARA_CONSELHO:
        # Só profissões não-médicas caem aqui (CRM sempre tenta a
        # checagem real, mesmo que hoje falhe por falta de credencial —
        # nesse caso o status é STATUS_ERRO_CHECAGEM, não este). Sem
        # nenhuma checagem automática possível para o conselho, libera
        # mesmo assim — decisão do Rafael em 06/08/2026 — porque o
        # escopo de prescrição dessas profissões já é restrito por
        # padrão (`app/services/kyc/escopo_profissional.py`), o que
        # reduz o risco de liberar sem confirmação. A informação segue
        # marcada como não verificada na fila de revisão manual.
        registro.status = "liberado_sem_checagem"
        registro.liberado_em = datetime.now(timezone.utc)

    # Médico convidado (08/08/2026, pedido do Rafael) — aprovação DEFINITIVA
    # automática, não apenas liberação provisória. Só entra aqui quem ainda
    # ficou em "aguardando_revisao" acima (o caso normal do CRM hoje, porque
    # a checagem do CFM ainda não tem credencial — cai em STATUS_ERRO_CHECAGEM,
    # nenhum dos dois ramos acima). Decisão explícita do Rafael de dispensar
    # a revisão manual só para conta marcada `convidado`, nunca em geral.
    if user.convidado and registro.status == "aguardando_revisao":
        registro.status = "aprovado"
        registro.liberado_em = datetime.now(timezone.utc)
        registro.aprovado_em = datetime.now(timezone.utc)
        registro.aprovado_por = None
        registro.nota_revisao = (
            "Aprovação automática — conta marcada como convidado (checagem do CFM "
            "ainda não disponível; revisão manual dispensada por decisão do Rafael)."
        )

    for nome_antigo in arquivos_antigos:
        if nome_antigo:
            cofre.apagar(nome_antigo, raiz=raiz)

    return registro


def obter(db: Session, user: User) -> KycVerification | None:
    return db.query(KycVerification).filter(KycVerification.owner_id == user.id).first()


def liberado_para_uso(registro: KycVerification | None) -> bool:
    """Regra de acesso: liberado se a checagem automática confirmou, OU se
    não havia checagem automática possível para o conselho (não-médico,
    ver `council_check.py`), OU se já passou pela revisão definitiva.
    "aguardando_revisao" sozinho NUNCA libera — é o caso em que a
    checagem (de CRM, hoje o único conselho com checagem em potencial)
    falhou ou não confirmou o registro."""
    return registro is not None and registro.status in (
        "liberado_conselho_ok", "liberado_sem_checagem", "aprovado",
    )


def listar_pendentes(db: Session) -> list[KycVerification]:
    """Fila do admin: tudo que ainda não recebeu aprovação DEFINITIVA —
    inclui tanto o que já está liberado (por checagem confirmada ou por
    checagem indisponível) quanto o que está travado esperando revisão."""
    return (
        db.query(KycVerification)
        .filter(KycVerification.status.in_([
            "aguardando_revisao", "liberado_conselho_ok", "liberado_sem_checagem",
        ]))
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
