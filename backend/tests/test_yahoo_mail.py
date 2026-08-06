"""app/services/yahoo_mail.py — IMAP/SMTP com senha de aplicativo, sem rede
real: `imaplib.IMAP4_SSL` e `smtplib.SMTP` são substituídos por dublês que
imitam só o subconjunto de protocolo que o módulo usa.
"""
from email.message import EmailMessage

import pytest

from app.services import yahoo_mail
from app.services.yahoo_mail import YahooMailError


class _IMAPFalso:
    """Simula só os métodos que yahoo_mail.py chama: login, list, select,
    uid("search"/"fetch"/"store"), logout."""

    def __init__(self, mensagens: dict[str, dict[bytes, dict]], *, falhar_login: bool = False):
        # mensagens: {"INBOX": {b"1": {"flags": "\\Seen", "raw": bytes}}, ...}
        self._mensagens = mensagens
        self._pasta_atual = None
        self._falhar_login = falhar_login

    def login(self, usuario, senha):
        if self._falhar_login:
            import imaplib
            raise imaplib.IMAP4.error("credenciais inválidas")
        return ("OK", [b"logged in"])

    def list(self):
        linhas = [f'(\\HasNoChildren) "/" "{nome}"'.encode() for nome in self._mensagens]
        return ("OK", linhas)

    def select(self, pasta, readonly=False):
        nome = pasta.strip('"')
        if nome not in self._mensagens:
            return ("NO", [b"no such mailbox"])
        self._pasta_atual = nome
        return ("OK", [str(len(self._mensagens[nome])).encode()])

    @staticmethod
    def _para_bytes(valor) -> bytes:
        return valor.encode() if isinstance(valor, str) else valor

    def uid(self, comando, *args):
        if comando == "search":
            uids = sorted(self._mensagens[self._pasta_atual].keys())
            return ("OK", [b" ".join(uids)])
        if comando == "fetch":
            # `get_message` passa o uid como STRING (extraído de "pasta:uid"),
            # `list_messages` re-lê o uid em bytes vindo do próprio `search` —
            # o real imaplib aceita os dois; o dublê normaliza pra bater com
            # as chaves em bytes do dicionário de mensagens do teste.
            uid_bytes = self._para_bytes(args[0])
            registro = self._mensagens[self._pasta_atual].get(uid_bytes)
            if registro is None:
                return ("OK", [None])
            # Formato real do imaplib varia por variante do FETCH, mas o
            # código só lê [0] (flags) na listagem e [1] (bytes da mensagem)
            # nos dois casos — um par (flags, raw) uniforme cobre ambos.
            return ("OK", [(registro.get("flags", "").encode(), registro["raw"])])
        if comando == "store":
            uids_alvo = str(args[0])  # imaplib aceita string de UIDs separados por vírgula
            sinal, flag = args[1], args[2]
            for uid_texto in uids_alvo.split(","):
                registro = self._mensagens[self._pasta_atual].get(self._para_bytes(uid_texto))
                if registro is None:
                    continue
                atuais = set(registro.get("flags", "").split())
                if sinal == "+FLAGS":
                    atuais.add(flag)
                else:
                    atuais.discard(flag)
                registro["flags"] = " ".join(atuais)
            return ("OK", [b"done"])
        raise AssertionError(f"comando IMAP não esperado no teste: {comando}")

    def logout(self):
        return ("BYE", [b"logging out"])


def _mensagem_crua(assunto: str, remetente: str, data: str, html: str | None = None, texto: str = "corpo") -> bytes:
    msg = EmailMessage()
    msg["Subject"] = assunto
    msg["From"] = remetente
    msg["To"] = "titular@yahoo.com"
    msg["Date"] = data
    if html:
        msg.set_content(texto)
        msg.add_alternative(html, subtype="html")
    else:
        msg.set_content(texto)
    return msg.as_bytes()


def _credenciais() -> dict:
    return {"username": "titular@yahoo.com", "app_specific_password": "senha-de-app-123"}


def test_diagnose_login_ok(monkeypatch):
    monkeypatch.setattr(yahoo_mail, "_conectar_imap", lambda credentials: _IMAPFalso({"INBOX": {}}))
    resultado = yahoo_mail.diagnose(_credenciais())
    assert resultado == {"ok": True, "provider": "yahoo_mail"}


def test_conectar_imap_login_recusado_vira_erro_tratado(monkeypatch):
    def _imap_ssl_falso(host, port, timeout=None):
        return _IMAPFalso({}, falhar_login=True)

    monkeypatch.setattr(yahoo_mail.imaplib, "IMAP4_SSL", _imap_ssl_falso)
    with pytest.raises(YahooMailError) as excinfo:
        yahoo_mail._conectar_imap(_credenciais())
    assert excinfo.value.status_code == 401


def test_credenciais_ausentes_nao_tenta_conectar():
    with pytest.raises(YahooMailError):
        yahoo_mail._conectar_imap({})


def test_list_folders_filtra_so_pastas_conhecidas(monkeypatch):
    fake = _IMAPFalso({"INBOX": {}, "Sent": {}, "PastaCustomizada": {}})
    monkeypatch.setattr(yahoo_mail, "_conectar_imap", lambda credentials: fake)
    pastas = yahoo_mail.list_folders(_credenciais())
    nomes = {p["folderId"] for p in pastas}
    assert nomes == {"INBOX", "Sent"}


