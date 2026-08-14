"""Regressões do modo Investidor definitivo — somente visualização."""
from app.core.security import create_access_token, hash_password, verify_password
from app.models.audit import AuditLog
from app.models.user import User


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _investidor(db, email: str = "investidor@teste.local") -> tuple[User, str]:
    user = User(
        email=email,
        full_name="Investidor Demonstração",
        role="leitor",
        password_hash=hash_password("senha-inicial-temporaria"),
        is_active=True,
        investidor=True,
        profile_completion_required=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user, create_access_token(user.email, scope="app")


def test_investidor_nasce_sem_perfil_sem_kyc_e_com_senha_fixa(client, db):
    user, token = _investidor(db)

    assert user.profile_completion_required is False
    assert user.onboarding_visto is False
    assert user.convidado is False
    assert user.status == "aprovado"
    assert verify_password("CorVIAOS", user.password_hash) is True
    assert verify_password("senha-inicial-temporaria", user.password_hash) is False

    resp = client.get("/api/auth/me", headers=_headers(token))
    assert resp.status_code == 200, resp.text
    corpo = resp.json()
    assert corpo["investidor"] is True
    assert corpo["profile_completion_required"] is False
    assert corpo["kyc_required"] is False
    assert corpo["onboarding_pendente"] is True


def test_investidor_pode_concluir_tour_e_depois_ir_para_home(client, db):
    user, token = _investidor(db)

    resp = client.post("/api/auth/me/onboarding-concluido", headers=_headers(token))
    assert resp.status_code == 200, resp.text

    db.expire_all()
    atualizado = db.get(User, user.id)
    assert atualizado.onboarding_visto is True

    resp = client.get("/api/auth/me", headers=_headers(token))
    assert resp.status_code == 200
    assert resp.json()["onboarding_pendente"] is False


def test_investidor_get_de_leitura_funciona_mas_put_operacional_e_403(client, db):
    user, token = _investidor(db)

    leitura = client.get("/api/presence/me", headers=_headers(token))
    assert leitura.status_code == 200, leitura.text

    escrita = client.put(
        "/api/presence/me",
        json={"visible": True},
        headers=_headers(token),
    )
    assert escrita.status_code == 403, escrita.text
    assert "somente para visualização" in escrita.json()["detail"]

    db.expire_all()
    assert db.get(User, user.id).show_online_status is False


def test_investidor_nao_pode_trocar_senha(client, db):
    user, token = _investidor(db)

    resp = client.post(
        "/api/auth/alterar-senha",
        json={"senha_atual": "CorVIAOS", "nova_senha": "OutraSenha123"},
        headers=_headers(token),
    )
    assert resp.status_code == 403, resp.text

    db.expire_all()
    atualizado = db.get(User, user.id)
    assert verify_password("CorVIAOS", atualizado.password_hash) is True
    assert verify_password("OutraSenha123", atualizado.password_hash) is False


def test_investidor_nao_inicia_oauth_da_agenda_por_get(client, db):
    _, token = _investidor(db)

    resp = client.get(
        "/api/agenda/oauth/google/start?contacts=true&mail=false&calendar_write=false&consent_accepted=true",
        headers=_headers(token),
        follow_redirects=False,
    )
    assert resp.status_code == 403, resp.text
    assert "somente para visualização" in resp.json()["detail"]


def test_investidor_bloqueia_gets_que_entregam_artefato_operacional(client, db):
    _, token = _investidor(db)

    for path in (
        "/api/document-templates/gerados/999/pdf",
        "/api/material-paciente/demo/pdf",
        "/api/pedidos/999/exame",
        "/api/prescriptions/999/imprimir",
        "/api/cursos/demo/material/999",
    ):
        resp = client.get(path, headers=_headers(token), follow_redirects=False)
        assert resp.status_code == 403, f"{path}: {resp.status_code} {resp.text}"
        assert "somente para visualização" in resp.json()["detail"]


def test_investidor_gets_de_navegacao_nao_persistem_auditoria(client, db):
    user, token = _investidor(db)

    receitas = client.get("/api/receituario", headers=_headers(token))
    documentos = client.get("/api/document-templates/gerados", headers=_headers(token))

    assert receitas.status_code == 200, receitas.text
    assert documentos.status_code == 200, documentos.text
    assert db.query(AuditLog).filter(
        AuditLog.user_id == user.id,
        AuditLog.action.in_(["listar_receituarios", "listar_documentos_gerados"]),
    ).count() == 0


def test_investidor_nao_gera_exportacao_prescricao_ou_documento(client, db):
    _, token = _investidor(db)

    for path in (
        "/api/exportar/conteudo",
        "/api/receituario",
        "/api/documentos",
    ):
        resp = client.post(path, json={}, headers=_headers(token))
        assert resp.status_code == 403, f"{path}: {resp.status_code} {resp.text}"
        assert "somente para visualização" in resp.json()["detail"]


def test_converter_conta_existente_em_investidor_redefine_matriz(db):
    user = User(
        email="convertido@teste.local",
        full_name="Conta Convertida",
        role="medico",
        password_hash=hash_password("SenhaAntiga123"),
        is_active=True,
        convidado=True,
        profile_completion_required=True,
        onboarding_visto=True,
        investidor=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    user.investidor = True
    db.commit()
    db.refresh(user)

    assert user.investidor is True
    assert user.convidado is False
    assert user.profile_completion_required is False
    assert user.onboarding_visto is False
    assert user.status == "aprovado"
    assert user.is_active is True
    assert verify_password("CorVIAOS", user.password_hash) is True
    assert verify_password("SenhaAntiga123", user.password_hash) is False


def test_converter_revoga_sessao_anterior_e_novo_login_corviaos_funciona(client, db):
    user = User(
        email="sessao-pre-conversao@teste.local",
        full_name="Conta Antes da Conversão",
        role="medico",
        password_hash=hash_password("SenhaAntiga123"),
        is_active=True,
        investidor=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token_antigo = create_access_token(user.email, scope="app")

    assert client.get("/api/auth/me", headers=_headers(token_antigo)).status_code == 200

    user.investidor = True
    db.commit()
    db.refresh(user)

    # A redefinição para a senha fixa é uma mudança de credencial real:
    # sessions_valid_after invalida tokens emitidos antes da conversão.
    assert client.get("/api/auth/me", headers=_headers(token_antigo)).status_code == 401

    login = client.post(
        "/api/auth/login",
        data={"username": user.email, "password": "CorVIAOS"},
    )
    assert login.status_code == 200, login.text
    token_novo = login.json()["access_token"]

    me = client.get("/api/auth/me", headers=_headers(token_novo))
    assert me.status_code == 200
    assert me.json()["investidor"] is True
    assert me.json()["kyc_required"] is False
    assert me.json()["onboarding_pendente"] is True


def test_investidor_mantem_senha_fixa_mesmo_se_codigo_legado_tentar_trocar(db):
    user, _ = _investidor(db)
    hash_fixo = user.password_hash

    user.password_hash = hash_password("TentativaDeTroca123")
    db.commit()
    db.refresh(user)

    assert user.password_hash == hash_fixo
    assert verify_password("CorVIAOS", user.password_hash) is True
    assert verify_password("TentativaDeTroca123", user.password_hash) is False


def test_convidado_nao_herda_readonly_do_investidor(client, db):
    user = User(
        email="convidado-write@teste.local",
        full_name="Convidado Com Escrita",
        role="medico",
        password_hash=hash_password("senha-convidado-123"),
        is_active=True,
        convidado=True,
        investidor=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(user.email, scope="app")

    resp = client.put(
        "/api/presence/me",
        json={"visible": True},
        headers=_headers(token),
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["visible"] is True
