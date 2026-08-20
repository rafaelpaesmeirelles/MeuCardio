"""Yahoo Mail para a caixa unificada do CorvIA Mail — via IMAP/SMTP com senha
específica de app, não OAuth.

A Yahoo descontinuou API própria de e-mail para terceiros: acesso
programático via OAuth a IMAP/CalDAV/CardDAV exige um "Yahoo Mail Products
Commercial Access Agreement" assinado com a Yahoo antes de sequer receber
credencial (confirmado em `help.yahoo.com`/`senders.yahooinc.com` em
06/08/2026) — processo comercial fora do alcance de uma integração de
usuário final. A via que NÃO exige isso, documentada oficialmente para
qualquer conta Yahoo (`help.yahoo.com/kb/SLN4075.html`,
`help.yahoo.com/kb/SLN15241.html`), é a mesma já usada neste projeto para a
Apple: o próprio titular gera uma **senha de aplicativo** em
login.yahoo.com → Segurança da conta, e essa senha autentica IMAP/SMTP
padrão — sem acordo comercial, sem app registrado, sem OAuth.

Servidores oficiais (mesma fonte acima, conferidos em 06/08/2026):
- IMAP: `imap.mail.yahoo.com:993` (SSL)
- SMTP: `smtp.mail.yahoo.com:587` (STARTTLS)

Diferença estrutural para `external_mail.py` (Gmail/Graph): aqui não há API
REST nem token — é protocolo IMAP/SMTP puro, biblioteca padrão do Python
(`imaplib`/`smtplib`), sem dependência nova. Identidade de mensagem é
`"{pasta}:{uid}"` (IMAP UID só é único DENTRO da pasta) — as rotas
existentes (`GET /externas/{id}/mensagens/{message_id}`) não recebem pasta
separada, então essa composição é o que permite localizar a mensagem sem
mudar a assinatura das rotas.

Escopo desta primeira versão: listar pastas, listar mensagens, ler mensagem
(marca como lida), enviar. Mover mensagem e sinalizador ficam para depois —
IMAP MOVE/flags custom variam mais entre servidores, e o produto já tem o
precedente de declarar escopo por capability em vez de fingir paridade.
"""

from __future__ import annotations

import imaplib
import smtplib
from datetime import datetime, timezone
from email import message_from_bytes
from email.header import decode_header
from email.message import EmailMessage
from email.utils import getaddresses, parsedate_to_datetime
from html import escape
from typing import TYPE_CHECKING, Any

from sqlalchemy.orm import Session

from app.services.assinatura import smime

if TYPE_CHECKING:
    from app.models.user import User

IMAP_HOST = "imap.mail.yahoo.com"
IMAP_PORT = 993
SMTP_HOST = "smtp.mail.yahoo.com"
SMTP_PORT = 587


class YahooMailError(RuntimeError):
    def __init__(self, message: str, *, status_code: int = 502):
        super().__init__(message)
        self.status_code = status_code


def _credenciais(credentials: dict[str, Any]) -> tuple[str, str]:
    usuario = str(credentials.get("username") or "")
    senha = str(credentials.get("app_specific_password") or "")
    if not usuario or not senha:
        raise YahooMailError("Conta Yahoo sem credencial armazenada — reconecte.", status_code=409)
    return usuario, senha


def _conectar_imap(credentials: dict[str, Any]) -> imaplib.IMAP4_SSL:
    usuario, senha = _credenciais(credentials)
    try:
        conexao = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT, timeout=15)
        conexao.login(usuario, senha)
    except imaplib.IMAP4.error as exc:
        raise YahooMailError("Login IMAP recusado pela Yahoo — a senha de aplicativo pode ter expirado.", status_code=401) from exc
    except OSError as exc:
        raise YahooMailError("Não foi possível conectar ao IMAP da Yahoo.", status_code=502) from exc
    return conexao


def _decodificar_cabecalho(bruto: str | None) -> str:
    if not bruto:
        return ""
    partes = decode_header(bruto)
    texto = ""
    for fragmento, codificacao in partes:
        if isinstance(fragmento, bytes):
            texto += fragmento.decode(codificacao or "utf-8", errors="replace")
        else:
            texto += fragmento
    return texto


def diagnose(credentials: dict[str, Any]) -> dict[str, Any]:
    """Login sem operação nenhuma além de autenticar — usado na conexão
    inicial para confirmar a senha de aplicativo antes de salvar."""
    conexao = _conectar_imap(credentials)
    try:
        conexao.logout()
    except Exception:  # noqa: BLE001 — logout falhar não deve mascarar que o login já funcionou
        pass
    return {"ok": True, "provider": "yahoo_mail"}


_PASTAS_VISIVEIS = {"INBOX": "Entrada", "Sent": "Enviados", "Draft": "Rascunhos", "Trash": "Lixeira", "Bulk": "Spam"}


