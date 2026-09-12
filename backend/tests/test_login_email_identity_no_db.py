"""Corpos reais dos escritores de identidade, isolados de app/DB/rede.

Executar diretamente com Python; não importar conftest. O dublê transacional
verifica ordem e rollback, não certifica locks PostgreSQL (cobertos na CI).
"""
import ast
import copy
import secrets
from datetime import date, datetime, timezone
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch

APP = Path(__file__).resolve().parents[1] / "app"


class HTTPException(Exception):
    def __init__(self, status_code, detail):
        self.status_code, self.detail = status_code, detail
        super().__init__(detail)


class IntegrityError(Exception):
    pass


class Field:
    def __init__(self, model, name, lower=False):
        self.model, self.name, self.lower = model, name, lower

    def value(self, row):
        value = getattr(row, self.name, None)
        return value.lower() if self.lower and isinstance(value, str) else value

    def __eq__(self, value):
        return lambda row: self.value(row) == value

    def __ne__(self, value):
        return lambda row: self.value(row) != value

    def is_(self, value):
        return self == value


class Row(SimpleNamespace):
    def __init__(self, **values):
        super().__init__(**{**dict(id=None, cpf=None, used=None, usado_em=None,
                                  usado_por_user_id=None, observacao=None,
                                  status="aprovado"), **values})


def model(name, fields):
    cls = type(name, (Row,), {})
    for key in fields:
        setattr(cls, key, Field(cls, key))
    return cls


User = model("User", ("email", "id", "cpf"))
Recovery = model("Recovery", ("email", "user_id"))
PreAuthorization = model("PreAuthorization", ("email", "usado_em"))
Audit = model("Audit", ("action",))


class Query:
    def __init__(self, db, selected):
        self.db, self.selected, self.conditions = db, selected, []
        self.model = selected.model if isinstance(selected, Field) else selected

    def filter(self, *conditions):
        self.conditions.extend(conditions)
        return self

    def with_for_update(self):
        self.db.events.append("row_lock")
        return self

    def first(self):
        return next((row for row in self.db.rows if isinstance(row, self.model)
                     and all(condition(row) for condition in self.conditions)), None)

    def scalar(self):
        row = self.first()
        return self.selected.value(row) if row is not None else None


class Transaction:
    def __init__(self, *rows):
        self.rows, self.events, self.sql = list(rows), [], []
        self.snapshot = [(row, copy.deepcopy(vars(row))) for row in self.rows]
        self.fail_commit = False

    def execute(self, sql, params):
        self.events.append("identity_lock")
        self.sql.append((sql, params))

    def query(self, selected):
        self.events.append("query")
        return Query(self, selected)

    def get(self, cls, ident):
        key = "user_id" if cls is Recovery else "id"
        return next((row for row in self.rows if isinstance(row, cls)
                     and getattr(row, key) == ident), None)

    def refresh(self, row, **_kwargs):
        self.events.append("refresh")

    def add(self, row):
        if row.id is None:
            row.id = 99000 + len(self.rows)
        self.rows.append(row)

    def flush(self):
        self.events.append("flush")

    def commit(self):
        self.events.append("commit")
        if self.fail_commit:
            raise IntegrityError("synthetic conflict")
        self.snapshot = [(row, copy.deepcopy(vars(row))) for row in self.rows]

    def rollback(self):
        self.events.append("rollback")
        self.rows = [row for row, _ in self.snapshot]
        for row, values in self.snapshot:
            vars(row).clear()
            vars(row).update(copy.deepcopy(values))

    def close(self):
        self.events.append("close")


def load(path, names, env):
    nodes = [node for node in ast.parse((APP / path).read_text()).body
             if isinstance(node, ast.FunctionDef) and node.name in names]
    assert len(nodes) == len(names), (path, names)
    for node in nodes:
        node.decorator_list = []
    module = ast.Module(body=[ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0), *nodes], type_ignores=[])
    exec(compile(ast.fix_missing_locations(module), str(APP / path), "exec"), env)


