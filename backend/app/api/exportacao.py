"""Tarefas 12 e 16 — exportação em PDF: material do paciente e modo apresentação.

As duas moram no mesmo router porque compartilham o mesmo motor de PDF e a
mesma regra de fundo: **exportar não cria conteúdo**. O que sai daqui é o que já
está publicado e verificado na plataforma, em outro formato.

O que muda entre elas é o destinatário, e isso muda tudo no desenho da página:
o material do paciente é retrato, corpo de leitura, linguagem leiga; a
apresentação é paisagem, corpo de projeção, um assunto por página.
"""

from __future__ import annotations

import re
import unicodedata
from datetime import datetime, timedelta, timezone
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.core.security import assinatura_email_ativa, current_user
from app.models.audit import AuditLog
from app.models.compartilhamento import DocumentShareLink
from app.models.content import Document
from app.models.email_account import EmailAccount
from app.models.patient_document_email_send import (
    CANAL_AUTO_CONTATO_CORVIA, CANAL_PROPRIO_CORVIA_MAIL, TIPO_MATERIAL,
    PatientDocumentEmailSend,
)
from app.models.patient_material import PatientMaterial
from app.models.patient_material_send import PatientMaterialSend
from app.services import anexo_email_proprio
from app.services import apresentacao as svc_apres
from app.services import apresentacao_pptx as svc_apres_pptx
from app.services import cofre, emails, mail360
from app.services import material_paciente as svc_material
from app.services.professional_profile import document_identity, professional_name
from app.services.mail360 import Mail360Error

router = APIRouter(tags=["exportação"])

LIMITE_ANOTACAO = 2000


def _dados_do_medico(user) -> dict:
    return document_identity(user)


def _nome_arquivo(base: str, sufixo: str, extensao: str = "pdf") -> str:
    """Nome de arquivo sem acento e sem espaço.

    O cabeçalho `Content-Disposition` é latin-1 por padrão: acento cru nele faz o
    navegador baixar com nome corrompido, ou o servidor recusar o header.
    """
    limpo = unicodedata.normalize("NFKD", base).encode("ascii", "ignore").decode()
    limpo = re.sub(r"[^A-Za-z0-9]+", "-", limpo).strip("-").lower()[:80]
    return f"{limpo or 'corvia'}-{sufixo}.{extensao}"


def _pdf(conteudo: bytes, nome: str) -> Response:
    return Response(
        content=conteudo,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{nome}"'},
    )


def _pptx(conteudo: bytes, nome: str) -> Response:
    return Response(
        content=conteudo,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={"Content-Disposition": f'attachment; filename="{nome}"'},
    )


# ---------------------------------------------------------------------------
# Tarefa 16 — modo apresentação
# ---------------------------------------------------------------------------

class PedidoApresentacao(BaseModel):
    anotacao: str = Field(default="", max_length=LIMITE_ANOTACAO)
    # PDF pronto para projetar (padrão, comportamento inalterado) ou PPTX
    # editável — pedido do Rafael em 07/08/2026, para o assinante poder
    # ajustar os slides (reordenar, cortar, incluir algo próprio) antes de
    # apresentar. Mesmo conteúdo nos dois formatos; só muda o arquivo.
    formato: str = Field(default="pdf")

    @field_validator("formato")
    @classmethod
    def _formato_valido(cls, v: str) -> str:
        v = (v or "pdf").strip().lower()
        if v not in ("pdf", "pptx"):
            raise ValueError("formato precisa ser 'pdf' ou 'pptx'.")
        return v


