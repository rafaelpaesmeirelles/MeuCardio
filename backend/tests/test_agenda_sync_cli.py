"""Auditoria AUTH/SESSION → AGENDA (issue #52, subfase 4): o supervisor de
sincronização periódica (`app/services/agenda_sync_cli.sincronizar_todas`),
o próprio ponto de entrada do cron (`infra/agenda_sync_cron.sh`).

Gap encontrado na auditoria: `test_agenda_sync_supervisor.py` já cobria
pedaços isolados (`_registrar_falha`, `ESTADOS_RECUPERAVEIS`) com um `FakeDb`
de mentira, mas `sincronizar_todas()` — a orquestração real de ~150 linhas
que decide o que sincronizar por conta, classifica erro transitório vs.
reautenticação, e conta sincronizadas/falharam/puladas — nunca tinha sido
exercitada de ponta a ponta contra o banco.

`sync_integration`/`sync_contacts`/`ensure_fresh_credentials` (a lógica de
conector propriamente dita) já têm cobertura própria
(`test_agenda_connectors.py`, `test_agenda_oauth_flow.py`) — aqui eles são
sempre mockados via monkeypatch, o interesse é só a orquestração: quais
contas entram na rodada, qual preferência é respeitada, como cada tipo de
erro é classificado e propagado ao estado da integração.
"""
from app.models.agenda import CalendarIntegration
from app.services import agenda_sync_cli
from app.services.agenda_integrada.connectors import ConnectorError
from app.services.agenda_integrada.domain import store_integration_credentials
from app.services.apple_mail import AppleMailError
from app.services.yahoo_mail import YahooMailError


def _integracao(
    db, user, *, provider="google_calendar", status="connected", enabled=True,
    sync_calendar=True, sync_mail=True, contacts_enabled=False,
    capabilities=None, external_account_id="ext-1", display_name="conta@exemplo.com",
):
    integ = CalendarIntegration(
        owner_id=user.id, provider=provider, display_name=display_name,
        external_account_id=external_account_id, status=status, enabled=enabled,
        sync_calendar=sync_calendar, sync_mail=sync_mail, contacts_enabled=contacts_enabled,
        capabilities=capabilities or {"read_mail": True},
        sync_strategy="external_authoritative", configuration={},
    )
    db.add(integ)
    db.flush()
    if provider in {"yahoo_mail", "apple_icloud"}:
        store_integration_credentials(integ, {
            "username": "titular@exemplo.com", "app_specific_password": "senha-app",
        })
    else:
        store_integration_credentials(integ, {
            "access_token": "access", "refresh_token": "refresh",
            "expires_at": "2099-01-01T00:00:00+00:00", "token_type": "Bearer", "scope": "",
        })
    db.commit()
    db.refresh(integ)
    return integ


def test_disabled_integration_is_never_touched(db, criar_usuario, monkeypatch):
    user, _ = criar_usuario(email="sync.desabilitada@teste.local")
    _integracao(db, user, enabled=False)
    monkeypatch.setattr(agenda_sync_cli, "sync_integration", lambda *a, **k: (_ for _ in ()).throw(AssertionError("não deveria sincronizar conta desabilitada")))

    resultado = agenda_sync_cli.sincronizar_todas()
    assert resultado == {"sincronizadas": 0, "falharam": 0, "puladas": 0, "detalhe": []}


def test_reauth_required_account_is_excluded_from_the_round_and_counted_as_pulada(
    db, criar_usuario, monkeypatch
):
    user, _ = criar_usuario(email="sync.reauth@teste.local")
    _integracao(db, user, status="reauth_required")
    monkeypatch.setattr(agenda_sync_cli, "sync_integration", lambda *a, **k: (_ for _ in ()).throw(AssertionError("reauth_required não deve ser tentado no cron")))
    monkeypatch.setattr(agenda_sync_cli, "ensure_fresh_credentials", lambda *a, **k: (_ for _ in ()).throw(AssertionError("reauth_required não deve ser tentado no cron")))

    resultado = agenda_sync_cli.sincronizar_todas()
    assert resultado["puladas"] == 1
    assert resultado["sincronizadas"] == 0
    assert resultado["falharam"] == 0


