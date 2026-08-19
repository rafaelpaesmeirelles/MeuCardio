"""Auditoria AUTH/SESSION → MAIL (issue #52, subfase 3): caixa unificada para
contas Google/Microsoft (`app/services/external_mail.py`).

Gap encontrado na auditoria: `delete_message` já tinha cobertura para os 4
provedores (`test_corvia_mail_external_ops.py`), e a renovação/retry de
token em 401 já tinha cobertura própria
(`test_external_account_refresh_resilience.py`) — mas `list_folders`,
`list_messages` (paginação), `get_message`, `act_on_messages` e
`send_message` para `google_calendar`/`microsoft_365` nunca tinham sido
exercitados por teste algum: só apareciam mockados no limite do módulo em
testes de rota mais acima (`test_email_mensagens_todas.py`,
`test_corvia_mail.py`), o que nunca chega a rodar a lógica real de
paginação/mapeamento de campo/payload deste arquivo.

Toda chamada de rede é interceptada via monkeypatch de `httpx.request` no
próprio módulo — nenhuma chamada real ao Gmail/Graph.
"""
import base64

import httpx
import pytest

from app.services import external_mail
from app.services.external_mail import ExternalMailError


class _Integration:
    def __init__(self, provider):
        self.provider = provider
        self.id = 1
        self.display_name = "Médico <medico@corvia.med.br>"
        self.external_account_id = "conta-1"


@pytest.fixture(autouse=True)
def _credenciais_ja_frescas(monkeypatch):
    """Isola estes testes da camada de OAuth (já auditada na subfase 2) —
    aqui o interesse é só a lógica de paginação/payload/mapeamento."""
    monkeypatch.setattr(
        external_mail, "ensure_fresh_credentials",
        lambda db, integration, **kw: {"access_token": "token-valido"},
    )


def _mock_request(monkeypatch, handler):
    chamadas = []

    def _request(method, url, headers=None, timeout=None, **kwargs):
        chamadas.append({"method": method, "url": url, "headers": headers, **kwargs})
        return handler(method, url, kwargs)

    monkeypatch.setattr(external_mail.httpx, "request", _request)
    return chamadas


# --- paginação -------------------------------------------------------------


def test_list_messages_google_slices_by_start_and_limit(monkeypatch):
    """3 mensagens na listagem, start=2/limit=1 deve devolver só a 2ª —
    slice local sobre a lista de ids, já que o Gmail não pagina por
    offset."""
    listagem = {"messages": [{"id": "m1"}, {"id": "m2"}, {"id": "m3"}]}
    detalhes = {
        "m2": {
            "id": "m2", "payload": {"headers": [
                {"name": "Subject", "value": "Assunto 2"},
                {"name": "From", "value": "a@x.com"},
            ]},
            "labelIds": [], "snippet": "resumo",
        },
    }

    def handler(method, url, kwargs):
        if url.endswith("/messages"):
            assert kwargs["params"]["maxResults"] == "2"  # start-1+limit = 1+1
            return httpx.Response(200, json=listagem)
        message_id = url.rsplit("/", 1)[-1]
        return httpx.Response(200, json=detalhes[message_id])

    _mock_request(monkeypatch, handler)
    resultado = external_mail.list_messages(
        None, _Integration("google_calendar"), folder=None, limit=1, start=2,
    )
    assert [m["messageId"] for m in resultado] == ["m2"]
    assert resultado[0]["subject"] == "Assunto 2"


def test_list_messages_google_caps_max_results_at_500(monkeypatch):
    def handler(method, url, kwargs):
        assert int(kwargs["params"]["maxResults"]) <= 500
        return httpx.Response(200, json={"messages": []})

    _mock_request(monkeypatch, handler)
    external_mail.list_messages(
        None, _Integration("google_calendar"), folder=None, limit=100, start=450,
    )


def test_list_messages_microsoft_maps_start_and_limit_to_skip_and_top(monkeypatch):
    def handler(method, url, kwargs):
        assert "/mailFolders/inbox/messages" in url
        assert kwargs["params"]["$top"] == "10"
        assert kwargs["params"]["$skip"] == "20"  # start=21 -> skip 20
        return httpx.Response(200, json={"value": [
            {"id": "g1", "subject": "Oi", "isRead": True, "receivedDateTime": "2026-08-01T10:00:00Z"},
        ]})

    _mock_request(monkeypatch, handler)
    resultado = external_mail.list_messages(
        None, _Integration("microsoft_365"), folder=None, limit=10, start=21,
    )
    assert resultado[0]["messageId"] == "g1"
    assert resultado[0]["status"] == "1"  # lida


def test_list_messages_microsoft_uses_custom_folder(monkeypatch):
    def handler(method, url, kwargs):
        assert "/mailFolders/sentitems/messages" in url
        return httpx.Response(200, json={"value": []})

    _mock_request(monkeypatch, handler)
    external_mail.list_messages(
        None, _Integration("microsoft_365"), folder="sentitems", limit=10, start=1,
    )