class LoginIdentityTests(unittest.TestCase):
    def setUp(self):
        self.tasks, self.notifications = [], []
        self.env = dict(
            User=User, AccountRecoveryEmail=Recovery, AuditLog=Audit,
            text=lambda value: value, func=SimpleNamespace(lower=lambda field: Field(field.model, field.name, True)),
            datetime=datetime, date=date, timezone=timezone,
            HTTPException=HTTPException, IntegrityError=IntegrityError,
            Depends=lambda fn: None, get_db=None, current_user=None, require_admin=None,
            hash_password=lambda _: "SYNTHETIC-HASH", verify_password=lambda password, _: password == "correct",
            cpf_valido=lambda _: True, limpar_cpf=lambda value: value,
            _tipo_acesso=lambda _: "normal", _resumo=lambda user, *_: vars(user),
            SolicitacaoAcesso=lambda **values: SimpleNamespace(**values),
            secrets=secrets, settings=SimpleNamespace(admin_email="owner@example.invalid"),
        )
        load("core/security.py", {"is_owner_admin", "require_manage_account"}, self.env)
        load("services/account_recovery.py", {
            "normalizar_email", "validar_email_basico", "bloquear_identidades_email",
            "email_ja_em_uso", "definir_email_recuperacao", "obter_email_recuperacao",
        }, self.env)
        self.recovery = SimpleNamespace(**{key: value for key, value in self.env.items() if callable(value)})
        for name in ("enviar_confirmacao_canal_recuperacao", "enviar_acesso_aprovado", "enviar_confirmacao_convite"):
            setattr(self.recovery, name, name)
        self.env["account_recovery"] = self.recovery
        self.env["emails"] = SimpleNamespace(enviar_troca_email="changed", enviar_solicitacao_recebida="received")
        self.background = SimpleNamespace(add_task=lambda *task: self.tasks.append(task))
        modules = {}
        for name, attrs in {
            "app.models.convidado_pre_autorizado": {"ConvidadoPreAutorizado": PreAuthorization},
            "app.services.notificar": {"notificar_admins_nova_solicitacao": self.notify},
            "app.api.auth": {"_perfil_completo": lambda _: False},
        }.items():
            module = ModuleType(name)
            module.__dict__.update(attrs)
            modules[name] = module
        self.modules = patch.dict(sys.modules, modules)
        self.modules.start()
        self.addCleanup(self.modules.stop)
        load("api/auth.py", {"trocar_email", "_preparar_solicitacao_acesso", "_concluir_solicitacao_acesso", "solicitar_acesso"}, self.env)
        load("api/password_reset.py", {"solicitar_acesso_com_recuperacao"}, self.env)
        load("api/admin_user_management.py", {"atualizar_usuario"}, self.env)
        load("services/bootstrap.py", {"create_admin_if_absent"}, self.env)
        load("commands/provision_staff_user.py", {"main"}, self.env)

    def notify(self, db, *args):
        self.assertIn("commit", db.events)
        self.assertNotIn("rollback", db.events)
        self.notifications.append(args)

    def payload(self, **changes):
        values = dict(full_name="Cadastro fictício", email="new@example.invalid",
                      recovery_email="recovery@example.invalid", birth_date=date(1980, 1, 1),
                      cpf="synthetic-cpf-not-validated-here", password="synthetic-password",
                      profession="Medicina", council_name="CRM", council_number="DEMO", council_state="SP",
                      council_name_other=None, council_state_other=None, specialty=None,
                      professional_title=None, workplace_name=None, workplace_department=None,
                      workplace_role=None, workplace_notes=None, include_workplace_on_documents=False)
        values.update(changes)
        data = SimpleNamespace(**values)
        data.model_dump = lambda exclude: {key: value for key, value in values.items() if key not in exclude}
        return data

    def test_common_lock_has_constant_namespace_and_no_identity_payload(self):
        db = Transaction()
        self.env["bloquear_identidades_email"](db)
        self.assertEqual(db.sql, [("SELECT pg_advisory_xact_lock(:namespace, :resource)",
                                   {"namespace": 0x434F5256, "resource": 1})])

    def test_all_five_login_writers_reject_another_recovery_after_lock(self):
        for path in ("signup", "self", "admin", "bootstrap", "staff"):
            with self.subTest(path=path):
                owner = User(id=1, email="owner@example.invalid")
                target = User(id=2, email="target@example.invalid", password_hash="hash", role="medico")
                channel = Recovery(user_id=1, email="OCCUPIED@example.invalid")
                db = Transaction(owner, target, channel)
                with self.assertRaises((HTTPException, ValueError, SystemExit)) as raised:
                    if path == "signup":
                        self.env["solicitar_acesso"](self.payload(email="occupied@example.invalid"), self.background, db)
                    elif path == "self":
                        self.env["trocar_email"](SimpleNamespace(senha_atual="correct", novo_email="occupied@example.invalid"), self.background, db, target)
                    elif path == "admin":
                        self.env["atualizar_usuario"](2, SimpleNamespace(email="occupied@example.invalid"), db, SimpleNamespace(id=3, role="admin"))
                    elif path == "bootstrap":
                        self.env["create_admin_if_absent"](db, email="occupied@example.invalid", password="demo")
                    else:
                        self.env.update(SessionLocal=lambda: db, parser=lambda: SimpleNamespace(parse_args=lambda: SimpleNamespace(email="occupied@example.invalid")),
                                        os=SimpleNamespace(getenv=lambda _: "synthetic-password"))
                        self.env["main"]()
                if isinstance(raised.exception, HTTPException):
                    self.assertEqual(raised.exception.status_code, 409)
                self.assertLess(db.events.index("identity_lock"), db.events.index("query"))
                self.assertNotIn("commit", db.events)
                self.assertEqual(target.email, "target@example.invalid")
        self.assertEqual(self.tasks, [])
        self.assertEqual(self.notifications, [])

    def test_self_noop_and_own_recovery_are_explicit_422(self):
        for destination in ("self@example.invalid", "own-channel@example.invalid"):
            user = User(id=1, email="self@example.invalid", password_hash="hash")
            db = Transaction(user, Recovery(user_id=1, email="own-channel@example.invalid"))
            with self.assertRaises(HTTPException) as raised:
                self.env["trocar_email"](SimpleNamespace(senha_atual="correct", novo_email=destination), self.background, db, user)
            self.assertEqual(raised.exception.status_code, 422)
            self.assertNotIn("commit", db.events)
        self.assertEqual(self.tasks, [])

    def test_self_email_success_and_commit_failure_schedule_only_after_commit(self):
        for failure in (False, True):
            with self.subTest(failure=failure):
                self.tasks.clear()
                user = User(id=1, email="self@example.invalid", password_hash="hash")
                db = Transaction(user)
                db.fail_commit = failure
                def schedule(*args):
                    self.assertEqual(db.events[-1], "commit")
                    self.tasks.append(args)
                background = SimpleNamespace(add_task=schedule)
                data = SimpleNamespace(senha_atual="correct", novo_email="changed@example.invalid")
                if failure:
                    with self.assertRaises(HTTPException) as raised:
                        self.env["trocar_email"](data, background, db, user)
                    self.assertEqual(raised.exception.status_code, 409)
                    self.assertEqual(user.email, "self@example.invalid")
                    self.assertEqual(self.tasks, [])
                else:
                    result = self.env["trocar_email"](data, background, db, user)
                    self.assertIn("E-mail alterado", result["nota"])
                    self.assertEqual(user.email, "changed@example.invalid")
                    self.assertEqual(self.tasks, [("changed", 1, "self@example.invalid", "changed@example.invalid")])

    def test_password_guard_precedes_lock_and_queries(self):
        user = User(id=1, email="self@example.invalid", password_hash="hash")
        db = Transaction(user)
        with self.assertRaises(HTTPException) as raised:
            self.env["trocar_email"](SimpleNamespace(senha_atual="wrong", novo_email="new@example.invalid"), self.background, db, user)
        self.assertEqual(raised.exception.status_code, 400)
        self.assertEqual(db.events, [])
        self.assertEqual(self.tasks, [])

    def test_admin_keeps_unchanged_login_and_recovery_while_updating_profile(self):
        user = User(id=1, email="self@example.invalid", full_name="Nome fictício",
                    role="medico", is_active=True)
        channel = Recovery(user_id=1, email="channel@example.invalid")
        db = Transaction(user, channel)
        data = self.payload(email=user.email, full_name="Nome fictício atualizado")
        data.role, data.is_active, data.tipo_acesso, data.rqe = "medico", True, "normal", None
        result = self.env["atualizar_usuario"](1, data, db, SimpleNamespace(id=2, role="admin"))
        self.assertEqual(result["full_name"], "Nome fictício atualizado")
        self.assertEqual(user.email, "self@example.invalid")
        self.assertEqual(channel.email, "channel@example.invalid")
        self.assertEqual(db.events.count("commit"), 1)

    def test_recovery_setter_revalidates_current_login_not_stale_user(self):
        current = User(id=1, email="new-login@example.invalid")
        stale = User(id=1, email="old-login@example.invalid")
        db = Transaction(current)
        with self.assertRaisesRegex(ValueError, "diferente"):
            self.env["definir_email_recuperacao"](db, stale, current.email)
        self.assertEqual(db.events[:2], ["identity_lock", "query"])
        self.assertEqual(len(db.rows), 1)

    def test_bootstrap_remains_idempotent_without_password_change(self):
        original = User(id=1, email="Admin@example.invalid", password_hash="original")
        db = Transaction(original)
        user, created = self.env["create_admin_if_absent"](db, email=" ADMIN@example.invalid ", password="different")
        self.assertIs(user, original)
        self.assertFalse(created)
        self.assertEqual(user.password_hash, "original")
        self.assertNotIn("commit", db.events)

    def test_signup_rolls_back_preauthorization_account_channel_and_audit_without_notifications(self):
        for failure in ("channel", "commit"):
            with self.subTest(failure=failure):
                pre = PreAuthorization(id=4, email="new@example.invalid")
                db = Transaction(pre)
                original_setter = self.recovery.definir_email_recuperacao
                if failure == "channel":
                    def fail_after_channel(*args):
                        original_setter(*args)
                        raise ValueError("Este e-mail já está vinculado a outra conta CorVIA.")
                    self.recovery.definir_email_recuperacao = fail_after_channel
                else:
                    db.fail_commit = True
                try:
                    with self.assertRaises(HTTPException) as raised:
                        self.env["solicitar_acesso_com_recuperacao"](self.payload(), self.background, db)
                    self.assertEqual(raised.exception.status_code, 409)
                finally:
                    self.recovery.definir_email_recuperacao = original_setter
                self.assertEqual(db.rows, [pre])
                self.assertIsNone(pre.usado_em)
                self.assertIsNone(pre.usado_por_user_id)
                self.assertEqual(db.events[-1], "rollback")
                self.assertEqual(self.tasks, [])
                self.assertEqual(self.notifications, [])

    def test_pending_and_guest_signup_commit_once_before_any_notifications(self):
        for guest in (False, True):
            with self.subTest(guest=guest):
                self.tasks.clear()
                self.notifications.clear()
                pre = PreAuthorization(id=4, email="new@example.invalid")
                db = Transaction(pre) if guest else Transaction()
                result = self.env["solicitar_acesso_com_recuperacao"](self.payload(), self.background, db)
                users = [row for row in db.rows if isinstance(row, User)]
                self.assertEqual(len(users), 1)
                user = users[0]
                self.assertEqual((user.status, user.is_active, user.convidado),
                                 ("pendente", False, False))
                self.assertEqual(db.events.count("commit"), 1)
                self.assertEqual(db.get(Recovery, user.id).email, "recovery@example.invalid")
                self.assertFalse(result.get("acesso_imediato"))
                self.assertEqual(len(self.notifications), 0 if guest else 1)
                self.assertEqual(len(self.tasks), 1 if guest else 2)
                if guest:
                    self.assertEqual(self.tasks, [("enviar_confirmacao_convite", user.id)])
                    self.assertIsNone(pre.usado_em)
                    self.assertIsNone(pre.usado_por_user_id)
                    self.assertFalse(any(isinstance(row, Audit) for row in db.rows))


if __name__ == "__main__":
    unittest.main()
