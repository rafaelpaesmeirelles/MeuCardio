import httpx
import pytest
from fastapi import HTTPException

from app.api.receituario import DestinatarioIn, _endereco_destinatario, consultar_cep


class _RespostaCep:
    def __init__(self, payload: dict):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


def test_endereco_estruturado_e_serializado_sem_migration():
    destinatario = DestinatarioIn(
        nome="Paciente Teste",
        documento="12345678900",
        cep="14010-090",
        logradouro="Rua Tibiriçá",
        numero="1172",
        complemento="Apto 10",
        bairro="Centro",
        cidade="Ribeirão Preto",
        uf="sp",
    )

    assert _endereco_destinatario(destinatario) == (
        "Rua Tibiriçá, 1172 - Apto 10 - Centro - Ribeirão Preto/SP - CEP 14010-090"
    )


def test_consulta_cep_retorna_campos_necessarios(monkeypatch):
    chamado = {}

    def _get(url, **kwargs):
        chamado.update(url=url, kwargs=kwargs)
        return _RespostaCep({
            "cep": "14010-090",
            "logradouro": "Rua Tibiriçá",
            "complemento": "",
            "bairro": "Centro",
            "localidade": "Ribeirão Preto",
            "uf": "SP",
        })

    monkeypatch.setattr(httpx, "get", _get)
    resultado = consultar_cep("14010-090", _=object())

    assert chamado["url"] == "https://viacep.com.br/ws/14010090/json/"
    assert chamado["kwargs"]["follow_redirects"] is False
    assert resultado == {
        "cep": "14010-090",
        "logradouro": "Rua Tibiriçá",
        "complemento": "",
        "bairro": "Centro",
        "cidade": "Ribeirão Preto",
        "uf": "SP",
    }


def test_consulta_cep_invalido_falha_antes_da_rede(monkeypatch):
    monkeypatch.setattr(httpx, "get", lambda *_args, **_kwargs: pytest.fail("não deveria chamar a rede"))

    with pytest.raises(HTTPException) as erro:
        consultar_cep("123", _=object())

    assert erro.value.status_code == 422
