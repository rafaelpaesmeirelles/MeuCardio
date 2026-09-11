"""Atomicidade do convite administrativo, sem app, banco ou envio real.

Executar diretamente com Python. Os corpos reais dos handlers são compilados;
somente ORM, schemas, transporte e dependências de autorização são substituídos.
O teste não comprova transação PostgreSQL nem permissões HTTP em produção.
"""

import ast
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch


APP = Path(__file__).resolve().parents[1] / "app"


class HTTPException(Exception):
    def __init__(self, status_code, detail):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


class IntegrityError(Exception):
    pass


class User(SimpleNamespace):
    email = "email-field"

    def __init__(self, **kwargs):
        super().__init__(id=99031, status="aprovado", **kwargs)


class Transaction:
    def __init__(self):
        self.pending = []
        self.persisted = []
        self.commits = 0
        self.rollbacks = 0
        self.events = []

    def add(self, item):
        self.pending.append(item)

    def query(self, _model):
        return SimpleNamespace(filter=lambda *_: SimpleNamespace(first=lambda: None))

    def get(self, model, user_id):
        return next((item for item in self.pending + self.persisted
                     if isinstance(item, model) and item.id == user_id), None)

    def flush(self):
        self.events.append("flush")

    def commit(self):
        self.events.append("commit")
        self.persisted.extend(self.pending)
        self.pending.clear()
        self.commits += 1

    def rollback(self):
        self.events.append("rollback")
        self.pending.clear()
        self.rollbacks += 1


def load_functions(path, names, env):
    tree = ast.parse((APP / path).read_text())
    nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
    for node in nodes:
        node.decorator_list = []
    module = ast.Module(body=[ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0), *nodes], type_ignores=[])
    exec(compile(ast.fix_missing_locations(module), str(APP / path), "exec"), env)