@router.post("/api/biblioteca/{slug}/apresentacao")
def exportar_apresentacao(
    slug: str,
    dados: PedidoApresentacao | None = None,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    """Exporta um documento publicado como apresentação para aula ou round,
    em PDF (pronto para projetar) ou PowerPoint (editável).

    A anotação chega por POST e **não é gravada em lugar nenhum**: ela existe
    durante a geração do arquivo e some. É deliberado — a observação de um round
    específico não é conteúdo da plataforma, e persistir seria o primeiro passo
    para ela reaparecer como se fosse.
    """
    doc = (db.query(Document)
             .filter(Document.slug == slug, Document.published.is_(True))
             .first())
    if doc is None:
        raise HTTPException(status_code=404, detail="Documento não encontrado ou não publicado.")

    anotacao = (dados.anotacao if dados else "") or ""
    formato = (dados.formato if dados else "pdf") or "pdf"
    medico = _dados_do_medico(user)

    if formato == "pptx":
        arquivo = svc_apres_pptx.gerar(doc, medico, anotacao=anotacao.strip())
        resposta = _pptx(arquivo, _nome_arquivo(doc.title, "apresentacao", "pptx"))
    else:
        arquivo = svc_apres.gerar(doc, medico, anotacao=anotacao.strip())
        resposta = _pdf(arquivo, _nome_arquivo(doc.title, "apresentacao"))

    db.add(AuditLog(user_id=user.id, action="exportar_apresentacao", entity="documents",
                    entity_id=slug[:255],
                    detail={"com_anotacao": bool(anotacao.strip()), "bytes": len(arquivo), "formato": formato}))
    db.commit()
    return resposta


# ---------------------------------------------------------------------------
# Tarefa 12 — material educativo do paciente
# ---------------------------------------------------------------------------

def _dump(m: PatientMaterial) -> dict:
    return {
        "slug": m.slug, "titulo": m.titulo, "subtitulo": m.subtitulo,
        "tema": m.tema, "resumo": m.resumo, "documento_slug": m.documento_slug,
        "secoes": m.secoes or [], "sinais_de_alerta": list(m.sinais_de_alerta or []),
        "perguntas": list(m.perguntas or []), "fontes": list(m.fontes or []),
    }


@router.get("/api/material-paciente")
def listar_materiais(db: Session = Depends(get_db), _=Depends(current_user)):
    itens = (db.query(PatientMaterial)
               .filter(PatientMaterial.published.is_(True))
               .order_by(PatientMaterial.titulo)
               .all())
    return [{"slug": m.slug, "titulo": m.titulo, "subtitulo": m.subtitulo,
             "tema": m.tema, "resumo": m.resumo} for m in itens]


@router.get("/api/material-paciente/{slug}")
def obter_material(slug: str, db: Session = Depends(get_db), _=Depends(current_user)):
    m = (db.query(PatientMaterial)
           .filter(PatientMaterial.slug == slug, PatientMaterial.published.is_(True))
           .first())
    if m is None:
        raise HTTPException(status_code=404, detail="Material não encontrado.")
    return _dump(m)


@router.get("/api/material-paciente/{slug}/pdf")
def baixar_material(slug: str, db: Session = Depends(get_db), user=Depends(current_user)):
    """Gera o PDF que o médico imprime e entrega ao paciente.

    A identificação do prescritor vem do perfil de quem pede — o papel sai com o
    nome de quem entrega, e não genérico, porque é a essa pessoa que o paciente
    volta com dúvida.
    """
    m = (db.query(PatientMaterial)
           .filter(PatientMaterial.slug == slug, PatientMaterial.published.is_(True))
           .first())
    if m is None:
        raise HTTPException(status_code=404, detail="Material não encontrado.")

    pdf = svc_material.gerar(m, _dados_do_medico(user))
    db.add(AuditLog(user_id=user.id, action="gerar_material_paciente",
                    entity="patient_materials", entity_id=slug[:255],
                    detail={"bytes": len(pdf)}))
    db.commit()
    return _pdf(pdf, _nome_arquivo(m.titulo, "material-do-paciente"))


# ---------------------------------------------------------------------------
# Envio de material do paciente por e-mail, do endereço do médico
# (material-paciente-por-email-spec.md, 02/08/2026)
# ---------------------------------------------------------------------------

DIAS_VALIDADE_LINK_MATERIAL = 14
# Teto por conta — spec: "sugestão inicial: 50/dia, 200/mês". Numa única
# constante para não divergir entre a checagem diária e a mensal.
LIMITE_DESTINATARIOS_DIA = 50
LIMITE_DESTINATARIOS_MES = 200


class EnvioMaterialPaciente(BaseModel):
    # O corpo do e-mail aprovado no spec usa "{{nome_paciente}}," na
    # saudação — a seção de Interface do mesmo spec listava só e-mail e
    # recado como campos, sem prever de onde viria o nome. Sem um campo
    # próprio o texto aprovado não tem como renderizar; acrescentado aqui
    # como o mínimo necessário para cumprir o texto já aprovado, não como
    # reescrita dele.
    nome_paciente: str = Field(min_length=1, max_length=200)
    email_paciente: str
    recado: str | None = Field(default=None, max_length=500)
    consentimento: bool = False

    @field_validator("email_paciente")
    @classmethod
    def _email(cls, v: str) -> str:
        v = v.strip().lower()
        if "@" not in v:
            raise ValueError("E-mail inválido.")
        return v

    @field_validator("recado")
    @classmethod
    def _recado_sem_marcacao(cls, v: str | None) -> str | None:
        # Texto puro, sem HTML — evita injeção no e-mail montado e evita que
        # o recado vire canal de mensagem clínica formatada (spec, seção
        # Interface: "texto puro, limitado, sem HTML").
        v = (v or "").strip()
        if not v:
            return None
        if "<" in v or ">" in v:
            raise ValueError("O recado não pode conter marcação (HTML).")
        return v


@router.post("/api/material-paciente/{slug}/enviar-email")
def enviar_material_por_email(
    slug: str, dados: EnvioMaterialPaciente,
    db: Session = Depends(get_db), user=Depends(current_user),
):
    """Só o link vai por e-mail, nunca o PDF anexado (regra inegociável do
    spec) — o e-mail sai do endereço do próprio médico via Mail360, com
    `Reply-To` implícito nele mesmo (é a caixa dele, a resposta cai lá sem
    configuração extra). Um médico sem CorvIA Mail ativo não consegue enviar
    por aqui de jeito nenhum, mesmo manipulando a chamada diretamente — a
    checagem do lado do servidor não depende do botão estar desabilitado no
    frontend."""
    m = (
        db.query(PatientMaterial)
        .filter(PatientMaterial.slug == slug, PatientMaterial.published.is_(True))
        .first()
    )
    if m is None:
        raise HTTPException(status_code=404, detail="Material não encontrado.")

    if not dados.consentimento:
        raise HTTPException(
            status_code=422,
            detail="Confirme que o paciente autorizou receber este material por e-mail.",
        )

    if not assinatura_email_ativa(db, user):
        raise HTTPException(
            status_code=409,
            detail=(
                "Enviar em nome próprio exige o CorvIA Mail ativo. "
                'Use "Gerar link" para compartilhar por outro canal.'
            ),
        )
    conta = db.query(EmailAccount).filter(EmailAccount.user_id == user.id).first()
    if not conta or conta.status != "ativa":
        raise HTTPException(status_code=409, detail="Sua caixa do CorvIA Mail não está ativa.")
    if conta.envio_material_suspenso:
        raise HTTPException(
            status_code=409,
            detail=(
                "O envio de material a pacientes está suspenso nesta conta por reclamações "
                "de spam. Fale com o suporte para reativar."
            ),
        )

    # Teto por conta ANTES de criar link ou tentar enviar — é a trava que
    # protege a reputação do domínio, tem que valer mesmo que o resto falhe.
    agora = datetime.now(timezone.utc)
    inicio_dia = agora.replace(hour=0, minute=0, second=0, microsecond=0)
    inicio_mes = agora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    envios_hoje = (
        db.query(PatientMaterialSend)
        .filter(PatientMaterialSend.enviado_por == user.id, PatientMaterialSend.created_at >= inicio_dia)
        .count()
    )
    if envios_hoje >= LIMITE_DESTINATARIOS_DIA:
        raise HTTPException(
            status_code=429, detail=f"Limite diário de {LIMITE_DESTINATARIOS_DIA} envios a pacientes atingido."
        )
    envios_mes = (
        db.query(PatientMaterialSend)
        .filter(PatientMaterialSend.enviado_por == user.id, PatientMaterialSend.created_at >= inicio_mes)
        .count()
    )
    if envios_mes >= LIMITE_DESTINATARIOS_MES:
        raise HTTPException(
            status_code=429, detail=f"Limite mensal de {LIMITE_DESTINATARIOS_MES} envios a pacientes atingido."
        )

    link = DocumentShareLink(
        tipo="patient_material", referencia_id=m.id, criado_por=user.id,
        expires_at=agora + timedelta(days=DIAS_VALIDADE_LINK_MATERIAL),
    )
    db.add(link)
    db.commit()
    db.refresh(link)

    envio = PatientMaterialSend(
        share_link_id=link.id, material_id=m.id, enviado_por=user.id,
        paciente_email_cifrado=cofre.cifrar_campo(dados.email_paciente, link.id),
        recado_cifrado=cofre.cifrar_campo(dados.recado, link.id) if dados.recado else None,
        consentimento_confirmado=True, canal="mail360",
    )
    db.add(envio)
    db.commit()

    url = f"{settings.public_url}/api/documentos-publicos/{link.token}"
    html = emails.montar_html_material_paciente(
        nome_paciente=dados.nome_paciente, nome_medico=user.full_name,
        recado=dados.recado, url=url, dias_validade=DIAS_VALIDADE_LINK_MATERIAL,
    )

    enviado, erro = True, None
    try:
        mail360.enviar_mensagem(
            account_key=conta.mail360_account_key, remetente=conta.email_address,
            para=dados.email_paciente, assunto=emails.ASSUNTO_MATERIAL_PACIENTE, corpo_html=html,
        )
    except Mail360Error as e:
        enviado, erro = False, str(e)

    db.add(AuditLog(
        user_id=user.id, action="enviar_material_paciente_email", entity="patient_materials",
        entity_id=slug[:255],
        detail={"enviado": enviado, "tem_recado": bool(dados.recado), "erro": erro},
    ))
    db.commit()

    if not enviado:
        raise HTTPException(
            status_code=502,
            detail='Não foi possível enviar o e-mail agora. Tente novamente, ou use "Gerar link".',
        )
    return {"enviado": True, "expira_em": link.expires_at}


@router.get("/api/material-paciente/{slug}/envios")
def listar_envios_material(slug: str, db: Session = Depends(get_db), user=Depends(current_user)):
    """Se o paciente abriu o link — informação clínica útil, e já vem de
    graça de `DocumentShareLink.primeiro_acesso_em`/`acessos` (spec: "custa
    zero a mais"). Nunca decifra o e-mail do paciente aqui: o médico já sabe
    para quem mandou, não precisa que o sistema reexiba."""
    m = (
        db.query(PatientMaterial)
        .filter(PatientMaterial.slug == slug, PatientMaterial.published.is_(True))
        .first()
    )
    if m is None:
        raise HTTPException(status_code=404, detail="Material não encontrado.")

    linhas = (
        db.query(PatientMaterialSend, DocumentShareLink)
        .join(DocumentShareLink, DocumentShareLink.id == PatientMaterialSend.share_link_id)
        .filter(PatientMaterialSend.material_id == m.id, PatientMaterialSend.enviado_por == user.id)
        .order_by(PatientMaterialSend.created_at.desc())
        .limit(50)
        .all()
    )
    return [
        {
            "enviado_em": envio.created_at, "expira_em": link.expires_at,
            "aberto": link.primeiro_acesso_em is not None, "acessos": link.acessos,
        }
        for envio, link in linhas
    ]


# ---------------------------------------------------------------------------
# Oferta unificada de envio ao paciente por e-mail (pedido do Rafael,
# 08/08/2026) — mesmo par de canais de `documents.py::envio_paciente_gerado`
# e `receituario.py::envio_paciente_receita`, sem a exigência de assinatura
# digital (Material ao Paciente não é documento assinado). Endpoint
# NOVO, distinto de `POST /enviar-email` acima (que continua existindo,
# inalterado, para quem já usa o fluxo antigo de link direto pela própria
# caixa).
# ---------------------------------------------------------------------------


class EnvioPacienteMaterialIn(BaseModel):
    email_paciente: str
    nome_paciente: str = Field(min_length=1, max_length=200)
    recado: str | None = Field(default=None, max_length=500)
    consentimento: bool = False
    canal: Literal["auto_contato_corvia", "proprio_corvia_mail"]

    @field_validator("email_paciente")
    @classmethod
    def _email(cls, v: str) -> str:
        v = v.strip().lower()
        if "@" not in v:
            raise ValueError("E-mail inválido.")
        return v

    @field_validator("recado")
    @classmethod
    def _recado_sem_marcacao(cls, v: str | None) -> str | None:
        v = (v or "").strip()
        if not v:
            return None
        if "<" in v or ">" in v:
            raise ValueError("O recado não pode conter marcação (HTML).")
        return v


@router.post("/api/material-paciente/{slug}/envio-paciente")
def envio_paciente_material(
    slug: str, dados: EnvioPacienteMaterialIn,
    db: Session = Depends(get_db), user=Depends(current_user),
):
    """Oferta de envio ao paciente logo depois de gerar o Material ao
    Paciente — mesmo fluxo de `documents.py`/`receituario.py`, sem a
    exigência de assinatura digital (este material não é documento clínico
    assinado). Mesmo teto diário/mensal de `enviar_material_por_email`
    acima, contado à parte na tabela nova (`PatientDocumentEmailSend`) —
    os dois canais daqui não compartilham volume com o fluxo antigo."""
    m = (
        db.query(PatientMaterial)
        .filter(PatientMaterial.slug == slug, PatientMaterial.published.is_(True))
        .first()
    )
    if m is None:
        raise HTTPException(status_code=404, detail="Material não encontrado.")
    if not dados.consentimento:
        raise HTTPException(
            status_code=422,
            detail="Confirme que o paciente autorizou receber este material por e-mail.",
        )

    if not assinatura_email_ativa(db, user):
        raise HTTPException(status_code=409, detail="Este recurso exige CorvIA Mail ativo.")
    conta = db.query(EmailAccount).filter(EmailAccount.user_id == user.id).first()
    if not conta or conta.status != "ativa":
        raise HTTPException(status_code=409, detail="Sua caixa do CorvIA Mail não está ativa.")
    if conta.envio_material_suspenso:
        raise HTTPException(
            status_code=409,
            detail=(
                "O envio de material a pacientes está suspenso nesta conta por reclamações "
                "de spam. Fale com o suporte para reativar."
            ),
        )

    agora = datetime.now(timezone.utc)
    inicio_dia = agora.replace(hour=0, minute=0, second=0, microsecond=0)
    inicio_mes = agora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    base_query = db.query(PatientDocumentEmailSend).filter(
        PatientDocumentEmailSend.enviado_por == user.id,
        PatientDocumentEmailSend.tipo_origem == TIPO_MATERIAL,
    )
    if base_query.filter(PatientDocumentEmailSend.created_at >= inicio_dia).count() >= LIMITE_DESTINATARIOS_DIA:
        raise HTTPException(
            status_code=429, detail=f"Limite diário de {LIMITE_DESTINATARIOS_DIA} envios a pacientes atingido."
        )
    if base_query.filter(PatientDocumentEmailSend.created_at >= inicio_mes).count() >= LIMITE_DESTINATARIOS_MES:
        raise HTTPException(
            status_code=429, detail=f"Limite mensal de {LIMITE_DESTINATARIOS_MES} envios a pacientes atingido."
        )

    if dados.canal == CANAL_AUTO_CONTATO_CORVIA:
        link = DocumentShareLink(
            tipo="patient_material", referencia_id=m.id, criado_por=user.id,
            expires_at=agora + timedelta(days=DIAS_VALIDADE_LINK_MATERIAL),
        )
        db.add(link)
        db.commit()
        db.refresh(link)

        url = f"{settings.public_url}/api/documentos-publicos/{link.token}"
        html = emails.montar_html_material_paciente(
            nome_paciente=dados.nome_paciente, nome_medico=professional_name(user),
            recado=dados.recado, url=url, dias_validade=DIAS_VALIDADE_LINK_MATERIAL,
        )
        resultado = emails.enviar_institucional_paciente(
            db, user_id=user.id, destinatario=dados.email_paciente,
            assunto=emails.ASSUNTO_MATERIAL_PACIENTE, html=html, tipo_log="material_paciente_auto",
        )
        db.add(PatientDocumentEmailSend(
            tipo_origem=TIPO_MATERIAL, referencia_id=m.id, canal=dados.canal,
            share_link_id=link.id, enviado_por=user.id,
            paciente_email_cifrado=cofre.cifrar_campo(dados.email_paciente, m.id),
            assinatura_confirmada=False, sucesso=resultado.enviado,
        ))
        db.add(AuditLog(
            user_id=user.id, action="envio_paciente_material", entity="patient_materials",
            entity_id=slug[:255],
            detail={"canal": dados.canal, "enviado": resultado.enviado, "erro": resultado.erro},
        ))
        db.commit()
        return {
            "canal": dados.canal, "enviado": resultado.enviado, "erro": resultado.erro,
            "anexo": None, "assunto_sugerido": None, "corpo_sugerido": None,
        }

    assert dados.canal == CANAL_PROPRIO_CORVIA_MAIL  # só resta este valor no Literal
    pdf = svc_material.gerar(m, _dados_do_medico(user))
    nome_arquivo = _nome_arquivo(m.titulo, "material-do-paciente")
    try:
        anexo = anexo_email_proprio.preparar(db, user, nome_arquivo=nome_arquivo, conteudo=pdf)
    except anexo_email_proprio.AnexoIndisponivel as e:
        raise HTTPException(status_code=502, detail=str(e)) from e

    db.add(PatientDocumentEmailSend(
        tipo_origem=TIPO_MATERIAL, referencia_id=m.id, canal=dados.canal,
        share_link_id=None, enviado_por=user.id,
        paciente_email_cifrado=cofre.cifrar_campo(dados.email_paciente, m.id),
        assinatura_confirmada=False, sucesso=True,
    ))
    db.add(AuditLog(
        user_id=user.id, action="envio_paciente_material", entity="patient_materials",
        entity_id=slug[:255], detail={"canal": dados.canal, "anexo_file_id": anexo.file_id},
    ))
    db.commit()
    corpo_sugerido = f"Olá {dados.nome_paciente},\n\n{dados.recado}\n" if dados.recado else ""
    return {
        "canal": dados.canal, "enviado": None, "erro": None,
        "anexo": {"file_id": anexo.file_id, "nome": anexo.nome},
        "assunto_sugerido": f"{m.titulo} — Corvia",
        "corpo_sugerido": corpo_sugerido,
    }
