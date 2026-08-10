from app.models.clinical_docs import Appointment, Prescription
from app.models.receituario import PrescriptionType
from app.models.round import Patient
from app.models.subscription import Subscription


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _criar_documento_gerado(client, token: str) -> int:
    template = client.post(
        "/api/document-templates",
        headers=_headers(token),
        json={
            "title": "Laudo privativo",
            "doc_type": "laudo",
            "body": "Documento clínico de {{nome}}.",
        },
    )
    assert template.status_code == 201, template.text

    gerado = client.post(
        "/api/document-templates/gerar",
        headers=_headers(token),
        json={
            "template_id": template.json()["id"],
            "variables": {"nome": "Paciente Sigiloso"},
        },
    )
    assert gerado.status_code == 201, gerado.text
    return gerado.json()["id"]


def _garantir_receituario_comum(db) -> None:
    existente = db.query(PrescriptionType).filter(
        PrescriptionType.codigo == "COMUM"
    ).first()
    if existente is None:
        db.add(
            PrescriptionType(
                codigo="COMUM",
                nome="Receituário comum",
                ativo=True,
            )
        )
        db.commit()


def test_even_admin_cannot_read_or_operate_another_doctors_generated_document(
    client, criar_usuario
):
    _, owner_token = criar_usuario(
        email="autor.documento@teste.local", role="admin"
    )
    _, other_token = criar_usuario(
        email="outro.admin@teste.local", role="admin"
    )
    generated_id = _criar_documento_gerado(client, owner_token)

    listing = client.get(
        "/api/document-templates/gerados", headers=_headers(other_token)
    )
    assert listing.status_code == 200
    payload = listing.json()
    assert payload["items"] == []
    assert payload["total"] == 0
    assert payload["has_more"] is False

    detail = client.get(
        f"/api/document-templates/gerados/{generated_id}",
        headers=_headers(other_token),
    )
    assert detail.status_code == 404

    pdf = client.get(
        f"/api/document-templates/gerados/{generated_id}/pdf?metodo=MANUAL",
        headers=_headers(other_token),
    )
    assert pdf.status_code == 404

    send = client.post(
        f"/api/document-templates/gerados/{generated_id}/enviar-email",
        headers=_headers(other_token),
        json={"email": "paciente@teste.local"},
    )
    assert send.status_code == 404


