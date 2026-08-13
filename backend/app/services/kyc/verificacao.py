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
from app.models.audit import AuditLog
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
    # Opcionais desde 13/08/2026 — investidor não envia documento
    # profissional (KYC pessoal simplificado). A obrigatoriedade por tipo de
    # conta é aplicada em `app/api/kyc.py`, antes de chegar aqui; `submeter`
    # abaixo confia que quem chamou já validou isso.
    doc_profissional_frente: bytes | None = None
    doc_profissional_verso: bytes | None = None
    selfie: bytes = b""
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
    eh_reenvio = existente is not None
    arquivos_antigos = []
    if existente:
        arquivos_antigos = [
            existente.doc_profissional_frente, existente.doc_profissional_verso,
            existente.doc_pessoal_frente, existente.doc_pessoal_verso,
            existente.doc_pessoal_digital, existente.selfie,
        ]

    raiz = _raiz()
    nome_prof_frente = cofre.guardar(docs.doc_profissional_frente, user.id, raiz=raiz) if docs.doc_profissional_frente else None
    nome_prof_verso = cofre.guardar(docs.doc_profissional_verso, user.id, raiz=raiz) if docs.doc_profissional_verso else None
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

    if user.investidor:
        # KYC pessoal simplificado (13/08/2026, pedido do Rafael): investidor
        # não é médico credenciado, não tem conselho/registro nenhum — checar
        # conselho profissional dele não faz sentido, e por isso NUNCA roda
        # aqui (diferente de convidado, ver ramo abaixo, onde a checagem
        # roda só como informação). Aprovação DEFINITIVA e automática assim
        # que documento pessoal + selfie chegam completos — nunca depende
        # de revisão do admin. "investidor isento de KYC deixa de existir...
        # passa a ter KYC de identidade pessoal simplificado e automático."
        registro.conselho_check_status = "nao_verificado"
        registro.conselho_check_detalhe = None
        registro.conselho_check_em = None
        registro.status = "aprovado"
        registro.liberado_em = datetime.now(timezone.utc)
        registro.aprovado_em = datetime.now(timezone.utc)
        registro.aprovado_por = None
        registro.nota_revisao = (
            "Aprovação automática — conta investidor (KYC pessoal simplificado, "
            "sem checagem de conselho e sem revisão administrativa)."
        )
    else:
        # Checagem de conselho — melhor esforço, nunca bloqueia a submissão.
        # Para convidado, o resultado é só informação/auditoria (nunca
        # decide o status final dele, ver bloco abaixo); para assinante
        # normal, decide os três estados de sempre.
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

        # Médico convidado (08/08/2026, pedido do Rafael) — aprovação
        # DEFINITIVA automática, SEMPRE, qualquer que tenha sido o resultado
        # (só informativo) da checagem de conselho acima. Corrigido em
        # 13/08/2026: antes só auto-aprovava quando a checagem deixava o
        # status em "aguardando_revisao" — se o conselho confirmasse
        # (liberado_conselho_ok) ou fosse indisponível (liberado_sem_checagem),
        # o convidado ficava parado num desses dois estados, que
        # `listar_pendentes()` inclui na fila do admin — exatamente a
        # dependência de revisão humana que o Rafael pediu para eliminar.
        # "Para convidado, toda submissão válida deve terminar definitivamente
        # em aprovado, independentemente do resultado informativo da
        # checagem automática do conselho."
        if user.convidado:
            registro.status = "aprovado"
            registro.liberado_em = datetime.now(timezone.utc)
            registro.aprovado_em = datetime.now(timezone.utc)
            registro.aprovado_por = None
            registro.nota_revisao = (
                "Aprovação automática — conta marcada como convidado (checagem de conselho "
                f"é só informativa para este tipo de conta; resultado: {resultado.status})."
            )

    # Auditoria da submissão em si — achado no hardening desta fase (issue #52):
    # nem o primeiro envio nem o reenvio geravam AuditLog. Nunca registra bytes/
    # conteúdo do documento, só o fato de que o titular enviou/reenviou.
    db.add(AuditLog(
        user_id=user.id, action="kyc_reenvio" if eh_reenvio else "kyc_submissao",
        entity="kyc_verifications", entity_id=str(registro.id),
        detail={"owner_id": user.id, "documento_pessoal": "digital" if tem_digital else "fotos"},
    ))
    if registro.status == "aprovado" and (user.convidado or user.investidor):
        db.add(AuditLog(
            user_id=user.id,
            action="aprovacao_automatica_investidor" if user.investidor else "aprovacao_automatica_convidado",
            entity="kyc_verifications", entity_id=str(registro.id),
            detail={"owner_id": user.id},
        ))

    for nome_antigo in arquivos_antigos:
        if nome_antigo:
            cofre.apagar(nome_antigo, raiz=raiz)
    if arquivos_antigos:
        # Os arquivos substituídos pelo reenvio são apagados do cofre acima —
        # é uma exclusão real de dado sensível, precisa do mesmo tipo de
        # rastro que uma exclusão por retenção teria.
        db.add(AuditLog(
            user_id=user.id, action="kyc_delete", entity="kyc_verifications",
            entity_id=str(registro.id),
            detail={"motivo": "reenvio_substituiu_arquivos_anteriores", "quantidade": len(
                [a for a in arquivos_antigos if a]
            )},
        ))

    return registro