class AdminInvitationAtomicityTests(unittest.TestCase):
    def setUp(self):
        self.db = Transaction()
        self.tasks = []
        self.fail_channel = False
        self.admin = SimpleNamespace(id=99100)
        self.payload = dict(
            email="novo@example.invalid", full_name="Conta fictícia", password="senha-sintetica",
            role="medico", tipo_acesso="normal", crm=None, profession=None,
            council_name=None, council_number=None, council_state=None, specialty=None,
            professional_title=None, workplace_name=None, workplace_department=None,
            workplace_role=None, workplace_notes=None, include_workplace_on_documents=False,
            profile_completion_required=False, kyc_waivers=None,
        )
        self.data = SimpleNamespace(**self.payload, recovery_email="canal@example.invalid")
        self.data.model_dump = lambda **_: self.payload.copy()
        self.background = SimpleNamespace(add_task=self.schedule)
        self.recovery = SimpleNamespace(
            normalizar_email=lambda value: value.strip().lower(),
            bloquear_identidades_email=lambda db: db.events.append("identity_lock"),
            email_ja_em_uso=lambda *_: False,
            definir_email_recuperacao=self.define_channel,
            enviar_primeiro_acesso=lambda _id: True,
        )
        self.env = dict(
            User=User, AuditLog=SimpleNamespace, HTTPException=HTTPException,
            IntegrityError=IntegrityError,
            Depends=lambda fn: fn, get_db=lambda: None, require_admin=lambda: None,
            NovoUsuario=lambda **values: SimpleNamespace(**values),
            account_recovery=self.recovery,
        )
        modules = {}
        for name, attrs in {
            "app.api.auth": {"_perfil_completo": lambda _user: False},
            "app.core.security": {"hash_password": lambda _: "HASH-SINTETICO"},
            "app.models.user": {"User": User},
        }.items():
            module = ModuleType(name)
            module.__dict__.update(attrs)
            modules[name] = module
        self.modules = patch.dict(sys.modules, modules)
        self.modules.start()
        self.addCleanup(self.modules.stop)
        load_functions("api/admin.py", {"criar_usuario", "_preparar_usuario_administrativo", "alternar_investidor"}, self.env)
        load_functions("api/password_reset.py", {"admin_criar_usuario_com_recuperacao"}, self.env)

    def schedule(self, callback, user_id):
        self.db.events.append("schedule")
        self.tasks.append((callback, user_id))

    def define_channel(self, db, user, address):
        db.events.append("channel")
        if self.fail_channel:
            raise ValueError("Este e-mail já está vinculado a outra conta CorVIA.")
        db.add(SimpleNamespace(user_id=user.id, email=address))

    def create(self):
        return self.env["admin_criar_usuario_com_recuperacao"](self.data, self.background, self.db, self.admin)

    def test_channel_conflict_does_not_leave_account_or_audit_persisted(self):
        self.fail_channel = True
        with self.assertRaises(HTTPException) as caught:
            self.create()
        self.assertEqual(caught.exception.status_code, 409)
        self.assertEqual(self.db.persisted, [])
        self.assertEqual(self.db.commits, 0)
        self.assertEqual(self.db.rollbacks, 1)
        self.assertEqual(self.tasks, [])

    def test_account_channel_and_audit_commit_once_before_single_invitation(self):
        response = self.create()
        self.assertEqual(response["recovery_email"], "canal@example.invalid")
        self.assertEqual(response["id"], 99031)
        self.assertEqual(self.db.commits, 1)
        self.assertEqual(len(self.db.persisted), 3)
        self.assertLess(self.db.events.index("identity_lock"), self.db.events.index("flush"))
        self.assertLess(self.db.events.index("channel"), self.db.events.index("commit"))
        self.assertLess(self.db.events.index("commit"), self.db.events.index("schedule"))
        self.assertEqual(self.tasks, [(self.recovery.enviar_primeiro_acesso, 99031)])

    def test_investor_is_rejected_before_account_or_channel_creation(self):
        self.data.tipo_acesso = "investidor"
        with self.assertRaises(HTTPException) as caught:
            self.create()
        self.assertEqual(caught.exception.status_code, 409)
        self.assertEqual(self.db.events, [])
        self.assertEqual(self.tasks, [])

    def test_legacy_creation_keeps_response_and_single_commit(self):
        response = self.env["criar_usuario"](SimpleNamespace(**self.payload), self.db, self.admin)
        self.assertEqual(response, dict(id=99031, email="novo@example.invalid", full_name="Conta fictícia", role="medico", tipo_acesso="normal", convidado=False, investidor=False))
        self.assertEqual(self.db.commits, 1)
        self.assertEqual(len(self.db.persisted), 2)
        self.assertLess(self.db.events.index("identity_lock"), self.db.events.index("flush"))

    def test_unique_violation_rolls_back_all_rows_and_never_schedules_email(self):
        def conflict():
            raise IntegrityError("SYNTHETIC-CONSTRAINT-DETAIL-MUST-NOT-LEAK")
        self.db.commit = conflict
        with self.assertRaises(HTTPException) as caught:
            self.create()
        self.assertEqual(caught.exception.status_code, 409)
        self.assertNotIn("SYNTHETIC", caught.exception.detail)
        self.assertEqual(self.db.persisted, [])
        self.assertEqual(self.db.pending, [])
        self.assertEqual(self.db.rollbacks, 1)
        self.assertEqual(self.tasks, [])

    def test_storage_failure_rolls_back_and_never_schedules_email(self):
        def unavailable():
            raise RuntimeError("SYNTHETIC-STORAGE-FAILURE")
        self.db.commit = unavailable
        with self.assertRaisesRegex(RuntimeError, "SYNTHETIC-STORAGE-FAILURE"):
            self.create()
        self.assertEqual(self.db.persisted, [])
        self.assertEqual(self.db.pending, [])
        self.assertEqual(self.db.rollbacks, 1)
        self.assertEqual(self.tasks, [])

    def test_guest_profile_rules_are_preserved(self):
        self.payload["tipo_acesso"] = self.data.tipo_acesso = "convidado"
        response = self.create()
        user = self.db.get(User, response["id"])
        self.assertTrue(user.convidado)
        self.assertFalse(user.investidor)
        self.assertTrue(user.profile_completion_required)
        self.assertEqual(self.db.commits, 1)

    def test_admin_dependency_is_kept_on_both_public_routes(self):
        for path, name in [("api/admin.py", "criar_usuario"), ("api/password_reset.py", "admin_criar_usuario_com_recuperacao")]:
            tree = ast.parse((APP / path).read_text())
            node = next(item for item in tree.body if isinstance(item, ast.FunctionDef) and item.name == name)
            self.assertEqual(ast.unparse(node.args.defaults[-1]), "Depends(require_admin)")

    def test_new_login_cannot_occupy_another_accounts_recovery_channel(self):
        self.recovery.email_ja_em_uso = lambda _db, address: address == self.payload["email"]
        with self.assertRaises(HTTPException) as caught:
            self.create()
        self.assertEqual(caught.exception.status_code, 409)
        self.assertEqual(self.db.persisted, [])
        self.assertEqual(self.db.pending, [])
        self.assertEqual(self.tasks, [])

    def test_new_investor_cannot_have_admin_role(self):
        self.payload.update(tipo_acesso="investidor", role="admin")
        with self.assertRaises(HTTPException) as caught:
            self.env["criar_usuario"](SimpleNamespace(**self.payload), self.db, self.admin)
        self.assertEqual(caught.exception.status_code, 422)
        self.assertEqual(self.db.pending, [])
        self.assertEqual(self.db.persisted, [])

    def test_admin_cannot_be_converted_to_investor(self):
        target = User(role="admin", investidor=False, email="admin-synthetic@example.invalid")
        self.db.persisted.append(target)
        with self.assertRaises(HTTPException) as caught:
            self.env["alternar_investidor"](target.id, True, self.db, self.admin)
        self.assertEqual(caught.exception.status_code, 409)
        self.assertFalse(target.investidor)
        self.assertEqual(self.db.commits, 0)

    def test_revoking_investor_flag_is_not_blocked_by_creation_guard(self):
        target = User(role="admin", investidor=True, email="legacy-synthetic@example.invalid")
        self.db.persisted.append(target)
        response = self.env["alternar_investidor"](target.id, False, self.db, self.admin)
        self.assertEqual(response, {"id": target.id, "investidor": False})
        self.assertFalse(target.investidor)
        self.assertEqual(target.role, "admin")
        self.assertEqual(self.db.commits, 1)


if __name__ == "__main__":
    unittest.main()
