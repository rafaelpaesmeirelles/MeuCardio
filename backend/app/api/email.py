"""Caixa de e-mail do assinante — CorvIA Mail (Tarefa 28).

Reformulado em 30/07/2026: deixou de ser benefício incluído na assinatura
principal e virou add-on cobrado à parte (`Subscription.kind == "email"`,
ver `app/api/billing.py`), com senha PRÓPRIA — distinta da senha da conta
Corvia — para a "sessão email". Ver `BRIEFING_CLAUDE_CODE_4.md` para o
histórico completo das duas decisões.

Duas famílias de rota, com dependências diferentes de propósito:
- `GET/POST /conta` e `GET /resumo` — status, ativação e o resumo mínimo
  (metadados de até três não lidas) vistos de DENTRO da conta Corvia
  normal (`current_user`): "eu, médico já logado na Corvia, tenho/quero uma
  caixa de e-mail?". O resumo nunca expõe corpo, anexos ou ações da caixa.
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
from datetime import datetime, timezone
from typing import Literal

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Response,
    UploadFile,
)
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.content import termo_lgpd_email
from app.core.config import settings
from app.core.db import get_db
from app.core.security import (
    assinatura_email_ativa,
    create_access_token,
    current_email_account,
    current_user,
    hash_password,
    verify_password,
)
from app.models.email_account import EmailAccount
from app.models.agenda import CalendarIntegration
from app.models.password_reset import PasswordResetToken
from app.models.user import User
from app.services import emails, mail360
from app.services import external_mail
from app.services.agenda_integrada.contacts import list_contacts
from app.services.email_signature import montar_assinatura_html, montar_corpo_com_assinatura
from app.services.mail360 import Mail360Error
from app.services.notificar import tentar_enviar_email

router = APIRouter(prefix="/api/email", tags=["caixa de e-mail"])


def _exigir_configurado():
    if not settings.mail360_configurado:
        raise HTTPException(status_code=503, detail="Caixa de e-mail ainda não está disponível.")


def _localpart_base(nome_completo: str) -> str:
    """'Rafael Paes Meirelles' -> 'rafael.paes'. Usa nome + primeiro
    sobrenome; se colidir, `_sugerir_local_part` acrescenta um número. É só
    a SUGESTÃO inicial — o médico pode editar antes de confirmar."""
    sem_acento = unicodedata.normalize("NFKD", nome_completo).encode("ascii", "ignore").decode()
    partes = [p.lower() for p in re.sub(r"[^a-zA-Z ]", "", sem_acento).split() if p]
    if not partes:
        return "assinante"
    if len(partes) == 1:
        return partes[0]
    return f"{partes[0]}.{partes[1]}"


def _sugerir_local_part(db: Session, nome_completo: str) -> str:
    """Sugestão de local-part livre — acrescenta número só se a base colidir
    com endereço já existente. Separado de `_gerar_endereco_unico` porque
    agora o médico pode editar a sugestão antes de confirmar (Tarefa 28,
    tela de cadastro do endereço); a versão anterior gerava e usava direto,
    sem dar ao médico chance de escolher."""
    base = _localpart_base(nome_completo)
    candidato = base
    n = 1
    while db.query(EmailAccount).filter(
        EmailAccount.email_address == f"{candidato}@{settings.mail360_dominio}"
    ).first():
        n += 1
        candidato = f"{base}{n}"
    return candidato


# RFC 5321 permite local-part bem mais exótico que isto, mas o Mail360 não
# documenta publicamente as regras que aceita (pesquisado em 30/07/2026 —
# só um relato de comunidade sobre o caractere "+" causar inconsistência
# entre app e API, nada sobre o restante). Em vez de inventar um limite,
# aplicamos aqui o subconjunto universalmente seguro que qualquer provedor de
# e-mail aceita — minúsculo, dígito, ponto, hífen, underscore, começando e
# terminando em letra/dígito — e deixamos a resposta REAL do Mail360 ser a
# palavra final: se algo passar daqui e for rejeitado lá, o erro do
# `criar_conta_nativa` chega ao médico do mesmo jeito, via 502.
_LOCAL_PART_RE = re.compile(r"^[a-z0-9]([a-z0-9._-]{1,28}[a-z0-9])?$")


def _validar_local_part(db: Session, local: str) -> str | None:
    """Devolve a mensagem de erro, ou None se o endereço passa no formato e
    está livre. Checagem de disponibilidade é case-insensitive porque o
    Mail360 trata o domínio como case-insensitive na prática (confirmado
    indiretamente: `POST /entrar` já normaliza para minúsculo)."""
    if not local:
        return "Escolha um endereço para sua caixa de e-mail."
    if not _LOCAL_PART_RE.match(local):
        return (
            "Use só letras minúsculas, números, ponto, hífen ou underscore, "
            "começando e terminando em letra ou número (3 a 30 caracteres)."
        )
    candidato = f"{local}@{settings.mail360_dominio}"
    if db.query(EmailAccount).filter(EmailAccount.email_address == candidato).first():
        return "Este endereço já está em uso. Escolha outro."
    return None


def _obter_conta(db: Session, user: User) -> EmailAccount | None:
    return db.query(EmailAccount).filter(EmailAccount.user_id == user.id).first()


# --------------------------------------------------------------------------
# Status e ativação — vistos de dentro da conta Corvia (current_user)
# --------------------------------------------------------------------------

@router.get("/conta")
def minha_conta(db: Session = Depends(get_db), user: User = Depends(current_user)):
    conta = _obter_conta(db, user)
    if not conta:
        return {"ativa": False, "assinatura_ativa": assinatura_email_ativa(db, user)}
    return {
        "ativa": True, "email_address": conta.email_address, "status": conta.status,
        "senha_definida": conta.password_hash is not None,
        "lgpd_aceite_versao": conta.lgpd_aceite_versao,
        "lgpd_versao_atual": termo_lgpd_email.VERSAO,
    }


class AssinaturaEmailIn(BaseModel):
    ativa: bool
    incluir_telefone: bool = False
    incluir_endereco: bool = False


@router.get("/assinatura")
def obter_assinatura(user: User = Depends(current_user)):
    return {
        "ativa": user.email_assinatura_ativa,
        "incluir_telefone": user.email_assinatura_incluir_telefone,
        "incluir_endereco": user.email_assinatura_incluir_endereco,
        "pre_visualizacao": montar_assinatura_html(user),
    }


@router.put("/assinatura")
def definir_assinatura(
    dados: AssinaturaEmailIn, db: Session = Depends(get_db), user: User = Depends(current_user),
):
    """Liga/desliga a assinatura anexada a todo e-mail enviado pelo CorvIA
    Mail (nativo e contas externas conectadas) — logo Corvia, logo
    profissional se houver, nome e CRM. Telefone e endereço do consultório
    são sub-opções independentes: só entram se o médico marcar cada uma,
    mesmo com a assinatura ligada."""
    user.email_assinatura_ativa = dados.ativa
    user.email_assinatura_incluir_telefone = dados.incluir_telefone
    user.email_assinatura_incluir_endereco = dados.incluir_endereco
    db.commit()
    return {
        "ativa": user.email_assinatura_ativa,
        "incluir_telefone": user.email_assinatura_incluir_telefone,
        "incluir_endereco": user.email_assinatura_incluir_endereco,
        "pre_visualizacao": montar_assinatura_html(user),
    }


def _nao_lida(mensagem: dict) -> bool:
    return str(mensagem.get("status", "")).lower() in {"0", "unread", "nao_lida"}


def _momento_da_mensagem(mensagem: dict) -> float:
    bruto = mensagem.get("receivedTime") or mensagem.get("sentDateInGMT") or mensagem.get("date")
    if bruto is None:
        return 0
    try:
        numero = float(bruto)
        return numero / 1000 if numero > 10_000_000_000 else numero
    except (TypeError, ValueError):
        try:
            return datetime.fromisoformat(str(bruto).replace("Z", "+00:00")).timestamp()
        except ValueError:
            return 0


@router.get("/resumo")
def resumo_da_caixa(db: Session = Depends(get_db), user: User = Depends(current_user)):
    """Resumo de privilégio mínimo para o cartão da página Hoje.

    A sessão principal pode ver somente remetente, assunto e horário das três
    mensagens não lidas mais recentes. Abrir o conteúdo, baixar anexos ou agir
    sobre qualquer mensagem continua exigindo a sessão própria do CorvIA Mail.
    """
    conta = _obter_conta(db, user)
    if not conta or not assinatura_email_ativa(db, user):
        return {"disponivel": False, "email_address": None, "pendentes": []}
    _exigir_configurado()
    try:
        pastas = mail360.listar_pastas(conta.mail360_account_key)
        entrada = next(
            (
                pasta for pasta in pastas
                if str(
                    pasta.get("folderType")
                    or pasta.get("folderName")
                    or pasta.get("name")
                    or ""
                ).lower() in {"inbox", "entrada"}
            ),
            None,
        )
        pasta_id = str(entrada.get("folderId") or entrada.get("id")) if entrada else None
        mensagens = mail360.listar_mensagens(
            conta.mail360_account_key, pasta=pasta_id, limite=30, inicio=1,
        )
    except Mail360Error as e:
        raise HTTPException(status_code=502, detail=str(e)) from e

    campos_permitidos = (
        "messageId", "id", "subject", "fromAddress", "sender",
        "receivedTime", "sentDateInGMT", "date", "status",
    )
    mensagens_nao_lidas = sorted(
        (mensagem for mensagem in mensagens if _nao_lida(mensagem)),
        key=_momento_da_mensagem,
        reverse=True,
    )
    pendentes = [
        {campo: mensagem.get(campo) for campo in campos_permitidos if mensagem.get(campo) is not None}
        for mensagem in mensagens_nao_lidas
    ][:3]
    return {
        "disponivel": True,
        "email_address": conta.email_address,
        "pendentes": pendentes,
    }


@router.get("/termo-lgpd")
def termo_lgpd(user: User = Depends(current_user)):
    """Texto do termo de consentimento para transferência internacional de
    dado (Zoho Mail360 não tem data center no Brasil — CLAUDE.md, item 14b).
    Exibido antes do checkbox de aceite em `POST /conta`; não pode ser
    embutido no aceite geral de termos de uso da Corvia, porque a base legal
    escolhida (art. 33, VIII da LGPD) exige consentimento específico e
    destacado, distinto de qualquer outro."""
    return {"versao": termo_lgpd_email.VERSAO, "texto": termo_lgpd_email.texto(settings.admin_email)}


@router.get("/sugestao-endereco")
def sugestao_endereco(db: Session = Depends(get_db), user: User = Depends(current_user)):
    """Sugestão inicial pra tela de cadastro do endereço — o médico ainda
    pode editar antes de confirmar em `POST /conta`. Se a caixa já existe,
    devolve o endereço real (não dá mais pra escolher, já foi criado no
    Mail360)."""
    existente = _obter_conta(db, user)
    if existente:
        local, _, dominio = existente.email_address.partition("@")
        return {"local_part": local, "dominio": dominio, "editavel": False}
    return {
        "local_part": _sugerir_local_part(db, user.full_name),
        "dominio": settings.mail360_dominio,
        "editavel": True,
    }


@router.get("/verificar-endereco")
def verificar_endereco(local: str, db: Session = Depends(get_db), _=Depends(current_user)):
    """Validação em tempo real pra tela de cadastro — formato e
    disponibilidade, sem reservar nada (a reserva de fato só acontece em
    `POST /conta`, que cria a conta no Mail360 na mesma chamada)."""
    local_normalizado = local.strip().lower()
    erro = _validar_local_part(db, local_normalizado)
    return {
        "disponivel": erro is None,
        "motivo": erro,
        "endereco": f"{local_normalizado}@{settings.mail360_dominio}",
    }


class AtivarConta(BaseModel):
    senha: str
    aceite_lgpd: bool = False
    local_part: str | None = None  # obrigatório só na primeira ativação


@router.post("/conta", status_code=201)
def ativar_conta(
    dados: AtivarConta, background_tasks: BackgroundTasks,
    db: Session = Depends(get_db), user: User = Depends(current_user),
):
    """Provisiona a caixa e define a senha própria da "sessão email" — as
    duas coisas juntas, porque uma caixa sem senha não serve pra nada (não
    tem como logar em `/entrar`). Exige a assinatura de CorvIA Mail ativa —
    não a assinatura principal, que é benefício diferente.

    `aceite_lgpd` é obrigatório em toda chamada (criação OU atualização de
    senha): é aqui, no momento em que a caixa é de fato provisionada no
    Mail360, que a transferência internacional acontece — sem aceite
    registrado, não ativa. Ver `app/content/termo_lgpd_email.py`.

    `local_part` é o endereço escolhido na tela de cadastro (Tarefa 28,
    30/07/2026) — obrigatório só na criação; numa reativação (senha nova
    numa caixa que já existe) é ignorado, porque o endereço já foi criado no
    Mail360 e não dá pra trocar sem apagar e recriar a conta lá, fora do
    escopo desta rota."""
    _exigir_configurado()
    if not assinatura_email_ativa(db, user):
        raise HTTPException(
            status_code=409,
            detail="Assine o CorvIA Mail antes de ativar sua caixa de e-mail.",
        )
    if len(dados.senha) < 8:
        raise HTTPException(status_code=422, detail="A senha precisa ter ao menos 8 caracteres.")
    if not dados.aceite_lgpd:
        raise HTTPException(
            status_code=422,
            detail="É preciso aceitar o termo de transferência internacional de dados para ativar a caixa.",
        )

    existente = _obter_conta(db, user)
    if existente:
        existente.password_hash = hash_password(dados.senha)
        existente.lgpd_aceite_em = datetime.now(timezone.utc)
        existente.lgpd_aceite_versao = termo_lgpd_email.VERSAO
        db.commit()
        return {"ativa": True, "email_address": existente.email_address, "ja_existia": True}

    local_normalizado = (dados.local_part or "").strip().lower()
    erro = _validar_local_part(db, local_normalizado)
    if erro:
        raise HTTPException(status_code=422, detail=erro)

    endereco = f"{local_normalizado}@{settings.mail360_dominio}"
    try:
        account_key = mail360.criar_conta_nativa(endereco, user.full_name)
    except Mail360Error as e:
        raise HTTPException(status_code=502, detail=str(e)) from e

    conta = EmailAccount(
        user_id=user.id, email_address=endereco, mail360_account_key=account_key,
        password_hash=hash_password(dados.senha),
        lgpd_aceite_em=datetime.now(timezone.utc), lgpd_aceite_versao=termo_lgpd_email.VERSAO,
    )
    db.add(conta)
    db.commit()
    # Item 11 do spec de e-mails transacionais: "caixa criada com sucesso" —
    # só na primeira criação (`ja_existia: False`), não numa reativação de
    # senha, que é o outro ramo desta rota.
    background_tasks.add_task(emails.enviar_corvia_mail_ativado, user.id, conta.email_address)
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


@router.get("/contas")
def contas_da_caixa_unificada(
    db: Session = Depends(get_db),
    conta: EmailAccount = Depends(current_email_account),
):
    """Caixa nativa e contas OAuth do mesmo titular, sem expor tokens."""
    resultado = [{
        "id": "corvia",
        "provider": "corvia",
        "display_name": "CorvIA Mail",
        "email_address": conta.email_address,
        "native": True,
        "read_mail": True,
        "send_mail": True,
    }]
    integracoes = db.query(CalendarIntegration).filter(
        CalendarIntegration.owner_id == conta.user_id,
        CalendarIntegration.enabled.is_(True),
        CalendarIntegration.status == "connected",
        CalendarIntegration.provider.in_(["google_calendar", "microsoft_365"]),
    ).order_by(CalendarIntegration.id.asc()).all()
    for integracao in integracoes:
        capacidades = integracao.capabilities or {}
        if not capacidades.get("read_mail"):
            continue
        resultado.append({
            "id": str(integracao.id),
            "provider": "google" if integracao.provider == "google_calendar" else "microsoft",
            "display_name": integracao.display_name,
            "email_address": integracao.display_name,
            "native": False,
            "read_mail": True,
            "send_mail": bool(capacidades.get("send_mail")),
        })
    return resultado


@router.get("/mensagens/todas")
def mensagens_todas(
    limite: int = 20,
    db: Session = Depends(get_db),
    conta: EmailAccount = Depends(current_email_account),
):
    """Uma lista só, misturando a caixa nativa CorvIA Mail com toda conta
    externa conectada que autorizou e-mail (Gmail/Outlook), ordenada por data
    de recebimento, mais recente primeiro.

    Cada mensagem carrega `origem` ("corvia" ou o id da integração) — é o
    dado que o frontend usa para saber a quem mandar uma ação (marcar
    lida, abrir a mensagem inteira): a rota certa continua sendo
    `/mensagens/{id}` para "corvia" ou
    `/externas/{origem}/mensagens/{id}` para as demais. Esta rota é só
    LEITURA da lista combinada — não substitui as rotas por conta.

    Falha em UMA fonte não derruba a lista inteira: a fonte que falhou entra
    em `fontes_com_erro` com o motivo, e as que responderam aparecem
    normalmente — nunca finge que uma fonte respondeu quando não respondeu.
    """
    if limite < 1 or limite > 50:
        raise HTTPException(status_code=422, detail="Limite deve ser entre 1 e 50.")

    mensagens: list[dict] = []
    fontes_com_erro: list[dict] = []

    try:
        _exigir_configurado()
        for item in mail360.listar_mensagens(conta.mail360_account_key, limite=limite):
            mensagens.append({**item, "origem": "corvia", "provider": "corvia"})
    except (Mail360Error, HTTPException) as exc:
        detalhe = exc.detail if isinstance(exc, HTTPException) else str(exc)
        fontes_com_erro.append({"origem": "corvia", "provider": "corvia", "erro": str(detalhe)})

    integracoes = db.query(CalendarIntegration).filter(
        CalendarIntegration.owner_id == conta.user_id,
        CalendarIntegration.enabled.is_(True),
        CalendarIntegration.status == "connected",
        CalendarIntegration.provider.in_(["google_calendar", "microsoft_365"]),
    ).order_by(CalendarIntegration.id.asc()).all()

    for integracao in integracoes:
        capacidades = integracao.capabilities or {}
        if not capacidades.get("read_mail"):
            continue
        provider = "google" if integracao.provider == "google_calendar" else "microsoft"
        try:
            externas = external_mail.list_messages(db, integracao, folder=None, limit=limite, start=1)
            for item in externas:
                mensagens.append({**item, "origem": str(integracao.id)})
        except external_mail.ExternalMailError as exc:
            fontes_com_erro.append({"origem": str(integracao.id), "provider": provider, "erro": str(exc)})

    mensagens.sort(key=_momento_da_mensagem, reverse=True)
    return {"mensagens": mensagens[:limite], "fontes_com_erro": fontes_com_erro}


@router.get("/pastas")
def pastas(conta: EmailAccount = Depends(current_email_account)):
    _exigir_configurado()
    try:
        return mail360.listar_pastas(conta.mail360_account_key)
    except Mail360Error as e:
        raise HTTPException(status_code=502, detail=str(e)) from e


@router.get("/mensagens")
def mensagens(
    pasta: str | None = None,
    limite: int = 100,
    inicio: int = 1,
    conta: EmailAccount = Depends(current_email_account),
):
    _exigir_configurado()
    try:
        return mail360.listar_mensagens(
            conta.mail360_account_key, pasta=pasta, limite=limite, inicio=inicio,
        )
    except Mail360Error as e:
        raise HTTPException(status_code=502, detail=str(e)) from e


class AcaoMensagens(BaseModel):
    message_ids: list[str]
    acao: Literal["lida", "nao_lida", "mover", "sinalizar"]
    pasta_destino: str | None = None
    sinalizador: Literal["info", "important", "followup", "flag_not_set"] | None = None


@router.put("/mensagens/acoes", status_code=204)
def agir_em_mensagens(
    dados: AcaoMensagens,
    conta: EmailAccount = Depends(current_email_account),
):
    _exigir_configurado()
    if not dados.message_ids:
        raise HTTPException(status_code=422, detail="Selecione ao menos uma mensagem.")
    if len(dados.message_ids) > 200:
        raise HTTPException(status_code=422, detail="Selecione no máximo 200 mensagens por vez.")
    try:
        mail360.alterar_mensagens(
            conta.mail360_account_key,
            dados.message_ids,
            dados.acao,
            pasta_destino=dados.pasta_destino,
            sinalizador=dados.sinalizador,
        )
    except Mail360Error as e:
        raise HTTPException(status_code=502, detail=str(e)) from e


@router.get("/mensagens/{message_id}")
def mensagem(message_id: str, conta: EmailAccount = Depends(current_email_account)):
    _exigir_configurado()
    try:
        resultado = mail360.obter_mensagem(conta.mail360_account_key, message_id)
        # Abrir uma mensagem equivale a lê-la. A falha desta atualização não
        # deve esconder um corpo que já foi obtido com sucesso.
        try:
            mail360.alterar_mensagens(conta.mail360_account_key, [message_id], "lida")
        except Mail360Error:
            pass
        return resultado
    except Mail360Error as e:
        raise HTTPException(status_code=502, detail=str(e)) from e


class NovaMensagem(BaseModel):
    para: str
    cc: str | None = None
    cco: str | None = None
    assunto: str
    corpo_html: str
    anexos: list[str] = []  # fileIds já devolvidos por POST /mensagens/anexos


@router.get("/contatos")
def contatos_sincronizados(
    q: str = "",
    limite: int = 50,
    db: Session = Depends(get_db),
    conta: EmailAccount = Depends(current_email_account),
):
    """Contatos Google/Microsoft/Apple do mesmo titular da caixa CorvIA Mail."""
    if len(q) > 200 or limite < 1 or limite > 100:
        raise HTTPException(status_code=422, detail="Parâmetros de busca de contatos inválidos.")
    return list_contacts(db, conta.user_id, query=q, limit=limite)


class ResponderMensagem(BaseModel):
    acao: Literal["reply", "replyall", "forward"]
    assunto: str
    conteudo: str
    para: str | None = None
    cc: str | None = None
    cco: str | None = None
    anexos: list[str] = []


TAMANHO_MAXIMO_ANEXO = 15 * 1024 * 1024  # 15 MB — anexo de e-mail comum, não exame


@router.post("/mensagens/anexos", status_code=201)
async def enviar_anexo(arquivo: UploadFile, conta: EmailAccount = Depends(current_email_account)):
    """Upload em duas etapas, espelhando a própria API do Mail360: sobe o
    arquivo aqui, recebe um `file_id`, e usa esse id em `POST /mensagens`
    (campo `anexos`) — o Mail360 não aceita o binário direto no envio."""
    _exigir_configurado()
    conteudo = await arquivo.read()
    if len(conteudo) > TAMANHO_MAXIMO_ANEXO:
        raise HTTPException(status_code=413, detail="O anexo precisa ter no máximo 15 MB.")
    try:
        file_id = mail360.upload_anexo(conta.mail360_account_key, arquivo.filename or "anexo", conteudo)
    except Mail360Error as e:
        raise HTTPException(status_code=502, detail=str(e)) from e
    return {"file_id": file_id, "nome": arquivo.filename}


@router.post("/mensagens", status_code=201)
def enviar(
    dados: NovaMensagem,
    db: Session = Depends(get_db),
    conta: EmailAccount = Depends(current_email_account),
):
    _exigir_configurado()
    titular = db.get(User, conta.user_id)
    corpo, formato = montar_corpo_com_assinatura(dados.corpo_html, montar_assinatura_html(titular))
    try:
        return mail360.enviar_mensagem(
            conta.mail360_account_key, conta.email_address, dados.para, dados.assunto, corpo,
            anexos=dados.anexos, cc=dados.cc, cco=dados.cco, mail_format=formato,
        )
    except Mail360Error as e:
        raise HTTPException(status_code=502, detail=str(e)) from e


@router.post("/mensagens/{message_id}/responder", status_code=201)
def responder(
    message_id: str,
    dados: ResponderMensagem,
    db: Session = Depends(get_db),
    conta: EmailAccount = Depends(current_email_account),
):
    _exigir_configurado()
    titular = db.get(User, conta.user_id)
    conteudo, formato = montar_corpo_com_assinatura(dados.conteudo, montar_assinatura_html(titular))
    try:
        return mail360.responder_mensagem(
            conta.mail360_account_key,
            message_id,
            conta.email_address,
            dados.acao,
            dados.assunto,
            conteudo,
            para=dados.para,
            cc=dados.cc,
            cco=dados.cco,
            anexos=dados.anexos,
            mail_format=formato,
        )
    except Mail360Error as e:
        raise HTTPException(status_code=502, detail=str(e)) from e


@router.get("/mensagens/{message_id}/anexos")
def anexos_da_mensagem(
    message_id: str,
    conta: EmailAccount = Depends(current_email_account),
):
    _exigir_configurado()
    try:
        return mail360.listar_anexos(conta.mail360_account_key, message_id)
    except Mail360Error as e:
        raise HTTPException(status_code=502, detail=str(e)) from e


@router.get("/mensagens/{message_id}/anexos/{attachment_id}")
def baixar_anexo_da_mensagem(
    message_id: str,
    attachment_id: str,
    nome: str = "anexo",
    conta: EmailAccount = Depends(current_email_account),
):
    _exigir_configurado()
    try:
        conteudo, media_type = mail360.baixar_anexo(
            conta.mail360_account_key, message_id, attachment_id,
        )
    except Mail360Error as e:
        raise HTTPException(status_code=502, detail=str(e)) from e
    nome_seguro = re.sub(r"[^a-zA-Z0-9._-]", "_", nome)[:180] or "anexo"
    return Response(
        content=conteudo,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{nome_seguro}"'},
    )


@router.delete("/mensagens/{message_id}", status_code=204)
def excluir(message_id: str, conta: EmailAccount = Depends(current_email_account)):
    _exigir_configurado()
    try:
        mail360.excluir_mensagem(conta.mail360_account_key, message_id)
    except Mail360Error as e:
        raise HTTPException(status_code=502, detail=str(e)) from e


# --------------------------------------------------------------------------
# Contas externas — proxy ao vivo; o conteúdo permanece no provedor
# --------------------------------------------------------------------------

def _integracao_email(
    db: Session,
    conta: EmailAccount,
    integration_id: int,
    *,
    escrita: bool = False,
) -> CalendarIntegration:
    integracao = db.query(CalendarIntegration).filter(
        CalendarIntegration.id == integration_id,
        CalendarIntegration.owner_id == conta.user_id,
        CalendarIntegration.enabled.is_(True),
        CalendarIntegration.status == "connected",
        CalendarIntegration.provider.in_(["google_calendar", "microsoft_365"]),
    ).first()
    capacidades = (integracao.capabilities or {}) if integracao else {}
    exigida = "send_mail" if escrita else "read_mail"
    if not integracao or not capacidades.get(exigida):
        raise HTTPException(
            status_code=403,
            detail="Esta conta não autorizou o CorvIA Mail. Reconecte-a na Agenda e aceite o acesso ao e-mail.",
        )
    return integracao


def _traduzir_erro_externo(exc: external_mail.ExternalMailError) -> HTTPException:
    return HTTPException(status_code=exc.status_code, detail=str(exc))


@router.get("/externas/{integration_id}/pastas")
def pastas_externas(
    integration_id: int,
    db: Session = Depends(get_db),
    conta: EmailAccount = Depends(current_email_account),
):
    integracao = _integracao_email(db, conta, integration_id)
    try:
        return external_mail.list_folders(db, integracao)
    except external_mail.ExternalMailError as exc:
        raise _traduzir_erro_externo(exc) from exc


@router.get("/externas/{integration_id}/mensagens")
def mensagens_externas(
    integration_id: int,
    pasta: str | None = None,
    limite: int = 50,
    inicio: int = 1,
    db: Session = Depends(get_db),
    conta: EmailAccount = Depends(current_email_account),
):
    if limite < 1 or limite > 100 or inicio < 1:
        raise HTTPException(status_code=422, detail="Paginação inválida.")
    integracao = _integracao_email(db, conta, integration_id)
    try:
        return external_mail.list_messages(db, integracao, folder=pasta, limit=limite, start=inicio)
    except external_mail.ExternalMailError as exc:
        raise _traduzir_erro_externo(exc) from exc


@router.get("/externas/{integration_id}/mensagens/{message_id}")
def mensagem_externa(
    integration_id: int,
    message_id: str,
    db: Session = Depends(get_db),
    conta: EmailAccount = Depends(current_email_account),
):
    integracao = _integracao_email(db, conta, integration_id)
    try:
        return external_mail.get_message(db, integracao, message_id)
    except external_mail.ExternalMailError as exc:
        raise _traduzir_erro_externo(exc) from exc


@router.put("/externas/{integration_id}/mensagens/acoes", status_code=204)
def agir_em_mensagens_externas(
    integration_id: int,
    dados: AcaoMensagens,
    db: Session = Depends(get_db),
    conta: EmailAccount = Depends(current_email_account),
):
    if not dados.message_ids or len(dados.message_ids) > 100:
        raise HTTPException(status_code=422, detail="Selecione entre 1 e 100 mensagens.")
    if dados.acao == "sinalizar":
        raise HTTPException(status_code=422, detail="Sinalizadores externos ainda não são compatíveis entre provedores.")
    if dados.acao == "mover" and not dados.pasta_destino:
        raise HTTPException(status_code=422, detail="Informe a pasta de destino.")
    integracao = _integracao_email(db, conta, integration_id)
    try:
        external_mail.act_on_messages(
            db, integracao, dados.message_ids, dados.acao, destination=dados.pasta_destino,
        )
    except external_mail.ExternalMailError as exc:
        raise _traduzir_erro_externo(exc) from exc


@router.post("/externas/{integration_id}/mensagens", status_code=201)
def enviar_mensagem_externa(
    integration_id: int,
    dados: NovaMensagem,
    db: Session = Depends(get_db),
    conta: EmailAccount = Depends(current_email_account),
):
    if dados.anexos:
        raise HTTPException(status_code=422, detail="Envie anexos pela caixa nativa; anexos externos serão liberados após validação específica de cada provedor.")
    integracao = _integracao_email(db, conta, integration_id, escrita=True)
    titular = db.get(User, conta.user_id)
    assinatura = montar_assinatura_html(titular)
    # send_message() já trata `html` como HTML de verdade (Gmail/Graph), ao
    # contrário da caixa nativa — por isso, sem assinatura, o corpo segue
    # exatamente como já era (comportamento inalterado). Só quando a
    # assinatura está ligada o texto do médico passa a ser escapado antes de
    # virar HTML, porque nesse caminho ele nunca foi escapado.
    corpo = dados.corpo_html if assinatura is None else montar_corpo_com_assinatura(dados.corpo_html, assinatura)[0]
    try:
        return external_mail.send_message(
            db, integracao, to=dados.para, subject=dados.assunto, html=corpo,
            cc=dados.cc, bcc=dados.cco,
        )
    except external_mail.ExternalMailError as exc:
        raise _traduzir_erro_externo(exc) from exc


@router.delete("/externas/{integration_id}/mensagens/{message_id}", status_code=204)
def excluir_mensagem_externa(
    integration_id: int,
    message_id: str,
    db: Session = Depends(get_db),
    conta: EmailAccount = Depends(current_email_account),
):
    integracao = _integracao_email(db, conta, integration_id)
    try:
        external_mail.delete_message(db, integracao, message_id)
    except external_mail.ExternalMailError as exc:
        raise _traduzir_erro_externo(exc) from exc
