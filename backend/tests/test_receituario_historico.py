"""Testes da Tarefa 4 — arquivo/histórico de receituário e "recriar baseado
numa anterior" (GET /api/receituario e extensão de GET /api/receituario/{id}).
"""
import pytest
from sqlalchemy import text

from app.models.audit import AuditLog

_TABELAS = (
    "prescription_documents", "prescription_recipients", "prescriptions",
)


@pytest.fixture(autouse=True)
def _limpar(db):
    db.execute(text(f"TRUNCATE {', '.join(_TABELAS)} RESTART IDENTITY CASCADE"))
    db.commit()
    yield


def _criar(client, token, nome="Paciente Um", endereco=None, documento=None, itens=None):
    itens = itens or [{"descricao": "Dipirona 500mg", "posologia": "1 cp a cada 6h"}]
    destinatario = {"nome": nome}
    if endereco:
        destinatario["endereco"] = endereco
    if documento:
        destinatario["documento"] = documento
    r = client.post(
        "/api/receituario",
        headers={"Authorization": f"Bearer {token}"},
        json={"destinatario": destinatario, "itens": itens},
    )
    assert r.status_code == 201, r.text
    return r.json()["prescricao_id"]


class TestListarReceituarios:
    def test_lista_com_nome_decifrado_e_documentos(self, client, criar_usuario):
        _, token = criar_usuario(role="admin")
        id1 = _criar(client, token, nome="Ana Paula")
        id2 = _criar(client, token, nome="Bruno Silva")

        r = client.get("/api/receituario", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200, r.text
        itens = r.json()
        assert len(itens) == 2
        por_id = {i["prescricao_id"]: i for i in itens}
        assert por_id[id1]["paciente_nome"] == "Ana Paula"
        assert por_id[id2]["paciente_nome"] == "Bruno Silva"
        assert por_id[id1]["documentos"][0]["tipo"] == "COMUM"
        assert por_id[id1]["documentos"][0]["status"] == "rascunho"
        # Mais recente primeiro.
        assert itens[0]["prescricao_id"] == id2

    def test_lista_audita_uma_vez_por_chamada_nao_por_paciente(self, client, criar_usuario, db):
        _, token = criar_usuario(role="admin")
        _criar(client, token, nome="Ana Paula")
        _criar(client, token, nome="Bruno Silva")

        client.get("/api/receituario", headers={"Authorization": f"Bearer {token}"})

        auditorias = db.query(AuditLog).filter(AuditLog.action == "listar_receituarios").all()
        assert len(auditorias) == 1
        assert auditorias[0].detail["count"] == 2

    def test_lista_so_traz_receituarios_do_proprio_medico(self, client, criar_usuario):
        _, token1 = criar_usuario(email="medico1@teste.local", role="admin")
        _, token2 = criar_usuario(email="medico2@teste.local", role="admin")
        _criar(client, token1, nome="Paciente do médico 1")

        r = client.get("/api/receituario", headers={"Authorization": f"Bearer {token2}"})
        assert r.status_code == 200
        assert r.json() == []


class TestRecriarBaseadoEmAnterior:
    def test_obter_traz_itens_originais_e_endereco_documento(self, client, criar_usuario):
        _, token = criar_usuario(role="admin")
        itens = [{"descricao": "Losartana 50mg", "posologia": "1 cp pela manhã", "orientacao": "Tomar em jejum"}]
        id1 = _criar(client, token, nome="Carla Mendes", endereco="Rua das Flores, 123", documento="123.456.789-00", itens=itens)

        r = client.get(f"/api/receituario/{id1}", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200, r.text
        corpo = r.json()
        assert corpo["destinatario"]["nome"] == "Carla Mendes"
        assert corpo["destinatario"]["endereco"] == "Rua das Flores, 123"
        assert corpo["destinatario"]["documento"] == "123.456.789-00"
        assert corpo["itens_originais"][0]["descricao"] == "Losartana 50mg"
        assert corpo["itens_originais"][0]["posologia"] == "1 cp pela manhã"
        assert corpo["itens_originais"][0]["orientacao"] == "Tomar em jejum"

    def test_recriar_com_dados_do_get_produz_prescricao_nova(self, client, criar_usuario):
        _, token = criar_usuario(role="admin")
        id1 = _criar(client, token, nome="Diego Alves", endereco="Av. Central, 1")

        detalhe = client.get(f"/api/receituario/{id1}", headers={"Authorization": f"Bearer {token}"}).json()

        r = client.post(
            "/api/receituario",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "destinatario": {
                    "nome": detalhe["destinatario"]["nome"],
                    "endereco": detalhe["destinatario"]["endereco"],
                },
                "itens": detalhe["itens_originais"],
            },
        )
        assert r.status_code == 201, r.text
        id2 = r.json()["prescricao_id"]
        assert id2 != id1

        lista = client.get("/api/receituario", headers={"Authorization": f"Bearer {token}"}).json()
        assert len(lista) == 2
        assert {i["prescricao_id"] for i in lista} == {id1, id2}