def test_admin_cannot_generate_document_linking_another_doctors_patient(
    client, criar_usuario, db
):
    owner, _ = criar_usuario(email="dono.paciente@teste.local", role="admin")
    _, other_token = criar_usuario(email="outro.medico@teste.local", role="admin")

    patient = Patient(
        record_number="PRONT-ISOLAMENTO-1",
        initials="PS",
        created_by=owner.id,
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)

    template = client.post(
        "/api/document-templates",
        headers=_headers(other_token),
        json={
            "title": "Documento do segundo médico",
            "doc_type": "laudo",
            "body": "Texto fixo.",
        },
    )
    assert template.status_code == 201, template.text

    response = client.post(
        "/api/document-templates/gerar",
        headers=_headers(other_token),
        json={
            "template_id": template.json()["id"],
            "patient_id": patient.id,
            "variables": {},
        },
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Paciente não encontrado."


def test_receituario_rejects_direct_id_access_from_another_admin(
    client, criar_usuario, db
):
    _garantir_receituario_comum(db)
    _, owner_token = criar_usuario(email="autor.receita@teste.local", role="admin")
    _, other_token = criar_usuario(email="intruso.receita@teste.local", role="admin")

    created = client.post(
        "/api/receituario",
        headers=_headers(owner_token),
        json={
            "destinatario": {"nome": "Paciente do Autor"},
            "itens": [
                {"descricao": "Dipirona 500 mg", "posologia": "1 cp se dor"}
            ],
        },
    )
    assert created.status_code == 201, created.text
    prescription_id = created.json()["prescricao_id"]
    document_id = created.json()["documentos"][0]["id"]

    detail = client.get(
        f"/api/receituario/{prescription_id}", headers=_headers(other_token)
    )
    assert detail.status_code == 404

    review = client.post(
        f"/api/receituario/documentos/{document_id}/revisar",
        headers=_headers(other_token),
        json={"confirmar": True},
    )
    assert review.status_code == 404

    emit = client.post(
        f"/api/receituario/documentos/{document_id}/emitir",
        headers=_headers(other_token),
        json={"metodo": "MANUAL"},
    )
    assert emit.status_code == 404

    send = client.post(
        f"/api/receituario/documentos/{document_id}/enviar-email",
        headers=_headers(other_token),
        json={"email": "paciente@teste.local"},
    )
    assert send.status_code == 404


def test_round_rejects_cross_tenant_access_even_for_admin(
    client, criar_usuario
):
    _, owner_token = criar_usuario(email="dono.round@teste.local", role="admin")
    _, other_token = criar_usuario(email="outro.round@teste.local", role="admin")

    created = client.post(
        "/api/round/patients",
        headers=_headers(owner_token),
        json={
            "record_number": "ROUND-ISOLAMENTO-1",
            "initials": "RI",
            "bed": "101",
            "unit": "Cardiologia",
        },
    )
    assert created.status_code == 201, created.text
    patient_id = created.json()["id"]

    listing = client.get(
        "/api/round/patients", headers=_headers(other_token)
    )
    assert listing.status_code == 200
    assert listing.json() == []

    attempts = (
        client.get(
            f"/api/round/patients/{patient_id}", headers=_headers(other_token)
        ),
        client.patch(
            f"/api/round/patients/{patient_id}",
            headers=_headers(other_token),
            json={"bed": "999"},
        ),
        client.post(
            f"/api/round/patients/{patient_id}/problems",
            headers=_headers(other_token),
            json={"label": "Problema indevido"},
        ),
        client.post(
            f"/api/round/patients/{patient_id}/notes",
            headers=_headers(other_token),
            json={"body": "Nota indevida"},
        ),
        client.get(
            f"/api/round/patients/{patient_id}/summary",
            headers=_headers(other_token),
        ),
        client.get(
            f"/api/round/patients/{patient_id}/ai-assist",
            headers=_headers(other_token),
        ),
    )
    assert all(response.status_code == 404 for response in attempts)


# ---------------------------------------------------------------------------
# 🚨 Achados da auditoria AUTH/SESSION (issue #52, subfase 1): a MESMA tabela
# Patient, com a MESMA regra de posse (`created_by`), é estritamente isolada
# em round.py (inclusive contra admin, ver teste acima) mas tem um bypass
# `... and user.role != "admin"` em pelo menos três outras rotas que também
# leem/escrevem dado ligado a Patient: timeline.py, prescriptions.py e
# appointments.py. Ou seja: o paciente de um médico, supostamente isolado até
# de outro admin, continua acessível a qualquer conta admin por essas rotas
# alternativas. Os testes abaixo documentam o comportamento ATUAL (o bypass
# funciona) para não regredir silenciosamente e para servir de cobertura a
# uma correção futura (alinhar as três rotas ao padrão de round.py/
# documents.py/receituario.py, que nunca abrem exceção para admin).
# ---------------------------------------------------------------------------


def test_timeline_route_denies_admin_reading_another_doctors_patient(
    client, criar_usuario, db
):
    """Achado de auditoria corrigido (issue #52, gate final): admin de
    outra conta não pode mais ler a timeline clínica de paciente que não é
    dele — `app/api/timeline.py` agora usa o mesmo ponto único de posse
    (`app/services/clinical_ownership.patient_for_user`) que a rota de
    posse direta (round.py) já usava, sem exceção para nenhum papel.

    Paciente criado direto via ORM (não pela rota) — o dono é `medico`
    deliberadamente, para o teste ser o caso real (médico comum, não outro
    admin), e `medico` exige assinatura ativa em `/api/round/patients`
    (`assinante_ativo`), que este teste não está cobrindo."""
    owner, _ = criar_usuario(email="dono.timeline@teste.local", role="medico")
    _, intruso_token = criar_usuario(email="intruso.timeline@teste.local", role="admin")

    patient = Patient(record_number="TIMELINE-ISOLAMENTO-1", initials="TI", created_by=owner.id)
    db.add(patient)
    db.commit()
    db.refresh(patient)
    patient_id = patient.id

    # A rota de posse direta já negava corretamente, mesmo para admin.
    round_direto = client.get(
        f"/api/round/patients/{patient_id}", headers=_headers(intruso_token)
    )
    assert round_direto.status_code == 404

    # A rota de timeline, para o MESMO paciente, agora nega igual — sem
    # vazar nenhum dado clínico no corpo da resposta de erro.
    timeline = client.get(
        f"/api/timeline/patient/{patient_id}", headers=_headers(intruso_token)
    )
    assert timeline.status_code == 404
    assert "TIMELINE-ISOLAMENTO-1" not in timeline.text


def test_timeline_route_still_works_for_the_actual_owner(client, criar_usuario, db):
    """Confirma que a correção do IDOR não é excessiva — o próprio médico
    dono do paciente continua lendo a timeline normalmente."""
    owner, owner_token = criar_usuario(email="dono.timeline2@teste.local", role="medico")
    # timeline.router está em ROUTERS_ASSINANTES — exige assinatura principal
    # ativa antes de qualquer checagem da própria rota (achado já registrado
    # na subfase 3 da estabilização para este mesmo padrão).
    db.add(Subscription(user_id=owner.id, kind="meucardio", plano="basico", status="ativo"))
    db.commit()

    patient = Patient(record_number="TIMELINE-DONO-1", initials="TD", created_by=owner.id)
    db.add(patient)
    db.commit()
    db.refresh(patient)

    resposta = client.get(
        f"/api/timeline/patient/{patient.id}", headers=_headers(owner_token)
    )
    assert resposta.status_code == 200


def test_prescriptions_route_denies_admin_reading_and_writing_another_doctors_patient(
    client, criar_usuario, db
):
    """Achado de auditoria corrigido (issue #52, gate final): admin de
    outra conta não pode mais LISTAR nem CRIAR prescrição de beira de leito
    vinculada a paciente de outro médico. Confirma também que a tentativa
    de criação não deixa efeito colateral nenhum — nenhuma linha de
    `Prescription` chega a existir para esse paciente."""
    owner, _ = criar_usuario(email="dono.prescricao@teste.local", role="medico")
    _, intruso_token = criar_usuario(email="intruso.prescricao@teste.local", role="admin")

    patient = Patient(record_number="PRESCRICAO-ISOLAMENTO-1", initials="PI", created_by=owner.id)
    db.add(patient)
    db.commit()
    db.refresh(patient)
    patient_id = patient.id

    listar = client.get(
        f"/api/prescriptions/patient/{patient_id}", headers=_headers(intruso_token)
    )
    assert listar.status_code == 404
    assert "PRESCRICAO-ISOLAMENTO-1" not in listar.text

    criar = client.post(
        "/api/prescriptions",
        headers=_headers(intruso_token),
        json={
            "patient_id": patient_id,
            "items": [{"drug_name": "Losartana 50mg", "posology": "1 cp/dia"}],
        },
    )
    assert criar.status_code == 404

    # Nenhum efeito colateral: a tentativa recusada não criou prescrição.
    assert db.query(Prescription).filter(Prescription.patient_id == patient_id).count() == 0


def test_appointments_route_denies_admin_linking_appointment_to_another_doctors_patient(
    client, criar_usuario, db
):
    """Achado de auditoria corrigido (issue #52, gate final): admin de
    outra conta não pode mais vincular um novo agendamento a `patient_id`
    de outro médico, e a tentativa recusada não deixa nenhum agendamento
    órfão no banco."""
    owner, _ = criar_usuario(email="dono.agenda@teste.local", role="medico")
    _, intruso_token = criar_usuario(email="intruso.agenda@teste.local", role="admin")

    patient = Patient(record_number="AGENDA-ISOLAMENTO-1", initials="AI", created_by=owner.id)
    db.add(patient)
    db.commit()
    db.refresh(patient)
    patient_id = patient.id

    criar = client.post(
        "/api/appointments",
        headers=_headers(intruso_token),
        json={
            "patient_id": patient_id,
            "scheduled_at": "2026-09-01T10:00:00Z",
            "appointment_type": "consulta",
        },
    )
    assert criar.status_code == 404
    assert db.query(Appointment).filter(Appointment.patient_id == patient_id).count() == 0