def test_list_messages_limit_and_start_are_clamped_to_sane_bounds(monkeypatch):
    """limit=0/negativo e start=0/negativo não podem virar paginação
    inválida (ex.: $skip negativo, maxResults zero) — a função já clampa,
    isto trava a garantia."""
    def handler(method, url, kwargs):
        assert int(kwargs["params"]["$top"]) >= 1
        assert int(kwargs["params"]["$skip"]) >= 0
        return httpx.Response(200, json={"value": []})

    _mock_request(monkeypatch, handler)
    external_mail.list_messages(
        None, _Integration("microsoft_365"), folder=None, limit=-5, start=-3,
    )


# --- listagem de pastas ------------------------------------------------


def test_list_folders_google_filters_to_known_and_user_labels(monkeypatch):
    def handler(method, url, kwargs):
        return httpx.Response(200, json={"labels": [
            {"id": "INBOX", "name": "Caixa de entrada"},
            {"id": "CHAT", "name": "Chat"},  # não está na allowlist nem é 'user'
            {"id": "Label_1", "name": "Pacientes", "type": "user"},
        ]})

    _mock_request(monkeypatch, handler)
    pastas = external_mail.list_folders(None, _Integration("google_calendar"))
    ids = {p["folderId"] for p in pastas}
    assert ids == {"INBOX", "Label_1"}
    assert "CHAT" not in ids


def test_list_folders_microsoft_maps_display_name(monkeypatch):
    def handler(method, url, kwargs):
        assert kwargs["params"]["$top"] == "100"
        return httpx.Response(200, json={"value": [
            {"id": "AAA", "displayName": "Caixa de Entrada", "wellKnownName": "inbox"},
        ]})

    _mock_request(monkeypatch, handler)
    pastas = external_mail.list_folders(None, _Integration("microsoft_365"))
    assert pastas == [{"folderId": "AAA", "id": "AAA", "folderName": "Caixa de Entrada", "folderType": "inbox"}]


# --- leitura de mensagem (marca como lida) -------------------------------


def test_get_message_google_marks_unread_as_read(monkeypatch):
    chamadas = _mock_request(monkeypatch, lambda method, url, kwargs: httpx.Response(200, json={
        "id": "m1", "payload": {"headers": [{"name": "Subject", "value": "Oi"}]}, "labelIds": ["UNREAD"],
    }))
    external_mail.get_message(None, _Integration("google_calendar"), "m1")
    modify = [c for c in chamadas if c["url"].endswith("/modify")]
    assert len(modify) == 1
    assert modify[0]["json"] == {"removeLabelIds": ["UNREAD"]}


def test_get_message_microsoft_only_patches_when_still_unread(monkeypatch):
    chamadas = _mock_request(monkeypatch, lambda method, url, kwargs: httpx.Response(200, json={
        "id": "m1", "subject": "Oi", "isRead": False,
    }))
    external_mail.get_message(None, _Integration("microsoft_365"), "m1")
    patches = [c for c in chamadas if c["method"] == "PATCH"]
    assert len(patches) == 1
    assert patches[0]["json"] == {"isRead": True}


def test_get_message_microsoft_skips_patch_when_already_read(monkeypatch):
    chamadas = _mock_request(monkeypatch, lambda method, url, kwargs: httpx.Response(200, json={
        "id": "m1", "subject": "Oi", "isRead": True,
    }))
    external_mail.get_message(None, _Integration("microsoft_365"), "m1")
    assert not [c for c in chamadas if c["method"] == "PATCH"]


# --- ações em lote ---------------------------------------------------------


def test_act_on_messages_google_move_adds_destination_and_removes_inbox(monkeypatch):
    chamadas = _mock_request(monkeypatch, lambda method, url, kwargs: httpx.Response(200, json={}))
    external_mail.act_on_messages(
        None, _Integration("google_calendar"), ["m1", "m2"], "mover", destination="Label_2",
    )
    assert len(chamadas) == 2
    for c in chamadas:
        assert c["json"] == {"addLabelIds": ["Label_2"], "removeLabelIds": ["INBOX"]}


def test_act_on_messages_microsoft_toggle_read(monkeypatch):
    chamadas = _mock_request(monkeypatch, lambda method, url, kwargs: httpx.Response(200, json={}))
    external_mail.act_on_messages(None, _Integration("microsoft_365"), ["m1"], "nao_lida")
    assert chamadas[0]["method"] == "PATCH"
    assert chamadas[0]["json"] == {"isRead": False}


