"""Focused access-notification regression tests: no app imports, ORM or network.

Run this file directly with Python/unittest, not pytest/conftest. Production
functions are compiled from their AST; only dependencies are replaced by fakes.
Provider protocol/confirmation is covered separately by the e-mail service.
"""

import ast
from dataclasses import dataclass
from html import escape, unescape
from html.parser import HTMLParser
import logging
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock


BACKEND = Path(__file__).resolve().parents[1]
NOTIFICAR = BACKEND / "app/services/notificar.py"
EMAIL_API = BACKEND / "app/api/email.py"


def load_functions(path, names, namespace):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    selected = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in names:
            node.decorator_list = []
            selected.append(node)
    if {node.name for node in selected} != set(names):
        raise AssertionError(f"Missing production functions in {path}")
    module = ast.Module(
        body=[ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0), *selected],
        type_ignores=[],
    )
    exec(compile(ast.fix_missing_locations(module), str(path), "exec"), namespace)
    return namespace


@dataclass
class SendResult:
    enviado: bool
    erro: str | None = None


class LogSession:
    def __init__(self):
        self.rows = []
        self.commits = 0
        self.closed = False

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.closed = True

    def add(self, row):
        self.rows.append(row)

    def commit(self):
        self.commits += 1


class LinkParser(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.links = []
        self.tags = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        if tag == "a":
            self.links.append(dict(attrs)["href"])


class AccessNotificationTransportTest(unittest.TestCase):
    def setUp(self):
        self.settings = SimpleNamespace(
            public_url="https://corvia.example.test", smtp_configurado=False,
            mail360_configurado=True, email_transacional_configurado=True,
        )
        self.provider = Mock(return_value=(True, None))
        service = {
            "settings": self.settings,
            "ResultadoEnvioInstitucional": SendResult,
            "_normalizar_branding": lambda text: text,
            "_texto_simples_de_html": lambda html: unescape(html),
            "_enviar_por_provider": self.provider,
            "EmailLog": SimpleNamespace,
        }
        # Exercise the real institutional orchestration and EmailLog commit,
        # without importing configuration, SQLAlchemy, credentials or conftest.
        load_functions(BACKEND / "app/services/emails_legacy.py", {"_registrar_log"}, service)
        load_functions(BACKEND / "app/services/emails.py", {"enviar_institucional_paciente"}, service)
        self.send = Mock(wraps=service["enviar_institucional_paciente"])
        self.sessions = []

        def new_session():
            session = LogSession()
            self.sessions.append(session)
            return session

        self.session_factory = Mock(side_effect=new_session)
        self.admins = [
            SimpleNamespace(id=7, email="admin-one@example.test"),
            SimpleNamespace(id=8, email="admin-two@example.test"),
        ]
        self.namespace = load_functions(NOTIFICAR, {
            "tentar_enviar_email", "tentar_enviar_email_transacional",
            "notificar_admins_nova_solicitacao", "notificar_admins_kyc_manual",
        }, {
            "settings": self.settings, "escape": escape,
            "SessionLocal": self.session_factory,
            "emails": SimpleNamespace(enviar_institucional_paciente=self.send),
            "log": logging.getLogger("isolated.access.notification"),
            "_admins_ativos": Mock(return_value=self.admins),
            "smtplib": SimpleNamespace(SMTP=Mock(side_effect=AssertionError("No real SMTP"))),
        })

    def notify(self, **overrides):
        args = {
            "destinatario": "owner@example.test", "assunto": "Recuperação DEMO",
            "corpo": "Link: {DOMINIO}/redefinir-senha?token=DEMO-ONLY&alvo=email",
            "user_id": 23, "tipo_log": "recuperar_senha_email",
            "link": "{DOMINIO}/redefinir-senha?token=DEMO-ONLY&alvo=email",
            **overrides,
        }
        return self.namespace["tentar_enviar_email_transacional"](**args)

    def test_mail360_without_smtp_uses_institutional_pipeline_and_isolated_log(self):
        self.assertTrue(self.notify())
        self.provider.assert_called_once()
        self.send.assert_called_once()
        session = self.sessions[0]
        self.assertIs(self.send.call_args.args[0], session)
        self.assertTrue(session.closed)
        self.assertEqual(session.commits, 1)
        self.assertEqual(vars(session.rows[0]), {
            "tipo": "recuperar_senha_email", "destinatario": "owner@example.test",
            "user_id": 23, "chave_idempotencia": None, "sucesso": True, "erro": None,
        })
        self.assertNotIn("DEMO-ONLY", repr(session.rows))
        self.namespace["smtplib"].SMTP.assert_not_called()

    def test_html_is_escaped_and_reset_link_preserves_token_and_target(self):
        self.assertTrue(self.notify(corpo=(
            '<img src="https://outside.invalid/pixel"> & "DEMO"\n'
            "{DOMINIO}/redefinir-senha?token=DEMO-ONLY&alvo=email"
        )))
        html = self.send.call_args.kwargs["html"]
        parsed = LinkParser(html)
        self.assertNotIn("img", parsed.tags)
        self.assertIn("&lt;img", html)
        self.assertIn("<br>", html)
        self.assertEqual(parsed.links, [
            "https://corvia.example.test/redefinir-senha?token=DEMO-ONLY&alvo=email",
        ])

    def test_config_unavailable_logs_failure_without_trying_a_transport(self):
        self.settings.email_transacional_configurado = False
        self.assertFalse(self.notify())
        self.provider.assert_not_called()
        self.assertFalse(self.sessions[0].rows[0].sucesso)
        self.assertTrue(self.sessions[0].closed)

    def test_provider_failure_is_logged_without_retry_or_success_claim(self):
        self.provider.return_value = (False, "Provider unavailable (fixture)")
        self.assertFalse(self.notify())
        self.provider.assert_called_once()
        row = self.sessions[0].rows[0]
        self.assertFalse(row.sucesso)
        self.assertEqual(row.erro, "Provider unavailable (fixture)")

    def test_unexpected_error_is_best_effort_and_does_not_log_secrets(self):
        self.send.side_effect = RuntimeError("SECRET-TOKEN owner@example.test body")
        with self.assertLogs("isolated.access.notification", level="WARNING") as captured:
            self.assertFalse(self.notify())
        self.assertTrue(self.sessions[0].closed)
        self.assertEqual(self.send.call_count, 1)
        output = " ".join(captured.output)
        self.assertIn("RuntimeError", output)
        self.assertNotIn("SECRET-TOKEN", output)
        self.assertNotIn("owner@example.test", output)
        self.assertNotIn("DEMO-ONLY", output)

    def test_session_creation_failure_remains_best_effort(self):
        self.session_factory.side_effect = RuntimeError("Unavailable database fixture")
        with self.assertLogs("isolated.access.notification", level="WARNING"):
            self.assertFalse(self.notify())
        self.send.assert_not_called()

    def test_admin_signup_uses_same_recipients_without_committing_business_session(self):
        business = Mock()
        self.namespace["notificar_admins_nova_solicitacao"](
            business, "<b>Cadastro DEMO</b>", "applicant@example.test",
        )
        self.namespace["_admins_ativos"].assert_called_once_with(business)
        self.assertEqual(self.send.call_count, 2)
        for call, admin in zip(self.send.call_args_list, self.admins):
            self.assertEqual(call.kwargs["destinatario"], admin.email)
            self.assertEqual(call.kwargs["user_id"], admin.id)
            self.assertEqual(call.kwargs["tipo_log"], "admin_nova_solicitacao")
            self.assertNotIn("<b>", call.kwargs["html"])
            self.assertEqual(LinkParser(call.kwargs["html"]).links, ["https://corvia.example.test/admin"])
            self.assertIsNot(call.args[0], business)
        business.commit.assert_not_called()
        business.rollback.assert_not_called()

    def test_manual_kyc_alert_is_text_only_and_does_not_commit_business_session(self):
        business = Mock()
        self.namespace["notificar_admins_kyc_manual"](
            business, nome="Pessoa DEMO", email="applicant@example.test",
            motivo="Revisão <manual> & independente",
        )
        self.assertEqual(self.send.call_count, 2)
        for call, admin in zip(self.send.call_args_list, self.admins):
            self.assertEqual(call.kwargs["destinatario"], admin.email)
            self.assertEqual(call.kwargs["user_id"], admin.id)
            self.assertEqual(call.kwargs["tipo_log"], "admin_kyc_manual")
            self.assertIn("Revisão &lt;manual&gt; &amp; independente", call.kwargs["html"])
            self.assertEqual(set(call.kwargs), {"user_id", "destinatario", "assunto", "html", "tipo_log"})
        business.commit.assert_not_called()
        business.rollback.assert_not_called()

    def test_one_failed_admin_delivery_does_not_suppress_the_next(self):
        self.provider.side_effect = [(False, "Fixture unavailable"), (True, None)]
        self.namespace["notificar_admins_nova_solicitacao"](Mock(), "DEMO", "applicant@example.test")
        self.assertEqual(self.provider.call_count, 2)
        self.assertEqual([session.rows[0].sucesso for session in self.sessions], [False, True])

    def test_legacy_generic_alert_still_uses_its_existing_smtp_guard(self):
        self.assertFalse(self.namespace["tentar_enviar_email"]("legacy@example.test", "DEMO", "DEMO"))
        self.send.assert_not_called()
        self.session_factory.assert_not_called()


class EmailRecoveryContractTest(unittest.TestCase):
    def setUp(self):
        self.events = []
        self.user = SimpleNamespace(id=23, email="primary@example.test", investidor=False, is_active=True)
        self.account = SimpleNamespace(user_id=23, email_address="locked@corvia.example.test", status="ativa")
        self.db = Mock()
        self.db.commit.side_effect = lambda: self.events.append("token_commit")
        self.send = Mock(side_effect=lambda **_: self.events.append("send") or True)
        field = Mock()
        field.__eq__ = Mock(return_value="normalized address condition")
        status_field = Mock()
        status_field.__eq__ = Mock(return_value="active account condition")
        user_id_field = Mock()
        user_id_field.__eq__ = Mock(return_value="owner condition")
        token_created_at = Mock()
        token_created_at.__gt__ = Mock(return_value="cooldown condition")
        token_user_id, token_target = Mock(), Mock()
        token_user_id.__eq__ = Mock(return_value="token owner condition")
        token_target.__eq__ = Mock(return_value="token target condition")
        class ResetToken(SimpleNamespace):
            id = object()
            user_id, alvo, created_at = token_user_id, token_target, token_created_at

            def __init__(self, **values):
                super().__init__(token="DEMO-ONLY", **values)

        account_model = SimpleNamespace(email_address=field, status=status_field)
        user_model = SimpleNamespace(id=user_id_field)
        account_query, user_query, recent_query = Mock(), Mock(), Mock()
        account_query.filter.return_value.first.side_effect = lambda: self.account
        user_query.filter.return_value.with_for_update.return_value.populate_existing.return_value.first.side_effect = lambda: self.user
        self.recent = None
        recent_query.filter.return_value.first.side_effect = lambda: self.recent

        def query(model):
            if model is account_model:
                return account_query
            if model is user_model:
                return user_query
            self.assertIs(model, ResetToken.id)
            return recent_query

        self.db.query.side_effect = query
        self.namespace = load_functions(EMAIL_API, {"esqueci_senha_email"}, {
            "Depends": lambda _: None, "get_db": None,
            "EmailAccount": account_model, "User": user_model,
            "PasswordResetToken": ResetToken,
            "tentar_enviar_email_transacional": self.send,
        })
        self.address_field = field
        self.status_field = status_field
        self.recovery_address = None
        channel = load_functions(BACKEND / "app/services/account_recovery.py", {"destinatario_seguro"}, {
            "obter_email_recuperacao": lambda _db, _id: self.recovery_address,
        })
        self.namespace["destinatario_seguro"] = channel["destinatario_seguro"]

    def recover(self):
        return self.namespace["esqueci_senha_email"](
            SimpleNamespace(endereco="  LOCKED@CORVIA.EXAMPLE.TEST  "), self.db,
        )

    def test_reset_target_primary_recipient_and_token_commit_order_are_preserved(self):
        result = self.recover()
        self.assertEqual(self.events, ["token_commit", "send"])
        self.address_field.__eq__.assert_called_once_with("locked@corvia.example.test")
        self.status_field.__eq__.assert_called_once_with("ativa")
        token = self.db.add.call_args.args[0]
        self.assertEqual((token.user_id, token.alvo), (23, "email"))
        self.send.assert_called_once()
        args = self.send.call_args.kwargs
        self.assertEqual(args["destinatario"], "primary@example.test")
        self.assertEqual(args["user_id"], 23)
        self.assertEqual(args["tipo_log"], "recuperar_senha_email")
        self.assertEqual(args["link"], "{DOMINIO}/redefinir-senha?token=DEMO-ONLY&alvo=email")
        self.assertIn("válido por 2 horas", args["corpo"])
        self.assertEqual(result, {"nota": "Se o endereço existir e estiver ativo, um link de redefinição foi gerado."})

    def test_missing_account_keeps_same_response_without_token_or_send(self):
        self.account = None
        result = self.recover()
        self.assertEqual(result, {"nota": "Se o endereço existir e estiver ativo, um link de redefinição foi gerado."})
        self.db.add.assert_not_called()
        self.db.commit.assert_not_called()
        self.send.assert_not_called()

    def test_locked_primary_uses_independent_recovery_channel(self):
        self.user.email = self.account.email_address
        self.recovery_address = "  INDEPENDENT@EXAMPLE.TEST  "
        self.recover()
        self.assertEqual(self.send.call_args.kwargs["destinatario"], "independent@example.test")
        self.assertEqual(self.events, ["token_commit", "send"])

    def test_recovery_channel_is_preferred_even_when_primary_is_external(self):
        self.recovery_address = "recovery@example.test"
        self.recover()
        self.assertEqual(self.send.call_args.kwargs["destinatario"], "recovery@example.test")

    def test_without_independent_channel_no_token_or_send_and_same_public_response(self):
        expected = {"nota": "Se o endereço existir e estiver ativo, um link de redefinição foi gerado."}
        self.user.email = "  LOCKED@CORVIA.EXAMPLE.TEST  "
        for recovery in (None, "locked@corvia.example.test", ""):
            with self.subTest(recovery=recovery):
                self.recovery_address = recovery
                self.assertEqual(self.recover(), expected)
                self.db.add.assert_not_called()
                self.db.commit.assert_not_called()
                self.send.assert_not_called()

    def test_missing_owner_keeps_same_response_without_token_or_send(self):
        self.user = None
        result = self.recover()
        self.assertEqual(result, {"nota": "Se o endereço existir e estiver ativo, um link de redefinição foi gerado."})
        self.db.add.assert_not_called()
        self.send.assert_not_called()

    def test_investor_keeps_same_response_without_token_write_or_dispatch(self):
        self.user.investidor = True
        token_factory = Mock(side_effect=AssertionError("Investor must not receive a personal reset token"))
        self.namespace["PasswordResetToken"] = token_factory
        result = self.recover()
        self.assertEqual(result, {"nota": "Se o endereço existir e estiver ativo, um link de redefinição foi gerado."})
        token_factory.assert_not_called()
        self.db.add.assert_not_called()
        self.db.commit.assert_not_called()
        self.db.flush.assert_not_called()
        self.send.assert_not_called()
        self.assertEqual(self.events, [])

    def test_delivery_failure_keeps_same_anti_enumeration_response_without_retry(self):
        self.send.side_effect = None
        self.send.return_value = False
        result = self.recover()
        self.assertEqual(result, {"nota": "Se o endereço existir e estiver ativo, um link de redefinição foi gerado."})
        self.send.assert_called_once()
        self.db.commit.assert_called_once()

    def test_recent_token_or_inactive_owner_keeps_neutral_response_without_dispatch(self):
        for recent, active in ((SimpleNamespace(id=1), True), (None, False)):
            with self.subTest(recent=recent is not None, active=active):
                self.recent, self.user.is_active = recent, active
                self.assertEqual(self.recover(), {
                    "nota": "Se o endereço existir e estiver ativo, um link de redefinição foi gerado.",
                })
                self.db.add.assert_not_called()
                self.db.commit.assert_not_called()
                self.send.assert_not_called()

    def test_http_contract_remains_202_and_router_import_uses_scoped_adapter(self):
        tree = ast.parse(EMAIL_API.read_text(encoding="utf-8"))
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "esqueci_senha_email")
        decorator = function.decorator_list[0]
        self.assertEqual(decorator.args[0].value, "/esqueci-senha")
        self.assertEqual(next(k.value.value for k in decorator.keywords if k.arg == "status_code"), 202)
        notification_import = next(node for node in tree.body if isinstance(node, ast.ImportFrom) and node.module == "app.services.notificar")
        self.assertEqual([alias.name for alias in notification_import.names], ["tentar_enviar_email_transacional"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
