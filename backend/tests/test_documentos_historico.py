"""Testes da Tarefa 4 — persistência de `variables` em `GeneratedDocument` e
"recriar baseado neste" para documento gerado a partir de modelo.
"""
import pytest
from sqlalchemy import text

_TABELAS = ("generated_documents", "document_templates")


@pytest.fixture(autouse=True)
def _limpar(db):
    db.execute(text(f"TRUNCATE {', '.join(_TABELAS)} RESTART IDENTITY CASCADE"))
    db.commit()
    yield


def _criar_template(client, token, body="Atesto que {{nome}} precisa de {{dias}} dias de repouso."):
    r = client.post(
        "/api/document-templates",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Atestado padrão", "doc_type": "atestado", "body": body},
    )
    assert r.status_code == 201, r.text
    return r.json()["id"]


class TestPersistenciaDeVariaveis:
    def test_gerar_persiste_variaveis_e_get_devolve(self, client, criar_usuario):
        _, token = criar_usuario(role="admin")
        template_id = _criar_template(client, token)

        r = client.post(
            "/api/document-templates/gerar",
            headers={"Authorization": f"Bearer {token}"},
            json={"template_id": template_id, "variables": {"nome": "Elisa Nunes", "dias": "3"}},
        )
        assert r.status_code == 201, r.text
        gerado_id = r.json()["id"]

        detalhe = client.get(f"/api/document-templates/gerados/{gerado_id}",
                             headers={"Authorization": f"Bearer {token}"}).json()
        assert detalhe["template_id"] == template_id
        assert detalhe["variables"] == {"nome": "Elisa Nunes", "dias": "3"}


class TestRecriarDocumentoBaseadoEmAnterior:
    def test_recriar_com_variaveis_do_anterior_gera_documento_novo(self, client, criar_usuario):
        _, token = criar_usuario(role="admin")
        template_id = _criar_template(client, token)

        primeiro = client.post(
            "/api/document-templates/gerar",
            headers={"Authorization": f"Bearer {token}"},
            json={"template_id": template_id, "variables": {"nome": "Fabio Rocha", "dias": "5"}},
        ).json()

        detalhe = client.get(f"/api/document-templates/gerados/{primeiro['id']}",
                             headers={"Authorization": f"Bearer {token}"}).json()

        segundo = client.post(
            "/api/document-templates/gerar",
            headers={"Authorization": f"Bearer {token}"},
            json={"template_id": detalhe["template_id"],
                  "variables": {**detalhe["variables"], "dias": "7"}},
        )
        assert segundo.status_code == 201, segundo.text
        assert segundo.json()["id"] != primeiro["id"]
        assert "7 dias" in segundo.json()["rendered_body"]

    def test_documento_gerado_antes_da_tarefa_nao_tem_variaveis(self, client, criar_usuario, db):
        """Simula um GeneratedDocument criado antes desta coluna existir —
        `variables` fica None, e o frontend precisa saber que não dá pra
        recriar automaticamente (ver Templates.tsx:recriarBaseadoEm)."""
        from app.models.clinical_docs import DocumentTemplate, GeneratedDocument

        user, token = criar_usuario(role="admin")
        t = DocumentTemplate(owner_id=user.id, title="Antigo", doc_type="atestado", body="Texto fixo.")
        db.add(t)
        db.flush()
        g = GeneratedDocument(created_by=user.id, template_id=t.id, doc_type="atestado",
                              title="Antigo", rendered_body="Texto fixo.", variables=None)
        db.add(g)
        db.commit()
        db.refresh(g)

        detalhe = client.get(f"/api/document-templates/gerados/{g.id}",
                             headers={"Authorization": f"Bearer {token}"}).json()
        assert detalhe["variables"] is None
