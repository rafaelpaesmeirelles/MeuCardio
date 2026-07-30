"""Caixa de e-mail do assinante — CorvIA Mail (Tarefa 28).

Reformulado em 30/07/2026: deixou de ser benefício incluído na assinatura
principal e virou add-on cobrado à parte (`Subscription.kind == "email"`,
ver `app/api/billing.py`), com senha PRÓPRIA — distinta da senha da conta
Corvia — para a "sessão email". Ver `BRIEFING_CLAUDE_CODE_4.md` para o
histórico completo das duas decisões.

Duas famílias de rota, com dependências diferentes de propósito:
- `GET/POST /conta` — status e ativação, vistos de DENTRO da conta Corvia
  normal (`current_user`): "eu, médico já logado na Corvia, tenho/quero uma
  caixa de e-mail?". Não expõe mensagem nenhuma.
- `POST /entrar`, `POST /esqueci-senha` (públicas) e as rotas de
  pastas/mensagens (`current_email_account`) — a "sessão email" em si, com
  login separado. Um token da conta Corvia NÃO abre essas rotas, e
  vice-versa (ver `scope` em `core/security.py`).

Escopo do conteúdo continua administrativo/profissional, não clínico
(decisão do Rafael) — ver a ressalva permanente na tela, em
`frontend/src/pages/CaixaDeEmail.tsx`.
"""
import re
import unicodedata

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.core.security import (
    assinatura_email_ativa, create_access_token, current_email_account,
    current_user, hash_password, verify_password,
)
from app.models.email_account import EmailAccount
from app.models.password_reset import PasswordResetToken
from app.models.user import User
from app.services import mail360
from app.services.mail360 import Mail360Error
from app.services.notificar import tentar_enviar_email

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


# --------------------------------------------------------------------------
# Status e ativação — vistos de dentro da conta Corvia (current_user)
# --------------------------------------------------------------------------

@router.get("/conta")
def minha_conta(db: Session = Depends(get_db), user: User = Depends(current_user)):
    conta = _obter_conta(db, user)
    if not conta:
        return {"ativa": False, "assinatura_ativa": assinatura_email_ativa(db, user.id)}
    return {
        "ativa": True, "email_address": conta.email_address, "status": conta.status,
        "senha_definida": conta.password_hash is not None,
    }


class AtivarConta(BaseModel):
    senha: str


@router.post("/conta", status_code=201)
def ativar_conta(dados: AtivarConta, db: Session = Depends(get_db), user: User = Depends(current_user)):
    """Provisiona a caixa e define a senha própria da "sessão email" — as
    duas coisas juntas, porque uma caixa sem senha não serve pra nada (não
    tem como logar em `/entrar`). Exige a assinatura de CorvIA Mail ativa —
    não a assinatura principal, que é benefício diferente."""
    _exigir_configurado()
    if not assinatura_email_ativa(db, user.id):
        raise HTTPException(
            status_code=409,
            detail="Assine o CorvIA Mail antes de ativar sua caixa de e-mail.",
        )
    if len(dados.senha) < 8:
        raise HTTPException(status_code=422, detail="A senha precisa ter ao menos 8 caracteres.")

    existente = _obter_conta(db, user)
    if existente:
        existente.password_hash = hash_password(dados.senha)
        db.commit()
        return {"ativa": True, "email_address": existente.email_address, "ja_existia": True}

    endereco = _gerar_endereco_unico(db, user.full_name)
    try:
        account_key = mail360.criar_conta_nativa(endereco, user.full_name)
    except Mail360Error as e:
        raise HTTPException(status_code=502, detail=str(e)) from e

    conta = EmailAccount(
        user_id=user.id, email_address=endereco, mail360_account_key=account_key,
        password_hash=hash_password(dados.senha),
    )
    db.add(conta)
    db.commit()
    return {"ativa": True, "email_address": conta.email_address, "ja_existia": False}


# --------------------------------------------------------------------------
# "Sessão email" — login próprio, separado da conta Corvia
# --------------------------------------------------------------------------

class LoginEmail(BaseModel):
    endereco: str
    senha: str


