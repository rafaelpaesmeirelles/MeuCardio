"""Testes do cliente `app/services/mail360.py` contra respostas GRAVADAS de
chamadas reais feitas em 30/07/2026 (troca de token, tentativa de criar
conta, GET /accounts, formatos documentados oficialmente para folders/
messages/content) — não contra a rede. Existem para travar o comportamento
que só a chamada real revelou (envelope `{"status", "data"}` em tudo, corpo
JSON no /access-token, `expires_in` como epoch-ms, e os dois endpoints
separados de mensagem) e pegar regressão se alguém editar o arquivo sem
saber por que ele é do jeito que é.
"""
from unittest.mock import patch

import httpx
import pytest

from app.services import mail360


def _resposta(status_code=200, json_body=None, content=b"{}"):
    r = httpx.Response(status_code=status_code, json=json_body, request=httpx.Request("GET", "https://x"))
    return r


@pytest.fixture(autouse=True)
def _sem_cache_de_token():
    """Cada teste começa sem token em cache, e não deixa um pra trás."""
    mail360._token_cache["token"] = ""
    mail360._token_cache["expira_em"] = 0.0
    yield
    mail360._token_cache["token"] = ""
    mail360._token_cache["expira_em"] = 0.0


class TestObterAccessToken:
    def test_manda_corpo_em_json_nao_form(self):
        """Regressão do bug real: `data=` (form-encoded) devolvia 400
        JSON_PARSE_ERROR contra a API de verdade."""
        with patch("httpx.Client.post") as post:
            post.return_value = _resposta(json_body={
                "status": {"code": 200, "description": "success"},
                "data": {"access_token": "tok-123", "expires_in": "1785414750629"},
            })
            token = mail360._obter_access_token()

        assert token == "tok-123"
        _, kwargs = post.call_args
        assert "json" in kwargs, "o corpo precisa ir em `json=`, não `data=`"
        assert kwargs["json"] == {
            "client_id": mail360.settings.mail360_client_id,
            "client_secret": mail360.settings.mail360_client_secret,
            "refresh_token": mail360.settings.mail360_refresh_token,
        }

    def test_le_access_token_de_dentro_de_data(self):
        """A resposta real vem embrulhada — `access_token` não está no
        nível raiz do JSON."""
        with patch("httpx.Client.post") as post:
            post.return_value = _resposta(json_body={
                "status": {"code": 200}, "data": {"access_token": "tok-aninhado"},
            })
            token = mail360._obter_access_token()
        assert token == "tok-aninhado"

    def test_sem_access_token_levanta_erro(self):
        with patch("httpx.Client.post") as post:
            post.return_value = _resposta(json_body={"status": {"code": 200}, "data": {}})
            with pytest.raises(mail360.Mail360Error):
                mail360._obter_access_token()

    def test_token_fica_em_cache_ate_o_ttl(self):
        with patch("httpx.Client.post") as post:
            post.return_value = _resposta(json_body={"status": {"code": 200}, "data": {"access_token": "tok-cache"}})
            primeiro = mail360._obter_access_token()
            segundo = mail360._obter_access_token()
        assert primeiro == segundo == "tok-cache"
        post.assert_called_once()  # a segunda chamada não bateu na rede de novo


