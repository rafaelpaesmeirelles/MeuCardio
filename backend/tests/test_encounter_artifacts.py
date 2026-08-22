"""Um cenário integrado cobre o contrato mínimo de artefatos do Encounter."""
from app.models.clinical_docs import GeneratedDocument, Prescription
from app.models.receituario import PrescriptionRecipient
from app.models.subscription import Subscription
from app.services import cofre


def _h(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _assinar(db, *users) -> None:
    db.add_all([Subscription(user_id=u.id, kind="meucardio", plano="basico", status="ativo") for u in users])
    db.commit()


def _prescricao(db, medico_id: int, nome: str) -> Prescription:
    row = Prescription(created_by=medico_id, items=[], notes=None)
    db.add(row); db.flush()
    db.add(PrescriptionRecipient(
        prescription_id=row.id,
        nome_cifrado=cofre.cifrar_campo(nome, row.id),
    ))
    db.commit(); db.refresh(row)
    return row


def test_encounter_vincula_prescricao_documento_idempotente_e_isola_tenant(client, db, criar_usuario):
    medico, token = criar_usuario(email="artefatos-a@teste.local")
    intruso, token_intruso = criar_usuario(email="artefatos-b@teste.local")
    _assinar(db, medico, intruso)

    perfil = client.post("/api/pacientes", headers=_h(token), json={"full_name": "Paciente Artefatos"})
    assert perfil.status_code == 201
    pid = perfil.json()["id"]
    atendimento = client.post(
        f"/api/pacientes/{pid}/atendimentos", headers=_h(token),
        json={"encounter_type": "consulta", "chief_complaint": "Retorno"},
    )
    assert atendimento.status_code == 201
    eid = atendimento.json()["id"]

    prescricao = _prescricao(db, medico.id, "Paciente Artefatos")
    documento = GeneratedDocument(
        created_by=medico.id, doc_type="atestado", title="Atestado",
        rendered_body="Conteúdo", patient_profile_id=pid,
    )
    db.add(documento); db.commit(); db.refresh(documento)

    base = f"/api/pacientes/{pid}/atendimentos/{eid}/artefatos"
    p = client.post(base, headers=_h(token), json={"tipo": "prescricao", "artifact_id": prescricao.id})
    d = client.post(base, headers=_h(token), json={"tipo": "documento", "artifact_id": documento.id})
    assert p.status_code == 201 and d.status_code == 201
    repetido = client.post(base, headers=_h(token), json={"tipo": "prescricao", "artifact_id": prescricao.id})
    assert repetido.status_code == 201 and repetido.json()["id"] == p.json()["id"]

    errada = _prescricao(db, medico.id, "Outro Paciente")
    assert client.post(
        base, headers=_h(token), json={"tipo": "prescricao", "artifact_id": errada.id},
    ).status_code == 409

    itens = client.get(base, headers=_h(token))
    assert itens.status_code == 200
    assert {x["tipo"] for x in itens.json()} == {"prescricao", "documento"}

    assert client.get(base, headers=_h(token_intruso)).status_code == 404

    finalizado = client.post(f"/api/pacientes/{pid}/atendimentos/{eid}/finalizar", headers=_h(token))
    assert finalizado.status_code == 200
    outro = GeneratedDocument(
        created_by=medico.id, doc_type="laudo", title="Laudo",
        rendered_body="Conteúdo", patient_profile_id=pid,
    )
    db.add(outro); db.commit(); db.refresh(outro)
    bloqueado = client.post(base, headers=_h(token), json={"tipo": "documento", "artifact_id": outro.id})
    assert bloqueado.status_code == 409