def obter(db: Session, user: User) -> KycVerification | None:
    return db.query(KycVerification).filter(KycVerification.owner_id == user.id).first()


def liberado_para_uso(registro: KycVerification | None) -> bool:
    """Regra de acesso: liberado se a checagem automática confirmou, OU se
    não havia checagem automática possível para o conselho (não-médico,
    ver `council_check.py`), OU se já passou pela revisão definitiva.
    "aguardando_revisao" sozinho NUNCA libera — é o caso em que a
    checagem (de CRM, hoje o único conselho com checagem em potencial)
    falhou ou não confirmou o registro. "rejeitado" e "reenvio_solicitado"
    (ver `solicitar_reenvio`) também nunca liberam — são as duas decisões
    definitivas que tiram o acesso até um novo envio."""
    return registro is not None and registro.status in (
        "liberado_conselho_ok", "liberado_sem_checagem", "aprovado",
    )


def listar_pendentes(db: Session) -> list[KycVerification]:
    """Fila do admin: tudo que ainda não recebeu aprovação DEFINITIVA —
    inclui tanto o que já está liberado (por checagem confirmada ou por
    checagem indisponível) quanto o que está travado esperando revisão.

    Convidado e investidor são excluídos explicitamente (13/08/2026, pedido
    do Rafael: "nenhum dos dois deve aparecer na fila de KYC pendente") —
    `submeter()` já os leva direto a "aprovado" numa submissão válida, então
    eles não deveriam aparecer aqui de qualquer forma; o filtro por `User`
    é defensivo, cobrindo também registro LEGADO que tenha ficado parado em
    "aguardando_revisao"/"liberado_conselho_ok"/"liberado_sem_checagem" de
    antes desta correção (ex.: convidado cuja checagem de conselho havia
    confirmado o registro antes de 13/08, ficando em "liberado_conselho_ok"
    em vez de "aprovado" — o bug que este filtro também corrige, sem
    precisar de um backfill de dado)."""
    from app.models.user import User

    return (
        db.query(KycVerification)
        .join(User, User.id == KycVerification.owner_id)
        .filter(KycVerification.status.in_([
            "aguardando_revisao", "liberado_conselho_ok", "liberado_sem_checagem",
        ]))
        .filter(User.convidado.is_(False))
        .filter(User.investidor.is_(False))
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


def solicitar_reenvio(db: Session, registro: KycVerification, admin: User, nota: str) -> KycVerification:
    """Decisão distinta de `rejeitar` (ficha administrativa do assinante,
    11/08/2026) — para quando a submissão está quase certa e só falta um
    documento melhor (foto ilegível, borrada, cortada), não uma recusa
    definitiva. Efeito de acesso é idêntico ao de `rejeitar`: o status sai
    do conjunto que `liberado_para_uso` aceita, então quem já estava usando
    a plataforma por checagem automática de conselho perde o acesso até
    reenviar — mesma severidade de `rejeitar`, só muda o rótulo e a
    mensagem que o assinante lê (`nota_revisao`), porque é isso que o
    distingue de uma rejeição definitiva. `submeter()` não olha o status
    anterior antes de aceitar um reenvio, então o assinante pode responder
    a qualquer momento, como já podia depois de `rejeitar`."""
    registro.status = "reenvio_solicitado"
    registro.aprovado_em = None
    registro.aprovado_por = admin.id
    registro.nota_revisao = nota
    return registro
