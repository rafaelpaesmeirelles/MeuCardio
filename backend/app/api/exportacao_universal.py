"""Exportação universal em PDF, PowerPoint e Word do CorVIA.

A API recebe apenas identificadores de objetos canônicos. O texto exportado é
resolvido novamente no servidor a partir do conteúdo publicado; nunca recebe
HTML/prosa clínica do cliente. Isso mantém a mesma barreira editorial da UI.

Assinantes com CorVIA Mail ativo também podem enviar o arquivo diretamente pela
própria caixa nativa. A checagem do add-on e da caixa é feita no servidor; o
botão do frontend é apenas conveniência visual, nunca controle de acesso.
"""
from __future__ import annotations

import re
import unicodedata

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import assinatura_email_ativa, current_user
from app.models.audit import AuditLog
from app.services import anexo_email_proprio, mail360
from app.services.email_signature import montar_assinatura_html, montar_corpo_com_assinatura
from app.services.exportacao_conteudo import TIPOS_EXPORTAVEIS, catalogo, gerar_pdf, resolver_conteudo
from app.services.exportacao_office import gerar_docx, gerar_pptx
from app.services.mail360 import Mail360Error
from app.services.professional_profile import document_identity
from app.services.assinatura.provedor import obter_provedor
from app.services.assinatura.verificacao_pdf import verificar as verificar_assinatura_pdf

router = APIRouter(prefix="/api/exportar", tags=["exportação"])
_EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


class ItemExportacao(BaseModel):
    tipo: str = Field(min_length=2, max_length=40)
    slug: str = Field(min_length=1, max_length=255)

    @field_validator("tipo")
    @classmethod
    def tipo_valido(cls, valor: str) -> str:
        valor = valor.strip().lower()
        if valor not in TIPOS_EXPORTAVEIS:
            raise ValueError(f"Tipo não exportável. Use um de: {', '.join(sorted(TIPOS_EXPORTAVEIS))}")
        return valor

    @field_validator("slug")
    @classmethod
    def slug_valido(cls, valor: str) -> str:
        valor = valor.strip()
        if not valor:
            raise ValueError("Identificador vazio.")
        return valor


class PedidoExportacao(BaseModel):
    itens: list[ItemExportacao] = Field(min_length=1, max_length=50)
    incluir_dados_assinante: bool = False
    titulo: str | None = Field(default=None, max_length=180)
    formato: str = Field(default="pdf")
    assinar_digitalmente: bool = False

    @field_validator("formato")
    @classmethod
    def formato_valido(cls, valor: str) -> str:
        valor = (valor or "pdf").strip().lower()
        if valor not in {"pdf", "pptx", "docx"}:
            raise ValueError("Formato inválido. Use 'pdf', 'pptx' ou 'docx'.")
        return valor

    @field_validator("itens")
    @classmethod
    def sem_duplicatas(cls, itens: list[ItemExportacao]) -> list[ItemExportacao]:
        vistos: set[tuple[str, str]] = set()
        saida: list[ItemExportacao] = []
        for item in itens:
            chave = (item.tipo, item.slug)
            if chave in vistos:
                continue
            vistos.add(chave)
            saida.append(item)
        if not saida:
            raise ValueError("Selecione pelo menos um conteúdo.")
        return saida


class PedidoEnvioEmail(PedidoExportacao):
    para: str = Field(min_length=5, max_length=320)
    assunto: str | None = Field(default=None, max_length=240)
    mensagem: str | None = Field(default=None, max_length=5000)
    cc: str | None = Field(default=None, max_length=320)
    cco: str | None = Field(default=None, max_length=320)

    @field_validator("para")
    @classmethod
    def destinatario_valido(cls, valor: str) -> str:
        valor = valor.strip().lower()
        if not valor or not _EMAIL_RE.fullmatch(valor):
            raise ValueError("Endereço de e-mail inválido.")
        return valor

    @field_validator("cc", "cco")
    @classmethod
    def email_opcional_valido(cls, valor: str | None) -> str | None:
        if valor is None:
            return None
        valor = valor.strip().lower()
        if not valor:
            return None
        if not _EMAIL_RE.fullmatch(valor):
            raise ValueError("Endereço de e-mail inválido.")
        return valor


class ArquivoGerado(BaseModel):
    nome: str
    titulo: str
    conteudo: bytes
    quantidade: int
    itens: list[dict]
    formato: str
    media_type: str
    assinado_digitalmente: bool = False


def _arquivo(nome: str, formato: str) -> str:
    valor = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode()
    valor = re.sub(r"[^A-Za-z0-9]+", "-", valor).strip("-").lower()[:90]
    return f"{valor or 'conteudo-corvia'}.{formato}"


