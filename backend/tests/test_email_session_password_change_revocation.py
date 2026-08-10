"""Auditoria AUTH/SESSION (issue #52) — revogação de sessão da caixa de
e-mail (CorvIA Mail, token `scope=email`) ao trocar a senha DA CAIXA.

Histórico: a subfase 1 (09/08/2026) documentou o gap — a sessão principal
já revogava token por troca de senha (`User.password_hash`, listener
SQLAlchemy que grava `sessions_valid_after`), a sessão separada da caixa
não tinha equivalente. **Corrigido no gate final** (10/08/2026):
`EmailAccount` ganhou o mesmo campo/listener (migração `525c83496f23`), e
`current_email_account()` (app/core/security.py) passou a rejeitar
qualquer token com `session_iat` anterior ao marco — mesmo mecanismo
genérico (`_sessao_valida_para_usuario`) que a sessão principal já usava.

Também corrigido, mesmo gate, achado relacionado: `current_email_account()`
nunca consultava `User.is_active` da conta principal — um médico banido
mantinha acesso à própria caixa via token já emitido. Agora as duas
sessões (principal e caixa) caem juntas.

Os testes abaixo confirmam a correção: token emitido ANTES da troca para
de servir IMEDIATAMENTE depois dela, "permanecer conectado" não sobrevive,
renovação não ressuscita sessão revogada, e o cenário de múltiplos
dispositivos/concorrência (dois tokens ativos ao mesmo tempo, um dispositivo
troca a senha, o outro perde acesso na próxima chamada) funciona como na
sessão principal.
"""
from datetime import datetime, timedelta, timezone

from app.core.security import create_access_token
from app.models.password_reset import PasswordResetToken
from app.models.subscription import TIPO_EMAIL, Subscription


def _dar_assinatura_email_ativa(db, user, status="ativo"):
    sub = Subscription(user_id=user.id, kind=TIPO_EMAIL, status=status)
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub


