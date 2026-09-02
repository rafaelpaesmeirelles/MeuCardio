"""Regressão: paginação real nos endpoints de listagem que antes devolviam a
coleção inteira sem offset/total (Parte I da correção coordenada de
02/09/2026 — casos clínicos, trilhas, checklists e material ao paciente
crescem no mesmo ritmo do resto do acervo científico; triagem por sintomas
ficou deliberadamente de fora, documentado em specialty_guides.py, por ser
uma taxonomia fechada)."""

import pytest
from sqlalchemy import text

from app.models.checklist import DischargeChecklist
from app.models.clinical_case import ClinicalCase
from app.models.patient_material import PatientMaterial
from app.models.study_track import StudyTrack


@pytest.fixture(autouse=True)
def _colecoes_limpas(db):
    tabelas = "clinical_cases, study_tracks, discharge_checklists, patient_materials"
    db.execute(text(f"TRUNCATE {tabelas} RESTART IDENTITY CASCADE"))
    db.commit()
    yield
    db.execute(text(f"TRUNCATE {tabelas} RESTART IDENTITY CASCADE"))
    db.commit()


def test_casos_clinicos_pagina_com_contrato_completo(client, db, criar_usuario):
    db.add_all([
        ClinicalCase(slug=f"caso-paginacao-{i}", titulo=f"Caso {i}", tema="Arritmias",
                     nivel="intermediario", enunciado="Enunciado de teste.",
                     pergunta="Qual a conduta?", opcoes=["A", "B"], resposta_correta=0,
                     explicacao="Explicação de teste.",
                     published=True, review_status="revisado")
        for i in range(5)
    ])
    db.commit()
    _, token = criar_usuario(role="admin")

    resposta = client.get(
        "/api/casos-clinicos", params={"limit": 2}, headers={"Authorization": f"Bearer {token}"},
    )
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["total"] == 5
    assert corpo["has_more"] is True
    assert corpo["next_offset"] == 2
    assert len(corpo["items"]) == 2


def test_trilhas_pagina_com_contrato_completo(client, db, criar_usuario):
    db.add_all([
        StudyTrack(slug=f"trilha-paginacao-{i}", titulo=f"Trilha {i}", tema="Geral",
                   published=True, review_status="revisado")
        for i in range(4)
    ])
    db.commit()
    _, token = criar_usuario(role="admin")

    resposta = client.get(
        "/api/trilhas", params={"limit": 3}, headers={"Authorization": f"Bearer {token}"},
    )
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["total"] == 4
    assert corpo["has_more"] is True
    assert len(corpo["items"]) == 3
    seguinte = client.get(
        "/api/trilhas", params={"limit": 3, "offset": corpo["next_offset"]},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert seguinte.json()["has_more"] is False
    assert len(seguinte.json()["items"]) == 1


def test_checklists_pagina_com_contrato_completo(client, db, criar_usuario):
    db.add_all([
        DischargeChecklist(slug=f"checklist-paginacao-{i}", condicao=f"Condição {i}",
                            scope_type="doenca", published=True, review_status="revisado")
        for i in range(3)
    ])
    db.commit()
    _, token = criar_usuario(role="admin")

    resposta = client.get(
        "/api/checklists", params={"limit": 1}, headers={"Authorization": f"Bearer {token}"},
    )
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["total"] == 3
    assert corpo["has_more"] is True
    assert corpo["next_offset"] == 1


def test_material_paciente_pagina_com_contrato_completo(client, db, criar_usuario):
    db.add_all([
        PatientMaterial(slug=f"material-paginacao-{i}", titulo=f"Material {i}", tema="Geral",
                         published=True, review_status="revisado")
        for i in range(3)
    ])
    db.commit()
    _, token = criar_usuario(role="admin")

    resposta = client.get(
        "/api/material-paciente", params={"limit": 2}, headers={"Authorization": f"Bearer {token}"},
    )
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["total"] == 3
    assert corpo["has_more"] is True
    assert corpo["next_offset"] == 2


def test_triagem_por_sintoma_permanece_sem_paginacao_de_proposito(client, criar_usuario):
    """Confirma a exceção documentada: continua devolvendo lista simples."""
    _, token = criar_usuario(role="admin")
    resposta = client.get(
        "/api/specialty-guides/triage", headers={"Authorization": f"Bearer {token}"},
    )
    assert resposta.status_code == 200
    assert isinstance(resposta.json(), list)
