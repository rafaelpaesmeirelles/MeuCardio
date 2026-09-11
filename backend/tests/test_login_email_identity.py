"""Integração de identidade entre tabelas; executar somente na CI PostgreSQL isolada.

Não executar este arquivo com o conftest local. Os emissores são substituídos;
nenhum teste envia e-mail ou utiliza contas/dados de produção.
"""
from concurrent.futures import ThreadPoolExecutor
from threading import Event
from time import monotonic, sleep

import pytest
from sqlalchemy import text

from app.api import auth
from app.core.db import SessionLocal
from app.models.account_recovery import AccountRecoveryEmail
from app.models.audit import AuditLog
from app.models.convidado_pre_autorizado import ConvidadoPreAutorizado
from app.models.user import User
from app.services import account_recovery, emails, notificar
from app.services.bootstrap import create_admin_if_absent


def _payload(**overrides):
    # CPF já usado pelas fixtures de cadastro do projeto; não identifica titular.
    return {**dict(full_name="Cadastro inteiramente fictício", birth_date="1980-01-01",
                   cpf="390.533.447-05", profession="Médico", council_name="CRM",
                   council_number="99999", council_state="SP", email="new@example.invalid",
                   recovery_email="new-channel@example.invalid", password="synthetic-password"), **overrides}