def test_sync_calendar_false_skips_calendar_but_still_syncs_mail(db, criar_usuario, monkeypatch):
    user, _ = criar_usuario(email="sync.so-mail@teste.local")
    _integracao(db, user, sync_calendar=False, sync_mail=True)
    chamadas = []
    monkeypatch.setattr(agenda_sync_cli, "sync_integration", lambda *a, **k: chamadas.append("calendario") or (_ for _ in ()).throw(AssertionError("sync_calendar=False não deveria chamar sync_integration")))
    monkeypatch.setattr(agenda_sync_cli, "ensure_fresh_credentials", lambda *a, **k: chamadas.append("mail") or {"access_token": "novo"})

    resultado = agenda_sync_cli.sincronizar_todas()
    assert chamadas == ["mail"]
    assert resultado["sincronizadas"] == 1
    assert resultado["detalhe"][0]["calendario"] is None
    assert resultado["detalhe"][0]["mail"] == {"ok": True, "modo": "oauth"}


def test_contacts_enabled_false_skips_contacts(db, criar_usuario, monkeypatch):
    user, _ = criar_usuario(email="sync.sem-contatos@teste.local")
    _integracao(db, user, contacts_enabled=False, sync_mail=False)
    monkeypatch.setattr(agenda_sync_cli, "sync_integration", lambda db, item, *, full: {"pulled": 0})
    monkeypatch.setattr(
        agenda_sync_cli, "sync_contacts",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("contacts_enabled=False não deveria sincronizar contatos")),
    )

    resultado = agenda_sync_cli.sincronizar_todas()
    assert resultado["sincronizadas"] == 1
    assert resultado["detalhe"][0]["contatos"] is None


def test_transient_calendar_error_keeps_account_eligible_for_next_round(db, criar_usuario, monkeypatch):
    """Erro de rede/provedor indisponível é retryable — a conta continua
    'connected' (elegível ao próximo round), não vira reauth_required."""
    user, _ = criar_usuario(email="sync.transitorio@teste.local")
    integ = _integracao(db, user, sync_mail=False)

    def _falha_transitoria(db, item, *, full):
        raise ConnectorError("provider_unavailable", "Provedor fora do ar", retryable=True, status_code=503)

    monkeypatch.setattr(agenda_sync_cli, "sync_integration", _falha_transitoria)

    resultado = agenda_sync_cli.sincronizar_todas()
    assert resultado["falharam"] == 1
    assert resultado["detalhe"][0]["erro_calendario"] == "provider_unavailable"

    db.refresh(integ)
    assert integ.status == "connected"  # elegível ao próximo round, não bloqueado
    assert integ.last_error_code == "provider_unavailable"


def test_true_reauth_calendar_error_marks_account_and_excludes_next_round(db, criar_usuario, monkeypatch):
    user, _ = criar_usuario(email="sync.reauth-real@teste.local")
    integ = _integracao(db, user, sync_mail=False)

    def _reauth(db, item, *, full):
        raise ConnectorError("reauth_required", "Consentimento revogado pelo usuário", status_code=409)

    monkeypatch.setattr(agenda_sync_cli, "sync_integration", _reauth)

    primeira = agenda_sync_cli.sincronizar_todas()
    assert primeira["falharam"] == 1

    db.refresh(integ)
    assert integ.status == "reauth_required"

    # Rodada seguinte: a conta marcada não é mais tentada — some do universo
    # de sincronizadas/falharam e vira "pulada".
    monkeypatch.setattr(agenda_sync_cli, "sync_integration", lambda *a, **k: (_ for _ in ()).throw(AssertionError("não deveria tentar de novo na mesma rodada de cron")))
    segunda = agenda_sync_cli.sincronizar_todas()
    assert segunda["puladas"] == 1
    assert segunda["sincronizadas"] == 0
    assert segunda["falharam"] == 0


