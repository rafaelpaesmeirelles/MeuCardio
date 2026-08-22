"""Cobertura mínima do núcleo do Prontuário Eletrônico CorVIA.

Somente três blocos de invariantes: fluxo básico + cifragem/auditoria,
ciclo de finalização/adendo/preservação e isolamento entre médicos.
"""
from app.models.audit import AuditLog
from app.models.prontuario import ClinicalEncounter
from app.models.subscription import Subscription


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _assinar(db, user) -> None:
    db.add(Subscription(user_id=user.id, kind="meucardio", plano="basico", status="ativo"))
    db.commit()


def _paciente(client, token: str, nome: str = "Paciente do Prontuário") -> dict:
    resposta = client.post(
        "/api/pacientes",
        headers=_headers(token),
        json={"full_name": nome, "birth_date": "1970-01-02", "sex": "M"},
    )
    assert resposta.status_code == 201, resposta.text
    return resposta.json()


def _atendimento(client, token: str, pid: int, **overrides) -> dict:
    payload = {
        "encounter_type": "consulta",
        "chief_complaint": "Dor torácica aos esforços",
        "anamnesis": "Sintomas há duas semanas.",
        "physical_exam": "Sem sinais de congestão.",
        "assessment": "Dor torácica em investigação.",
        "plan": "Prosseguir investigação dirigida.",
        "vital_signs": {"pa_sistolica": 128, "pa_diastolica": 78, "fc": 68},
    }
    payload.update(overrides)
    resposta = client.post(
        f"/api/pacientes/{pid}/atendimentos",
        headers=_headers(token),
        json=payload,
    )
    assert resposta.status_code == 201, resposta.text
    return resposta.json()


def test_fluxo_basico_cifra_e_audita(client, db, criar_usuario):
    user, token = criar_usuario()
    _assinar(db, user)
    paciente = _paciente(client, token)
    criado = _atendimento(client, token, paciente["id"])

    row = db.get(ClinicalEncounter, criado["id"])
    assert criado["status"] == "draft"
    assert criado["vital_signs"]["fc"] == 68
    assert row is not None
    assert row.chief_complaint_cifrado is not None and b"Dor tor" not in row.chief_complaint_cifrado
    assert row.anamnesis_cifrado is not None and b"Sintomas" not in row.anamnesis_cifrado
    assert row.vital_signs_cifrado is not None and b"128" not in row.vital_signs_cifrado

    lista = client.get(f"/api/pacientes/{paciente['id']}/atendimentos", headers=_headers(token))
    detalhe = client.get(
        f"/api/pacientes/{paciente['id']}/atendimentos/{criado['id']}", headers=_headers(token)
    )
    assert lista.status_code == 200 and [x["id"] for x in lista.json()] == [criado["id"]]
    assert detalhe.status_code == 200 and detalhe.json()["assessment"] == "Dor torácica em investigação."

    acoes = {x.action for x in db.query(AuditLog).filter(AuditLog.user_id == user.id).all()}
    assert {"create_clinical_encounter", "read_clinical_encounter"}.issubset(acoes)


def test_finalizacao_adendo_e_preservacao_do_historico(client, db, criar_usuario):
    user, token = criar_usuario()
    _assinar(db, user)
    paciente = _paciente(client, token)
    original = _atendimento(client, token, paciente["id"])

    editado = client.patch(
        f"/api/pacientes/{paciente['id']}/atendimentos/{original['id']}",
        headers=_headers(token), json={"status": "in_progress", "plan": "Plano revisado."},
    )
    assert editado.status_code == 200 and editado.json()["plan"] == "Plano revisado."

    finalizar_url = f"/api/pacientes/{paciente['id']}/atendimentos/{original['id']}/finalizar"
    finalizado = client.post(finalizar_url, headers=_headers(token))
    repetido = client.post(finalizar_url, headers=_headers(token))
    assert finalizado.status_code == 200 and finalizado.json()["status"] == "finalized"
    assert repetido.status_code == 200 and repetido.json()["finalized_at"] == finalizado.json()["finalized_at"]

    bloqueado = client.patch(
        f"/api/pacientes/{paciente['id']}/atendimentos/{original['id']}",
        headers=_headers(token), json={"assessment": "Tentativa de reescrever histórico."},
    )
    assert bloqueado.status_code == 409

    adendo = client.post(
        f"/api/pacientes/{paciente['id']}/atendimentos",
        headers=_headers(token),
        json={
            "amendment_of_id": original["id"],
            "amendment_reason": "Correção de informação registrada.",
            "assessment": "Informação corrigida em adendo.",
        },
    )
    assert adendo.status_code == 201
    assert adendo.json()["encounter_type"] == "adendo"
    assert adendo.json()["amendment_of_id"] == original["id"]

    assert client.delete(f"/api/pacientes/{paciente['id']}", headers=_headers(token)).status_code == 409


def test_isolamento_entre_medicos(client, db, criar_usuario):
    medico_a, token_a = criar_usuario(email="medico-a-prontuario@teste.local")
    medico_b, token_b = criar_usuario(email="medico-b-prontuario@teste.local")
    _assinar(db, medico_a)
    _assinar(db, medico_b)
    paciente_a = _paciente(client, token_a, "Paciente exclusivo A")
    encontro_a = _atendimento(client, token_a, paciente_a["id"])

    assert client.get(
        f"/api/pacientes/{paciente_a['id']}/atendimentos", headers=_headers(token_b)
    ).status_code == 404
    assert client.patch(
        f"/api/pacientes/{paciente_a['id']}/atendimentos/{encontro_a['id']}",
        headers=_headers(token_b), json={"plan": "intrusão"},
    ).status_code == 404
