"""Focused real-function tests, direct unittest: no ORM, network or conftest.

Provider envelope: https://www.zoho.com/mail360/help/api/sending-email-messages.html
"""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, MagicMock


ROOT = Path(__file__).resolve().parents[2]


def functions_from(path, names, namespace):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    selected = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in names]
    assert {node.name for node in selected} == set(names)
    exec(compile(ast.Module(body=selected, type_ignores=[]), str(path), "exec"), namespace)
    return namespace


class TransactionalAcceptanceTest(unittest.TestCase):
    def setUp(self):
        # The HTTP boundary is entirely synthetic; no optional runtime
        # packages, TLS context or socket is needed to exercise the decoder.
        self.httpx = SimpleNamespace(Client=Mock(), HTTPStatusError=type("HTTPStatusError", (Exception,), {}),
                                     HTTPError=type("HTTPError", (Exception,), {}))
        self.client = functions_from(ROOT / "backend/app/services/mail360.py", {"Mail360Error", "_chamar"}, {
            "httpx": self.httpx, "_cabecalho": lambda: {}, "BASE": "https://provider.invalid/api", "TIMEOUT": 1,
            "log": Mock(),
        })
        self.email = functions_from(ROOT / "backend/app/services/emails.py", {
            "_normalizar_branding", "_mail360_enviar", "_enviar_por_provider", "_enviar",
        }, {
            "settings": SimpleNamespace(mail360_transactional_account_key="synthetic-account",
                                        email_transacional_provider_efetivo="mail360", email_transacional_configurado=True),
            "Mail360Error": self.client["Mail360Error"], "log": Mock(),
            "_reply_to_da_plataforma": lambda: "sender@example.invalid",
            "_ja_enviado": Mock(return_value=False), "_renderizar": Mock(return_value=("<p>demo</p>", "demo")),
            "_registrar_log": Mock(),
        })

    def call(self, payload=None, status=200):
        response = SimpleNamespace(content=b"" if status == 204 else b"json", json=lambda: payload,
                                   raise_for_status=Mock())
        client = MagicMock()
        client.__enter__.return_value = client
        client.request.return_value = response
        self.httpx.Client.return_value = client
        return self.client["_chamar"]("POST", "/messages")

    def test_http_200_with_provider_error_is_not_success_or_sensitive_error_text(self):
        with self.assertRaises(self.client["Mail360Error"]) as context:
            self.call({"status": {"code": 500}, "data": {"moreInfo": "SENSITIVE-SYNTHETIC"}})
        self.assertIn("500", str(context.exception))
        self.assertNotIn("SENSITIVE", str(context.exception))

    def test_success_dict_list_and_delete_remain_supported(self):
        self.assertEqual(self.call({"status": {"code": 200}, "data": {"messageId": "demo"}}), {"messageId": "demo"})
        self.assertEqual(self.call({"status": {"code": "200"}, "data": [{"folderId": "demo"}]}), [{"folderId": "demo"}])
        self.assertEqual(self.call(status=204), {})

    def test_invalid_status_does_not_get_unwrapped(self):
        for code in (None, True, "unexpected", "200.0", 0, 401):
            with self.subTest(code=code), self.assertRaises(self.client["Mail360Error"]):
                self.call({"status": {"code": code}, "data": {"messageId": "demo"}})

    def test_missing_message_identifier_does_not_confirm_send(self):
        for payload in (None, {}, [], {"moreInfo": "error"}, {"messageId": " "}, {"messageId": False}):
            with self.subTest(payload=payload):
                self.email["enviar_mensagem_mail360"] = Mock(return_value=payload)
                ok, error = self.email["_mail360_enviar"]("recipient@example.invalid", "Demo", "<p>demo</p>")
                self.assertFalse(ok)
                self.assertIn("não confirmado", error)

    def test_message_identifier_confirms_acceptance_and_preserves_sender_and_format(self):
        send = self.email["enviar_mensagem_mail360"] = Mock(return_value={"messageId": "demo-id"})
        self.assertEqual(self.email["_mail360_enviar"]("recipient@example.invalid", "Demo", "<p>demo</p>"), (True, None))
        self.assertEqual(send.call_args.args[:3], ("synthetic-account", "sender@example.invalid", "recipient@example.invalid"))
        self.assertEqual(send.call_args.kwargs, {"mail_format": "html"})

    def test_unconfirmed_send_is_logged_as_failure_not_idempotent_success(self):
        self.email["enviar_mensagem_mail360"] = Mock(return_value={})
        db = object()
        result = self.email["_enviar"](db, tipo="primeiro_acesso", destinatario="recipient@example.invalid",
                                        assunto="Demo", template="demo", contexto={}, user_id=-1)
        self.assertFalse(result)
        args = self.email["_registrar_log"].call_args.args
        self.assertIs(args[-2], False)
        self.assertIn("não confirmado", args[-1])

    def test_network_failure_remains_a_failure(self):
        self.email["enviar_mensagem_mail360"] = Mock(side_effect=self.client["Mail360Error"]("unavailable"))
        self.assertEqual(self.email["_mail360_enviar"]("recipient@example.invalid", "Demo", "<p>demo</p>"), (False, "unavailable"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
