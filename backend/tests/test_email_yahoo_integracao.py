"""Contrato de retirada da integração Yahoo do produto."""

from app.models.agenda import CalendarIntegration


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_conectar_yahoo_nao_esta_mais_disponivel(client, db, criar_usuario):
    user, token = criar_usuario(email="sem-yahoo@teste.local")

    resposta = client.post(
        "/api/email/conectar-yahoo",
        json={
            "endereco": "titular@yahoo.com",
            "senha_de_app": "abcd1234",
            "consent_accepted": True,
        },
        headers=_headers(token),
    )

    assert resposta.status_code == 410
    assert "não está mais disponível" in resposta.json()["detail"]
    assert db.query(CalendarIntegration).filter(
        CalendarIntegration.owner_id == user.id,
        CalendarIntegration.provider == "yahoo_mail",
    ).count() == 0
