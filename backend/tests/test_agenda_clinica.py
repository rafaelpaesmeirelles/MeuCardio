"""Um único cenário integrado para os invariantes críticos Agenda -> Prontuário."""
from datetime import datetime, timezone

from app.models.clinical_docs import Appointment
from app.models.prontuario import ClinicalEncounter
from app.models.subscription import Subscription


def _h(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _assinar(db, *users) -> None:
    db.add_all([Subscription(user_id=u.id, kind="meucardio", plano="basico", status="ativo") for u in users])
    db.commit()


def test_sala_espera_vincula_inicia_conclui_e_isola_tenant(client, db, criar_usuario):
    medico, token = criar_usuario(email="agenda-clinica-a@teste.local")
    intruso, token_intruso = criar_usuario(email="agenda-clinica-b@teste.local")
    _assinar(db, medico, intruso)

    perfil = client.post(
        "/api/pacientes",
        headers=_h(token),
        json={"full_name": "Paciente Agenda Clínica", "birth_date": "1970-01-02", "sex": "F"},
    )
    assert perfil.status_code == 201, perfil.text
    pid = perfil.json()["id"]

    appointment = Appointment(
        owner_id=medico.id,
        patient_name_temp="Paciente da agenda",
        scheduled_at=datetime.now(timezone.utc),
        duration_minutes=30,
        appointment_type="consulta",
        status="confirmado",
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    fila = client.get("/api/agenda-clinica/hoje", headers=_h(token))
    assert fila.status_code == 200
    assert [x["appointment_id"] for x in fila.json()] == [appointment.id]

    vinculo = client.post(
        f"/api/agenda-clinica/{appointment.id}/vincular",
        headers=_h(token), json={"patient_profile_id": pid},
    )
    assert vinculo.status_code == 200 and vinculo.json()["patient_profile_id"] == pid

    for action, expected in (("arrive", "arrived"), ("call", "called"), ("start", "in_service")):
        resposta = client.post(
            f"/api/agenda-clinica/{appointment.id}/transicao",
            headers=_h(token), json={"action": action},
        )
        assert resposta.status_code == 200, resposta.text
        assert resposta.json()["state"] == expected

    encounter_id = resposta.json()["encounter_id"]
    repetido = client.post(
        f"/api/agenda-clinica/{appointment.id}/transicao",
        headers=_h(token), json={"action": "start"},
    )
    assert repetido.status_code == 200 and repetido.json()["encounter_id"] == encounter_id
    assert db.query(ClinicalEncounter).filter(ClinicalEncounter.appointment_id == appointment.id).count() == 1

    prematuro = client.post(
        f"/api/agenda-clinica/{appointment.id}/transicao",
        headers=_h(token), json={"action": "complete"},
    )
    assert prematuro.status_code == 409

    finalizado = client.post(
        f"/api/pacientes/{pid}/atendimentos/{encounter_id}/finalizar",
        headers=_h(token),
    )
    assert finalizado.status_code == 200
    concluido = client.post(
        f"/api/agenda-clinica/{appointment.id}/transicao",
        headers=_h(token), json={"action": "complete"},
    )
    assert concluido.status_code == 200 and concluido.json()["state"] == "completed"
    db.refresh(appointment)
    assert appointment.status == "realizado"

    assert client.get("/api/agenda-clinica/hoje", headers=_h(token_intruso)).json() == []
    assert client.post(
        f"/api/agenda-clinica/{appointment.id}/transicao",
        headers=_h(token_intruso), json={"action": "arrive"},
    ).status_code == 404
