"""No database writes or email transport when issuance/signing is incomplete."""
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.api import documents, receituario


@pytest.mark.parametrize("emission", [None,
    SimpleNamespace(metodo="GOVBR", assinado_em=None),
    SimpleNamespace(metodo="A1_ARQUIVO", assinado_em=None),
])
def test_email_rejects_unissued_or_unsigned_document_before_side_effects(monkeypatch, emission):
    doc = SimpleNamespace(id=20, created_by=7)
    db = SimpleNamespace(get=lambda *_: doc)
    monkeypatch.setattr(documents.assinatura_emissao, "buscar", lambda *a, **kw: emission)
    with pytest.raises(HTTPException) as error:
        documents.enviar_email_gerado(20, documents.EnviarEmailIn(email="paciente@teste.local"),
                                      db=db, user=SimpleNamespace(id=7))
    assert error.value.status_code == 409
    assert not hasattr(doc, "destinatario_email_cifrado")


def test_dosage_and_orientation_survive_resolution_and_immutable_snapshot():
    original = receituario.ItemIn(descricao="Item de demonstração", posologia="Texto de posologia.",
                                 orientacao="Orientação complementar.\nSegunda linha.")
    resolved = receituario._resolver(SimpleNamespace(), [original])[0]
    snapshot = receituario._item_snapshot(resolved)
    assert snapshot["posologia"] == original.posologia
    assert snapshot["orientacao"] == original.orientacao