@router.post("/entrar")
def entrar(dados: LoginEmail, db: Session = Depends(get_db)):
    _exigir_configurado()
    endereco = dados.endereco.strip().lower()
    conta = db.query(EmailAccount).filter(EmailAccount.email_address == endereco).first()
    erro = HTTPException(status_code=401, detail="Endereço ou senha incorretos.")
    if not conta or not conta.password_hash or not verify_password(dados.senha, conta.password_hash):
        raise erro
    if conta.status != "ativa":
        raise HTTPException(status_code=403, detail="Esta caixa de e-mail está suspensa.")
    return {"access_token": create_access_token(conta.email_address, scope="email"), "token_type": "bearer"}


class EsqueciSenhaEmail(BaseModel):
    endereco: str


@router.post("/esqueci-senha", status_code=202)
def esqueci_senha_email(dados: EsqueciSenhaEmail, db: Session = Depends(get_db)):
    """Sempre responde 202 — não confirma se o endereço existe (evita
    enumeração). O link vai para o e-mail PRINCIPAL da conta Corvia
    (`users.email`), nunca para o próprio endereço @corvia.med.br: mandar a
    recuperação para dentro da caixa trancada trancaria de vez quem
    esqueceu a senha."""
    endereco = dados.endereco.strip().lower()
    conta = db.query(EmailAccount).filter(EmailAccount.email_address == endereco).first()
    if conta:
        user = db.get(User, conta.user_id)
        if user:
            token = PasswordResetToken(user_id=user.id, alvo="email")
            db.add(token)
            db.commit()
            link = f"/redefinir-senha?token={token.token}&alvo=email"
            tentar_enviar_email(
                destinatario=user.email,
                assunto="CorvIA Mail — redefinição de senha da caixa de e-mail",
                corpo=(
                    f"Use este link para redefinir a senha da sua caixa {conta.email_address} "
                    f"(válido por 2 horas): {{DOMINIO}}{link}"
                ),
            )
    return {"nota": "Se o endereço existir e estiver ativo, um link de redefinição foi gerado."}


# --------------------------------------------------------------------------
# Pastas e mensagens — exigem a "sessão email" (current_email_account)
# --------------------------------------------------------------------------

@router.get("/eu")
def eu(conta: EmailAccount = Depends(current_email_account)):
    """"Quem sou eu" da sessão email — o token aqui é outro (scope="email"),
    então `GET /api/auth/me` não serve: essa rota nem aceita esse token."""
    return {"email_address": conta.email_address}


@router.get("/pastas")
def pastas(conta: EmailAccount = Depends(current_email_account)):
    _exigir_configurado()
    try:
        return mail360.listar_pastas(conta.mail360_account_key)
    except Mail360Error as e:
        raise HTTPException(status_code=502, detail=str(e)) from e


@router.get("/mensagens")
def mensagens(pasta: str | None = None, conta: EmailAccount = Depends(current_email_account)):
    _exigir_configurado()
    try:
        return mail360.listar_mensagens(conta.mail360_account_key, pasta=pasta)
    except Mail360Error as e:
        raise HTTPException(status_code=502, detail=str(e)) from e


@router.get("/mensagens/{message_id}")
def mensagem(message_id: str, conta: EmailAccount = Depends(current_email_account)):
    _exigir_configurado()
    try:
        return mail360.obter_mensagem(conta.mail360_account_key, message_id)
    except Mail360Error as e:
        raise HTTPException(status_code=502, detail=str(e)) from e


class NovaMensagem(BaseModel):
    para: str
    assunto: str
    corpo_html: str


@router.post("/mensagens", status_code=201)
def enviar(dados: NovaMensagem, conta: EmailAccount = Depends(current_email_account)):
    _exigir_configurado()
    try:
        return mail360.enviar_mensagem(conta.mail360_account_key, dados.para, dados.assunto, dados.corpo_html)
    except Mail360Error as e:
        raise HTTPException(status_code=502, detail=str(e)) from e


@router.delete("/mensagens/{message_id}", status_code=204)
def excluir(message_id: str, conta: EmailAccount = Depends(current_email_account)):
    _exigir_configurado()
    try:
        mail360.excluir_mensagem(conta.mail360_account_key, message_id)
    except Mail360Error as e:
        raise HTTPException(status_code=502, detail=str(e)) from e
