"""Gestão administrativa de contas gratuitas/de demonstração.

Cobertura propositalmente focada no contrato novo: edição, proteção contra
exclusão indevida e remoção coordenada da caixa Mail360. Não replica a suíte
administrativa geral.
"""
from app.models.email_account import EmailAccount
from app.models.subscription import Subscription, TIPO_MEUCARDIO
from app.models.user import User
from app.services import mail360
from app.services.mail360 import Mail360Error


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _admin(criar_usuario):
    return criar_usuario(email="admin-gestao@teste.local", role="admin")


def _payload(usuario: User, **mudancas):
    dados = {
        "full_name": usuario.full_name,
        "email": usuario.email,
        "role": usuario.role,
        "birth_date": None,
        "cpf": None,
        "profession": None,
        "council_name": None,
        "council_number": None,
        "council_state": None,
        "specialty": None,
        "rqe": None,
        "professional_title": None,
        "workplace_name": None,
        "workplace_department": None,
        "workplace_role": None,
        "workplace_notes": None,
        "is_active": True,
        "tipo_acesso": "normal",
    }
    dados.update(mudancas)
    return dados


def _delete(client, url: str, token: str, payload: dict):
    # Starlette/httpx nesta versão não aceita json= no atalho client.delete().
    # request() preserva o corpo JSON do DELETE sem mudar o contrato da API.
    return client.request("DELETE", url, headers=_headers(token), json=payload)


def test_edita_dados_e_tipo_de_acesso(client, db, criar_usuario):
    _, token_admin = _admin(criar_usuario)
    alvo, _ = criar_usuario(email="natalia@teste.local", full_name="Natalia")

    resposta = client.patch(
        f"/api/admin/user-management/{alvo.id}",
        headers=_headers(token_admin),
        json=_payload(
            alvo,
            full_name="Natalia Atualizada",
            email="natalia.nova@teste.local",
            profession="Medica",
            council_name="CRM",
            council_number="12345",
            council_state="SP",
            tipo_acesso="convidado",
            is_active=False,
        ),
    )

    assert resposta.status_code == 200, resposta.text
    corpo = resposta.json()
    assert corpo["full_name"] == "Natalia Atualizada"
    assert corpo["email"] == "natalia.nova@teste.local"
    assert corpo["tipo_acesso"] == "convidado"
    assert corpo["is_active"] is False

    db.expire_all()
    salvo = db.get(User, alvo.id)
    assert salvo is not None
    assert salvo.convidado is True
    assert salvo.investidor is False
    assert salvo.council_state == "SP"


def test_nao_permite_excluir_admin_nem_propria_conta(client, criar_usuario):
    admin, token_admin = _admin(criar_usuario)
    resposta = _delete(
        client,
        f"/api/admin/user-management/{admin.id}",
        token_admin,
        {"confirmar_email": admin.email, "excluir_corvia_mail": True},
    )
    assert resposta.status_code == 409


def test_bloqueia_exclusao_com_cobranca_stripe(client, db, criar_usuario):
    _, token_admin = _admin(criar_usuario)
    alvo, _ = criar_usuario(email="pago@teste.local")
    db.add(Subscription(
        user_id=alvo.id,
        kind=TIPO_MEUCARDIO,
        status="ativo",
        stripe_customer_id="cus_teste",
        stripe_subscription_id="sub_teste",
    ))
    db.commit()

    resposta = _delete(
        client,
        f"/api/admin/user-management/{alvo.id}",
        token_admin,
        {"confirmar_email": alvo.email, "excluir_corvia_mail": True},
    )
    assert resposta.status_code == 409
    assert db.get(User, alvo.id) is not None


def test_confirmacao_exige_email_exato(client, db, criar_usuario):
    _, token_admin = _admin(criar_usuario)
    alvo, _ = criar_usuario(email="carol@teste.local")

    resposta = _delete(
        client,
        f"/api/admin/user-management/{alvo.id}",
        token_admin,
        {"confirmar_email": "outra@teste.local", "excluir_corvia_mail": True},
    )
    assert resposta.status_code == 422
    assert db.get(User, alvo.id) is not None


def test_exclui_usuario_gratuito_e_caixa_mail360_por_account_key(client, db, criar_usuario, monkeypatch):
    _, token_admin = _admin(criar_usuario)
    alvo, _ = criar_usuario(email="lenira@teste.local", full_name="Lenira")
    alvo.convidado = True
    db.add(EmailAccount(
        user_id=alvo.id,
        email_address="lenira@corvia.med.br",
        mail360_account_key="mail-key-lenira",
        status="ativa",
    ))
    db.commit()
    alvo_id = alvo.id
    alvo_email = alvo.email

    chamadas = []
    monkeypatch.setattr(mail360, "_chamar", lambda metodo, caminho, **kwargs: chamadas.append((metodo, caminho)) or {})

    resposta = _delete(
        client,
        f"/api/admin/user-management/{alvo_id}",
        token_admin,
        {"confirmar_email": alvo_email, "excluir_corvia_mail": True},
    )

    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["corvia_mail_excluido"] is True
    assert chamadas == [("DELETE", "/accounts/mail-key-lenira")]
    db.expire_all()
    assert db.get(User, alvo_id) is None
    assert db.query(EmailAccount).filter(EmailAccount.user_id == alvo_id).count() == 0


def test_falha_mail360_mantem_conta_local(client, db, criar_usuario, monkeypatch):
    _, token_admin = _admin(criar_usuario)
    alvo, _ = criar_usuario(email="wladmir@teste.local", full_name="Wladmir")
    alvo.convidado = True
    db.add(EmailAccount(
        user_id=alvo.id,
        email_address="wladmir@corvia.med.br",
        mail360_account_key="mail-key-wladmir",
        status="ativa",
    ))
    db.commit()

    def falhar(*args, **kwargs):
        raise Mail360Error("indisponível")

    monkeypatch.setattr(mail360, "_chamar", falhar)
    resposta = _delete(
        client,
        f"/api/admin/user-management/{alvo.id}",
        token_admin,
        {"confirmar_email": alvo.email, "excluir_corvia_mail": True},
    )

    assert resposta.status_code == 502
    db.expire_all()
    assert db.get(User, alvo.id) is not None
    assert db.query(EmailAccount).filter(EmailAccount.user_id == alvo.id).count() == 1
