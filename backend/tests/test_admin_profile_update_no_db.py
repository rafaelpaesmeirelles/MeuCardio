"""Exercise the real schemas/handlers with AST isolation, no app/DB/conftest.

Run directly: python -B backend/tests/test_admin_profile_update_no_db.py
The fake unit of work cannot query a database or execute background email work.
"""
import ast
from datetime import date
from pathlib import Path
from types import SimpleNamespace
import unittest

from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator


APP = Path(__file__).resolve().parents[1] / "app"


class HttpFailure(Exception):
    def __init__(self, status_code, detail):
        super().__init__(detail)
        self.status_code, self.detail = status_code, detail


def load_nodes(path, names, namespace):
    tree = ast.parse(path.read_text())
    selected = []
    for node in tree.body:
        if isinstance(node, (ast.ClassDef, ast.FunctionDef)) and node.name in names:
            if isinstance(node, ast.FunctionDef):
                node.decorator_list = []  # route registration only; body unchanged
            selected.append(node)
        elif isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id in names for target in node.targets):
            selected.append(node)
    module = ast.Module(body=[ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0), *selected], type_ignores=[])
    exec(compile(ast.fix_missing_locations(module), str(path), "exec"), namespace)


def real_handlers():
    ns = {"BaseModel": BaseModel, "Field": Field, "field_validator": field_validator,
          "model_validator": model_validator, "date": date, "HTTPException": HttpFailure,
          "Depends": lambda dependency: None, "get_db": object(), "require_admin": object(),
          "current_user": object(), "User": object, "re": __import__("re")}
    load_nodes(APP / "services/professional_profile.py", {
        "PROFESSIONAL_TITLES", "COUNCILS", "normalize_council", "normalize_professional_title",
    }, ns)
    load_nodes(APP / "core/validators.py", {"UFS", "limpar_cpf", "cpf_valido"}, ns)
    load_nodes(APP / "api/admin_user_management.py", {"_email_valido", "AtualizarUsuario", "atualizar_usuario"}, ns)
    load_nodes(APP / "api/auth.py", {
        "DadosPessoais", "_ROTULOS_CADASTRO", "_CAMPOS_ENDERECO_RESIDENCIAL",
        "_CAMPOS_ENDERECO_PROFISSIONAL", "_nome_real", "_campos_pendentes_perfil",
        "_perfil_completo", "atualizar_me",
    }, ns)
    ns["AtualizarUsuario"].model_rebuild(_types_namespace=ns)
    ns["DadosPessoais"].model_rebuild(_types_namespace=ns)
    ns["_perfil"] = lambda db, user: vars(user).copy()
    ns["emails"] = SimpleNamespace(enviar_alteracao_cadastro=object())
    return ns


class NoDatabase:
    def __init__(self, user):
        self.user, self.commits, self.refreshes = user, 0, 0

    def get(self, model, user_id):
        assert self.user.id == user_id
        return self.user

    def query(self, *args, **kwargs):
        raise AssertionError("No database queries are permitted in this isolated test")

    def commit(self):
        self.commits += 1

    def refresh(self, user):
        assert user is self.user
        self.refreshes += 1


class PendingTasks:
    def __init__(self):
        self.items = []

    def add_task(self, callback, *args):
        self.items.append((callback, args))  # never execute email or external IO


class AdminProfileUpdateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.real = real_handlers()

    def fixture(self):
        fields = {name: None for name in self.real["DadosPessoais"].model_fields}
        fields.update(id=99001, role="admin", email="demo@example.invalid", full_name="Profissional de Demonstração",
                      profession="Medicina", council_name="CRM", council_number="DEMO", council_state="SP",
                      specialty="Especialidade demonstrativa", professional_title="Dr.",
                      home_street="Rua Demonstrativa", home_number="0", home_state="SP",
                      practice_street="Local demonstrativo", practice_phone="DEMO", include_workplace_on_documents=True,
                      cpf=None, birth_date=date(1980, 1, 1), convidado=False, investidor=False,
                      is_active=True, profile_completion_required=False)
        user = SimpleNamespace(**fields)
        return user, NoDatabase(user), PendingTasks()

    def payload(self, user, **changes):
        allowed = self.real["DadosPessoais"].model_fields
        values = {key: getattr(user, key, None) for key in allowed if key not in {"cpf", "birth_date"}}
        values.update(changes)
        return self.real["DadosPessoais"](**values)

    def test_original_admin_payload_is_rejected_by_real_role_schema(self):
        with self.assertRaises(ValidationError) as raised:
            self.real["AtualizarUsuario"](full_name="Profissional de Demonstração", email="demo@example.invalid",
                                         role="admin", is_active=True, tipo_acesso="normal")
        self.assertEqual(raised.exception.errors()[0]["loc"], ("role",))

    def test_generic_admin_handler_keeps_self_and_other_admin_protection(self):
        for actor_id in (99001, 99002):
            with self.subTest(actor_id=actor_id):
                user, db, _ = self.fixture()
                before = vars(user).copy()
                data = self.real["AtualizarUsuario"](full_name="Tentativa demonstrativa", email="other@example.invalid",
                        role="medico", is_active=False, tipo_acesso="investidor")
                with self.assertRaises(HttpFailure) as raised:
                    self.real["atualizar_usuario"](user.id, data, db, SimpleNamespace(id=actor_id, role="admin"))
                self.assertEqual(raised.exception.status_code, 409)
                self.assertEqual(vars(user), before)
                self.assertEqual(db.commits, 0)

    def test_real_self_handler_persists_professional_fields_without_changing_governance_or_unshown_fields(self):
        user, db, tasks = self.fixture()
        protected = {name: getattr(user, name) for name in (
            "id", "role", "email", "is_active", "convidado", "investidor", "cpf", "birth_date",
            "home_street", "home_number", "practice_street", "practice_phone", "include_workplace_on_documents",
        )}
        changes = {"full_name":"Profissional Atualizado Demonstrativo", "specialty":"Especialidade atualizada",
                   "workplace_name":"Instituição fictícia", "workplace_department":"Setor demonstrativo",
                   "workplace_role":"Função demonstrativa", "workplace_notes":"Nota demonstrativa", "professional_title":"Dra."}
        data = self.payload(user, **changes, role="leitor", email="ignored@example.invalid", is_active=False, investidor=True)
        result = self.real["atualizar_me"](data, tasks, db, user)
        for name, value in changes.items():
            self.assertEqual(result[name], value)
        for name, value in protected.items():
            self.assertEqual(getattr(user, name), value)
        self.assertEqual((db.commits, db.refreshes), (1, 1))
        self.assertEqual(len(tasks.items), 1)
        self.assertEqual(tasks.items[0][1][0], user.id)

    def test_self_handler_keeps_existing_birth_date_and_cpf_immutable(self):
        for changes in ({"birth_date":"1981-01-01"}, {"cpf":"000.000.000-00"}):
            with self.subTest(field=next(iter(changes))):
                user, db, tasks = self.fixture()
                user.cpf = "11111111111"  # explicitly invalid fixture, not a real identifier
                before = vars(user).copy()
                with self.assertRaises(HttpFailure) as raised:
                    self.real["atualizar_me"](self.payload(user, **changes), tasks, db, user)
                self.assertEqual(raised.exception.status_code, 422)
                self.assertEqual(vars(user), before)
                self.assertEqual(db.commits, 0)

    def test_invalid_professional_title_and_uf_remain_field_specific_validation_errors(self):
        user, _, _ = self.fixture()
        for field, value in (("professional_title", "INVALID_DEMO"), ("council_state", "XX")):
            with self.subTest(field=field), self.assertRaises(ValidationError) as raised:
                self.payload(user, **{field:value})
            self.assertEqual(raised.exception.errors()[0]["loc"], (field,))


if __name__ == "__main__":
    unittest.main()
