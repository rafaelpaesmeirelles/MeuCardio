"""Controle administrativo de recuperação e e-mail transacional."""

from app.api import account_access_admin
from app.services import account_recovery


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_aprovacao_pela_rota_historica_dispara_notificacao_segura(
    client, criar_usuario, db, monkeypatch
):
    pendente, _ = criar_usuario(email="pendente.aprovacao@teste.local")
    pendente.status = "pendente"
    pendente.is_active = False
    db.commit()
    _, admin_token = criar_usuario(email="admin.aprovacao@teste.local", role="admin")

    enviados: list[int] = []
    monkeypatch.setattr(
        account_recovery,
        "enviar_acesso_aprovado",
        lambda user_id: enviados.append(user_id) or True,
    )

    resposta = client.post(
        f"/api/admin/users/{pendente.id}/decidir",
        json={"aprovar": True, "role": "medico", "nota": "Registro conferido"},
        headers=_headers(admin_token),
    )
    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["status"] == "aprovado"
    assert enviados == [pendente.id]


def test_email_status_nao_expoe_credenciais(client, criar_usuario):
    _, admin_token = criar_usuario(email="admin.smtp.status@teste.local", role="admin")
    resposta = client.get(
        "/api/admin/account-access/email-status",
        headers=_headers(admin_token),
    )
    assert resposta.status_code == 200, resposta.text
    payload = resposta.json()
    serializado = str(payload).lower()
    for segredo in (
        "smtp_password",
        "mail360_client_secret",
        "mail360_refresh_token",
        "mail360_transactional_account_key",
        "access_token",
    ):
        assert segredo not in serializado
    assert "password" not in serializado
    assert "email_transacional_configurado" in payload
    assert "email_transacional_provider" in payload
    assert "mail360_configurado" in payload
    assert "mail360_transacional_configurado" in payload
    # Mantidos por compatibilidade com versões anteriores do painel.
    assert "smtp_user_canonico" in payload
    assert "smtp_from_canonico" in payload


def test_email_probe_funciona_com_provider_mail360_sem_smtp(
    client, criar_usuario, monkeypatch
):
    _, admin_token = criar_usuario(email="admin.mail360.probe@teste.local", role="admin")
    settings = account_access_admin.settings
    monkeypatch.setattr(settings, "email_transacional_provider", "mail360")
    monkeypatch.setattr(settings, "mail360_client_id", "client-id-teste")
    monkeypatch.setattr(settings, "mail360_client_secret", "client-secret-teste")
    monkeypatch.setattr(settings, "mail360_refresh_token", "refresh-token-teste")
    monkeypatch.setattr(settings, "mail360_transactional_account_key", "account-key-teste")
    monkeypatch.setattr(settings, "smtp_host", "")
    monkeypatch.setattr(settings, "smtp_user", "")
    monkeypatch.setattr(settings, "smtp_password", "")
    monkeypatch.setattr(
        account_recovery,
        "enviar_teste_transacional",
        lambda email, admin_id: True,
    )

    resposta = client.post(
        "/api/admin/account-access/email-probe",
        json={"email": "externo@teste.local"},
        headers=_headers(admin_token),
    )
    assert resposta.status_code == 200, resposta.text
    payload = resposta.json()
    assert payload == {
        "ok": True,
        "provider": "mail360",
        "remetente": "contato@corvia.med.br",
    }


def test_admin_reset_exige_segundo_canal(client, criar_usuario):
    alvo, _ = criar_usuario(email="sem.segundo.canal@corvia.med.br")
    _, admin_token = criar_usuario(email="admin.reset.seguro@teste.local", role="admin")
    resposta = client.post(
        f"/api/admin/users/{alvo.id}/enviar-recuperacao",
        headers=_headers(admin_token),
    )
    assert resposta.status_code == 409
