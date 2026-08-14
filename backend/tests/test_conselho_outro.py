"""Conselho "Outro": campos de texto livre para nome do conselho e
estado/região (08/08/2026, pedido do Rafael).

Cobre os dois pontos de entrada onde council_name pode ser "OUTRO":
`POST /api/auth/solicitar-acesso-com-recuperacao` (cadastro canônico) e
`PATCH /api/auth/me` (Minha Conta). Em nenhum dos dois `council_name` deixa de
gravar o valor literal "OUTRO" — é o que `escopo_profissional.escopo_de()` usa
para o fail-closed do escopo de prescrição; só a EXIBIÇÃO troca pelo texto livre.
"""
from app.models.user import User


CADASTRO = "/api/auth/solicitar-acesso-com-recuperacao"


def _payload_solicitacao(**overrides):
    base = dict(
        full_name="João da Silva", birth_date="1980-01-01", cpf="529.982.247-25",
        profession="Farmacêutico", council_name="Outro", council_number="1234",
        council_name_other="Ordem dos Farmacêuticos", council_state_other="Lisboa",
        email="joao@teste.local", recovery_email="joao.recuperacao@externo.test",
        password="senha-forte-123",
    )
    base.update(overrides)
    return base


def test_solicitar_acesso_com_outro_exige_conselho_e_estado_livres(client):
    resp = client.post(CADASTRO, json=_payload_solicitacao(
        council_name_other="", council_state_other="",
    ))
    assert resp.status_code == 422


def test_solicitar_acesso_com_outro_persiste_texto_livre_e_conselho_literal(client, db):
    resp = client.post(CADASTRO, json=_payload_solicitacao())
    assert resp.status_code == 201, resp.text

    user = db.query(User).filter(User.email == "joao@teste.local").first()
    assert user is not None
    assert user.council_name == "OUTRO"
    assert user.council_state is None
    assert user.council_name_other == "Ordem dos Farmacêuticos"
    assert user.council_state_other == "Lisboa"


def test_solicitar_acesso_conselho_comum_continua_exigindo_uf(client):
    resp = client.post(CADASTRO, json=_payload_solicitacao(
        council_name="CRM", council_number="123456",
        council_name_other=None, council_state_other=None,
        email="crm@teste.local", recovery_email="crm.recuperacao@externo.test",
    ))
    assert resp.status_code == 422

    resp = client.post(CADASTRO, json=_payload_solicitacao(
        council_name="CRM", council_number="123456", council_state="SP",
        council_name_other=None, council_state_other=None,
        email="crm2@teste.local", recovery_email="crm2.recuperacao@externo.test",
    ))
    assert resp.status_code == 201, resp.text


def test_solicitar_acesso_uf_invalida_para_conselho_comum_e_rejeitada(client):
    resp = client.post(CADASTRO, json=_payload_solicitacao(
        council_name="CRM", council_number="123456", council_state="ZZ",
        council_name_other=None, council_state_other=None,
        email="crm3@teste.local", recovery_email="crm3.recuperacao@externo.test",
    ))
    assert resp.status_code == 422


def test_atualizar_me_com_outro_persiste_texto_livre(client, criar_usuario, db):
    user, token = criar_usuario()
    resp = client.patch(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "full_name": user.full_name, "council_name": "Outro",
            "council_name_other": "Conselho Regional de Psicologia",
            "council_state_other": "Rio de Janeiro",
        },
    )
    assert resp.status_code == 200, resp.text
    corpo = resp.json()
    assert corpo["council_name"] == "OUTRO"
    assert corpo["council_name_other"] == "Conselho Regional de Psicologia"
    assert corpo["council_state_other"] == "Rio de Janeiro"

    db.refresh(user)
    assert user.council_name == "OUTRO"
    assert user.council_name_other == "Conselho Regional de Psicologia"
    assert user.council_state_other == "Rio de Janeiro"


def test_atualizar_me_com_outro_sem_texto_livre_e_rejeitado(client, criar_usuario):
    user, token = criar_usuario()
    resp = client.patch(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"full_name": user.full_name, "council_name": "Outro"},
    )
    assert resp.status_code == 422


def test_perfil_exibe_texto_livre_no_lugar_de_outro(client, criar_usuario, db):
    user, token = criar_usuario()
    user.council_name = "OUTRO"
    user.council_number = "999"
    user.council_name_other = "Ordem dos Farmacêuticos"
    user.council_state_other = "Lisboa"
    db.commit()

    resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    corpo = resp.json()
    assert corpo["council"] == "Ordem dos Farmacêuticos 999/Lisboa"
    assert corpo["council_name"] == "OUTRO"
    assert corpo["council_name_other"] == "Ordem dos Farmacêuticos"
