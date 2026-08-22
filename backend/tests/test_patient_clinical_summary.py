"""Um único cenário integrado cobre resumo clínico, resultados e timeline longitudinal."""
from app.models.prontuario import PatientClinicalItem, PatientExamResult
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

    resultados = f"/api/pacientes/{pid}/resultados"
    troponina = client.post(
        resultados, headers=_h(token),
        json={
            "exam_kind": "laboratorial", "exam_name": "Troponina I", "result": "12",
            "unit": "ng/L", "reference_range": "< 19", "notes": "Amostra sem hemólise",
            "source_encounter_id": eid,
        },
    )
    assert troponina.status_code == 201
    rid = troponina.json()["id"]
    db.expire_all()
    resultado_row = db.get(PatientExamResult, rid)
    assert resultado_row is not None and resultado_row.payload_cifrado
    assert b"Troponina" not in resultado_row.payload_cifrado and b"Amostra" not in resultado_row.payload_cifrado

    lista_resultados = client.get(resultados, headers=_h(token))
    assert lista_resultados.status_code == 200 and lista_resultados.json()[0]["exam_name"] == "Troponina I"
    assert client.get(resultados, headers=_h(token_intruso)).status_code == 404

    correcao = client.post(
        resultados, headers=_h(token),
        json={
            "exam_kind": "laboratorial", "exam_name": "Troponina I", "result": "13", "unit": "ng/L",
            "correction_of_id": rid, "correction_reason": "Correção do valor transcrito", "source_encounter_id": eid,
        },
    )
    assert correcao.status_code == 201
    assert correcao.json()["correction_of_id"] == rid
    assert len(client.get(resultados, headers=_h(token)).json()) == 2

    timeline = client.get(f"/api/pacientes/{pid}/linha-do-tempo", headers=_h(token))
    assert timeline.status_code == 200
    tipos = {evento["tipo"] for evento in timeline.json()}
    assert {"atendimento", "problema", "alergia", "medicacao", "resultado_exame"}.issubset(tipos)
    assert any(evento["titulo"] == "Medicação inativada" for evento in timeline.json())
    assert any(evento["titulo"] == "Correção de resultado" for evento in timeline.json())
    assert client.get(f"/api/pacientes/{pid}/linha-do-tempo", headers=_h(token_intruso)).status_code == 404

    # Qualquer dado longitudinal torna o cadastro parte do prontuário e impede deleção física.
    assert client.delete(f"/api/pacientes/{pid}", headers=_h(token)).status_code == 409
    so_exame = client.post("/api/pacientes", headers=_h(token), json={"full_name": "Paciente Só Exame"})
    pid_so_exame = so_exame.json()["id"]
    assert client.post(
        f"/api/pacientes/{pid_so_exame}/resultados", headers=_h(token),
        json={"exam_kind": "metodo_grafico", "exam_name": "ECG", "result": "Ritmo sinusal"},
    ).status_code == 201
    assert client.delete(f"/api/pacientes/{pid_so_exame}", headers=_h(token)).status_code == 409
