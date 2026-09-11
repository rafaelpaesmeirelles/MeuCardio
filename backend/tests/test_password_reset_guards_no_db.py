"""Guards de recuperação/ativação reais com dependências só em memória.

Executar diretamente com Python. Não importa app/config/DB nem usa conftest;
não envia mensagens, não gera tokens reais e não exerce permissões de produção.
"""

import ast
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch


APP = Path(__file__).resolve().parents[1] / "app"


def load_functions(path, names, env):
    tree = ast.parse((APP / path).read_text())
    nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
    assert {node.name for node in nodes} == set(names)
    for node in nodes:
        node.decorator_list = []
    module = ast.Module(body=[
        ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0), *nodes,
    ], type_ignores=[])
    exec(compile(ast.fix_missing_locations(module), str(APP / path), "exec"), env)


class HTTPException(Exception):
    def __init__(self, status_code, detail):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


class Field:
    def __init__(self, name):
        self.name = name

    def __eq__(self, value):
        return self.name, value


class Query:
    def __init__(self, rows):
        self.rows = rows

    def filter(self, *conditions):
        return Query([row for row in self.rows if all(getattr(row, key) == value for key, value in conditions)])

    def first(self):
        return next(iter(self.rows), None)


class Token(SimpleNamespace):
    token = Field("token")

    @property
    def valido(self):
        return not self.used and not self.expired


