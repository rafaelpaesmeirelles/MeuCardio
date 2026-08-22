"""Um cenário integrado cobre resumo, resultados e timeline longitudinal."""
from datetime import datetime

from app.models.lab_test import LabTest
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
    catalogo = db.query(LabTest).filter_by(slug="troponina-i-teste-longitudinal").one_or_none()
    if catalogo is None:
        catalogo = LabTest(
            slug="troponina-i-teste-longitudinal", name="Troponina I", category="laboratorial",
            what_it_measures="Lesão miocárdica", indications="Suspeita de SCA",
            interpretation="Interpretar no contexto clínico", theme="biomarcadores",
            tags=[], source_refs=[], published=True,
        )
        db.add(catalogo)
    catalogo.published = True
    db.commit()
    db.refresh(catalogo)
    troponina = client.post(
        resultados, headers=_h(token),
        json={
            "exam_kind": "laboratorial", "exam_name": "Troponina I", "structured_result": "12",
            "unit": "ng/L", "reference_range": "< 19", "notes": "Amostra sem hemólise",
            "source": "Laboratório externo", "lab_test_id": catalogo.id,
            "source_encounter_id": eid, "performed_at": "2026-08-22T10:00:00-03:00",
        },
    )
    assert troponina.status_code == 201
    rid = troponina.json()["id"]
    db.expire_all()
    resultado_row = db.get(PatientExamResult, rid)
    assert resultado_row is not None and resultado_row.payload_cifrado
    assert resultado_row.patient_profile_id == pid and resultado_row.author_id == medico.id
    assert resultado_row.source_encounter_id == eid and resultado_row.lab_test_id == catalogo.id
    assert all(term not in resultado_row.payload_cifrado for term in (b"Troponina", b"Amostra", b"Laborat"))

    lista_resultados = client.get(resultados, headers=_h(token))
    assert lista_resultados.status_code == 200 and lista_resultados.json()[0]["exam_name"] == "Troponina I"
    assert lista_resultados.json()[0]["structured_result"] == "12"
    assert lista_resultados.json()[0]["lab_test_slug"] == catalogo.slug
    assert lista_resultados.json()[0]["source"] == "Laboratório externo"
    detalhe = client.get(f"{resultados}/{rid}", headers=_h(token))
    assert detalhe.status_code == 200 and detalhe.json()["result"]["notes"] == "Amostra sem hemólise"
    assert client.get(resultados, headers=_h(token_intruso)).status_code == 404
    assert client.get(f"{resultados}/{rid}", headers=_h(token_intruso)).status_code == 404

    ecg = client.post(
        resultados, headers=_h(token),
        json={
            "exam_kind": "metodo_grafico", "exam_name": "ECG",
            "report_text": "Ritmo sinusal. Sem alterações isquêmicas agudas.",
            "source": "Clínica", "performed_at": "2026-08-21T09:00:00-03:00",
        },
    )
    assert ecg.status_code == 201
    assert ecg.json()["structured_result"] is None
    assert ecg.json()["report_text"].startswith("Ritmo sinusal")

    correcao = client.post(
        f"{resultados}/{rid}/correcoes", headers=_h(token),
        json={
            "exam_kind": "laboratorial", "exam_name": "Troponina I", "structured_result": "13", "unit": "ng/L",
            "reference_range": "< 19", "source": "Laboratório externo", "lab_test_id": catalogo.id,
            "correction_reason": "Correção do valor transcrito", "source_encounter_id": eid,
            "performed_at": "2026-08-22T10:00:00-03:00",
        },
    )
    assert correcao.status_code == 201
    assert correcao.json()["correction_of_id"] == rid
    atualizados = client.get(resultados, headers=_h(token)).json()
    assert len(atualizados) == 3
    original = next(item for item in atualizados if item["id"] == rid)
    assert original["is_superseded"] is True and original["corrected_by_id"] == correcao.json()["id"]
    historico_correcao = client.get(f"{resultados}/{correcao.json()['id']}", headers=_h(token))
    assert [item["id"] for item in historico_correcao.json()["history"]] == [rid, correcao.json()["id"]]
    assert historico_correcao.json()["history"][1]["correction_reason"] == "Correção do valor transcrito"
    assert client.post(
        f"{resultados}/{rid}/correcoes", headers=_h(token),
        json={"exam_name": "Troponina I", "structured_result": "14", "correction_reason": "Nova tentativa"},
    ).status_code == 409
    assert client.post(
        f"{resultados}/{rid}/correcoes", headers=_h(token_intruso),
        json={"exam_name": "Troponina I", "structured_result": "99", "correction_reason": "Acesso indevido"},
    ).status_code == 404

    timeline = client.get(f"/api/pacientes/{pid}/linha-do-tempo", headers=_h(token))
    assert timeline.status_code == 200
    tipos = {evento["tipo"] for evento in timeline.json()}
    assert {"atendimento", "problema", "alergia", "medicacao", "resultado_exame"}.issubset(tipos)
    assert any(evento["titulo"] == "Medicação inativada" for evento in timeline.json())
    assert any(evento["titulo"] == "Correção de resultado" for evento in timeline.json())
    eventos_exame = [evento for evento in timeline.json() if evento["tipo"] == "resultado_exame"]
    assert any(evento["source"] == "Laboratório externo" and evento["lab_test_id"] == catalogo.id for evento in eventos_exame)
    original_timeline = next(evento for evento in eventos_exame if evento["exam_result_id"] == rid)
    assert original_timeline["status"] == "substituido"
    assert original_timeline["is_superseded"] is True
    assert original_timeline["corrected_by_id"] == correcao.json()["id"]
    datas = [datetime.fromisoformat(evento["data"]) for evento in timeline.json()]
    assert datas == sorted(datas, reverse=True)
    assert client.get(f"/api/pacientes/{pid}/linha-do-tempo", headers=_h(token_intruso)).status_code == 404

    # Qualquer dado longitudinal torna o cadastro parte do prontuário e impede deleção física.
    assert client.delete(f"/api/pacientes/{pid}", headers=_h(token)).status_code == 409
    so_exame = client.post("/api/pacientes", headers=_h(token), json={"full_name": "Paciente Só Exame"})
    pid_so_exame = so_exame.json()["id"]
    assert client.post(
        f"/api/pacientes/{pid_so_exame}/resultados", headers=_h(token),
        json={"exam_kind": "metodo_grafico", "exam_name": "ECG", "report_text": "Ritmo sinusal"},
    ).status_code == 201
    assert client.delete(f"/api/pacientes/{pid_so_exame}", headers=_h(token)).status_code == 409
