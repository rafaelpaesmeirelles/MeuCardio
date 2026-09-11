"""Reenvio administrativo: funções reais, sem importar app/config/banco.

Execução local segura: python backend/tests/test_admin_access_resend_no_db.py
Os únicos efeitos são sobre objetos em memória; não usa conftest ou transporte.
"""

import ast
import logging
from pathlib import Path
from types import SimpleNamespace
import unittest


APP = Path(__file__).resolve().parents[1] / "app"


def load_functions(relative_path, names, namespace):
    source = ast.parse((APP / relative_path).read_text())
    selected = []
    for node in source.body:
        if isinstance(node, ast.FunctionDef) and node.name in names:
            node.decorator_list = []
            selected.append(node)
    assert {node.name for node in selected} == set(names)
    module = ast.Module(
        body=[ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0), *selected],
        type_ignores=[],
    )
    exec(compile(ast.fix_missing_locations(module), str(APP / relative_path), "exec"), namespace)


class Field:
    def __init__(self, name):
        self.name = name

    def __eq__(self, value):
        return self.name, value

    def is_(self, value):
        return self.name, value


class EmailLog(SimpleNamespace):
    tipo = Field("tipo")
    chave_idempotencia = Field("chave_idempotencia")
    sucesso = Field("sucesso")


class Query:
    def __init__(self, rows):
        self.rows = rows

    def filter(self, *conditions):
        return Query([row for row in self.rows if all(getattr(row, key) == value for key, value in conditions)])

    def first(self):
        return next(iter(self.rows), None)


class HTTPException(Exception):
    def __init__(self, status_code, detail):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