def _gerar_do_pedido(dados: PedidoExportacao, db: Session, user) -> ArquivoGerado:
    if dados.assinar_digitalmente and dados.formato != "pdf":
        raise HTTPException(
            status_code=422,
            detail=(
                "A assinatura digital qualificada está disponível somente para PDF. "
                "PowerPoint e Word permanecem editáveis e não recebem uma imagem que simule assinatura."
            ),
        )

    uf = (user.council_state or "").strip().upper() or None
    resolvidos = []
    ausentes = []
    for pedido in dados.itens:
        item = resolver_conteudo(db, pedido.tipo, pedido.slug, uf=uf)
        if item is None:
            ausentes.append({"tipo": pedido.tipo, "slug": pedido.slug})
        else:
            resolvidos.append(item)

    # Fail closed: não gera um arquivo parcial silenciosamente. Se o usuário
    # selecionou 8 itens e um foi despublicado entre a seleção e o clique,
    # precisa saber; omitir esse item sem aviso faria o arquivo parecer completo.
    if ausentes:
        raise HTTPException(
            status_code=409,
            detail={
                "erro": "Um ou mais conteúdos deixaram de estar disponíveis para exportação.",
                "itens": [f"{item['tipo']}:{item['slug']}" for item in ausentes],
            },
        )

    try:
        geradores = {"pdf": gerar_pdf, "pptx": gerar_pptx, "docx": gerar_docx}
        conteudo = geradores[dados.formato](
            resolvidos, user=user,
            incluir_dados_assinante=dados.incluir_dados_assinante,
            titulo=dados.titulo,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    assinado_digitalmente = False
    if dados.assinar_digitalmente:
        provedor = obter_provedor("A1_ARQUIVO", db=db, user=user)
        disponivel, motivo = provedor.disponivel()
        if not disponivel:
            raise HTTPException(status_code=409, detail=motivo or "Certificado A1 indisponível.")

        assinatura = provedor.assinar(
            conteudo,
            document_identity(user),
            {"tipo": "exportação de conteúdo CorVIA"},
        )
        if assinatura.estado != "assinado" or assinatura.pdf is None:
            raise HTTPException(
                status_code=502,
                detail=assinatura.motivo or "O certificado não concluiu a assinatura digital.",
            )

        verificacao = verificar_assinatura_pdf(assinatura.pdf)
        if not verificacao or not (
            verificacao.intacta
            and verificacao.estrutura_valida
            and verificacao.cobre_documento_inteiro
        ):
            raise HTTPException(
                status_code=502,
                detail="A assinatura foi interrompida porque a verificação criptográfica final não foi aprovada.",
            )
        conteudo = assinatura.pdf
        assinado_digitalmente = True

    titulo = (dados.titulo or (resolvidos[0].titulo if len(resolvidos) == 1 else "Seleção de conteúdo CorVIA")).strip()
    return ArquivoGerado(
        nome=_arquivo(titulo, dados.formato),
        titulo=titulo,
        conteudo=conteudo,
        quantidade=len(resolvidos),
        itens=[{"tipo": item.tipo, "slug": item.slug} for item in resolvidos],
        formato=dados.formato,
        media_type={
            "pdf": "application/pdf",
            "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        }[dados.formato],
        assinado_digitalmente=assinado_digitalmente,
    )


@router.get("/catalogo")
def catalogo_exportavel(
    q: str | None = Query(None, max_length=160),
    tipo: str | None = Query(None, max_length=40),
    slug: str | None = Query(None, max_length=255),
    limite: int = Query(120, ge=1, le=200),
    db: Session = Depends(get_db),
    _=Depends(current_user),
):
    if tipo is not None and tipo not in TIPOS_EXPORTAVEIS:
        raise HTTPException(status_code=422, detail="Tipo de conteúdo não exportável.")
    itens = catalogo(db, q=q, tipo=tipo, slug=slug, limite=limite)
    return {"total": len(itens), "itens": itens, "tipos": sorted(TIPOS_EXPORTAVEIS)}


@router.get("/corvia-mail")
def disponibilidade_corvia_mail(
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    """Estado mínimo para a UI da exportação, sem abrir sessão da caixa.

    A exportação usa a sessão principal do CorVIA e pode enviar diretamente
    apenas pela caixa nativa do próprio usuário. A senha/sessão específica da
    caixa continua necessária para abrir e navegar no cliente de e-mail, mas
    não para anexar/enviar um arquivo que o próprio backend acabou de gerar.
    """
    if getattr(user, "investidor", False):
        return {"disponivel": False, "motivo": "Recurso indisponível no modo investidor.", "email_address": None}
    if not assinatura_email_ativa(db, user):
        return {"disponivel": False, "motivo": "O envio direto exige assinatura ativa do CorVIA Mail.", "email_address": None}
    if user.email_assinatura_digital_ativa:
        return {
            "disponivel": False,
            "motivo": (
                "A caixa nativa não suporta assinatura digital S/MIME. "
                "Envie por uma conta Google, Microsoft, Yahoo ou iCloud conectada."
            ),
            "email_address": None,
        }
    try:
        conta = anexo_email_proprio.obter_conta_nativa_ativa(db, user)
    except anexo_email_proprio.AnexoIndisponivel as exc:
        return {"disponivel": False, "motivo": str(exc), "email_address": None}
    return {"disponivel": True, "motivo": None, "email_address": conta.email_address}


@router.post("/conteudo")
def exportar_conteudo(
    dados: PedidoExportacao,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    arquivo = _gerar_do_pedido(dados, db, user)
    db.add(AuditLog(
        user_id=user.id,
        action="exportar_conteudo",
        entity="content_export",
        detail={
            "quantidade": arquivo.quantidade,
            "itens": arquivo.itens,
            "incluir_dados_assinante": dados.incluir_dados_assinante,
            "bytes": len(arquivo.conteudo),
            "formato": arquivo.formato,
            "assinado_digitalmente": arquivo.assinado_digitalmente,
        },
    ))
    db.commit()
    return Response(
        content=arquivo.conteudo,
        media_type=arquivo.media_type,
        headers={"Content-Disposition": f'attachment; filename="{arquivo.nome}"'},
    )


@router.post("/conteudo/enviar-email", status_code=201)
def enviar_conteudo_por_email(
    dados: PedidoEnvioEmail,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    """Gera e envia o formato escolhido diretamente pela caixa nativa CorVIA Mail.

    O arquivo é regenerado no servidor no momento do envio. Portanto não existe um
    caminho em que o cliente possa trocar o binário por outro arquivo ou mandar
    conteúdo clínico arbitrário sob a identidade do CorVIA.
    """
    if getattr(user, "investidor", False):
        raise HTTPException(status_code=403, detail="Recurso indisponível no modo investidor.")
    if not assinatura_email_ativa(db, user):
        raise HTTPException(status_code=409, detail="O envio direto exige assinatura ativa do CorVIA Mail.")
    if user.email_assinatura_digital_ativa:
        raise HTTPException(
            status_code=409,
            detail=(
                "A caixa nativa não suporta assinatura digital S/MIME. "
                "Envie por uma conta Google, Microsoft, Yahoo ou iCloud conectada."
            ),
        )

    try:
        conta = anexo_email_proprio.obter_conta_nativa_ativa(db, user)
    except anexo_email_proprio.AnexoIndisponivel as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    arquivo = _gerar_do_pedido(dados, db, user)
    if len(arquivo.conteudo) > 15 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="O arquivo gerado excede o limite de 15 MB para anexos do CorVIA Mail.")

    try:
        anexo = anexo_email_proprio.preparar(
            db,
            user,
            nome_arquivo=arquivo.nome,
            conteudo=arquivo.conteudo,
        )
    except anexo_email_proprio.AnexoIndisponivel as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    assunto = re.sub(r"[\r\n]+", " ", (dados.assunto or f"{arquivo.titulo} — CorVIA")).strip()
    mensagem = (dados.mensagem or "Segue em anexo o conteúdo exportado do CorVIA.").strip()
    corpo, formato = montar_corpo_com_assinatura(mensagem, montar_assinatura_html(user))
    try:
        resultado = mail360.enviar_mensagem(
            conta.mail360_account_key,
            conta.email_address,
            dados.para,
            assunto,
            corpo,
            anexos=[anexo.file_id],
            cc=dados.cc,
            cco=dados.cco,
            mail_format=formato,
        )
    except Mail360Error as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    # Não persiste endereço do destinatário em claro no audit log. O provedor
    # de e-mail já registra a mensagem na caixa do titular; para auditoria do
    # produto basta saber que houve envio, quais objetos originaram o arquivo e o
    # tamanho do arquivo.
    db.add(AuditLog(
        user_id=user.id,
        action="enviar_exportacao_corvia_mail",
        entity="content_export",
        detail={
            "quantidade": arquivo.quantidade,
            "itens": arquivo.itens,
            "incluir_dados_assinante": dados.incluir_dados_assinante,
            "bytes": len(arquivo.conteudo),
            "formato": arquivo.formato,
            "assinado_digitalmente": arquivo.assinado_digitalmente,
            "anexo_file_id": anexo.file_id,
            "com_cc": bool(dados.cc),
            "com_cco": bool(dados.cco),
        },
    ))
    db.commit()
    return {
        "enviado": True,
        "remetente": conta.email_address,
        "para": dados.para,
        "assunto": assunto,
        "arquivo": arquivo.nome,
        "message_id": resultado.get("messageId") if isinstance(resultado, dict) else None,
    }