class TestChamarDesembrulhaData:
    def _com_token_valido(self):
        mail360._token_cache["token"] = "tok-fixo"
        mail360._token_cache["expira_em"] = mail360.time.monotonic() + 999

    def test_desembrulha_dict(self):
        self._com_token_valido()
        with patch("httpx.Client.request") as request:
            request.return_value = _resposta(json_body={
                "status": {"code": 200}, "data": {"account_key": "abc123"},
            })
            resultado = mail360._chamar("GET", "/algo")
        assert resultado == {"account_key": "abc123"}

    def test_desembrulha_lista(self):
        self._com_token_valido()
        with patch("httpx.Client.request") as request:
            request.return_value = _resposta(json_body={
                "status": {"code": 200}, "data": [{"folderId": "1", "folderName": "Inbox"}],
            })
            resultado = mail360._chamar("GET", "/accounts/x/folders")
        assert resultado == [{"folderId": "1", "folderName": "Inbox"}]

    def test_corpo_vazio_devolve_dict_vazio(self):
        self._com_token_valido()
        with patch("httpx.Client.request") as request:
            r = httpx.Response(status_code=204, request=httpx.Request("DELETE", "https://x"))
            request.return_value = r
            resultado = mail360._chamar("DELETE", "/algo")
        assert resultado == {}

    def test_erro_http_vira_mail360error(self):
        """Regressão real: foi exatamente este 500 que a API devolveu ao
        tentar criar conta num domínio ainda não cadastrado no Mail360
        (`MailServerException: Local domain does not exists`)."""
        self._com_token_valido()
        with patch("httpx.Client.request") as request:
            request.return_value = httpx.Response(
                status_code=500,
                json={"status": {"code": 500}, "data": {"errorCode": "1000"}},
                request=httpx.Request("POST", "https://x"),
            )
            with pytest.raises(mail360.Mail360Error):
                mail360._chamar("POST", "/algo")


class TestFuncoesDeAltoNivel:
    def _mockar_chamar(self, monkeypatch, retorno):
        chamadas = []

        def fake(metodo, caminho, **kwargs):
            chamadas.append((metodo, caminho, kwargs))
            if isinstance(retorno, list):
                return retorno.pop(0)
            return retorno

        monkeypatch.setattr(mail360, "_chamar", fake)
        return chamadas

    def test_criar_conta_nativa_le_account_key_snake_case(self, monkeypatch):
        self._mockar_chamar(monkeypatch, {"account_key": "N7A0CM"})
        chave = mail360.criar_conta_nativa("teste@corvia.med.br", "Teste")
        assert chave == "N7A0CM"

    def test_criar_conta_nativa_sem_account_key_levanta_erro(self, monkeypatch):
        self._mockar_chamar(monkeypatch, {})
        with pytest.raises(mail360.Mail360Error):
            mail360.criar_conta_nativa("teste@corvia.med.br", "Teste")

    def test_upload_anexo_le_file_id_direto_sem_desembrulhar_de_novo(self, monkeypatch):
        """Regressão: antes do refactor de `_chamar`, este código fazia
        `(dados.get("data") or {}).get("fileId")` — depois que `_chamar`
        passou a desembrulhar sozinho, isso quebraria por desembrulhar
        duas vezes se não tivesse sido ajustado junto."""
        self._mockar_chamar(monkeypatch, {"fileId": "file-abc"})
        file_id = mail360.upload_anexo("acc-1", "doc.pdf", b"conteudo")
        assert file_id == "file-abc"

    def test_obter_mensagem_funde_metadado_e_conteudo(self, monkeypatch):
        chamadas = self._mockar_chamar(monkeypatch, [
            {"messageId": "m1", "subject": "Oi", "fromAddress": "a@x.com"},
            {"messageId": "m1", "content": "<p>corpo</p>"},
        ])
        msg = mail360.obter_mensagem("acc-1", "m1")
        assert msg["subject"] == "Oi"
        assert msg["fromAddress"] == "a@x.com"
        assert msg["content"] == "<p>corpo</p>"
        assert chamadas[0][1] == "/accounts/acc-1/messages/m1"
        assert chamadas[1][1] == "/accounts/acc-1/messages/m1/content"

    def test_obter_mensagem_sem_conteudo_ainda_devolve_metadado(self, monkeypatch):
        """Se o segundo endpoint falhar, a mensagem não pode desaparecer
        inteira — assunto e remetente continuam úteis sem o corpo."""
        def fake(metodo, caminho, **kwargs):
            if caminho.endswith("/content"):
                raise mail360.Mail360Error("falhou")
            return {"messageId": "m1", "subject": "Oi"}

        monkeypatch.setattr(mail360, "_chamar", fake)
        msg = mail360.obter_mensagem("acc-1", "m1")
        assert msg["subject"] == "Oi"
        assert msg["content"] is None
