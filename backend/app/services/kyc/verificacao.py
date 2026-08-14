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
from app.models.kyc_waiver import KycRequirementWaiver
from app.models.user import User
from app.services import cofre
from app.services.kyc import council_check


class DocumentoPessoalIncompleto(ValueError):
    """Nem uma via pessoal enviada/dispensada satisfez o requisito."""


class DocumentoProfissionalIncompleto(ValueError):
    """Um requisito de documento profissional não enviado nem dispensado."""


class SelfieObrigatoria(ValueError):
    """Selfie não enviada e sem dispensa administrativa válida."""


class InvestidorNaoFazKyc(PermissionError):
    """Conta Investidor é demonstração somente leitura e não submete KYC."""


def _raiz() -> Path:
    return Path(settings.kyc_dir)


@dataclass
class DocumentosSubmissao:
    # Opcionais no dataclass para permitir validação na borda HTTP e
    # diferentes combinações de documento pessoal. Contas reais continuam
    # exigindo o documento profissional no endpoint.
    doc_profissional_frente: bytes | None = None
    doc_profissional_verso: bytes | None = None
    selfie: bytes | None = None
    doc_pessoal_frente: bytes | None = None
    doc_pessoal_verso: bytes | None = None
    doc_pessoal_digital: bytes | None = None


WAIVER_FIELDS = (
    "professional_front", "professional_back", "personal_front",
    "personal_back", "personal_digital", "selfie",
)


def _waivers_vazias() -> dict[str, bool]:
    return {campo: False for campo in WAIVER_FIELDS}


def dispensas_aplicaveis(db: Session, user: User) -> dict[str, bool]:
    """Retorna dispensas efetivas; só Convidado pode recebê-las.

    Ausência de configuração é fail-closed (todos os requisitos permanecem).
    """
    if not user.convidado or user.investidor:
        return _waivers_vazias()
    linha = db.get(KycRequirementWaiver, user.id)
    if linha is None:
        return _waivers_vazias()
    return {campo: bool(getattr(linha, campo)) for campo in WAIVER_FIELDS}


def requisitos_publicos(db: Session, user: User) -> dict[str, bool]:
    """Mapa de campos obrigatórios para a UI; backend continua fonte da verdade."""
    waivers = dispensas_aplicaveis(db, user)
    return {campo: not dispensado for campo, dispensado in waivers.items()}


def _requisitos_satisfeitos_por_arquivos(
    *,
    professional_front: bool,
    professional_back: bool,
    personal_front: bool,
    personal_back: bool,
    personal_digital: bool,
    selfie: bool,
    waivers: dict[str, bool],
) -> bool:
    profissional_ok = (
        (professional_front or waivers["professional_front"])
        and (professional_back or waivers["professional_back"])
    )
    fotos_pessoais_ok = (
        (personal_front or waivers["personal_front"])
        and (personal_back or waivers["personal_back"])
    )
    digital_ok = personal_digital or waivers["personal_digital"]
    selfie_ok = selfie or waivers["selfie"]
    return profissional_ok and (fotos_pessoais_ok or digital_ok) and selfie_ok


def registro_satisfaz_requisitos(registro: KycVerification | None, waivers: dict[str, bool]) -> bool:
    if registro is None:
        return _requisitos_satisfeitos_por_arquivos(
            professional_front=False, professional_back=False,
            personal_front=False, personal_back=False, personal_digital=False,
            selfie=False, waivers=waivers,
        )
    return _requisitos_satisfeitos_por_arquivos(
        professional_front=bool(registro.doc_profissional_frente),
        professional_back=bool(registro.doc_profissional_verso),
        personal_front=bool(registro.doc_pessoal_frente),
        personal_back=bool(registro.doc_pessoal_verso),
        personal_digital=bool(registro.doc_pessoal_digital),
        selfie=bool(registro.selfie), waivers=waivers,
    )


def _validar_submissao(user: User, docs: DocumentosSubmissao, waivers: dict[str, bool]) -> tuple[bool, bool]:
    if user.investidor:
        raise InvestidorNaoFazKyc("Conta Investidor não participa do fluxo de KYC.")

    if not docs.doc_profissional_frente and not waivers["professional_front"]:
        raise DocumentoProfissionalIncompleto("Documento profissional — frente é obrigatório.")
    if not docs.doc_profissional_verso and not waivers["professional_back"]:
        raise DocumentoProfissionalIncompleto("Documento profissional — verso é obrigatório.")
    if not docs.selfie and not waivers["selfie"]:
        raise SelfieObrigatoria("Selfie ao vivo é obrigatória.")

    fotos_ok = (
        (bool(docs.doc_pessoal_frente) or waivers["personal_front"])
        and (bool(docs.doc_pessoal_verso) or waivers["personal_back"])
    )
    digital_ok = bool(docs.doc_pessoal_digital) or waivers["personal_digital"]
    if not fotos_ok and not digital_ok:
        raise DocumentoPessoalIncompleto(
            "Envie a frente e o verso do documento pessoal (salvo itens dispensados), "
            "ou o PDF digital, salvo dispensa administrativa correspondente."
        )
    return fotos_ok, digital_ok