def _ativar_caixa(client, token_app, senha, local_part=None):
    if local_part is None:
        sugestao = client.get(
            "/api/email/sugestao-endereco", headers={"Authorization": f"Bearer {token_app}"},
        )
        local_part = sugestao.json()["local_part"]
    resp = client.post(
        "/api/email/conta",
        json={"senha": senha, "aceite_lgpd": True, "local_part": local_part},
        headers={"Authorization": f"Bearer {token_app}"},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_email_session_token_is_revoked_on_password_change_via_reactivation(
    client, criar_usuario, db, monkeypatch_mail360,
):
    """Reativar a caixa com senha nova (`POST /api/email/conta` numa conta
    que já existe) revoga IMEDIATAMENTE o token `scope=email` emitido antes
    da troca — mesmo comportamento já garantido para a sessão principal
    (`test_authenticated_password_change_revokes_previous_tokens`, em
    `test_session_revocation.py`)."""
    user, token_app = criar_usuario(email="revogacao.email1@teste.local")
    _dar_assinatura_email_ativa(db, user)

    ativado = _ativar_caixa(client, token_app, "senha-original-1")
    endereco = ativado["email_address"]

    login = client.post("/api/email/entrar", json={"endereco": endereco, "senha": "senha-original-1"})
    assert login.status_code == 200, login.text
    token_antigo = login.json()["access_token"]
    assert client.get("/api/email/eu", headers={"Authorization": f"Bearer {token_antigo}"}).status_code == 200

    trocar = client.post(
        "/api/email/conta",
        json={"senha": "senha-nova-2", "aceite_lgpd": True},
        headers={"Authorization": f"Bearer {token_app}"},
    )
    assert trocar.status_code == 201, trocar.text
    assert trocar.json()["ja_existia"] is True

    # O token emitido ANTES da troca não serve mais.
    revogado = client.get("/api/email/eu", headers={"Authorization": f"Bearer {token_antigo}"})
    assert revogado.status_code == 401

    # A senha antiga também já não serve para logar de novo.
    login_com_senha_antiga = client.post(
        "/api/email/entrar", json={"endereco": endereco, "senha": "senha-original-1"},
    )
    assert login_com_senha_antiga.status_code == 401

    # O médico consegue logar de novo com a senha nova e usar a caixa.
    login_novo = client.post("/api/email/entrar", json={"endereco": endereco, "senha": "senha-nova-2"})
    assert login_novo.status_code == 200, login_novo.text
    token_novo = login_novo.json()["access_token"]
    assert client.get("/api/email/eu", headers={"Authorization": f"Bearer {token_novo}"}).status_code == 200


def test_email_session_token_is_revoked_on_password_reset_via_recovery_link(
    client, criar_usuario, db, monkeypatch_mail360,
):
    """Mesma correção pelo outro caminho de troca de senha da caixa: link
    de recuperação de uso único (`PasswordResetToken(alvo='email')`,
    `POST /api/auth/redefinir-senha`)."""
    user, token_app = criar_usuario(email="revogacao.email2@teste.local")
    _dar_assinatura_email_ativa(db, user)

    ativado = _ativar_caixa(client, token_app, "senha-original-3")
    endereco = ativado["email_address"]

    login = client.post("/api/email/entrar", json={"endereco": endereco, "senha": "senha-original-3"})
    assert login.status_code == 200, login.text
    token_antigo = login.json()["access_token"]
    assert client.get("/api/email/eu", headers={"Authorization": f"Bearer {token_antigo}"}).status_code == 200

    reset = PasswordResetToken(
        user_id=user.id, alvo="email",
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    db.add(reset)
    db.commit()
    db.refresh(reset)

    redefinir = client.post(
        "/api/auth/redefinir-senha",
        json={"token": reset.token, "nova_senha": "senha-pos-reset-4"},
    )
    assert redefinir.status_code == 200, redefinir.text

    revogado = client.get("/api/email/eu", headers={"Authorization": f"Bearer {token_antigo}"})
    assert revogado.status_code == 401

    login_com_senha_antiga = client.post(
        "/api/email/entrar", json={"endereco": endereco, "senha": "senha-original-3"},
    )
    assert login_com_senha_antiga.status_code == 401


def test_email_session_token_is_revoked_on_main_account_deactivation(
    client, criar_usuario, db, monkeypatch_mail360,
):
    """Achado relacionado, corrigido no mesmo gate: um admin que desativa a
    conta principal de um médico (banimento) agora derruba também a
    sessão da caixa de e-mail — inclusive impedindo renová-la."""
    user, token_app = criar_usuario(email="revogacao.email5@teste.local")
    admin, admin_token = criar_usuario(email="admin.banimento@teste.local", role="admin")
    _dar_assinatura_email_ativa(db, user)

    ativado = _ativar_caixa(client, token_app, "senha-conta-banida-1")
    endereco = ativado["email_address"]
    login = client.post("/api/email/entrar", json={"endereco": endereco, "senha": "senha-conta-banida-1"})
    assert login.status_code == 200, login.text
    token_email = login.json()["access_token"]

    desativar = client.patch(
        f"/api/admin/users/{user.id}/ativo",
        params={"ativo": False},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert desativar.status_code == 200, desativar.text
    assert desativar.json()["is_active"] is False

    assert client.get(
        "/api/auth/me", headers={"Authorization": f"Bearer {token_app}"}
    ).status_code == 401

    # A sessão da caixa de e-mail agora cai junto, coerente com a principal.
    revogado = client.get("/api/email/eu", headers={"Authorization": f"Bearer {token_email}"})
    assert revogado.status_code == 401
    renovar = client.post(
        "/api/email/renovar-sessao", headers={"Authorization": f"Bearer {token_email}"}
    )
    assert renovar.status_code == 401


def test_persistent_email_session_does_not_survive_password_change(
    client, criar_usuario, db, monkeypatch_mail360,
):
    """"Permanecer conectado" (token de 30 dias,
    `SESSAO_EMAIL_PERSISTENTE_MINUTOS`) não sobrevive a uma troca de senha
    — a duração longa do token não é uma exceção à revogação."""
    user, token_app = criar_usuario(email="revogacao.persistente@teste.local")
    _dar_assinatura_email_ativa(db, user)

    ativado = _ativar_caixa(client, token_app, "senha-persistente-1")
    endereco = ativado["email_address"]

    login = client.post(
        "/api/email/entrar",
        json={"endereco": endereco, "senha": "senha-persistente-1", "permanecer_conectado": True},
    )
    assert login.status_code == 200, login.text
    token_persistente = login.json()["access_token"]
    assert client.get(
        "/api/email/eu", headers={"Authorization": f"Bearer {token_persistente}"}
    ).status_code == 200

    client.post(
        "/api/email/conta",
        json={"senha": "senha-persistente-2", "aceite_lgpd": True},
        headers={"Authorization": f"Bearer {token_app}"},
    )

    revogado = client.get("/api/email/eu", headers={"Authorization": f"Bearer {token_persistente}"})
    assert revogado.status_code == 401


def test_renewal_does_not_resurrect_a_revoked_email_session(
    client, criar_usuario, db, monkeypatch_mail360,
):
    """Renovação deslizante (`POST /api/email/renovar-sessao`) exige o
    token atual já ser válido (`Depends(current_email_account)`) — um token
    revogado não consegue se renovar e assim ressuscitar a sessão."""
    user, token_app = criar_usuario(email="revogacao.renovacao@teste.local")
    _dar_assinatura_email_ativa(db, user)

    ativado = _ativar_caixa(client, token_app, "senha-renovacao-1")
    endereco = ativado["email_address"]
    login = client.post("/api/email/entrar", json={"endereco": endereco, "senha": "senha-renovacao-1"})
    token_antigo = login.json()["access_token"]

    client.post(
        "/api/email/conta",
        json={"senha": "senha-renovacao-2", "aceite_lgpd": True},
        headers={"Authorization": f"Bearer {token_app}"},
    )

    renovar = client.post(
        "/api/email/renovar-sessao", headers={"Authorization": f"Bearer {token_antigo}"}
    )
    assert renovar.status_code == 401


def test_concurrent_devices_one_password_change_revokes_all_previous_sessions(
    client, criar_usuario, db, monkeypatch_mail360,
):
    """Múltiplos dispositivos logados na mesma caixa ao mesmo tempo: os
    DOIS tokens (emitidos em momentos diferentes, simulando dois
    dispositivos) ficam inválidos assim que QUALQUER um deles troca a
    senha — não é uma corrida vencida por quem chega primeiro, é uma marca
    de tempo que invalida tudo que veio antes dela, em qualquer
    dispositivo."""
    user, token_app = criar_usuario(email="revogacao.multidispositivo@teste.local")
    _dar_assinatura_email_ativa(db, user)

    ativado = _ativar_caixa(client, token_app, "senha-multi-1")
    endereco = ativado["email_address"]

    # "Dispositivo A" loga primeiro.
    login_a = client.post("/api/email/entrar", json={"endereco": endereco, "senha": "senha-multi-1"})
    token_a = login_a.json()["access_token"]

    # "Dispositivo B" loga um pouco depois — dois tokens simultaneamente
    # válidos para a mesma caixa, cenário real de celular + computador.
    login_b = client.post("/api/email/entrar", json={"endereco": endereco, "senha": "senha-multi-1"})
    token_b = login_b.json()["access_token"]

    assert client.get("/api/email/eu", headers={"Authorization": f"Bearer {token_a}"}).status_code == 200
    assert client.get("/api/email/eu", headers={"Authorization": f"Bearer {token_b}"}).status_code == 200

    # O dispositivo B troca a senha (ex.: suspeita de acesso indevido).
    client.post(
        "/api/email/conta",
        json={"senha": "senha-multi-2", "aceite_lgpd": True},
        headers={"Authorization": f"Bearer {token_app}"},
    )

    # Os DOIS tokens anteriores — inclusive o do próprio dispositivo que
    # pediu a troca — precisam de novo login; nenhuma sessão sobrevive.
    assert client.get("/api/email/eu", headers={"Authorization": f"Bearer {token_a}"}).status_code == 401
    assert client.get("/api/email/eu", headers={"Authorization": f"Bearer {token_b}"}).status_code == 401

    # Um novo login, com a senha nova, funciona normalmente.
    login_pos_troca = client.post("/api/email/entrar", json={"endereco": endereco, "senha": "senha-multi-2"})
    assert login_pos_troca.status_code == 200, login_pos_troca.text
    assert client.get(
        "/api/email/eu", headers={"Authorization": f"Bearer {login_pos_troca.json()['access_token']}"}
    ).status_code == 200


def test_first_activation_does_not_revoke_anything(client, criar_usuario, db, monkeypatch_mail360):
    """A ativação inicial da caixa (primeira senha, `EmailAccount` recém
    criada) não deve marcar revogação nenhuma — não existe sessão anterior
    para revogar, e o listener de `password_hash` já distingue criação de
    troca (mesmo padrão de `User.password_hash`)."""
    from app.models.email_account import EmailAccount

    user, token_app = criar_usuario(email="revogacao.primeira-ativacao@teste.local")
    _dar_assinatura_email_ativa(db, user)

    ativado = _ativar_caixa(client, token_app, "senha-primeira-1")

    conta = db.query(EmailAccount).filter(EmailAccount.email_address == ativado["email_address"]).one()
    assert conta.sessions_valid_after is None

    login = client.post(
        "/api/email/entrar", json={"endereco": ativado["email_address"], "senha": "senha-primeira-1"},
    )
    assert login.status_code == 200, login.text
    assert client.get(
        "/api/email/eu", headers={"Authorization": f"Bearer {login.json()['access_token']}"}
    ).status_code == 200
