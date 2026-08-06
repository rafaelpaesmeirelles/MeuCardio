"""Assinatura de e-mail (logo Corvia + logo/dados profissionais) — unidade
(app/services/email_signature.py), rota HTTP (GET/PUT /api/email/assinatura)
e o efeito real no envio (mailFormat muda, corpo do médico não é alterado
quando a opção está desligada).
"""
from app.core.security import create_access_token
from app.services.email_signature import montar_assinatura_html, montar_corpo_com_assinatura


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _token_email(client, db, user, monkeypatch_mail360, senha="senha-caixa-123"):
    from app.models.email_account import EmailAccount
    from app.models.subscription import TIPO_EMAIL, Subscription

    db.add(Subscription(user_id=user.id, kind=TIPO_EMAIL, status="ativo"))
    db.commit()
    token_app = create_access_token(user.email, scope="app")
    sugestao = client.get("/api/email/sugestao-endereco", headers=_headers(token_app))
    local_part = sugestao.json()["local_part"]
    ativar = client.post(
        "/api/email/conta",
        json={"senha": senha, "aceite_lgpd": True, "local_part": local_part},
        headers=_headers(token_app),
    )
    assert ativar.status_code == 201, ativar.text
    endereco = db.query(EmailAccount).filter(EmailAccount.user_id == user.id).first().email_address
    login = client.post("/api/email/entrar", json={"endereco": endereco, "senha": senha})
    return login.json()["access_token"]


# ---------------------------------------------------------------------------
# Unidade: app/services/email_signature.py
# ---------------------------------------------------------------------------

def test_assinatura_desligada_devolve_none(db, criar_usuario):
    user, _ = criar_usuario()
    assert user.email_assinatura_ativa is False  # padrão da coluna
    assert montar_assinatura_html(user) is None


def test_assinatura_ligada_contem_nome_e_logo_corvia(db, criar_usuario):
    user, _ = criar_usuario(full_name="Ana Souza")
    user.email_assinatura_ativa = True
    user.professional_title = "Dra."
    html = montar_assinatura_html(user)
    assert html is not None
    assert "Dra. Ana Souza" in html
    assert "corvia-logo-compacta.png" in html


def test_telefone_e_endereco_sao_opt_in_independentes_da_assinatura(db, criar_usuario):
    user, _ = criar_usuario()
    user.email_assinatura_ativa = True
    user.practice_phone = "(11) 4000-0000"
    user.practice_street = "Av. Paulista"
    user.practice_number = "1000"
    user.practice_city = "São Paulo"
    user.practice_state = "SP"

    sem_nenhum = montar_assinatura_html(user)
    assert "4000-0000" not in sem_nenhum
    assert "Paulista" not in sem_nenhum

    user.email_assinatura_incluir_telefone = True
    so_telefone = montar_assinatura_html(user)
    assert "4000-0000" in so_telefone
    assert "Paulista" not in so_telefone

    user.email_assinatura_incluir_endereco = True
    os_dois = montar_assinatura_html(user)
    assert "4000-0000" in os_dois
    assert "Paulista" in os_dois


def test_assinatura_escapa_dados_do_usuario():
    """Nome/especialidade vêm de campo de perfil, não de entrada arbitrária de
    terceiro — mas escapar por padrão custa nada e evita HTML acidental se
    algum campo algum dia aceitar texto mais livre."""
    class _Falso:
        email_assinatura_ativa = True
        email_assinatura_incluir_telefone = False
        email_assinatura_incluir_endereco = False
        full_name = "<script>alert(1)</script>"
        professional_title = None
        specialty = None
        council_name = None
        council_number = None
        council_state = None
        include_workplace_on_documents = False
        workplace_name = None
        workplace_department = None
        workplace_role = None
        workplace_notes = None
        practice_phone = None
        practice_street = None
        practice_number = None
        practice_city = None
        practice_state = None
        document_logo_url = None

    html = montar_assinatura_html(_Falso())
    assert "<script>" not in html
    assert "&lt;script&gt;" in html


def test_montar_corpo_sem_assinatura_preserva_texto_original_e_plaintext():
    corpo, formato = montar_corpo_com_assinatura("Olá, tudo bem?", None)
    assert corpo == "Olá, tudo bem?"
    assert formato == "plaintext"


def test_montar_corpo_com_assinatura_escapa_e_vira_html():
    corpo, formato = montar_corpo_com_assinatura("Olá <time>", "<i>assinatura</i>")
    assert formato == "html"
    assert "&lt;time&gt;" in corpo
    assert "<i>assinatura</i>" in corpo


# ---------------------------------------------------------------------------
# Rota HTTP — current_user (conta Corvia, não a sessão de e-mail)
# ---------------------------------------------------------------------------

def test_get_assinatura_comeca_desligada(client, criar_usuario):
    _, token = criar_usuario()
    resposta = client.get("/api/email/assinatura", headers=_headers(token))
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["ativa"] is False
    assert corpo["pre_visualizacao"] is None


def test_put_assinatura_liga_e_reflete_na_pre_visualizacao(client, criar_usuario):
    _, token = criar_usuario(full_name="Bruno Lima")
    resposta = client.put(
        "/api/email/assinatura",
        json={"ativa": True, "incluir_telefone": False, "incluir_endereco": False},
        headers=_headers(token),
    )
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["ativa"] is True
    assert "Bruno Lima" in corpo["pre_visualizacao"]

    status = client.get("/api/email/assinatura", headers=_headers(token))
    assert status.json()["ativa"] is True


def test_put_assinatura_exige_autenticacao():
    from fastapi.testclient import TestClient
    from app.main import app

    resposta = TestClient(app).put("/api/email/assinatura", json={"ativa": True})
    assert resposta.status_code in (401, 403)


# ---------------------------------------------------------------------------
# Efeito real no envio — mailFormat muda, corpo sem assinatura não muda
# ---------------------------------------------------------------------------

def test_enviar_sem_assinatura_mantem_texto_e_plaintext(client, db, criar_usuario, monkeypatch_mail360):
    user, _ = criar_usuario()
    token = _token_email(client, db, user, monkeypatch_mail360)
    resposta = client.post(
        "/api/email/mensagens",
        json={"para": "destino@example.com", "assunto": "Oi", "corpo_html": "Texto simples", "anexos": []},
        headers=_headers(token),
    )
    assert resposta.status_code == 201
    enviada = monkeypatch_mail360["mensagens_enviadas"][0]
    assert enviada["corpo"] == "Texto simples"
    assert enviada["mail_format"] == "plaintext"


def test_enviar_com_assinatura_ativa_anexa_html(client, db, criar_usuario, monkeypatch_mail360):
    from app.core.db import SessionLocal

    user, _ = criar_usuario(full_name="Carla Dias")
    token_app = create_access_token(user.email, scope="app")
    client.put(
        "/api/email/assinatura", json={"ativa": True, "incluir_telefone": False, "incluir_endereco": False},
        headers=_headers(token_app),
    )
    token = _token_email(client, db, user, monkeypatch_mail360)
    resposta = client.post(
        "/api/email/mensagens",
        json={"para": "destino@example.com", "assunto": "Oi", "corpo_html": "Texto simples", "anexos": []},
        headers=_headers(token),
    )
    assert resposta.status_code == 201
    enviada = monkeypatch_mail360["mensagens_enviadas"][0]
    assert enviada["mail_format"] == "html"
    assert "Texto simples" in enviada["corpo"]
    assert "Carla Dias" in enviada["corpo"]
    assert "corvia-logo-compacta.png" in enviada["corpo"]