def reavaliar_convidado_com_dispensas(db: Session, user: User, *, admin_id: int | None = None) -> KycVerification | None:
    """Reavalia imediatamente o KYC após alteração administrativa de dispensas.

    Se todos os requisitos remanescentes já estiverem satisfeitos, aprova sem
    revisão manual. Se uma dispensa removida torna um documento novamente
    obrigatório e ele não existe, exige reenvio. Assim a configuração tem
    efeito real no backend e nunca é apenas cosmética de frontend.
    """
    if not user.convidado or user.investidor:
        return obter(db, user)
    waivers = dispensas_aplicaveis(db, user)
    registro = obter(db, user)
    satisfaz = registro_satisfaz_requisitos(registro, waivers)

    if satisfaz and registro is None:
        registro = KycVerification(owner_id=user.id, selfie=None)
        db.add(registro)
        db.flush()

    if registro is None:
        return None

    agora = datetime.now(timezone.utc)
    if satisfaz:
        registro.status = "aprovado"
        registro.liberado_em = agora
        registro.aprovado_em = agora
        registro.aprovado_por = admin_id
        registro.nota_revisao = "Aprovação automática — todos os requisitos KYC não dispensados estão satisfeitos."
    elif registro.status == "aprovado":
        registro.status = "reenvio_solicitado"
        registro.liberado_em = None
        registro.aprovado_em = None
        registro.aprovado_por = None
        registro.nota_revisao = "Dispensas KYC alteradas: envie os requisitos que voltaram a ser obrigatórios."
    return registro


def submeter(db: Session, user: User, docs: DocumentosSubmissao) -> KycVerification:
    """Substitui a submissão anterior e aplica dispensas apenas a Convidado."""
    waivers = dispensas_aplicaveis(db, user)
    fotos_ok, digital_ok = _validar_submissao(user, docs, waivers)

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
    nome_selfie = cofre.guardar(docs.selfie, user.id, raiz=raiz) if docs.selfie else None
    nome_pessoal_frente = cofre.guardar(docs.doc_pessoal_frente, user.id, raiz=raiz) if docs.doc_pessoal_frente else None
    nome_pessoal_verso = cofre.guardar(docs.doc_pessoal_verso, user.id, raiz=raiz) if docs.doc_pessoal_verso else None
    nome_pessoal_digital = cofre.guardar(docs.doc_pessoal_digital, user.id, raiz=raiz) if docs.doc_pessoal_digital else None

    registro = existente or KycVerification(owner_id=user.id, selfie=None)
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
        registro.status = "liberado_sem_checagem"
        registro.liberado_em = datetime.now(timezone.utc)

    if user.convidado:
        agora = datetime.now(timezone.utc)
        registro.status = "aprovado"
        registro.liberado_em = agora
        registro.aprovado_em = agora
        registro.aprovado_por = None
        registro.nota_revisao = (
            "Aprovação automática — conta Convidado; todos os requisitos KYC "
            f"não dispensados foram satisfeitos. Conselho: {resultado.status}."
        )

    dispensadas = [campo for campo, ativo in waivers.items() if ativo]
    db.add(AuditLog(
        user_id=user.id, action="kyc_reenvio" if eh_reenvio else "kyc_submissao",
        entity="kyc_verifications", entity_id=str(registro.id),
        detail={
            "owner_id": user.id,
            "documento_pessoal": "digital" if docs.doc_pessoal_digital else "fotos" if (docs.doc_pessoal_frente or docs.doc_pessoal_verso) else "dispensado",
            "dispensas_aplicadas": dispensadas,
        },
    ))
    if registro.status == "aprovado" and user.convidado:
        db.add(AuditLog(
            user_id=user.id, action="aprovacao_automatica_convidado",
            entity="kyc_verifications", entity_id=str(registro.id),
            detail={"owner_id": user.id, "dispensas_aplicadas": dispensadas},
        ))

    for nome_antigo in arquivos_antigos:
        if nome_antigo:
            cofre.apagar(nome_antigo, raiz=raiz)
    if arquivos_antigos:
        db.add(AuditLog(
            user_id=user.id, action="kyc_delete", entity="kyc_verifications",
            entity_id=str(registro.id),
            detail={"motivo": "reenvio_substituiu_arquivos_anteriores", "quantidade": len([a for a in arquivos_antigos if a])},
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

    Convidado é excluído porque toda submissão válida termina aprovada.
    Investidor é excluído porque não participa de KYC; o filtro também cobre
    eventual registro legado anterior à regra definitiva. O filtro por `User`
    é defensivo, cobrindo ainda registro que tenha ficado parado em
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
