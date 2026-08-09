from types import SimpleNamespace

from app.services import external_mail, imap_mail_ops
from app.services.agenda_integrada import domain


def test_delete_yahoo_uses_imap_not_graph(monkeypatch):
    calls = []
    monkeypatch.setattr(domain, "integration_credentials", lambda integration: {
        "username": "titular@yahoo.com", "app_specific_password": "segredo",
    })
    monkeypatch.setattr(
        imap_mail_ops,
        "move_to_trash",
        lambda credentials, message_id, **kwargs: calls.append((credentials, message_id, kwargs)),
    )
    monkeypatch.setattr(external_mail, "_request", lambda *a, **k: (_ for _ in ()).throw(AssertionError("não deve usar REST")))

    external_mail.delete_message(None, SimpleNamespace(provider="yahoo_mail"), "INBOX:42")

    assert calls[0][0]["username"] == "titular@yahoo.com"
    assert calls[0][1] == "INBOX:42"
    assert calls[0][2]["host"] == "imap.mail.yahoo.com"
    assert calls[0][2]["trash_folder"] == "Trash"


def test_delete_icloud_uses_imap_not_graph(monkeypatch):
    calls = []
    monkeypatch.setattr(domain, "integration_credentials", lambda integration: {
        "username": "titular@icloud.com", "app_specific_password": "segredo",
    })
    monkeypatch.setattr(
        imap_mail_ops,
        "move_to_trash",
        lambda credentials, message_id, **kwargs: calls.append((credentials, message_id, kwargs)),
    )
    monkeypatch.setattr(external_mail, "_request", lambda *a, **k: (_ for _ in ()).throw(AssertionError("não deve usar REST")))

    external_mail.delete_message(None, SimpleNamespace(provider="apple_icloud"), "INBOX:9")

    assert calls[0][2]["host"] == "imap.mail.me.com"
    assert calls[0][2]["trash_folder"] == "Trash"


def test_delete_google_moves_to_trash(monkeypatch):
    calls = []
    monkeypatch.setattr(external_mail, "_request", lambda *a, **k: calls.append((a, k)))

    external_mail.delete_message(None, SimpleNamespace(provider="google_calendar"), "abc/123")

    assert calls
    assert calls[0][0][2] == "POST"
    assert calls[0][0][3].endswith("/messages/abc%2F123/trash")


def test_delete_microsoft_uses_graph_delete(monkeypatch):
    calls = []
    monkeypatch.setattr(external_mail, "_request", lambda *a, **k: calls.append((a, k)))

    external_mail.delete_message(None, SimpleNamespace(provider="microsoft_365"), "A+B/C")

    assert calls[0][0][2] == "DELETE"
    assert calls[0][0][3].endswith("/messages/A%2BB%2FC")


def test_imap_move_to_trash_copies_then_deletes(monkeypatch):
    operations = []

    class FakeImap:
        def __init__(self, host, port, timeout):
            operations.append(("connect", host, port, timeout))
        def login(self, username, password):
            operations.append(("login", username, password))
        def select(self, folder):
            operations.append(("select", folder)); return "OK", []
        def uid(self, command, *args):
            operations.append(("uid", command, *args)); return "OK", []
        def expunge(self):
            operations.append(("expunge",)); return "OK", []
        def logout(self):
            operations.append(("logout",))

    monkeypatch.setattr(imap_mail_ops.imaplib, "IMAP4_SSL", FakeImap)
    imap_mail_ops.move_to_trash(
        {"username": "u@example.com", "app_specific_password": "pw"},
        "INBOX:77", host="imap.example.com", trash_folder="Trash", error_cls=RuntimeError,
    )

    assert ("uid", "copy", "77", '"Trash"') in operations
    assert ("uid", "store", "77", "+FLAGS", "\\Deleted") in operations
    assert ("expunge",) in operations
