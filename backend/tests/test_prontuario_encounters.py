"""Núcleo de Encounter do Prontuário Eletrônico CorVIA.

Os invariantes mais importantes aqui são: tenant isolation, conteúdo clínico
cifrado em repouso, finalização imutável e correção somente por adendo.
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


class TestEncounterBasico:
    def test_cria_lista_le_e_cifra_conteudo(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _assinar(db, user)
        paciente = _paciente(client, token)
        criado = _atendimento(client, token, paciente["id"])

        assert criado["status"] == "draft"
        assert criado["chief_complaint"] == "Dor torácica aos esforços"
        assert criado["vital_signs"]["fc"] == 68

        row = db.get(ClinicalEncounter, criado["id"])
        assert row is not None
        assert row.chief_complaint_cifrado is not None
        assert b"Dor toracica" not in row.chief_complaint_cifrado
        assert b"Dor tor" not in row.chief_complaint_cifrado
        assert row.anamnesis_cifrado is not None
        assert b"Sintomas" not in row.anamnesis_cifrado
        assert row.vital_signs_cifrado is not None
        assert b"128" not in row.vital_signs_cifrado

        lista = client.get(
            f"/api/pacientes/{paciente['id']}/atendimentos",
            headers=_headers(token),
        )
        assert lista.status_code == 200
        assert [item["id"] for item in lista.json()] == [criado["id"]]

        detalhe = client.get(
            f"/api/pacientes/{paciente['id']}/atendimentos/{criado['id']}",
            headers=_headers(token),
        )
        assert detalhe.status_code == 200
        assert detalhe.json()["assessment"] == "Dor torácica em investigação."

        acoes = {
            row.action for row in db.query(AuditLog).filter(AuditLog.user_id == user.id).all()
        }
        assert "create_clinical_encounter" in acoes
        assert "list_clinical_encounters" in acoes
        assert "read_clinical_encounter" in acoes

    def test_edita_rascunho_e_finaliza_idempotente(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _assinar(db, user)
        paciente = _paciente(client, token)
        criado = _atendimento(client, token, paciente["id"])

        editado = client.patch(
            f"/api/pacientes/{paciente['id']}/atendimentos/{criado['id']}",
            headers=_headers(token),
            json={"status": "in_progress", "plan": "Plano revisado."},
        )
        assert editado.status_code == 200, editado.text
        assert editado.json()["status"] == "in_progress"
        assert editado.json()["plan"] == "Plano revisado."

        finalizado = client.post(
            f"/api/pacientes/{paciente['id']}/atendimentos/{criado['id']}/finalizar",
            headers=_headers(token),
        )
        assert finalizado.status_code == 200
        assert finalizado.json()["status"] == "finalized"
        assert finalizado.json()["finalized_at"] is not None

        novamente = client.post(
            f"/api/pacientes/{paciente['id']}/atendimentos/{criado['id']}/finalizar",
            headers=_headers(token),
        )
        assert novamente.status_code == 200
        assert novamente.json()["finalized_at"] == finalizado.json()["finalized_at"]

    def test_finalizado_nao_pode_ser_sobrescrito_e_aceita_adendo(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _assinar(db, user)
        paciente = _paciente(client, token)
        original = _atendimento(client, token, paciente["id"])
        client.post(
            f"/api/pacientes/{paciente['id']}/atendimentos/{original['id']}/finalizar",
            headers=_headers(token),
        )

        bloqueado = client.patch(
            f"/api/pacientes/{paciente['id']}/atendimentos/{original['id']}",
            headers=_headers(token),
            json={"assessment": "Tentativa de reescrever histórico."},
        )
        assert bloqueado.status_code == 409

        sem_motivo = client.post(
            f"/api/pacientes/{paciente['id']}/atendimentos",
            headers=_headers(token),
            json={"amendment_of_id": original["id"], "assessment": "Correção."},
        )
        assert sem_motivo.status_code == 422

        adendo = client.post(
            f"/api/pacientes/{paciente['id']}/atendimentos",
            headers=_headers(token),
            json={
                "amendment_of_id": original["id"],
                "amendment_reason": "Correção de informação registrada na evolução.",
                "assessment": "Informação corrigida em adendo, preservando o original.",
            },
        )
        assert adendo.status_code == 201, adendo.text
        assert adendo.json()["encounter_type"] == "adendo"
        assert adendo.json()["amendment_of_id"] == original["id"]
        assert "Correção de informação" in adendo.json()["amendment_reason"]

    def test_paciente_com_prontuario_nao_e_apagado_fisicamente(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _assinar(db, user)
        paciente = _paciente(client, token)
        _atendimento(client, token, paciente["id"])

        resposta = client.delete(
            f"/api/pacientes/{paciente['id']}", headers=_headers(token)
        )
        assert resposta.status_code == 409
        assert client.get(
            f"/api/pacientes/{paciente['id']}", headers=_headers(token)
        ).status_code == 200


class TestIsolamentoEncounter:
    def test_outro_medico_nao_consegue_enumerar_prontuario(self, client, db, criar_usuario):
        medico_a, token_a = criar_usuario(email="medico-a-prontuario@teste.local")
        medico_b, token_b = criar_usuario(email="medico-b-prontuario@teste.local")
        _assinar(db, medico_a)
        _assinar(db, medico_b)

        paciente_a = _paciente(client, token_a, "Paciente exclusivo A")
        encontro_a = _atendimento(client, token_a, paciente_a["id"])

        assert client.get(
            f"/api/pacientes/{paciente_a['id']}/atendimentos",
            headers=_headers(token_b),
        ).status_code == 404
        assert client.get(
            f"/api/pacientes/{paciente_a['id']}/atendimentos/{encontro_a['id']}",
            headers=_headers(token_b),
        ).status_code == 404
        assert client.patch(
            f"/api/pacientes/{paciente_a['id']}/atendimentos/{encontro_a['id']}",
            headers=_headers(token_b),
            json={"plan": "intrusão"},
        ).status_code == 404
        assert client.post(
            f"/api/pacientes/{paciente_a['id']}/atendimentos/{encontro_a['id']}/finalizar",
            headers=_headers(token_b),
        ).status_code == 404
