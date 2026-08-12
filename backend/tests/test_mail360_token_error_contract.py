"""Regressões do contrato de erro na renovação OAuth do Mail360."""
from unittest.mock import patch

import httpx
import pytest

from app.services import mail360


@pytest.fixture(autouse=True)
def _sem_cache_de_token():
    mail360._token_cache["token"] = ""
    mail360._token_cache["expira_em"] = 0.0
    yield
    mail360._token_cache["token"] = ""
    mail360._token_cache["expira_em"] = 0.0


def test_status_http_na_renovacao_vira_mail360error():
    resposta = httpx.Response(
        status_code=500,
        json={"status": {"code": 500}},
        request=httpx.Request("POST", mail360.TOKEN_URL),
    )
    with patch("httpx.Client.post", return_value=resposta):
        with pytest.raises(mail360.Mail360Error, match="erro 500"):
            mail360._obter_access_token()


def test_falha_de_rede_na_renovacao_vira_mail360error():
    request = httpx.Request("POST", mail360.TOKEN_URL)
    with patch("httpx.Client.post", side_effect=httpx.ConnectError("offline", request=request)):
        with pytest.raises(mail360.Mail360Error, match="renovar a sessão"):
            mail360._obter_access_token()