def list_folders(credentials: dict[str, Any]) -> list[dict[str, Any]]:
    conexao = _conectar_imap(credentials)
    try:
        status, dados = conexao.list()
        if status != "OK":
            raise YahooMailError("Não foi possível listar as pastas da Yahoo.")
        resultado = []
        for linha in dados or []:
            texto = linha.decode(errors="replace") if isinstance(linha, bytes) else str(linha)
            # Formato IMAP: (flags) "delimitador" "NomeDaPasta" — o nome pode
            # vir entre aspas (com espaço) ou solto.
            nome = texto.rsplit('"', 2)[-2] if texto.count('"') >= 2 else texto.split()[-1]
            if nome not in _PASTAS_VISIVEIS:
                continue
            resultado.append({"folderId": nome, "id": nome, "folderName": _PASTAS_VISIVEIS[nome], "folderType": nome})
        return resultado
    finally:
        conexao.logout()


def _uid_para_data(cabecalho_data: str | None) -> str:
    if not cabecalho_data:
        return ""
    try:
        momento = parsedate_to_datetime(cabecalho_data)
        if momento.tzinfo is None:
            momento = momento.replace(tzinfo=timezone.utc)
        return str(int(momento.timestamp() * 1000))
    except (TypeError, ValueError):
        return ""


def list_messages(credentials: dict[str, Any], *, folder: str | None, limit: int, start: int) -> list[dict[str, Any]]:
    pasta = folder or "INBOX"
    conexao = _conectar_imap(credentials)
    try:
        status, _ = conexao.select(f'"{pasta}"', readonly=True)
        if status != "OK":
            raise YahooMailError(f"Pasta '{pasta}' não encontrada na Yahoo.", status_code=404)
        status, dados = conexao.uid("search", None, "ALL")
        if status != "OK":
            raise YahooMailError("Falha ao buscar mensagens na Yahoo.")
        uids = (dados[0].split() if dados and dados[0] else [])[::-1]  # mais recentes primeiro (UID crescente)
        pagina = uids[start - 1: start - 1 + limit]
        resultado = []
        for uid in pagina:
            status, dados_msg = conexao.uid(
                "fetch", uid, "(FLAGS BODY.PEEK[HEADER.FIELDS (SUBJECT FROM DATE)])",
            )
            if status != "OK" or not dados_msg or not dados_msg[0]:
                continue
            cabecalhos = message_from_bytes(dados_msg[0][1])
            bruto_flags = dados_msg[0][0].decode(errors="replace") if isinstance(dados_msg[0][0], bytes) else str(dados_msg[0][0])
            lida = "\\Seen" in bruto_flags
            resultado.append({
                "messageId": f"{pasta}:{uid.decode()}",
                "id": f"{pasta}:{uid.decode()}",
                "subject": _decodificar_cabecalho(cabecalhos.get("Subject")) or "(sem assunto)",
                "fromAddress": _decodificar_cabecalho(cabecalhos.get("From")),
                "receivedTime": _uid_para_data(cabecalhos.get("Date")),
                "summary": "",
                "status": "1" if lida else "0",
                "hasAttachment": 0,  # exigiria BODYSTRUCTURE completo; fora do escopo da listagem
                "provider": "yahoo",
            })
        return resultado
    finally:
        conexao.logout()


def _corpo_da_mensagem(msg) -> tuple[str | None, str]:
    html_body = None
    texto_body = ""
    if msg.is_multipart():
        for parte in msg.walk():
            tipo = parte.get_content_type()
            if tipo == "text/html" and html_body is None:
                html_body = parte.get_payload(decode=True).decode(parte.get_content_charset() or "utf-8", errors="replace")
            elif tipo == "text/plain" and not texto_body:
                texto_body = parte.get_payload(decode=True).decode(parte.get_content_charset() or "utf-8", errors="replace")
    else:
        conteudo = msg.get_payload(decode=True) or b""
        decodificado = conteudo.decode(msg.get_content_charset() or "utf-8", errors="replace")
        if msg.get_content_type() == "text/html":
            html_body = decodificado
        else:
            texto_body = decodificado
    return html_body, texto_body