class PasswordResetGuardsTests(unittest.TestCase):
    def setUp(self):
        self.user = SimpleNamespace(
            id=9002, email="login@example.invalid", full_name="Pessoa de Demonstração",
            is_active=True, status="aprovado", investidor=False, password_hash="HASH-ORIGINAL",
        )
        self.User = type("User", (), {"email": Field("email")})
        self.Mail = type("EmailAccount", (), {"user_id": Field("user_id")})
        self.mail = SimpleNamespace(user_id=9002, password_hash="HASH-CAIXA-ORIGINAL")
        self.token = Token(token="TOKEN-SINTETICO-NAO-REAL", user_id=9002, alvo="ativacao", used=False, expired=False)
        self.tasks, self.hashes, self.created_tokens, self.deliveries = [], [], [], []
        self.commits = self.closed = self.channel_updates = self.created_users = 0
        self.background = SimpleNamespace(add_task=lambda fn, *args, **kwargs: self.tasks.append((fn, args, kwargs)))
        self.db = SimpleNamespace(get=lambda _model, _id: self.user, query=self.query, commit=self.commit, close=self.close)
        self.recovery = SimpleNamespace(
            encontrar_usuario_por_identificador=lambda _db, _value: self.user,
            enviar_recuperacao_senha=lambda _id: None,
            enviar_confirmacao_canal_recuperacao=lambda _id: None,
            definir_email_recuperacao=self.define_channel,
        )
        self.env = {
            "User": self.User, "PasswordResetToken": Token,
            "Depends": lambda fn: fn, "get_db": lambda: None,
            "current_user": lambda: None, "require_admin": lambda: None,
            "HTTPException": HTTPException, "hash_password": self.hash_password,
            "account_recovery": self.recovery,
            "emails": SimpleNamespace(enviar_reenvio_ativacao=lambda _id: None, enviar_senha_alterada=lambda _id: None),
        }
        load_functions("api/password_reset.py", {
            "esqueci_senha", "reenviar_ativacao", "_ativacao_permitida", "redefinir_senha",
            "admin_atualizar_email_recuperacao", "admin_criar_usuario_com_recuperacao",
        }, self.env)

    def query(self, model):
        rows = [self.user] if model is self.User else [self.mail] if model is self.Mail else [self.token]
        return Query([row for row in rows if row is not None])

    def commit(self):
        self.commits += 1

    def close(self):
        self.closed += 1

    def hash_password(self, value):
        self.hashes.append(value)
        return "HASH-NOVO-SINTETICO"

    def define_channel(self, *_args):
        self.channel_updates += 1
        return SimpleNamespace(email="canal@example.invalid")

    def reset(self):
        return self.env["redefinir_senha"](
            SimpleNamespace(token=self.token.token, nova_senha="Senha-ficticia-123"), self.background, self.db,
        )

    def assert_no_mutation(self):
        self.assertEqual(self.commits, 0)
        self.assertEqual(self.hashes, [])
        self.assertEqual(self.tasks, [])
        self.assertFalse(self.token.used)
        self.assertEqual(self.user.password_hash, "HASH-ORIGINAL")
        self.assertEqual(self.mail.password_hash, "HASH-CAIXA-ORIGINAL")

    def test_activation_request_is_neutral_and_only_dispatches_for_approved_active_real_account(self):
        original = vars(self.user).copy()
        responses = []
        for label, changes, should_send in [
            ("approved_active", {}, True),
            ("admin_disabled", {"is_active": False}, False),
            ("pending", {"status": "pendente", "is_active": False}, False),
            ("rejected", {"status": "rejeitado", "is_active": False}, False),
            ("investor", {"investidor": True}, False),
            ("missing", None, False),
        ]:
            with self.subTest(label=label):
                self.user = None if changes is None else SimpleNamespace(**{**original, **changes})
                self.tasks.clear()
                responses.append(self.env["reenviar_ativacao"](
                    SimpleNamespace(email=" LOGIN@example.invalid "), self.background, self.db,
                ))
                self.assertEqual(len(self.tasks), int(should_send))
        self.assertTrue(all(response == responses[0] for response in responses))
        self.assertEqual(self.commits, 0)

    def test_previously_issued_activation_cannot_reactivate_or_approve(self):
        for active, status in [(False, "aprovado"), (False, "pendente"), (False, "rejeitado"), (True, "pendente"), (True, "rejeitado")]:
            with self.subTest(active=active, status=status):
                self.user.is_active, self.user.status = active, status
                with self.assertRaises(HTTPException) as caught:
                    self.reset()
                self.assertEqual(caught.exception.status_code, 400)
                self.assert_no_mutation()
                self.assertEqual((self.user.is_active, self.user.status), (active, status))

    def test_legitimate_active_approved_activation_sets_password_without_changing_access(self):
        self.assertIn("nota", self.reset())
        self.assertEqual(self.user.password_hash, "HASH-NOVO-SINTETICO")
        self.assertTrue(self.token.used)
        self.assertEqual((self.user.is_active, self.user.status), (True, "aprovado"))
        self.assertEqual(self.commits, 1)
        self.assertEqual(self.tasks, [])

    def test_normal_first_access_and_recovery_token_stay_valid_and_single_use(self):
        self.token.alvo = "conta"
        self.assertIn("nota", self.reset())
        self.assertEqual(self.user.password_hash, "HASH-NOVO-SINTETICO")
        self.assertTrue(self.token.used)
        self.assertEqual(len(self.tasks), 1)
        with self.assertRaises(HTTPException) as caught:
            self.reset()
        self.assertEqual(caught.exception.status_code, 400)
        self.assertEqual(self.commits, 1)

    def test_investor_previously_issued_tokens_are_rejected_for_every_target(self):
        self.user.investidor = True
        details = []
        for target in ["conta", "ativacao", "email"]:
            with self.subTest(target=target):
                self.token.alvo = target
                with self.assertRaises(HTTPException) as caught:
                    self.reset()
                self.assertEqual(caught.exception.status_code, 400)
                details.append(caught.exception.detail)
                self.assert_no_mutation()
        self.assertEqual(len(set(details)), 1)
        self.assertNotIn("Investidor", details[0])

    def test_public_investor_recovery_does_not_schedule_but_keeps_neutral_response(self):
        self.user.investidor = True
        investor = self.env["esqueci_senha"](SimpleNamespace(email=self.user.email), self.background, self.db)
        self.assertEqual(self.tasks, [])
        self.user.investidor = False
        normal = self.env["esqueci_senha"](SimpleNamespace(email=self.user.email), self.background, self.db)
        self.assertEqual(investor, normal)
        self.assertEqual(len(self.tasks), 1)

    def test_legacy_admin_recovery_alias_blocks_investor_before_write(self):
        self.user.investidor = True
        with self.assertRaises(HTTPException) as caught:
            self.env["admin_atualizar_email_recuperacao"](
                9002, SimpleNamespace(recovery_email="canal@example.invalid"), self.background, self.db, object(),
            )
        self.assertEqual(caught.exception.status_code, 409)
        self.assertEqual(self.channel_updates, 0)
        self.assert_no_mutation()

    def test_legacy_admin_recovery_alias_preserves_normal_account_update(self):
        response = self.env["admin_atualizar_email_recuperacao"](
            9002, SimpleNamespace(recovery_email="canal@example.invalid"), self.background, self.db, object(),
        )
        self.assertEqual(response, {"user_id": 9002, "recovery_email": "canal@example.invalid"})
        self.assertEqual(self.channel_updates, 1)
        self.assertEqual(self.commits, 1)
        self.assertEqual(len(self.tasks), 1)

    def test_investor_creation_with_recovery_fails_before_base_creation_or_channel_lookup(self):
        # Nenhum stub de criar_usuario/normalizar_email é oferecido: se chegar
        # a esses efeitos antes do guard, o teste falha por dependência ausente.
        with self.assertRaises(HTTPException) as caught:
            self.env["admin_criar_usuario_com_recuperacao"](
                SimpleNamespace(tipo_acesso="investidor"), self.background, self.db, object(),
            )
        self.assertEqual(caught.exception.status_code, 409)
        self.assert_no_mutation()

    def test_existing_mail_reset_still_changes_only_mail_password(self):
        self.token.alvo = "email"
        module = ModuleType("app.models.email_account")
        module.EmailAccount = self.Mail
        with patch.dict(sys.modules, {"app.models.email_account": module}):
            self.assertIn("nota", self.reset())
        self.assertEqual(self.mail.password_hash, "HASH-NOVO-SINTETICO")
        self.assertEqual(self.user.password_hash, "HASH-ORIGINAL")
        self.assertTrue(self.token.used)

    def test_deferred_personal_recovery_jobs_recheck_investor_before_token_or_dispatch(self):
        self.user.investidor = True
        env = {"SessionLocal": lambda: self.db, "User": self.User}
        names = {"enviar_recuperacao_senha", "enviar_primeiro_acesso", "enviar_confirmacao_canal_recuperacao"}
        load_functions("services/account_recovery.py", names, env)
        # Token, destinatário e transporte não são fornecidos; chegar a eles
        # num job que se tornou inelegível deve falhar o teste.
        for name in names:
            self.assertFalse(env[name](9002))
        self.assertEqual(self.closed, 3)
        self.assert_no_mutation()

    def test_public_status_and_admin_dependencies_preserved(self):
        tree = ast.parse((APP / "api/password_reset.py").read_text())
        nodes = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
        for name in ["esqueci_senha", "reenviar_ativacao"]:
            self.assertIn("status_code=202", ast.unparse(nodes[name].decorator_list[0]))
        for name in ["admin_atualizar_email_recuperacao", "admin_criar_usuario_com_recuperacao"]:
            self.assertEqual(ast.unparse(nodes[name].args.defaults[-1]), "Depends(require_admin)")


if __name__ == "__main__":
    unittest.main()