def _headers(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def no_email(monkeypatch):
    calls = []
    for module, name in (
        (emails, "enviar_troca_email"), (emails, "enviar_solicitacao_recebida"),
        (account_recovery, "enviar_confirmacao_canal_recuperacao"),
        (account_recovery, "enviar_acesso_aprovado"),
        (notificar, "notificar_admins_nova_solicitacao"),
    ):
        monkeypatch.setattr(module, name, lambda *args, _name=name: calls.append((_name, args)))
    return calls


@pytest.mark.parametrize("route", ["/api/auth/solicitar-acesso", "/api/auth/solicitar-acesso-com-recuperacao"])
def test_signup_rejects_another_accounts_recovery_login(route, client, db, criar_usuario, no_email):
    owner, _ = criar_usuario(email="owner@example.invalid")
    account_recovery.definir_email_recuperacao(db, owner, "occupied@example.invalid")
    db.commit()
    payload = _payload(email="occupied@example.invalid")
    if route.endswith("/solicitar-acesso"):
        payload.pop("recovery_email")
    response = client.post(route, json=payload)
    if route == "/api/auth/solicitar-acesso":
        # O middleware canônico encerra a URL legada antes do handler: não
        # reabrir cadastro sem segundo canal para exercitar o conflito abaixo.
        assert response.status_code == 410, response.text
        assert response.json()["detail"] == (
            "Este fluxo de cadastro foi substituído. Use o cadastro atual, "
            "que exige um segundo e-mail externo para recuperação de acesso."
        )
        assert response.headers["cache-control"] == "no-store"
    else:
        assert response.status_code == 409, response.text
    db.expire_all()
    assert db.query(User).filter(User.email == payload["email"]).first() is None
    assert no_email == []


@pytest.mark.parametrize("via_admin", [False, True])
@pytest.mark.parametrize("destination,expected", [("occupied@example.invalid", 409), ("own-channel@example.invalid", 422)])
def test_email_changes_preserve_foreign_and_own_recovery_channels(
    via_admin, destination, expected, client, db, criar_usuario, no_email,
):
    owner, _ = criar_usuario(email="owner@example.invalid")
    target, target_token = criar_usuario(email="target@example.invalid")
    _, admin_token = criar_usuario(email="admin@example.invalid", role="admin")
    account_recovery.definir_email_recuperacao(db, owner, "occupied@example.invalid")
    account_recovery.definir_email_recuperacao(db, target, "own-channel@example.invalid")
    db.commit()
    if via_admin:
        response = client.patch(f"/api/admin/user-management/{target.id}", headers=_headers(admin_token),
                                json={"full_name": target.full_name, "email": destination,
                                      "role": "medico", "is_active": True, "tipo_acesso": "normal"})
    else:
        response = client.post("/api/auth/trocar-email", headers=_headers(target_token),
                               json={"senha_atual": "senha-conta-123", "novo_email": destination})
    assert response.status_code == expected, response.text
    db.refresh(target)
    assert target.email == "target@example.invalid"
    assert db.get(AccountRecoveryEmail, target.id).email == "own-channel@example.invalid"
    assert no_email == []


def test_bootstrap_rejects_foreign_recovery_and_keeps_existing_account_idempotent(db, criar_usuario):
    owner, _ = criar_usuario(email="owner@example.invalid")
    account_recovery.definir_email_recuperacao(db, owner, "occupied@example.invalid")
    db.commit()
    with pytest.raises(ValueError, match="outra conta"):
        create_admin_if_absent(db, email="occupied@example.invalid", password="synthetic-password")
    db.rollback()
    password_before, name_before = owner.password_hash, owner.full_name
    existing, created = create_admin_if_absent(db, email=" OWNER@example.invalid ", password="do-not-replace")
    assert existing.id == owner.id and created is False
    assert (existing.password_hash, existing.full_name) == (password_before, name_before)
    assert existing.role == "medico"


@pytest.mark.parametrize("guest", [False, True])
def test_public_signup_rollback_keeps_preauthorization_unused_and_sends_nothing(
    guest, client, db, monkeypatch, no_email,
):
    pre = ConvidadoPreAutorizado(email="new@example.invalid")
    if guest:
        db.add(pre)
        db.commit()
    original = account_recovery.definir_email_recuperacao

    def fail_after_flush(*args):
        original(*args)
        raise ValueError("Este e-mail já está vinculado a outra conta CorVIA.")

    monkeypatch.setattr(account_recovery, "definir_email_recuperacao", fail_after_flush)
    response = client.post("/api/auth/solicitar-acesso-com-recuperacao", json=_payload())
    assert response.status_code == 409, response.text
    db.expire_all()
    assert db.query(User).filter(User.email == "new@example.invalid").first() is None
    assert db.query(AccountRecoveryEmail).filter(AccountRecoveryEmail.email == "new-channel@example.invalid").first() is None
    assert db.query(AuditLog).filter(AuditLog.action == "convidado_via_pre_autorizacao").count() == 0
    if guest:
        db.refresh(pre)
        assert pre.usado_em is None and pre.usado_por_user_id is None
    assert no_email == []


@pytest.mark.parametrize("guest", [False, True])
def test_public_signup_commits_complete_state_before_any_notification(
    guest, client, db, monkeypatch, no_email,
):
    if guest:
        db.add(ConvidadoPreAutorizado(email="new@example.invalid"))
        db.commit()
    calls = []

    def observe(*_args):
        # Sessão independente: flush sem commit não pode satisfazer esta prova.
        with SessionLocal() as observer:
            user = observer.query(User).filter(User.email == "new@example.invalid").one()
            assert observer.get(AccountRecoveryEmail, user.id).email == "new-channel@example.invalid"
            assert (user.status, user.is_active, user.convidado) == (
                ("aprovado", True, True) if guest else ("pendente", False, False))
            if guest:
                pre = observer.query(ConvidadoPreAutorizado).filter(ConvidadoPreAutorizado.email == user.email).one()
                assert pre.usado_em is not None and pre.usado_por_user_id == user.id
                assert observer.query(AuditLog).filter(AuditLog.action == "convidado_via_pre_autorizacao").count() == 1
        calls.append(True)

    for module, name in ((notificar, "notificar_admins_nova_solicitacao"),
                         (emails, "enviar_solicitacao_recebida"),
                         (account_recovery, "enviar_confirmacao_canal_recuperacao"),
                         (account_recovery, "enviar_acesso_aprovado")):
        monkeypatch.setattr(module, name, observe)
    response = client.post("/api/auth/solicitar-acesso-com-recuperacao", json=_payload())
    assert response.status_code == 201, response.text
    assert bool(response.json().get("acesso_imediato")) is guest
    assert len(calls) == (2 if guest else 3)


@pytest.mark.parametrize("first", ["login", "recovery"])
@pytest.mark.parametrize("finish", ["commit", "rollback"])
def test_concurrent_login_and_recovery_serialize_and_revalidate(
    first, finish, db, criar_usuario, no_email,
):
    owner, _ = criar_usuario(email="owner@example.invalid")
    owner_id = owner.id
    shared = "race@example.invalid"
    db.execute(text("SET LOCAL lock_timeout = '5s'"))
    db.execute(text("SET LOCAL statement_timeout = '8s'"))
    if first == "login":
        data = _payload(email=shared)
        data.pop("recovery_email")
        auth._preparar_solicitacao_acesso(auth.SolicitacaoAcesso(**data), db)
    else:
        account_recovery.definir_email_recuperacao(db, owner, shared)

    started = Event()
    worker_pid = []

    def compete():
        with SessionLocal() as second:
            second.execute(text("SET LOCAL lock_timeout = '5s'"))
            second.execute(text("SET LOCAL statement_timeout = '8s'"))
            worker_pid.append(second.execute(text("SELECT pg_backend_pid()")).scalar_one())
            started.set()
            try:
                if first == "login":
                    account_recovery.definir_email_recuperacao(second, second.get(User, owner_id), shared)
                    second.commit()
                else:
                    create_admin_if_absent(second, email=shared, password="synthetic-password")
                return "accepted"
            except ValueError as exc:
                second.rollback()
                assert "outra conta" in str(exc)
                return "conflict"

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(compete)
        try:
            assert started.wait(3), "O segundo escritor não iniciou"
            deadline = monotonic() + 3
            waiting = False
            while monotonic() < deadline and not future.done():
                waiting = bool(db.execute(text(
                    "SELECT EXISTS (SELECT 1 FROM pg_locks WHERE pid=:pid "
                    "AND locktype='advisory' AND NOT granted)"
                ), {"pid": worker_pid[0]}).scalar_one())
                if waiting:
                    break
                sleep(0.02)
            assert waiting, "O segundo escritor não aguardou o lock comum de identidade"
            getattr(db, finish)()
            assert future.result(timeout=9) == ("conflict" if finish == "commit" else "accepted")
        finally:
            db.rollback()  # libera o lock mesmo se uma asserção falhar
            future.result(timeout=9)

    db.expire_all()
    login_count = db.query(User).filter(User.email == shared).count()
    recovery_count = db.query(AccountRecoveryEmail).filter(AccountRecoveryEmail.email == shared).count()
    assert login_count + recovery_count == 1
    assert not (login_count and recovery_count)
    assert no_email == []