def get_message(credentials: dict[str, Any], message_id: str) -> dict[str, Any]:
    if ":" not in message_id:
        raise YahooMailError("Identificador de mensagem inválido.", status_code=422)
    pasta, uid = message_id.split(":", 1)
    conexao = _conectar_imap(credentials)
    try:
        status, _ = conexao.select(f'"{pasta}"')
        if status != "OK":
            raise YahooMailError(f"Pasta '{pasta}' não encontrada na Yahoo.", status_code=404)
        status, dados = conexao.uid("fetch", uid, "(RFC822)")
        if status != "OK" or not dados or not dados[0]:
            raise YahooMailError("Mensagem não encontrada.", status_code=404)
        msg = message_from_bytes(dados[0][1])
        # Marca como lida — mesma semântica de "abrir = ler" das outras origens.
        conexao.uid("store", uid, "+FLAGS", "\\Seen")
        html_body, texto_body = _corpo_da_mensagem(msg)
        return {
            "messageId": message_id,
            "id": message_id,
            "subject": _decodificar_cabecalho(msg.get("Subject")) or "(sem assunto)",
            "fromAddress": _decodificar_cabecalho(msg.get("From")),
            "toAddress": _decodificar_cabecalho(msg.get("To")),
            "ccAddress": _decodificar_cabecalho(msg.get("Cc")),
            "receivedTime": _uid_para_data(msg.get("Date")),
            "htmlContent": html_body,
            "content": html_body or escape(texto_body).replace("\n", "<br>"),
            "provider": "yahoo",
        }
    finally:
        conexao.logout()


def act_on_messages(credentials: dict[str, Any], message_ids: list[str], acao: str) -> None:
    if acao not in ("lida", "nao_lida"):
        raise YahooMailError("Esta ação ainda não é compatível com a Yahoo — só marcar lida/não lida.", status_code=422)
    por_pasta: dict[str, list[str]] = {}
    for message_id in message_ids:
        if ":" not in message_id:
            continue
        pasta, uid = message_id.split(":", 1)
        por_pasta.setdefault(pasta, []).append(uid)
    conexao = _conectar_imap(credentials)
    try:
        for pasta, uids in por_pasta.items():
            status, _ = conexao.select(f'"{pasta}"')
            if status != "OK":
                continue
            comando = "+FLAGS" if acao == "lida" else "-FLAGS"
            conexao.uid("store", ",".join(uids), comando, "\\Seen")
    finally:
        conexao.logout()


def send_message(
    credentials: dict[str, Any], *, to: str, subject: str, html: str,
    cc: str | None = None, bcc: str | None = None,
    db: Session | None = None, user: "User | None" = None, assinar_smime: bool = False,
) -> dict[str, Any]:
    """`assinar_smime=True` (pedido do Rafael em 06/08/2026 — "assinar
    digitalmente um email pra enviar") exige `db`/`user`, porque a
    assinatura usa o certificado A1 do próprio médico (mesma infra do
    Trabalho 7, ver `services/assinatura/smime.py`). Neste módulo o MIME
    bruto segue por SMTP; a caixa nativa Mail360 não aceita corpo
    pré-montado."""
    usuario, senha = _credenciais(credentials)
    destinatarios = [endereco for _, endereco in getaddresses([to]) if endereco]
    cc_lista = [endereco for _, endereco in getaddresses([cc or ""]) if endereco]
    bcc_lista = [endereco for _, endereco in getaddresses([bcc or ""]) if endereco]
    if not destinatarios:
        raise YahooMailError("Informe ao menos um destinatário válido.", status_code=422)

    if assinar_smime:
        if db is None or user is None:
            raise YahooMailError("Assinatura S/MIME exige usuário autenticado.", status_code=422)
        try:
            mensagem_bytes = smime.montar_mensagem_assinada(
                db, user, remetente=usuario, para=destinatarios, cc=cc_lista or None,
                assunto=subject, html=html,
            )
        except smime.SmimeIndisponivel as exc:
            raise YahooMailError(f"Não foi possível assinar o e-mail: {exc}", status_code=409) from exc
        try:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as smtp:
                smtp.starttls()
                smtp.login(usuario, senha)
                smtp.sendmail(usuario, destinatarios + cc_lista + bcc_lista, mensagem_bytes)
        except smtplib.SMTPAuthenticationError as exc:
            raise YahooMailError("Login SMTP recusado pela Yahoo — a senha de aplicativo pode ter expirado.", status_code=401) from exc
        except (smtplib.SMTPException, OSError) as exc:
            raise YahooMailError("Falha ao enviar pela Yahoo.", status_code=502) from exc
        return {"status": "sent", "assinado_smime": True}

    mensagem = EmailMessage()
    mensagem["From"] = usuario
    mensagem["To"] = ", ".join(destinatarios)
    if cc_lista:
        mensagem["Cc"] = ", ".join(cc_lista)
    mensagem["Subject"] = subject
    mensagem.set_content("Esta mensagem contém conteúdo HTML.")
    mensagem.add_alternative(html, subtype="html")

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as smtp:
            smtp.starttls()
            smtp.login(usuario, senha)
            smtp.send_message(mensagem, to_addrs=destinatarios + cc_lista + bcc_lista)
    except smtplib.SMTPAuthenticationError as exc:
        raise YahooMailError("Login SMTP recusado pela Yahoo — a senha de aplicativo pode ter expirado.", status_code=401) from exc
    except (smtplib.SMTPException, OSError) as exc:
        raise YahooMailError("Falha ao enviar pela Yahoo.", status_code=502) from exc
    return {"status": "sent"}
