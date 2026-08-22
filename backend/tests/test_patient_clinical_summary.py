"""Um único cenário integrado cobre resumo clínico e timeline longitudinal."""
from app.models.prontuario import PatientClinicalItem
from app.models.subscription import Subscription


def _h(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _assinar(db, *users) -> None:
    db.add_all([Subscription(user_id=u.id, kind="meucardio", plano="basico", status="ativo") for u in users])
    db.commit()


def test_resumo_clinico_cifra_preserva_historico_e_isola_medicos(client, db, criar_usuario):
    medico, token = criar_usuario(email="resumo-a@teste.local")
    intruso, token_intruso = criar_usuario(email="resumo-b@teste.local")
    _assinar(db, medico, intruso)

    perfil = client.post("/api/pacientes", headers=_h(token), json={"full_name": "Paciente Resumo"})
    assert perfil.status_code == 201
    pid = perfil.json()["id"]
    atendimento = client.post(
        f"/api/pacientes/{pid}/atendimentos", headers=_h(token),
        json={"encounter_type": "consulta", "chief_complaint": "Retorno"},
    )
    assert atendimento.status_code == 201
    eid = atendimento.json()["id"]

    base = f"/api/pacientes/{pid}/resumo-clinico"
    problema = client.post(base, headers=_h(token), json={"kind": "problema", "name": "Hipertensão arterial"})
    alergia = client.post(base, headers=_h(token), json={"kind": "alergia", "name": "Penicilina", "details": "Urticária"})
    medicacao = client.post(
        base, headers=_h(token),
        json={"kind": "medicacao", "name": "Losartana", "details": "Uso contínuo", "source_encounter_id": eid},
    )
    assert problema.status_code == alergia.status_code == medicacao.status_code == 201

    db.expire_all()
    row = db.get(PatientClinicalItem, problema.json()["id"])
    assert row is not None and row.payload_cifrado
    assert b"Hipertens" not in row.payload_cifrado

    ativos = client.get(base, headers=_h(token))
    assert ativos.status_code == 200
    assert {x["kind"] for x in ativos.json()} == {"problema", "alergia", "medicacao"}
    assert client.get(base, headers=_h(token_intruso)).status_code == 404

    inativado = client.post(f"{base}/{medicacao.json()['id']}/inativar", headers=_h(token))
    assert inativado.status_code == 200
    assert inativado.json()["is_active"] is False and inativado.json()["ended_at"]
    assert len(client.get(base, headers=_h(token)).json()) == 2
    historico = client.get(f"{base}?incluir_inativos=true", headers=_h(token))
    assert historico.status_code == 200 and len(historico.json()) == 3

    timeline = client.get(f"/api/pacientes/{pid}/linha-do-tempo", headers=_h(token))
    assert timeline.status_code == 200
    tipos = {evento["tipo"] for evento in timeline.json()}
    assert {"atendimento", "problema", "alergia", "medicacao"}.issubset(tipos)
    assert any(evento["titulo"] == "Medicação inativada" for evento in timeline.json())
    assert client.get(f"/api/pacientes/{pid}/linha-do-tempo", headers=_h(token_intruso)).status_code == 404

    # Um resumo clínico já torna o cadastro parte do prontuário e impede deleção física.
    assert client.delete(f"/api/pacientes/{pid}", headers=_h(token)).status_code == 409