def test_unexpected_exception_in_one_account_does_not_abort_the_batch(db, criar_usuario, monkeypatch):
    """Concorrência/isolamento entre contas: uma conta com erro inesperado
    (bug de conector, não ConnectorError) não pode impedir as demais de
    serem sincronizadas na mesma rodada."""
    user_a, _ = criar_usuario(email="sync.explode@teste.local")
    user_b, _ = criar_usuario(email="sync.ok@teste.local")
    integ_a = _integracao(db, user_a, sync_mail=False, external_account_id="ext-a", display_name="a@exemplo.com")
    integ_b = _integracao(db, user_b, sync_mail=False, external_account_id="ext-b", display_name="b@exemplo.com")

    def _sync(db, item, *, full):
        if item.id == integ_a.id:
            raise RuntimeError("bug inesperado no conector")
        return {"pulled": 3}

    monkeypatch.setattr(agenda_sync_cli, "sync_integration", _sync)

    resultado = agenda_sync_cli.sincronizar_todas()
    assert resultado["sincronizadas"] == 1
    assert resultado["falharam"] == 1
    rotulos_ok = {d["conta"] for d in resultado["detalhe"] if d["ok"]}
    assert "google_calendar:b@exemplo.com" in rotulos_ok

    db.refresh(integ_a)
    db.refresh(integ_b)
    assert integ_a.last_error_code == "erro_inesperado"
    assert integ_a.status == "connected"  # não trava a conta, tenta de novo depois
    assert integ_b.status == "connected"
    assert integ_b.last_error_code is None


def test_imap_heartbeat_login_refused_marks_reauth_required(db, criar_usuario, monkeypatch):
    user, _ = criar_usuario(email="sync.yahoo-401@teste.local")
    integ = _integracao(
        db, user, provider="yahoo_mail", sync_calendar=False, contacts_enabled=False, sync_mail=True,
        capabilities={"read_mail": True},
    )
    monkeypatch.setattr(
        agenda_sync_cli.yahoo_mail, "diagnose",
        lambda creds: (_ for _ in ()).throw(YahooMailError("login recusado", status_code=401)),
    )

    resultado = agenda_sync_cli.sincronizar_todas()
    assert resultado["falharam"] == 1
    assert resultado["detalhe"][0]["erro_mail"] == "reauth_required"

    db.refresh(integ)
    assert integ.status == "reauth_required"


def test_imap_heartbeat_network_error_is_treated_as_transient(db, criar_usuario, monkeypatch):
    user, _ = criar_usuario(email="sync.apple-503@teste.local")
    integ = _integracao(
        db, user, provider="apple_icloud", sync_calendar=False, contacts_enabled=False, sync_mail=True,
        capabilities={"read_mail": True},
    )
    monkeypatch.setattr(
        agenda_sync_cli.apple_mail, "diagnose",
        lambda creds: (_ for _ in ()).throw(AppleMailError("servidor indisponível", status_code=503)),
    )

    resultado = agenda_sync_cli.sincronizar_todas()
    assert resultado["falharam"] == 1
    assert resultado["detalhe"][0]["erro_mail"] == "mail_provider_unavailable"

    db.refresh(integ)
    assert integ.status == "connected"  # não é falha de credencial — tenta de novo


def test_sincronizar_todas_is_idempotent_across_consecutive_successful_rounds(db, criar_usuario, monkeypatch):
    """Rodar o cron duas vezes seguidas sobre a mesma conta já saudável
    produz o mesmo resultado nas duas vezes — nenhum efeito colateral
    cumulativo (contador de sincronizadas sempre 1, estado sempre
    'connected', sem duplicar nada)."""
    user, _ = criar_usuario(email="sync.idempotente@teste.local")
    _integracao(db, user, sync_mail=False, contacts_enabled=False)
    monkeypatch.setattr(agenda_sync_cli, "sync_integration", lambda db, item, *, full: {"pulled": 1})

    primeira = agenda_sync_cli.sincronizar_todas()
    segunda = agenda_sync_cli.sincronizar_todas()

    assert primeira["sincronizadas"] == segunda["sincronizadas"] == 1
    assert primeira["falharam"] == segunda["falharam"] == 0
    assert primeira["puladas"] == segunda["puladas"] == 0