class AccessResendTests(unittest.TestCase):
    def setUp(self):
        self.user = SimpleNamespace(
            id=9001, email="login@example.invalid", full_name="Pessoa de Demonstração",
            is_active=True, status="aprovado", investidor=False,
        )
        self.channel = "recuperacao@example.invalid"
        self.logs = []
        self.deliveries = []
        self.provider_ok = True
        self.closed = 0
        self.User = type("User", (), {})
        self.Recovery = type("AccountRecoveryEmail", (), {})
        self.db = SimpleNamespace(
            get=self.get, query=lambda _model: Query(self.logs), add=self.logs.append,
            commit=lambda: None, close=self.close,
        )
        env = {
            "EmailLog": EmailLog, "settings": SimpleNamespace(
                email_transacional_configurado=True, public_url="https://example.invalid",
            ), "log": logging.getLogger("isolated-resend"),
            "_normalizar_branding": lambda value: value,
            "_renderizar": lambda _template, context: (context["link_login"], "texto demonstrativo"),
            "_enviar_por_provider": self.provider,
        }
        load_functions("services/emails_legacy.py", {"_ja_enviado", "_registrar_log"}, env)
        load_functions("services/emails.py", {"_enviar"}, env)
        env.update({
            "User": self.User, "AccountRecoveryEmail": self.Recovery,
            "SessionLocal": lambda: self.db, "emails": SimpleNamespace(_enviar=env["_enviar"]),
        })
        load_functions("services/account_recovery.py", {
            "obter_email_recuperacao", "destinatario_seguro", "enviar_acesso_aprovado",
        }, env)
        self.send = env["enviar_acesso_aprovado"]
        self.tasks = []
        env.update({
            "account_recovery": SimpleNamespace(enviar_acesso_aprovado=self.send),
            "HTTPException": HTTPException, "Depends": lambda dependency: dependency,
            "get_db": lambda: None, "require_admin": lambda: None,
            "admin_api": SimpleNamespace(decidir_solicitacao=lambda *_args: {"status": "aprovado"}),
        })
        load_functions("api/account_access_admin.py", {
            "admin_reenviar_acesso", "decidir_solicitacao_com_notificacao",
        }, env)
        self.resend = env["admin_reenviar_acesso"]
        self.approve = env["decidir_solicitacao_com_notificacao"]

    def get(self, model, user_id):
        if user_id != 9001:
            return None
        if model is self.User:
            return self.user
        if model is self.Recovery and self.channel:
            return SimpleNamespace(email=self.channel)
        return None

    def close(self):
        self.closed += 1

    def provider(self, destination, subject, html, text):
        self.deliveries.append((destination, subject, html, text))
        return self.provider_ok, None if self.provider_ok else "Falha fictícia do gateway"

    def prior_success(self):
        self.logs.append(EmailLog(
            tipo="acesso_aprovado", chave_idempotencia="acesso_aprovado:9001", sucesso=True,
        ))

    def test_manual_resend_dispatches_after_previous_success(self):
        self.prior_success()
        self.assertEqual(self.resend(9001, self.db, object()), {"ok": True})
        self.assertEqual(len(self.deliveries), 1)
        self.assertEqual(self.deliveries[0][0], self.channel)
        self.assertIsNone(self.logs[-1].chave_idempotencia)
        self.assertTrue(self.logs[-1].sucesso)
        self.assertEqual(self.closed, 1)

    def test_automatic_approval_stays_deduplicated(self):
        self.assertTrue(self.send(9001))
        self.assertTrue(self.send(9001))
        self.assertEqual(len(self.deliveries), 1)
        self.assertEqual(self.logs[-1].chave_idempotencia, "acesso_aprovado:9001")

    def test_approval_route_uses_default_deduplication(self):
        self.prior_success()
        background = SimpleNamespace(add_task=lambda fn, *args, **kwargs: self.tasks.append((fn, args, kwargs)))
        self.approve(9001, SimpleNamespace(aprovar=True), background, self.db, object())
        self.assertEqual(len(self.tasks), 1)
        fn, args, kwargs = self.tasks[0]
        self.assertEqual(kwargs, {})
        self.assertTrue(fn(*args, **kwargs))
        self.assertEqual(self.deliveries, [])

    def test_manual_resend_uses_current_recovery_channel(self):
        self.assertTrue(self.send(9001))
        self.channel = "canal-corrigido@example.invalid"
        self.resend(9001, self.db, object())
        self.assertEqual([row[0] for row in self.deliveries], [
            "recuperacao@example.invalid", "canal-corrigido@example.invalid",
        ])

    def test_provider_failure_still_returns_502_after_previous_success(self):
        self.prior_success()
        self.provider_ok = False
        with self.assertRaises(HTTPException) as caught:
            self.resend(9001, self.db, object())
        self.assertEqual(caught.exception.status_code, 502)
        self.assertEqual(len(self.deliveries), 1)
        self.assertFalse(self.logs[-1].sucesso)
        self.assertEqual(self.closed, 1)

    def test_ineligible_accounts_do_not_dispatch(self):
        cases = [
            ("missing", None, 404),
            ("investor", {"investidor": True}, 409),
            ("inactive", {"is_active": False}, 409),
            ("pending", {"status": "pendente"}, 409),
            ("rejected", {"status": "rejeitado"}, 409),
        ]
        original = self.user
        for label, changes, status in cases:
            with self.subTest(label=label):
                self.user = None if changes is None else SimpleNamespace(**{**vars(original), **changes})
                with self.assertRaises(HTTPException) as caught:
                    self.resend(9001, self.db, object())
                self.assertEqual(caught.exception.status_code, status)
                self.assertEqual(self.deliveries, [])

    def test_manual_endpoint_keeps_admin_dependency(self):
        tree = ast.parse((APP / "api/account_access_admin.py").read_text())
        node = next(item for item in tree.body if isinstance(item, ast.FunctionDef) and item.name == "admin_reenviar_acesso")
        self.assertEqual(ast.unparse(node.args.defaults[-1]), "Depends(require_admin)")
        self.assertEqual(ast.unparse(node.decorator_list[0]), "router.post('/users/{user_id}/reenviar-acesso')")


if __name__ == "__main__":
    unittest.main()
