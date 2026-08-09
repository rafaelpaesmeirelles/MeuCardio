"""Auditoria AUTH/SESSION (issue #52, subfase 1) — revogação de sessão da
caixa de e-mail (CorvIA Mail, token `scope=email`) ao trocar a senha DA CAIXA.

Achado (severidade média, ver relatório da subfase 1): a sessão principal da
conta Corvia tem revogação de token por troca de senha — `User.password_hash`
tem um listener SQLAlchemy que grava `sessions_valid_after` a cada rotação
(`app/models/user.py`), e `current_user()` rejeita qualquer JWT emitido antes
desse marco (coberto por `test_session_revocation.py`). A sessão separada da
caixa de e-mail (`EmailAccount`, token `scope=email`) **não tem equivalente**:
não existe nenhum campo `sessions_valid_after` (ou análogo) em
`app/models/email_account.py`, e `current_email_account()` (`app/core/
security.py`) só confere `status == "ativa"`, nunca o instante de emissão do
token contra o de uma eventual troca de senha.

Consequência prática: um token `scope=email` já emitido continua válido até
a própria expiração (até 30 dias corridos, com "permanecer conectado" — ver
`SESSAO_EMAIL_PERSISTENTE_MINUTOS`/renovação deslizante em
`app/api/email_session.py`) mesmo depois de o médico redefinir a senha da
caixa — seja reativando (`POST /api/email/conta`) seja pelo link de
recuperação (`POST /api/auth/redefinir-senha`, `alvo="email"`). O token
também fica em `localStorage`/`sessionStorage` no navegador (ver
`frontend/src/lib/apiEmail.ts`), acessível a JavaScript — mais exposto a
roubo via XSS do que o cookie HttpOnly da sessão principal —, o que torna a
ausência de revogação mais relevante do que seria só pela duração.

Os dois testes abaixo documentam o comportamento ATUAL, não o desejado: o
token emitido antes da troca de senha continua servindo depois dela. Se um
marcador de revogação for adicionado a `EmailAccount` numa subfase futura
(mudança de esquema, fora do escopo desta auditoria — que é aditiva e não
faz migração de banco), os `assert` marcados abaixo devem passar a esperar
401, não 200.
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


def test_email_session_token_survives_password_change_via_reactivation(
    client, criar_usuario, db, monkeypatch_mail360,
):
    """🚨 GAP: reativar a caixa com senha nova (`POST /api/email/conta` numa
    conta que já existe) NÃO revoga o token `scope=email` emitido antes da
    troca — ao contrário da sessão principal, que revoga na hora (ver
    `test_authenticated_password_change_revokes_previous_tokens`, em
    `test_session_revocation.py`)."""
    user, token_app = criar_usuario(email="revogacao.email1@teste.local")
    _dar_assinatura_email_ativa(db, user)

    ativado = _ativar_caixa(client, token_app, "senha-original-1")
    endereco = ativado["email_address"]

    login = client.post("/api/email/entrar", json={"endereco": endereco, "senha": "senha-original-1"})
    assert login.status_code == 200, login.text
    token_antigo = login.json()["access_token"]
    assert client.get("/api/email/eu", headers={"Authorization": f"Bearer {token_antigo}"}).status_code == 200

    # O médico "troca a senha" pensando estar encerrando o acesso de quem
    # tinha o token antigo — reativação atualiza a senha sem recriar a conta.
    trocar = client.post(
        "/api/email/conta",
        json={"senha": "senha-nova-2", "aceite_lgpd": True},
        headers={"Authorization": f"Bearer {token_app}"},
    )
    assert trocar.status_code == 201, trocar.text
    assert trocar.json()["ja_existia"] is True

    # Comportamento ATUAL (o achado desta auditoria): o token emitido ANTES
    # da troca continua válido depois dela.
    ainda_valido = client.get("/api/email/eu", headers={"Authorization": f"Bearer {token_antigo}"})
    assert ainda_valido.status_code == 200, (
        "Se este assert falhar, o gap de revogação foi corrigido — troque "
        "para esperar 401 e remova este comentário/achado do relatório."
    )

    # Confirma que o gap é estritamente sobre o TOKEN já emitido, não sobre
    # a senha em si: a senha antiga já não serve para logar de novo.
    login_com_senha_antiga = client.post(
        "/api/email/entrar", json={"endereco": endereco, "senha": "senha-original-1"},
    )
    assert login_com_senha_antiga.status_code == 401


def test_email_session_token_survives_password_reset_via_recovery_link(
    client, criar_usuario, db, monkeypatch_mail360,
):
    """Mesmo gap pelo outro caminho de troca de senha da caixa: link de
    recuperação de uso único (`PasswordResetToken(alvo='email')`,
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

    ainda_valido = client.get("/api/email/eu", headers={"Authorization": f"Bearer {token_antigo}"})
    assert ainda_valido.status_code == 200, (
        "Se este assert falhar, o gap de revogação foi corrigido — troque "
        "para esperar 401 e remova este comentário/achado do relatório."
    )

    login_com_senha_antiga = client.post(
        "/api/email/entrar", json={"endereco": endereco, "senha": "senha-original-3"},
    )
    assert login_com_senha_antiga.status_code == 401


def test_email_session_token_survives_main_account_deactivation(
    client, criar_usuario, db, monkeypatch_mail360,
):
    """🚨 GAP relacionado, mesma causa raiz: `current_email_account()` (app/
    core/security.py) nunca consulta `User.is_active` nem qualquer marco de
    revogação — só `EmailAccount.status == "ativa"`. Um admin que desativa a
    conta principal de um médico (`PATCH /api/admin/users/{id}/ativo?
    ativo=false`, ex.: banimento por má conduta) bloqueia `current_user()`
    (a conta Corvia) na hora, mas a caixa de e-mail (CorvIA Mail) continua
    acessível pelo token scope=email já emitido — o médico banido mantém
    acesso à própria caixa (e pode inclusive renová-la via
    POST /api/email/renovar-sessao) mesmo sem poder mais logar na
    plataforma."""
    user, token_app = criar_usuario(email="revogacao.email5@teste.local")
    admin, admin_token = criar_usuario(email="admin.banimento@teste.local", role="admin")
    _dar_assinatura_email_ativa(db, user)

    ativado = _ativar_caixa(client, token_app, "senha-conta-banida-1")
    endereco = ativado["email_address"]
    login = client.post("/api/email/entrar", json={"endereco": endereco, "senha": "senha-conta-banida-1"})
    assert login.status_code == 200, login.text
    token_email = login.json()["access_token"]

    # A conta principal é desativada por um admin (ex.: banimento).
    desativar = client.patch(
        f"/api/admin/users/{user.id}/ativo",
        params={"ativo": False},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert desativar.status_code == 200, desativar.text
    assert desativar.json()["is_active"] is False

    # A sessão principal já não funciona mais — como esperado.
    assert client.get(
        "/api/auth/me", headers={"Authorization": f"Bearer {token_app}"}
    ).status_code == 401

    # Comportamento ATUAL (o achado): a sessão da caixa de e-mail permanece
    # utilizável, inclusive renovável, mesmo com a conta principal banida.
    ainda_valido = client.get("/api/email/eu", headers={"Authorization": f"Bearer {token_email}"})
    assert ainda_valido.status_code == 200, (
        "Se este assert falhar, current_email_account() passou a checar "
        "User.is_active — atualize o teste para esperar 401 e o relatório "
        "da auditoria."
    )
    renovar = client.post(
        "/api/email/renovar-sessao", headers={"Authorization": f"Bearer {token_email}"}
    )
    assert renovar.status_code == 200, renovar.text
