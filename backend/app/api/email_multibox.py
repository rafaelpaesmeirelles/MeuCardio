"""Extensão da caixa unificada para múltiplas caixas nativas CorVIA Mail.

Mantém a titularidade original de cada EmailAccount e concede acesso por uma
tabela explícita de delegação. Este router é incluído antes de ``email.router``
para substituir somente os contratos de contas/caixa unificada e acrescentar
rotas literais ``corvia-<id>``; todas as demais rotas continuam no módulo
canônico existente.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api import email as email_api
from app.core.db import get_db
from app.core.security import current_email_account
from app.models.email_account import EmailAccount
from app.models.user import User
from app.services import mail360
from app.services.mail360 import Mail360Error

router = APIRouter(prefix="/api/email", tags=["caixa de e-mail"])


def _pseudo_id(account_id: int) -> str:
    return f"corvia-{account_id}"


def _linked_accounts(db: Session, conta: EmailAccount) -> list[EmailAccount]:
    ids = list(
        db.execute(
            text(
                "SELECT email_account_id FROM email_mailbox_access "
                "WHERE owner_user_id = :owner ORDER BY email_account_id"
            ),
            {"owner": conta.user_id},
        ).scalars()
    )
    if not ids:
        return []
    contas = db.query(EmailAccount).filter(EmailAccount.id.in_(ids)).all()
    por_id = {item.id: item for item in contas}
    return [por_id[item_id] for item_id in ids if item_id in por_id and item_id != conta.id]


def _linked_account(db: Session, conta: EmailAccount, account_id: int) -> EmailAccount:
    permitido = db.execute(
        text(
            "SELECT 1 FROM email_mailbox_access "
            "WHERE owner_user_id = :owner AND email_account_id = :account LIMIT 1"
        ),
        {"owner": conta.user_id, "account": account_id},
    ).scalar_one_or_none()
    alvo = db.get(EmailAccount, account_id) if permitido else None
    if alvo is None or alvo.id == conta.id:
        raise HTTPException(status_code=404, detail="Caixa delegada não encontrada.")
    if not alvo.mail360_account_key:
        raise HTTPException(status_code=503, detail="Caixa delegada ainda não está disponível.")
    return alvo


@router.get("/contas")
def contas_da_caixa_unificada(
    db: Session = Depends(get_db),
    conta: EmailAccount = Depends(current_email_account),
):
    resultado = email_api.contas_da_caixa_unificada(db=db, conta=conta)
    titular = db.get(User, conta.user_id)
    padrao = (titular.email_conta_padrao_envio if titular else None) or "corvia"
    existentes = {item["id"] for item in resultado}
    for alvo in _linked_accounts(db, conta):
        pseudo = _pseudo_id(alvo.id)
        if pseudo in existentes:
            continue
        resultado.append(
            {
                "id": pseudo,
                "provider": "corvia",
                "display_name": "CorvIA Mail",
                "email_address": alvo.email_address,
                "native": True,
                "read_mail": True,
                "send_mail": True,
                "padrao": padrao == pseudo,
            }
        )
    return resultado


@router.put("/conta-padrao-envio")
def definir_conta_padrao_envio(
    dados: email_api.ContaPadraoEnvioIn,
    db: Session = Depends(get_db),
    conta: EmailAccount = Depends(current_email_account),
):
    validos = {item["id"] for item in contas_da_caixa_unificada(db=db, conta=conta) if item["send_mail"]}
    if dados.conta_id not in validos:
        raise HTTPException(status_code=422, detail="Conta inválida ou sem permissão de envio.")
    titular = db.get(User, conta.user_id)
    if titular is None:
        raise HTTPException(status_code=404, detail="Titular não encontrado.")
    titular.email_conta_padrao_envio = None if dados.conta_id == "corvia" else dados.conta_id
    db.commit()
    return {"conta_padrao_envio": dados.conta_id}


@router.get("/mensagens/todas")
def mensagens_todas(
    limite: int = 20,
    contas: str | None = None,
    db: Session = Depends(get_db),
    conta: EmailAccount = Depends(current_email_account),
):
    resultado = email_api.mensagens_todas(limite=limite, contas=contas, db=db, conta=conta)
    pedidas = {item.strip() for item in contas.split(",") if item.strip()} if contas is not None else None
    mensagens = list(resultado.get("mensagens", []))
    fontes_com_erro = list(resultado.get("fontes_com_erro", []))

    for alvo in _linked_accounts(db, conta):
        pseudo = _pseudo_id(alvo.id)
        if pedidas is not None and pseudo not in pedidas:
            continue
        try:
            email_api._exigir_configurado()
            for item in mail360.listar_mensagens(alvo.mail360_account_key, limite=limite):
                mensagens.append({**item, "origem": pseudo, "provider": "corvia"})
        except (Mail360Error, HTTPException) as exc:
            detalhe = exc.detail if isinstance(exc, HTTPException) else str(exc)
            fontes_com_erro.append({"origem": pseudo, "provider": "corvia", "erro": str(detalhe)})

    mensagens.sort(key=email_api._momento_da_mensagem, reverse=True)
    return {"mensagens": mensagens[:limite], "fontes_com_erro": fontes_com_erro}


@router.get("/externas/corvia-{account_id}/pastas")
def pastas_linked(
    account_id: int,
    db: Session = Depends(get_db),
    conta: EmailAccount = Depends(current_email_account),
):
    return email_api.pastas(conta=_linked_account(db, conta, account_id))


@router.get("/externas/corvia-{account_id}/mensagens")
def mensagens_linked(
    account_id: int,
    pasta: str | None = None,
    limite: int = 100,
    inicio: int = 1,
    db: Session = Depends(get_db),
    conta: EmailAccount = Depends(current_email_account),
):
    return email_api.mensagens(
        pasta=pasta,
        limite=limite,
        inicio=inicio,
        conta=_linked_account(db, conta, account_id),
    )


@router.get("/externas/corvia-{account_id}/mensagens/{message_id}")
def mensagem_linked(
    account_id: int,
    message_id: str,
    db: Session = Depends(get_db),
    conta: EmailAccount = Depends(current_email_account),
):
    return email_api.mensagem(message_id, conta=_linked_account(db, conta, account_id))


@router.put("/externas/corvia-{account_id}/mensagens/acoes", status_code=204)
def agir_em_mensagens_linked(
    account_id: int,
    dados: email_api.AcaoMensagens,
    db: Session = Depends(get_db),
    conta: EmailAccount = Depends(current_email_account),
):
    return email_api.agir_em_mensagens(dados, conta=_linked_account(db, conta, account_id))


@router.delete("/externas/corvia-{account_id}/mensagens/{message_id}", status_code=204)
def excluir_linked(
    account_id: int,
    message_id: str,
    db: Session = Depends(get_db),
    conta: EmailAccount = Depends(current_email_account),
):
    return email_api.excluir(message_id, conta=_linked_account(db, conta, account_id))


@router.post("/externas/corvia-{account_id}/mensagens", status_code=201)
def enviar_linked(
    account_id: int,
    dados: email_api.NovaMensagem,
    db: Session = Depends(get_db),
    conta: EmailAccount = Depends(current_email_account),
):
    alvo = _linked_account(db, conta, account_id)
    titular = db.get(User, conta.user_id)
    if email_api._assinatura_digital_solicitada(titular):
        raise HTTPException(
            status_code=409,
            detail=(
                "A assinatura digital S/MIME está ativa. A caixa nativa CorVIA/Mail360 não aceita "
                "MIME assinado; selecione uma conta externa compatível para enviar."
            ),
        )
    corpo, formato = email_api.montar_corpo_com_assinatura(
        dados.corpo_html, email_api.montar_assinatura_html(titular)
    )
    try:
        return mail360.enviar_mensagem(
            alvo.mail360_account_key,
            alvo.email_address,
            dados.para,
            dados.assunto,
            corpo,
            anexos=dados.anexos,
            cc=dados.cc,
            cco=dados.cco,
            mail_format=formato,
        )
    except Mail360Error as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/externas/corvia-{account_id}/mensagens/{message_id}/responder", status_code=201)
def responder_linked(
    account_id: int,
    message_id: str,
    dados: email_api.ResponderMensagem,
    db: Session = Depends(get_db),
    conta: EmailAccount = Depends(current_email_account),
):
    alvo = _linked_account(db, conta, account_id)
    titular = db.get(User, conta.user_id)
    if email_api._assinatura_digital_solicitada(titular):
        raise HTTPException(status_code=409, detail="A assinatura digital S/MIME está ativa; responda por uma conta externa compatível.")
    conteudo, formato = email_api.montar_corpo_com_assinatura(
        dados.conteudo, email_api.montar_assinatura_html(titular)
    )
    try:
        return mail360.responder_mensagem(
            alvo.mail360_account_key,
            message_id,
            alvo.email_address,
            dados.acao,
            dados.assunto,
            conteudo,
            para=dados.para,
            cc=dados.cc,
            cco=dados.cco,
            anexos=dados.anexos,
            mail_format=formato,
        )
    except Mail360Error as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/externas/corvia-{account_id}/mensagens/anexos", status_code=201)
async def enviar_anexo_linked(
    account_id: int,
    arquivo: UploadFile,
    db: Session = Depends(get_db),
    conta: EmailAccount = Depends(current_email_account),
):
    return await email_api.enviar_anexo(arquivo, conta=_linked_account(db, conta, account_id))


@router.post("/externas/corvia-{account_id}/mensagens/anexos/verificar-assinatura")
async def verificar_assinatura_linked(
    account_id: int,
    arquivo: UploadFile,
    db: Session = Depends(get_db),
    conta: EmailAccount = Depends(current_email_account),
):
    _linked_account(db, conta, account_id)
    return await email_api.verificar_assinatura_anexo(arquivo, conta=conta)


@router.get("/externas/corvia-{account_id}/mensagens/{message_id}/anexos")
def anexos_linked(
    account_id: int,
    message_id: str,
    db: Session = Depends(get_db),
    conta: EmailAccount = Depends(current_email_account),
):
    return email_api.anexos_da_mensagem(message_id, conta=_linked_account(db, conta, account_id))


@router.get("/externas/corvia-{account_id}/mensagens/{message_id}/anexos/{attachment_id}")
def baixar_anexo_linked(
    account_id: int,
    message_id: str,
    attachment_id: str,
    nome: str = "anexo",
    db: Session = Depends(get_db),
    conta: EmailAccount = Depends(current_email_account),
):
    return email_api.baixar_anexo_da_mensagem(
        message_id,
        attachment_id,
        nome=nome,
        conta=_linked_account(db, conta, account_id),
    )
