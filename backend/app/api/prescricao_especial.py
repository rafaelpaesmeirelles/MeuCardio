from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Literal

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.core.security import current_user
from app.core.uploads import UploadRejected, validate_file
from app.models.audit import AuditLog
from app.models.clinical_docs import GeneratedDocument
from app.models.compartilhamento import DocumentShareLink
from app.models.email_account import EmailAccount
from app.models.user import User
from app.services import cofre, emails, envio_documento_email
from app.services.assinatura import divulgacao_email
from app.services.assinatura import emissao as assinatura_emissao
from app.services.professional_profile import document_identity, professional_name

router = APIRouter(prefix="/api/prescricao-especial", tags=["prescrição especial"])

DOC_TYPE = "prescricao_livre_especial"
TITULO = "Receituário"
VALIDADE_LINK_DIAS = 7
TAMANHO_MAXIMO_PDF_ASSINADO = 15 * 1024 * 1024

# Identidade privilegiada do Dr. Rafael: somente identificadores de login
# estáveis (não editáveis pela tela de perfil). Nome, CRM e UF são dados
# profissionais editáveis e não podem conceder autorização de assinatura.
_Rafael_LOGIN_EMAILS = {
    "rafael@cardiobeneribeirao.com.br",
    "rafael@corvia.med.br",
}

# A permissão é deliberadamente nominal e fechada. O endereço CorVIA Mail é
# usado como identidade estável da conta, independentemente do e-mail externo
# usado para login.
_USUARIOS_ESPECIAIS = {
    "natalia@corvia.med.br": {"codigo": "natalia", "permite_propria": True},
    "lenira@corvia.med.br": {"codigo": "lenira", "permite_propria": True},
    "wladmir@corvia.med.br": {"codigo": "wladmir", "permite_propria": False},
}


def _agora() -> datetime:
    return datetime.now(timezone.utc)


def _emails_da_conta(db: Session, user: User) -> set[str]:
    emails_conta = {(user.email or "").strip().lower()}
    caixa = db.query(EmailAccount).filter(EmailAccount.user_id == user.id).first()
    if caixa and caixa.email_address:
        emails_conta.add(caixa.email_address.strip().lower())
    return {x for x in emails_conta if x}


def _perfil_especial(db: Session, user: User) -> dict | None:
    for endereco, perfil in _USUARIOS_ESPECIAIS.items():
        if endereco in _emails_da_conta(db, user):
            return {**perfil, "email_corvia": endereco}
    return None


def _eh_rafael(user: User) -> bool:
    return bool(
        user.role == "admin"
        and user.is_active
        and (user.email or "").strip().lower() in _Rafael_LOGIN_EMAILS
    )


def _rafael(db: Session) -> User:
    encontrados = (
        db.query(User)
        .filter(
            User.role == "admin",
            User.is_active.is_(True),
            User.email.in_(sorted(_Rafael_LOGIN_EMAILS)),
        )
        .all()
    )
    if len(encontrados) != 1:
        raise HTTPException(
            status_code=409,
            detail="O prescritor Dr. Rafael não pôde ser resolvido de forma única. Nenhuma receita foi encaminhada.",
        )
    return encontrados[0]


def _meta(g: GeneratedDocument) -> dict:
    return dict(g.variables or {})


def _set_meta(g: GeneratedDocument, **mudancas) -> None:
    dados = _meta(g)
    dados.update(mudancas)
    g.variables = dados


def _origem_id(g: GeneratedDocument) -> int | None:
    valor = _meta(g).get("originator_id")
    try:
        return int(valor)
    except (TypeError, ValueError):
        return None


def _signer_id(g: GeneratedDocument) -> int | None:
    valor = _meta(g).get("signer_id")
    try:
        return int(valor)
    except (TypeError, ValueError):
        return None


def _status(g: GeneratedDocument) -> str:
    return str(_meta(g).get("status") or "rascunho")


def _paciente(g: GeneratedDocument) -> str | None:
    if not g.patient_name_cifrado:
        return None
    return cofre.decifrar_campo(g.patient_name_cifrado, g.id)


