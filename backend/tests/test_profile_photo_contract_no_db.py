"""Profile retirement/upload regressions, executed without app imports or DB.

Run directly: python -B backend/tests/test_profile_photo_contract_no_db.py
Retired names appear only in negative assertions and legacy-data fixtures.
The real function bodies run against explicit in-memory dependencies; no
conftest, filesystem upload, database, external request or background job runs.
"""
import ast
import asyncio
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location("profile_test_helpers", HERE / "test_admin_profile_update_no_db.py")
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)
RETIRED = ("instagram_handle", "instagram_photo_url")


def load_function(name, namespace, *, omit_dependency_import=False):
    path = helpers.APP / "api/auth.py"
    node = next(node for node in ast.parse(path.read_text()).body
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name)
    node.decorator_list = []  # no router registration
    if omit_dependency_import:
        # Only the entitlement import is replaced by explicit dependency stubs.
        # The real serialization body, including its field allowlist, is unchanged.
        node.body = [item for item in node.body if not (
            isinstance(item, ast.ImportFrom) and item.module == "app.services.entitlement")]
    module = ast.Module(body=[ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0), node], type_ignores=[])
    exec(compile(ast.fix_missing_locations(module), str(path), "exec"), namespace)


class ProfilePhotoContractTest(unittest.TestCase):
    def setUp(self):
        self.ns = helpers.real_handlers()
        self.user, self.db, self.tasks = helpers.AdminProfileUpdateTest.fixture(SimpleNamespace(real=self.ns))
        self.user.photo_url = "/fotos/fixture-existing.png"
        self.user.instagram_handle = "legacy-fixture-not-an-account"
        self.user.instagram_photo_url = "/fotos/fixture-legacy-existing.png"

    def test_retired_fields_are_not_part_of_either_real_input_schema(self):
        helpers.load_nodes(helpers.APP / "api/auth.py", {"SolicitacaoAcesso"}, self.ns)
        self.ns["SolicitacaoAcesso"].model_rebuild(_types_namespace=self.ns)
        for name in ("DadosPessoais", "SolicitacaoAcesso"):
            self.assertTrue(set(RETIRED).isdisjoint(self.ns[name].model_fields))
        signup = self.ns["SolicitacaoAcesso"](
            full_name="Pessoa Demonstrativa", birth_date="1980-01-01", cpf="00000000000",
            profession="Medicina", council_name="CRM", council_number="DEMO", council_state="SP",
            email="demo@example.invalid", password="example-only-not-a-credential",
            instagram_handle="ignored-legacy-input",
        )
        self.assertNotIn("instagram_handle", signup.model_dump())
        self.assertEqual(signup.council_number, "DEMO")

    def test_profile_update_ignores_retired_input_without_deleting_legacy_data_or_photo(self):
        before = {key: getattr(self.user, key) for key in (*RETIRED, "photo_url", "role", "email", "is_active")}
        data = helpers.AdminProfileUpdateTest.payload(SimpleNamespace(real=self.ns), self.user,
            full_name="Nome Atualizado Demonstrativo", specialty="Especialidade demonstrativa",
            instagram_handle=None, instagram_photo_url="/not-permitted.png")
        self.ns["atualizar_me"](data, self.tasks, self.db, self.user)
        self.assertEqual(self.user.full_name, "Nome Atualizado Demonstrativo")
        self.assertEqual({key: getattr(self.user, key) for key in before}, before)
        self.assertEqual(self.db.commits, 1)

    def test_real_profile_response_keeps_manual_photo_and_profession_but_not_retired_fields(self):
        for key in ("crm", "created_at", "document_logo_url", "sex", "boas_vindas_pendente", "assinatura_metodo_preferido"):
            setattr(self.user, key, None)
        self.ns.update(eh_socio=lambda user: False, tem_acesso_ao_produto=lambda db, user: True,
            _kyc_required=lambda db, user: False, _onboarding_pendente=lambda db, user: False,
            _cpf_mascarado=lambda value: None, logo_needs_dark_plate=lambda value: False)
        helpers.load_nodes(helpers.APP / "services/professional_profile.py", {"council_display", "profile_payload"}, self.ns)
        load_function("_perfil", self.ns, omit_dependency_import=True)
        result = self.ns["_perfil"](self.db, self.user)
        self.assertTrue(set(RETIRED).isdisjoint(result))
        self.assertEqual(result["photo_url"], "/fotos/fixture-existing.png")
        self.assertEqual(result["specialty"], self.user.specialty)
        self.assertEqual(result["role"], "admin")
        self.assertTrue(result["product_access"])

    def test_no_operational_references_or_services_remain(self):
        for folder in (ROOT / "frontend/src", helpers.APP):
            hits = []
            for path in folder.rglob("*"):
                if path.suffix not in {".py", ".ts", ".tsx", ".css", ".json"}:
                    continue
                for line in path.read_text().splitlines():
                    if "instagram" in line.casefold():
                        hits.append((path.relative_to(ROOT).as_posix(), line.strip()))
            self.assertEqual(hits, [])
        for module in ("instagram_profile.py", "instagram_handle.py"):
            self.assertFalse((helpers.APP / "services" / module).exists())

    def photo_handler(self):
        calls = []
        self.ns.update(File=lambda *args: None, TAMANHO_MAXIMO=3 * 1024 * 1024,
                       _publicar_imagem_perfil=lambda **kwargs: calls.append(kwargs) or {"photo_url": "/fotos/fixture-new.png"})
        load_function("enviar_foto", self.ns)
        return calls

    def test_real_manual_upload_dispatches_only_to_current_users_photo(self):
        calls = self.photo_handler()
        reads = []
        async def read(limit):
            reads.append(limit)
            return b"synthetic-image-payload"
        result = asyncio.run(self.ns["enviar_foto"](SimpleNamespace(read=read, filename="fixture.png"), self.db, self.user))
        self.assertEqual(reads, [3 * 1024 * 1024 + 1])
        self.assertEqual(result["photo_url"], "/fotos/fixture-new.png")
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["atributo"], "photo_url")
        self.assertEqual(calls[0]["subdiretorio"], "fotos")
        self.assertIs(calls[0]["user"], self.user)
        self.assertEqual(self.db.commits, 0)  # publisher is an isolated boundary

    def test_real_manual_upload_keeps_size_and_empty_guards(self):
        calls = self.photo_handler()
        for payload, expected in ((b"", 422), (b"x" * (3 * 1024 * 1024 + 1), 413)):
            async def read(limit):
                return payload[:limit]
            with self.subTest(status=expected), self.assertRaises(helpers.HttpFailure) as raised:
                asyncio.run(self.ns["enviar_foto"](SimpleNamespace(read=read, filename="fixture.png"), self.db, self.user))
            self.assertEqual(raised.exception.status_code, expected)
        self.assertEqual(calls, [])
        self.assertEqual(self.user.photo_url, "/fotos/fixture-existing.png")


if __name__ == "__main__":
    unittest.main()
