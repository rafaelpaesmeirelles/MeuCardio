"""app/services/pricing/bps_provider.py — camada institucional (BPS) da
arquitetura multi-fonte de preços (issue #52).

Nunca faz chamada de rede real nos testes — o cliente HTTP é sempre
mockado (mesmo padrão de test_instagram_handle.py), mesmo o endpoint real
tendo sido confirmado funcionando ao vivo nesta sessão.
"""
from datetime import datetime, timezone
from decimal import Decimal

import httpx
import pytest
from sqlalchemy import text

from app.models.drug import Drug
from app.services.pricing import bps_provider as bps_mod
from app.services.pricing.bps_provider import BPSProvider


@pytest.fixture(autouse=True)
def _limpar_drugs(db):
    # `drugs` é tabela de conteúdo, não coberta pelo `_banco_limpo` autouse
    # do conftest — mesmo padrão de test_pricing_cmed_provider.py.
    db.execute(text("TRUNCATE drugs RESTART IDENTITY CASCADE"))
    db.commit()
    yield


def _drug(db, slug="losartana-potassica-teste-bps") -> Drug:
    d = Drug(slug=slug, generic_name="Losartana potássica", drug_class="BRA", published=True)
    db.add(d)
    db.commit()
    db.refresh(d)
    return d


class _RespostaFalsa:
    def __init__(self, corpo: dict, status_code: int = 200):
        self._corpo = corpo
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("erro", request=None, response=self)

    def json(self):
        return self._corpo


def test_farmaco_fora_do_crosswalk_devolve_lista_vazia_sem_chamar_rede(db, monkeypatch):
    chamou = {"vezes": 0}
    monkeypatch.setattr(bps_mod.httpx, "get", lambda *a, **k: chamou.__setitem__("vezes", chamou["vezes"] + 1))
    d = _drug(db, slug="farmaco-sem-catmat-teste")
    resultado = BPSProvider(db).observations_for(d.id)
    assert resultado == []
    assert chamou["vezes"] == 0, "não deveria nem tentar chamar a API sem CATMAT conhecido"


def test_farmaco_no_crosswalk_traduz_resposta_real_para_price_observation(db, monkeypatch):
    corpo = {
        "bps": [
            {
                "anoCompra": 2026, "nomeInstituicao": "FUNDO MUNICIPAL DE SAUDE - TESTE",
                "municipio": "TESTOPOLIS", "estado": "PB", "dataCompra": "2026-07-08",
                "codigoCatmat": "268856", "descricaoItem": "LOSARTANA POTÁSSICA, DOSAGEM:50 MG",
                "generico": True, "registroAnvisa": "1037005050027", "modalidade": "Pregão",
                "tipoCompra": "ADMINISTRATIVA", "nomeFornecedor": "FORNECEDOR TESTE",
                "nomeFabricante": "FABRICANTE TESTE", "quantidade": 9000, "precoUnitario": 0.05,
                "precoTotal": 450.0,
            },
        ],
    }
    monkeypatch.setattr(bps_mod.httpx, "get", lambda *a, **k: _RespostaFalsa(corpo))

    d = _drug(db, slug="losartana-potassica")  # bate o crosswalk verificado
    observacoes = BPSProvider(db).observations_for(d.id)

    assert len(observacoes) == 1
    obs = observacoes[0]
    assert obs.source == "bps"
    assert obs.source_type == "institutional"
    assert obs.price_type == "institutional_purchase"
    assert obs.price == Decimal("0.05")
    assert obs.presentation_ref == "268856"
    assert obs.region == "PB"
    assert obs.observed_at == datetime(2026, 7, 8, tzinfo=timezone.utc)
    assert "NÃO é preço de varejo" in obs.metadata["aviso"]
    assert obs.metadata["fabricante"] == "FABRICANTE TESTE"


def test_linha_sem_preco_unitario_e_descartada(db, monkeypatch):
    corpo = {"bps": [{"codigoCatmat": "268856", "dataCompra": "2026-01-01", "precoUnitario": None}]}
    monkeypatch.setattr(bps_mod.httpx, "get", lambda *a, **k: _RespostaFalsa(corpo))
    d = _drug(db, slug="losartana-potassica")
    assert BPSProvider(db).observations_for(d.id) == []


def test_falha_de_rede_devolve_lista_vazia_sem_lancar_excecao(db, monkeypatch):
    def _explode(*a, **k):
        raise httpx.ConnectError("timeout simulado")
    monkeypatch.setattr(bps_mod.httpx, "get", _explode)
    d = _drug(db, slug="losartana-potassica")
    assert BPSProvider(db).observations_for(d.id) == []


def test_erro_http_devolve_lista_vazia_sem_lancar_excecao(db, monkeypatch):
    monkeypatch.setattr(bps_mod.httpx, "get", lambda *a, **k: _RespostaFalsa({}, status_code=503))
    d = _drug(db, slug="losartana-potassica")
    assert BPSProvider(db).observations_for(d.id) == []


def test_farmaco_inexistente_devolve_lista_vazia(db, monkeypatch):
    monkeypatch.setattr(bps_mod.httpx, "get", lambda *a, **k: pytest.fail("não deveria chamar a rede"))
    assert BPSProvider(db).observations_for(999999) == []