def _serializar(db: Session, g: GeneratedDocument) -> dict:
    meta = _meta(g)
    signer = db.get(User, _signer_id(g)) if _signer_id(g) else None
    originator = db.get(User, _origem_id(g)) if _origem_id(g) else None
    emitido = assinatura_emissao.buscar(
        db, tipo=assinatura_emissao.TIPO_DOCUMENTO, referencia_id=g.id,
    )
    disponivel = bool(
        emitido
        and (emitido.assinado_em is not None or _status(g) == "emitida_manual")
    )
    return {
        "id": g.id,
        "patient_name": _paciente(g),
        "body": g.rendered_body,
        "mode": meta.get("mode"),
        "status": _status(g),
        "originator_id": _origem_id(g),
        "originator_name": professional_name(originator) if originator else None,
        "signer_id": _signer_id(g),
        "signer_name": professional_name(signer) if signer else None,
        "review_note": meta.get("review_note"),
        "created_at": g.created_at,
        "signed_at": emitido.assinado_em if emitido else None,
        "signed": bool(emitido and emitido.assinado_em is not None),
        "pdf_available": disponivel,
        "method": emitido.metodo if emitido else None,
        "awaiting_external_signature": bool(
            emitido and emitido.assinado_em is None and _status(g) == "aguardando_assinatura_externa"
        ),
    }


def _documento_especial(db: Session, gid: int) -> GeneratedDocument:
    g = db.get(GeneratedDocument, gid)
    if not g or g.doc_type != DOC_TYPE:
        raise HTTPException(status_code=404, detail="Prescrição não encontrada.")
    return g


def _autoriza_leitura(g: GeneratedDocument, user: User) -> bool:
    return user.id in {_origem_id(g), _signer_id(g)}


class _TextoPrescricaoMixin(BaseModel):
    patient_name: str = Field(min_length=2, max_length=200)
    body: str = Field(min_length=3, max_length=12000)

    @field_validator("patient_name", "body", mode="before")
    @classmethod
    def _normalizar_texto_obrigatorio(cls, value):
        return value.strip() if isinstance(value, str) else value


class CriarIn(_TextoPrescricaoMixin):
    mode: Literal["propria", "rafael"]


class AtualizarIn(_TextoPrescricaoMixin):
    pass


class DecisaoIn(BaseModel):
    action: Literal["aprovar", "devolver", "recusar"]
    note: str | None = Field(default=None, max_length=1000)


class EmitirIn(BaseModel):
    metodo: str = "A1_ARQUIVO"
    endereco: Literal["residencial", "profissional"] | None = None


class EnviarEmailIn(BaseModel):
    email: str = Field(min_length=5, max_length=320)


@router.get("/capacidades")
def capacidades(db: Session = Depends(get_db), user: User = Depends(current_user)):
    perfil = _perfil_especial(db, user)
    return {
        "enabled": perfil is not None,
        "allows_self": bool(perfil and perfil["permite_propria"]),
        "rafael_signer": _eh_rafael(user),
        "profile": perfil["codigo"] if perfil else None,
    }


