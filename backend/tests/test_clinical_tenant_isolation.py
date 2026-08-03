from app.models.receituario import PrescriptionType
from app.models.round import Patient


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
    if db.get(PrescriptionType, "COMUM") is None:
        # A PK real é inteira; buscar pelo código evita depender da sequence.
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
    assert listing.json() == []

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
