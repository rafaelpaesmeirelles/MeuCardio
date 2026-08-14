"""Regressão P1: conta convertida em Investidor nunca lê Agenda histórica."""

from datetime import datetime, timedelta, timezone

from app.models.clinical_docs import Appointment
from app.services.investidor_demo import SENHA_FIXA_INVESTIDOR


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _login_investidor(client, email: str) -> str:
    resposta = client.post(
        "/api/auth/login",
        data={"username": email, "password": SENHA_FIXA_INVESTIDOR},
    )
    assert resposta.status_code == 200, resposta.text
    payload = resposta.json()
    return payload.get("access_token") or payload.get("token")


def test_conversao_para_investidor_esconde_agendamento_local_real(
    client, criar_usuario, db
):
    user, _ = criar_usuario(email="convertido.agenda@teste.local")
    inicio = datetime.now(timezone.utc) + timedelta(days=1)
    db.add(Appointment(
        owner_id=user.id,
        patient_name_temp="PACIENTE REAL QUE NAO PODE VAZAR",
        patient_phone_temp="16999999999",
        scheduled_at=inicio,
        ends_at=inicio + timedelta(minutes=30),
        notes="PHI REAL ANTIGA",
        source="corvia",
        integration_id=None,  # caso que escapava da quarentena de integrações
    ))
    db.commit()

    user.investidor = True
    db.commit()
    db.refresh(user)

    token = _login_investidor(client, user.email)
    resposta = client.get("/api/agenda/appointments", headers=_headers(token))
    assert resposta.status_code == 200, resposta.text
    corpo = resposta.json()
    serializado = str(corpo)
    assert "PACIENTE REAL QUE NAO PODE VAZAR" not in serializado
    assert "PHI REAL ANTIGA" not in serializado
    assert "16999999999" not in serializado
    assert corpo
    assert corpo[0]["patient_name"] == "Paciente demonstrativo"
    assert corpo[0]["id"] < 0


def test_investidor_agenda_get_novo_nao_catalogado_falha_fechado(
    client, criar_usuario, db
):
    user, _ = criar_usuario(email="investidor.agenda.unknown@teste.local")
    user.investidor = True
    db.commit()
    token = _login_investidor(client, user.email)

    resposta = client.get("/api/agenda/rota-futura-nao-catalogada", headers=_headers(token))
    assert resposta.status_code == 403


def test_flags_de_ux_do_investidor_simulam_sucesso_sem_persistir(
    client, criar_usuario, db
):
    user, _ = criar_usuario(email="investidor.ux@teste.local")
    user.investidor = True
    db.commit()
    db.refresh(user)
    assert user.onboarding_visto is False

    token = _login_investidor(client, user.email)
    resposta = client.post("/api/auth/me/onboarding-concluido", headers=_headers(token))
    assert resposta.status_code == 200
    assert resposta.json() == {"onboarding_pendente": False}

    db.expire_all()
    persistido = db.get(type(user), user.id)
    assert persistido.onboarding_visto is False
