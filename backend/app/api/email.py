"""Caixa de e-mail do assinante (Tarefa 28) — webmail próprio sobre a API de
dados do Zoho Mail360. Decisão do Rafael em 30/07/2026: em vez de embutir um
webmail de terceiro (nenhum fornecedor pesquisado garantia SSO recorrente
para isso), a Corvia constrói a interface e nunca expõe login externo — o
backend guarda as credenciais OAuth do Mail360 e fala com a API em nome do
assinante já autenticado na própria sessão da Corvia. Ver
`BRIEFING_CLAUDE_CODE_4.md` para o histórico completo da decisão.

Escopo: uso administrativo/profissional geral, não clínico (decisão do
Rafael) — por isso este router não usa o padrão de cifragem do Cofre do
telediagnóstico.
"""
import re
import unicodedata

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.core.security import current_user
from app.models.email_account import EmailAccount
from app.models.user import User
from app.services import mail360
from app.services.mail360 import Mail360Error

router = APIRouter(prefix="/api/email", tags=["caixa de e-mail"])


def _exigir_configurado():
    if not settings.mail360_configurado:
        raise HTTPException(status_code=503, detail="Caixa de e-mail ainda não está disponível.")


def _localpart_base(nome_completo: str) -> str:
    """'Rafael Paes Meirelles' -> 'rafael.paes'. Usa nome + primeiro
    sobrenome; se colidir, `_gerar_endereco_unico` acrescenta um número."""
    sem_acento = unicodedata.normalize("NFKD", nome_completo).encode("ascii", "ignore").decode()
    partes = [p.lower() for p in re.sub(r"[^a-zA-Z ]", "", sem_acento).split() if p]
    if not partes:
        return "assinante"
    if len(partes) == 1:
        return partes[0]
    return f"{partes[0]}.{partes[1]}"


def _gerar_endereco_unico(db: Session, nome_completo: str) -> str:
    base = _localpart_base(nome_completo)
    candidato = f"{base}@{settings.mail360_dominio}"
    n = 1
    while db.query(EmailAccount).filter(EmailAccount.email_address == candidato).first():
        n += 1
        candidato = f"{base}{n}@{settings.mail360_dominio}"
    return candidato


def _obter_conta(db: Session, user: User) -> EmailAccount | None:
    return db.query(EmailAccount).filter(EmailAccount.user_id == user.id).first()


def _exigir_conta(db: Session, user: User) -> EmailAccount:
    conta = _obter_conta(db, user)
    if not conta:
        raise HTTPException(status_code=404, detail="Você ainda não ativou sua caixa de e-mail.")
    if conta.status != "ativa":
        raise HTTPException(status_code=403, detail="Sua caixa de e-mail está suspensa.")
    return conta


@router.get("/conta")
def minha_conta(db: Session = Depends(get_db), user: User = Depends(current_user)):
    _exigir_configurado()
    conta = _obter_conta(db, user)
    if not conta:
        return {"ativa": False}
    return {"ativa": True, "email_address": conta.email_address, "status": conta.status}


@router.post("/conta", status_code=201)
def ativar_conta(db: Session = Depends(get_db), user: User = Depends(current_user)):
    """Provisiona a caixa sob demanda — não é criada automaticamente no
    cadastro. Escolha deliberada: nem todo assinante vai querer usar, e o
    preço de produção do Mail360 ainda não foi confirmado (ver briefing);
    provisionar só quando o médico pede evita gerar custo por caixas que
    ninguém usaria."""
    _exigir_configurado()
    existente = _obter_conta(db, user)
    if existente:
        return {"ativa": True, "email_address": existente.email_address, "ja_existia": True}

    endereco = _gerar_endereco_unico(db, user.full_name)
    try:
        account_key = mail360.criar_conta_nativa(endereco, user.full_name)
    except Mail360Error as e:
        raise HTTPException(status_code=502, detail=str(e)) from e

    conta = EmailAccount(user_id=user.id, email_address=endereco, mail360_account_key=account_key)
    db.add(conta)
    db.commit()
    return {"ativa": True, "email_address": conta.email_address, "ja_existia": False}


@router.get("/pastas")
def pastas(db: Session = Depends(get_db), user: User = Depends(current_user)):
    _exigir_configurado()
    conta = _exigir_conta(db, user)
    try:
        return mail360.listar_pastas(conta.mail360_account_key)
    except Mail360Error as e:
        raise HTTPException(status_code=502, detail=str(e)) from e


@router.get("/mensagens")
def mensagens(pasta: str | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)):
    _exigir_configurado()
    conta = _exigir_conta(db, user)
    try:
        return mail360.listar_mensagens(conta.mail360_account_key, pasta=pasta)
    except Mail360Error as e:
        raise HTTPException(status_code=502, detail=str(e)) from e


@router.get("/mensagens/{message_id}")
def mensagem(message_id: str, db: Session = Depends(get_db), user: User = Depends(current_user)):
    _exigir_configurado()
    conta = _exigir_conta(db, user)
    try:
        return mail360.obter_mensagem(conta.mail360_account_key, message_id)
    except Mail360Error as e:
        raise HTTPException(status_code=502, detail=str(e)) from e


class NovaMensagem(BaseModel):
    para: str
    assunto: str
    corpo_html: str


@router.post("/mensagens", status_code=201)
def enviar(dados: NovaMensagem, db: Session = Depends(get_db), user: User = Depends(current_user)):
    _exigir_configurado()
    conta = _exigir_conta(db, user)
    try:
        return mail360.enviar_mensagem(conta.mail360_account_key, dados.para, dados.assunto, dados.corpo_html)
    except Mail360Error as e:
        raise HTTPException(status_code=502, detail=str(e)) from e


@router.delete("/mensagens/{message_id}", status_code=204)
def excluir(message_id: str, db: Session = Depends(get_db), user: User = Depends(current_user)):
    _exigir_configurado()
    conta = _exigir_conta(db, user)
    try:
        mail360.excluir_mensagem(conta.mail360_account_key, message_id)
    except Mail360Error as e:
        raise HTTPException(status_code=502, detail=str(e)) from e