@router.post("", status_code=201)
def criar(dados: CriarIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    perfil = _perfil_especial(db, user)
    if not perfil:
        raise HTTPException(status_code=403, detail="Prescrição livre especial não habilitada para esta conta.")
    if dados.mode == "propria" and not perfil["permite_propria"]:
        raise HTTPException(
            status_code=403,
            detail="Esta conta pode emitir prescrição livre somente com assinatura do Dr. Rafael.",
        )

    signer = user if dados.mode == "propria" else _rafael(db)
    status = "pronta_assinatura" if dados.mode == "propria" else "pendente_assinatura"
    g = GeneratedDocument(
        patient_id=None,
        template_id=None,
        created_by=signer.id if dados.mode == "rafael" else user.id,
        doc_type=DOC_TYPE,
        title=TITULO,
        rendered_body=dados.body,
        endereco_exibido="profissional",
        variables={
            "special_prescription": True,
            "originator_id": user.id,
            "signer_id": signer.id,
            "mode": dados.mode,
            "status": status,
            "review_note": None,
        },
    )
    db.add(g)
    db.flush()
    g.patient_name_cifrado = cofre.cifrar_campo(dados.patient_name, g.id)
    db.add(AuditLog(
        user_id=user.id,
        action="criar_prescricao_livre_especial",
        entity="generated_document",
        entity_id=str(g.id),
        detail={"mode": dados.mode, "signer_id": signer.id, "perfil": perfil["codigo"]},
    ))
    db.commit()
    db.refresh(g)
    return _serializar(db, g)


@router.get("/minhas")
def minhas(db: Session = Depends(get_db), user: User = Depends(current_user)):
    if not _perfil_especial(db, user):
        return []
    rows = db.query(GeneratedDocument).filter(GeneratedDocument.doc_type == DOC_TYPE).order_by(
        GeneratedDocument.created_at.desc()
    ).all()
    return [_serializar(db, g) for g in rows if _origem_id(g) == user.id]


@router.get("/pendentes")
def pendentes(db: Session = Depends(get_db), user: User = Depends(current_user)):
    if not _eh_rafael(user):
        raise HTTPException(status_code=403, detail="Fila exclusiva do Dr. Rafael.")
    rows = db.query(GeneratedDocument).filter(GeneratedDocument.doc_type == DOC_TYPE).order_by(
        GeneratedDocument.created_at.asc()
    ).all()
    permitidos = {
        "pendente_assinatura", "aprovada", "aguardando_assinatura_externa",
    }
    return [
        _serializar(db, g) for g in rows
        if _signer_id(g) == user.id and _origem_id(g) != user.id and _status(g) in permitidos
    ]


@router.put("/{gid}")
def corrigir(gid: int, dados: AtualizarIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    g = _documento_especial(db, gid)
    if _origem_id(g) != user.id:
        raise HTTPException(status_code=404, detail="Prescrição não encontrada.")
    if _status(g) != "devolvida":
        raise HTTPException(status_code=409, detail="Somente prescrição devolvida pode ser corrigida.")
    if assinatura_emissao.buscar(db, tipo=assinatura_emissao.TIPO_DOCUMENTO, referencia_id=g.id):
        raise HTTPException(status_code=409, detail="Documento já emitido não pode ser alterado.")

    g.rendered_body = dados.body
    g.patient_name_cifrado = cofre.cifrar_campo(dados.patient_name, g.id)
    _set_meta(g, status="pendente_assinatura", review_note=None)
    db.add(AuditLog(
        user_id=user.id, action="corrigir_prescricao_livre_especial",
        entity="generated_document", entity_id=str(g.id),
    ))
    db.commit()
    return _serializar(db, g)


@router.post("/{gid}/decisao")
def decidir(gid: int, dados: DecisaoIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    g = _documento_especial(db, gid)
    if not _eh_rafael(user) or _signer_id(g) != user.id or _origem_id(g) == user.id:
        raise HTTPException(status_code=403, detail="Esta solicitação não pertence à sua fila de assinatura.")
    if _status(g) not in {"pendente_assinatura", "aprovada"}:
        raise HTTPException(status_code=409, detail="Esta solicitação não aceita mais revisão.")

    novo = {
        "aprovar": "aprovada",
        "devolver": "devolvida",
        "recusar": "recusada",
    }[dados.action]
    if dados.action in {"devolver", "recusar"} and not (dados.note or "").strip():
        raise HTTPException(status_code=422, detail="Informe o motivo para devolver ou recusar.")
    _set_meta(g, status=novo, review_note=(dados.note or "").strip() or None)
    db.add(AuditLog(
        user_id=user.id, action=f"{dados.action}_prescricao_livre_especial",
        entity="generated_document", entity_id=str(g.id),
        detail={"originator_id": _origem_id(g), "note": (dados.note or "").strip() or None},
    ))
    db.commit()
    return _serializar(db, g)


@router.post("/{gid}/emitir")
def emitir(gid: int, dados: EmitirIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    from app.services.pdf_documento import documento_generico, resolver_endereco

    g = _documento_especial(db, gid)
    if _signer_id(g) != user.id:
        raise HTTPException(status_code=403, detail="Somente o prescritor designado pode emitir esta receita.")
    modo = str(_meta(g).get("mode") or "")
    permitido = {"pronta_assinatura"} if modo == "propria" else {"aprovada"}
    if _status(g) not in permitido:
        raise HTTPException(status_code=409, detail="A receita ainda não está liberada para assinatura.")

    existente = assinatura_emissao.buscar(
        db, tipo=assinatura_emissao.TIPO_DOCUMENTO, referencia_id=g.id,
    )
    if existente:
        raise HTTPException(status_code=409, detail="Esta receita já foi emitida.")

    try:
        provedor, info = assinatura_emissao.preparar(dados.metodo, db=db, user=user)
    except assinatura_emissao.MetodoInvalido as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    disponivel, motivo = provedor.disponivel()
    if not disponivel:
        raise HTTPException(status_code=409, detail=motivo)
    if modo == "rafael" and info.nivel != "qualificada":
        raise HTTPException(
            status_code=409,
            detail="Receitas encaminhadas ao Dr. Rafael exigem assinatura digital qualificada.",
        )

    medico = document_identity(user)
    paciente = _paciente(g) or ""
    corpo = f"Paciente: {paciente}\n\n{g.rendered_body}" if paciente else g.rendered_body
    data_emissao = _agora()
    pdf_visual = documento_generico(
        titulo=TITULO,
        corpo=corpo,
        medico=medico,
        endereco=resolver_endereco(user, dados.endereco or g.endereco_exibido),
        data_emissao=data_emissao,
        metodo_assinatura=dados.metodo,
        provedor_nome=info.nome,
    )
    try:
        emitido = assinatura_emissao.assinar_e_persistir(
            db,
            tipo=assinatura_emissao.TIPO_DOCUMENTO,
            referencia_id=g.id,
            metodo=dados.metodo,
            provedor=provedor,
            info=info,
            pdf_visual=pdf_visual,
            medico=medico,
            criado_por=user.id,
            data_emissao=data_emissao,
        )
    except assinatura_emissao.AssinaturaNaoDetectada as exc:
        raise HTTPException(
            status_code=409,
            detail=f"A assinatura digital nao pode ser validada: {exc}",
        ) from exc
    if emitido.registro.assinado_em is not None:
        novo_status = "assinado"
    elif dados.metodo == "MANUAL":
        if modo != "propria":
            raise HTTPException(status_code=409, detail="Emissão manual não é permitida no fluxo delegado.")
        novo_status = "emitida_manual"
    else:
        novo_status = "aguardando_assinatura_externa"
    _set_meta(g, status=novo_status, signed_by=user.id if novo_status == "assinado" else None,
              issued_at=data_emissao.isoformat())
    db.add(AuditLog(
        user_id=user.id, action="emitir_prescricao_livre_especial",
        entity="generated_document", entity_id=str(g.id),
        detail={"originator_id": _origem_id(g), "metodo": dados.metodo, "status": novo_status},
    ))
    db.commit()
    sufixo = "-assinado" if emitido.registro.assinado_em is not None else ""
    return Response(
        content=emitido.pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="receituario-{g.id}{sufixo}.pdf"',
            "X-Corvia-Assinatura": "assinada" if emitido.registro.assinado_em is not None else "nao-assinada",
        },
    )


@router.post("/{gid}/assinatura-externa")
async def assinatura_externa(
    gid: int,
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    g = _documento_especial(db, gid)
    if _signer_id(g) != user.id:
        raise HTTPException(status_code=403, detail="Somente o prescritor designado pode concluir a assinatura.")
    if _status(g) != "aguardando_assinatura_externa":
        raise HTTPException(status_code=409, detail="Esta receita não aguarda assinatura externa.")

    registro_original = assinatura_emissao.buscar(
        db, tipo=assinatura_emissao.TIPO_DOCUMENTO, referencia_id=g.id,
    )
    if registro_original is None or registro_original.assinado_em is not None:
        raise HTTPException(status_code=409, detail="O PDF original desta receita não está disponível para assinatura externa.")
    pdf_original = assinatura_emissao.ler_bytes(registro_original)

    conteudo = await arquivo.read(TAMANHO_MAXIMO_PDF_ASSINADO + 1)
    if len(conteudo) > TAMANHO_MAXIMO_PDF_ASSINADO:
        raise HTTPException(status_code=413, detail="O PDF assinado precisa ter no máximo 15 MB.")
    if not conteudo:
        raise HTTPException(status_code=422, detail="Envie o PDF assinado.")
    try:
        validate_file(conteudo, arquivo.filename or "receita-assinada.pdf", "exam")
    except UploadRejected as erro:
        raise HTTPException(status_code=erro.status_code, detail=erro.detail) from None
    if not conteudo.startswith(b"%PDF-"):
        raise HTTPException(status_code=422, detail="Envie o PDF assinado, não uma imagem.")
    # O Assinador ITI/PAdES trabalha por atualização incremental: os bytes
    # do documento que saiu da CorVIA permanecem como prefixo exato e a
    # assinatura é acrescentada. Isso impede aceitar um PDF assinado de
    # outra receita apenas porque sua assinatura criptográfica é válida.
    if not conteudo.startswith(pdf_original):
        raise HTTPException(
            status_code=422,
            detail="O PDF enviado não corresponde à receita emitida pela CorVIA. Assine e devolva exatamente o arquivo original.",
        )

    try:
        emitido = await asyncio.to_thread(
            assinatura_emissao.concluir_assinatura_externa,
            db,
            tipo=assinatura_emissao.TIPO_DOCUMENTO,
            referencia_id=g.id,
            pdf_assinado=conteudo,
            criado_por=user.id,
        )
    except assinatura_emissao.AssinaturaNaoDetectada as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except assinatura_emissao.FluxoAssinaturaExternaInvalido as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    _set_meta(g, status="assinado", signed_by=user.id)
    db.add(AuditLog(
        user_id=user.id, action="concluir_assinatura_externa_prescricao_especial",
        entity="generated_document", entity_id=str(g.id),
        detail={"originator_id": _origem_id(g), "sha256": emitido.registro.sha256},
    ))
    db.commit()
    return _serializar(db, g)


@router.get("/{gid}/pdf")
def pdf(gid: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    g = _documento_especial(db, gid)
    if not _autoriza_leitura(g, user):
        raise HTTPException(status_code=404, detail="Prescrição não encontrada.")
    registro = assinatura_emissao.buscar(
        db, tipo=assinatura_emissao.TIPO_DOCUMENTO, referencia_id=g.id,
    )
    if not registro or (registro.assinado_em is None and _status(g) != "emitida_manual"):
        raise HTTPException(status_code=409, detail="A receita ainda não está disponível para impressão/download.")
    conteudo = assinatura_emissao.ler_bytes(registro)
    sufixo = "-assinado" if registro.assinado_em is not None else ""
    return Response(
        content=conteudo,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="receituario-{g.id}{sufixo}.pdf"',
            "X-Corvia-Assinatura": "assinada" if registro.assinado_em is not None else "nao-assinada",
        },
    )


@router.post("/{gid}/enviar-email")
def enviar_email(
    gid: int,
    dados: EnviarEmailIn,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    g = _documento_especial(db, gid)
    if _origem_id(g) != user.id:
        raise HTTPException(status_code=404, detail="Prescrição não encontrada.")
    registro = assinatura_emissao.buscar(
        db, tipo=assinatura_emissao.TIPO_DOCUMENTO, referencia_id=g.id,
    )
    if not registro or (registro.assinado_em is None and _status(g) != "emitida_manual"):
        raise HTTPException(status_code=409, detail="A receita ainda não está disponível para envio.")

    signer = db.get(User, _signer_id(g))
    link = DocumentShareLink(
        tipo="generated_document",
        referencia_id=g.id,
        criado_por=user.id,
        expires_at=_agora() + timedelta(days=VALIDADE_LINK_DIAS),
    )
    db.add(link)
    db.commit()
    db.refresh(link)
    url = f"{settings.public_url}/api/documentos-publicos/{link.token}"
    divulgacao = None
    if registro.assinado_em is not None and registro.nivel == "qualificada":
        divulgacao = divulgacao_email.texto_divulgacao(assinatura_emissao.ler_bytes(registro))
    html = emails.montar_html_documento_disponivel(
        nome_medico=professional_name(signer) if signer else "CorVIA",
        url=url,
        dias_validade=VALIDADE_LINK_DIAS,
        divulgacao_assinatura=divulgacao,
    )
    resultado = envio_documento_email.enviar(
        db,
        user,
        destinatario=dados.email,
        assunto=emails.ASSUNTO_DOCUMENTO_DISPONIVEL,
        corpo_html=html,
    )
    db.add(AuditLog(
        user_id=user.id,
        action="enviar_email_prescricao_livre_especial",
        entity="generated_document",
        entity_id=str(g.id),
        detail={"enviado": resultado.enviado, "erro": resultado.erro, "signer_id": _signer_id(g)},
    ))
    db.commit()
    return {
        "enviado": resultado.enviado,
        "link": None if resultado.enviado else url,
        "erro": None if resultado.enviado else resultado.erro,
    }