def test_act_on_messages_microsoft_move_uses_move_endpoint(monkeypatch):
    chamadas = _mock_request(monkeypatch, lambda method, url, kwargs: httpx.Response(200, json={}))
    external_mail.act_on_messages(
        None, _Integration("microsoft_365"), ["m1"], "mover", destination="deleteditems",
    )
    assert chamadas[0]["url"].endswith("/messages/m1/move")
    assert chamadas[0]["json"] == {"destinationId": "deleteditems"}


def test_act_on_messages_unknown_action_makes_no_request(monkeypatch):
    chamadas = _mock_request(monkeypatch, lambda method, url, kwargs: httpx.Response(200, json={}))
    external_mail.act_on_messages(None, _Integration("google_calendar"), ["m1"], "arquivar_para_sempre")
    assert chamadas == []


# --- envio -------------------------------------------------------------


def test_send_message_google_builds_multipart_and_base64url_payload(monkeypatch):
    chamadas = _mock_request(monkeypatch, lambda method, url, kwargs: httpx.Response(200, json={"id": "sent-1"}))
    resultado = external_mail.send_message(
        None, _Integration("google_calendar"),
        to="Paciente <paciente@teste.local>", subject="Retorno",
        html="<p>Olá</p>", cc=None, bcc=None,
    )
    assert resultado == {"id": "sent-1"}
    assert chamadas[0]["url"].endswith("/messages/send")
    assert "raw" in chamadas[0]["json"]


def test_send_message_microsoft_builds_graph_payload_with_cc_bcc(monkeypatch):
    chamadas = _mock_request(monkeypatch, lambda method, url, kwargs: httpx.Response(202))
    external_mail.send_message(
        None, _Integration("microsoft_365"),
        to="a@x.com", subject="Retorno", html="<p>Olá</p>",
        cc="b@x.com", bcc="c@x.com",
    )
    payload = chamadas[0]["json"]["message"]
    assert payload["toRecipients"] == [{"emailAddress": {"address": "a@x.com"}}]
    assert payload["ccRecipients"] == [{"emailAddress": {"address": "b@x.com"}}]
    assert payload["bccRecipients"] == [{"emailAddress": {"address": "c@x.com"}}]


def test_send_message_google_smime_usa_mime_bruto_base64url(monkeypatch):
    bruto = b"From: medico@corvia.med.br\r\nContent-Type: multipart/signed\r\n\r\ncorpo"
    monkeypatch.setattr(external_mail.smime, "montar_mensagem_assinada", lambda *a, **k: bruto)
    chamadas = _mock_request(
        monkeypatch,
        lambda method, url, kwargs: httpx.Response(200, json={"id": "signed-1"}),
    )

    resultado = external_mail.send_message(
        None, _Integration("google_calendar"), to="paciente@x.com",
        subject="Retorno", html="<p>Olá</p>", user=object(), assinar_smime=True,
    )

    assert resultado == {"id": "signed-1", "assinado_smime": True}
    assert base64.urlsafe_b64decode(chamadas[0]["json"]["raw"] + "==") == bruto


def test_send_message_microsoft_smime_usa_mime_bruto_base64(monkeypatch):
    bruto = b"From: medico@corvia.med.br\r\nContent-Type: multipart/signed\r\n\r\ncorpo"
    monkeypatch.setattr(external_mail.smime, "montar_mensagem_assinada", lambda *a, **k: bruto)
    chamadas = _mock_request(monkeypatch, lambda method, url, kwargs: httpx.Response(202))

    resultado = external_mail.send_message(
        None, _Integration("microsoft_365"), to="paciente@x.com",
        subject="Retorno", html="<p>Olá</p>", user=object(), assinar_smime=True,
    )

    assert resultado == {"sent": True, "assinado_smime": True}
    assert chamadas[0]["headers"]["Content-Type"] == "text/plain"
    assert base64.b64decode(chamadas[0]["content"]) == bruto


@pytest.mark.parametrize("provider", ["google_calendar", "microsoft_365"])
def test_send_message_without_any_recipient_is_rejected_before_any_request(monkeypatch, provider):
    chamadas = _mock_request(monkeypatch, lambda method, url, kwargs: httpx.Response(200, json={}))
    with pytest.raises(ExternalMailError) as exc:
        external_mail.send_message(
            None, _Integration(provider), to="", subject="X", html="<p/>",
        )
    assert exc.value.status_code == 422
    assert chamadas == []  # falha antes de qualquer chamada de rede


# --- mapeamento de erro HTTP -> ExternalMailError -------------------------


@pytest.mark.parametrize(
    "status,esperado_status_code",
    [(403, 403), (429, 503), (500, 503), (400, 502)],
)
def test_request_maps_provider_status_to_expected_error(monkeypatch, status, esperado_status_code):
    _mock_request(monkeypatch, lambda method, url, kwargs: httpx.Response(status, json={}))
    with pytest.raises(ExternalMailError) as exc:
        external_mail.list_folders(None, _Integration("microsoft_365"))
    assert exc.value.status_code == esperado_status_code
