"""Regressão: o status editorial canônico precisa chegar ao Drug existente."""

import json
from types import SimpleNamespace

from app.services import carregar_drugs


class _Query:
    def __init__(self, existente):
        self.existente = existente

    def filter(self, *_args, **_kwargs):
        return self

    def first(self):
        return self.existente


class _DB:
    def __init__(self, existente):
        self.existente = existente
        self.commits = 0

    def query(self, _model):
        return _Query(self.existente)

    def add(self, _item):
        raise AssertionError("o cenário de regressão deve atualizar registro existente")

    def commit(self):
        self.commits += 1

    def close(self):
        pass


def test_atualizacao_propaga_review_status_pendente(monkeypatch, tmp_path):
    existente = SimpleNamespace(
        slug="farmaco-teste",
        generic_name="Fármaco antigo",
        review_status="revisado",
    )
    db = _DB(existente)
    monkeypatch.setattr(carregar_drugs, "SessionLocal", lambda: db)

    manifesto = tmp_path / "medicamentos.json"
    manifesto.write_text(json.dumps([{
        "slug": "farmaco-teste",
        "generic_name": "Fármaco atualizado",
        "review_status": "pendente_revisao",
    }]), encoding="utf-8")

    resultado = carregar_drugs.carregar(str(manifesto))

    assert resultado == {"total": 1, "novos": 0, "atualizados": 1}
    assert existente.generic_name == "Fármaco atualizado"
    assert existente.review_status == "pendente_revisao"
    assert db.commits == 1