def test_list_messages_mais_recente_primeiro_e_status_lida(monkeypatch):
    mensagens = {
        "INBOX": {
            b"1": {"flags": "\\Seen", "raw": _mensagem_crua("Antiga", "a@ex.com", "Mon, 01 Jun 2026 10:00:00 +0000")},
            b"2": {"flags": "", "raw": _mensagem_crua("Nova", "b@ex.com", "Tue, 02 Jun 2026 10:00:00 +0000")},
        },
    }
    fake = _IMAPFalso(mensagens)
    monkeypatch.setattr(yahoo_mail, "_conectar_imap", lambda credentials: fake)
    resultado = yahoo_mail.list_messages(_credenciais(), folder=None, limit=10, start=1)
    assert [m["subject"] for m in resultado] == ["Nova", "Antiga"]
    assert resultado[0]["status"] == "0"  # não lida
    assert resultado[1]["status"] == "1"  # lida
    assert resultado[0]["messageId"] == "INBOX:2"


def test_list_messages_pasta_inexistente_devolve_404(monkeypatch):
    fake = _IMAPFalso({"INBOX": {}})
    monkeypatch.setattr(yahoo_mail, "_conectar_imap", lambda credentials: fake)
    with pytest.raises(YahooMailError) as excinfo:
        yahoo_mail.list_messages(_credenciais(), folder="NaoExiste", limit=10, start=1)
    assert excinfo.value.status_code == 404


def test_get_message_marca_como_lida_e_extrai_html(monkeypatch):
    mensagens = {
        "INBOX": {
            b"5": {"flags": "", "raw": _mensagem_crua("Oi", "c@ex.com", "Wed, 03 Jun 2026 10:00:00 +0000", html="<p>Olá</p>")},
        },
    }
    fake = _IMAPFalso(mensagens)
    monkeypatch.setattr(yahoo_mail, "_conectar_imap", lambda credentials: fake)
    resultado = yahoo_mail.get_message(_credenciais(), "INBOX:5")
    assert resultado["subject"] == "Oi"
    assert "<p>Olá</p>" in resultado["htmlContent"]
    assert "\\Seen" in mensagens["INBOX"][b"5"]["flags"]


def test_get_message_id_sem_pasta_e_rejeitado():
    with pytest.raises(YahooMailError):
        yahoo_mail.get_message(_credenciais(), "sem-pasta-aqui")


def test_get_message_inexistente_devolve_404(monkeypatch):
    fake = _IMAPFalso({"INBOX": {}})
    monkeypatch.setattr(yahoo_mail, "_conectar_imap", lambda credentials: fake)
    with pytest.raises(YahooMailError) as excinfo:
        yahoo_mail.get_message(_credenciais(), "INBOX:999")
    assert excinfo.value.status_code == 404


def test_act_on_messages_marcar_lida_e_nao_lida(monkeypatch):
    mensagens = {"INBOX": {b"7": {"flags": "", "raw": b""}}}
    fake = _IMAPFalso(mensagens)
    monkeypatch.setattr(yahoo_mail, "_conectar_imap", lambda credentials: fake)

    yahoo_mail.act_on_messages(_credenciais(), ["INBOX:7"], "lida")
    assert "\\Seen" in mensagens["INBOX"][b"7"]["flags"]

    yahoo_mail.act_on_messages(_credenciais(), ["INBOX:7"], "nao_lida")
    assert "\\Seen" not in mensagens["INBOX"][b"7"]["flags"]


def test_act_on_messages_mover_nao_suportado(monkeypatch):
    fake = _IMAPFalso({"INBOX": {}})
    monkeypatch.setattr(yahoo_mail, "_conectar_imap", lambda credentials: fake)
    with pytest.raises(YahooMailError):
        yahoo_mail.act_on_messages(_credenciais(), ["INBOX:1"], "mover")


class _SMTPFalso:
    def __init__(self, enviados: list, *, falhar_login: bool = False):
        self._enviados = enviados
        self._falhar_login = falhar_login

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def starttls(self):
        pass

    def login(self, usuario, senha):
        if self._falhar_login:
            import smtplib
            raise smtplib.SMTPAuthenticationError(535, b"auth failed")

    def send_message(self, mensagem, to_addrs=None):
        self._enviados.append({"mensagem": mensagem, "to_addrs": to_addrs})


def test_send_message_envia_multipart_html(monkeypatch):
    enviados: list = []
    monkeypatch.setattr(yahoo_mail.smtplib, "SMTP", lambda host, port, timeout=None: _SMTPFalso(enviados))
    resultado = yahoo_mail.send_message(
        _credenciais(), to="destino@example.com", subject="Assunto", html="<b>oi</b>",
    )
    assert resultado == {"status": "sent"}
    assert len(enviados) == 1
    assert enviados[0]["to_addrs"] == ["destino@example.com"]
    assert enviados[0]["mensagem"]["Subject"] == "Assunto"


def test_send_message_sem_destinatario_valido_e_422():
    with pytest.raises(YahooMailError) as excinfo:
        yahoo_mail.send_message(_credenciais(), to="", subject="Oi", html="<p>x</p>")
    assert excinfo.value.status_code == 422


def test_send_message_login_recusado_vira_401(monkeypatch):
    monkeypatch.setattr(
        yahoo_mail.smtplib, "SMTP",
        lambda host, port, timeout=None: _SMTPFalso([], falhar_login=True),
    )
    with pytest.raises(YahooMailError) as excinfo:
        yahoo_mail.send_message(_credenciais(), to="destino@example.com", subject="Oi", html="<p>x</p>")
    assert excinfo.value.status_code == 401
