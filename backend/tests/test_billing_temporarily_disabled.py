import pytest

from app.api import billing
from app.core.config import settings


@pytest.mark.parametrize(
    "path",
    [
        "/api/billing/checkout?plano=basico&periodicidade=mensal",
        "/api/billing/checkout-email",
        "/api/billing/trocar-plano?plano=completo&periodicidade=anual",
    ],
)
def test_novas_assinaturas_e_trocas_ficam_bloqueadas_sem_chamar_stripe(
    client, criar_usuario, monkeypatch, path,
):
    _, token = criar_usuario(email="assinatura-pausada@teste.local")
    monkeypatch.setattr(settings, "subscriptions_enabled", False)
    monkeypatch.setattr(
        billing.stripe.Customer,
        "create",
        lambda **_: pytest.fail("Stripe não pode ser chamado durante a pausa comercial."),
    )

    resposta = client.post(path, headers={"Authorization": f"Bearer {token}"})

    assert resposta.status_code == 503
    assert resposta.json()["detail"] == (
        "Assinaturas temporariamente indisponíveis. Conheça o CorVIA no tour."
    )


def test_status_da_assinatura_continua_disponivel_durante_a_pausa(
    client, criar_usuario, monkeypatch,
):
    _, token = criar_usuario(email="status-assinatura@teste.local")
    monkeypatch.setattr(settings, "subscriptions_enabled", False)

    resposta = client.get(
        "/api/billing/status",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resposta.status_code == 200
