"""Contrato do MICA não estimado, executável diretamente sem app/DB/conftest.

Extrai funções, schema e registro reais por AST. Somente os modelos de
persistência, autenticação e resolução de identidade são substituídos em memória.
"""

import ast
from pathlib import Path
from types import SimpleNamespace
import unittest


APP = Path(__file__).resolve().parents[1] / "app"


def compile_nodes(nodes, path, env):
    for node in nodes:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            node.decorator_list = []
    module = ast.Module(body=[
        ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0), *nodes,
    ], type_ignores=[])
    exec(compile(ast.fix_missing_locations(module), str(path), "exec"), env)


def load_calculators():
    path = APP / "services/calculators.py"
    tree = ast.parse(path.read_text())
    env = {
        "Field": lambda *_args, **_kwargs: None,
        "Calculator": lambda **kwargs: SimpleNamespace(status="implementada", **kwargs),
    }
    functions = {"_rcri", "_rcri_txt", "_gupta_mica", "_gupta_mica_txt", "run"}
    nodes = [node for node in tree.body if (
        isinstance(node, ast.FunctionDef) and node.name in functions
    ) or (
        isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "_GUPTA_PROCEDIMENTOS" for target in node.targets)
    )]
    compile_nodes(nodes, path, env)
    registry = next(node for node in tree.body if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == "REGISTRY")
    selected = [(key, value) for key, value in zip(registry.value.keys, registry.value.values) if ast.literal_eval(key) in {"rcri", "gupta-mica"}]
    expression = ast.Expression(ast.Dict(
        keys=[key for key, _ in selected], values=[value for _, value in selected],
    ))
    env["REGISTRY"] = eval(compile(ast.fix_missing_locations(expression), str(path), "eval"), env)
    return env


class InputModel:
    """Materializa somente os campos/defaults da classe real, sem Pydantic/IO."""

    def __init__(self, **values):
        for name in self.__annotations__:
            setattr(self, name, values.get(name, getattr(type(self), name, None)))


class HTTPException(Exception):
    def __init__(self, status_code, detail):
        self.status_code = status_code
        super().__init__(detail)


class Document(SimpleNamespace):
    def __init__(self, **fields):
        super().__init__(id=99001, created_at="DATA-DEMONSTRATIVA", **fields)


class GuptaNotEstimatedTests(unittest.TestCase):
    def setUp(self):
        self.calc = load_calculators()
        self.added, self.calculated = [], []
        self.commits = 0
        self.db = SimpleNamespace(
            add=self.added.append, flush=lambda: None, commit=self.commit, refresh=lambda _obj: None,
        )
        self.user = SimpleNamespace(id=99002)
        self.env = {
            "BaseModel": InputModel, "Depends": lambda dep: dep,
            "get_db": lambda: None, "current_user": lambda: None,
            "HTTPException": HTTPException, "calc": SimpleNamespace(run=self.run_calculator),
            "GeneratedDocument": Document, "AuditLog": SimpleNamespace,
            "DOC_TYPE": "avaliacao_preoperatoria", "TITULO_DOCUMENTO": "Avaliação de demonstração",
            "document_identity": lambda _user: {"full_name": "Profissional de demonstração"},
            "patient_profile_service": SimpleNamespace(resolver_paciente_documento=lambda *_args, **_kwargs: (None, None, None)),
        }
        path = APP / "api/avaliacao_preoperatoria.py"
        tree = ast.parse(path.read_text())
        names = {"GerarIn", "_resultado_calculadora", "_montar_corpo", "gerar"}
        compile_nodes([node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in names], path, self.env)

    def commit(self):
        self.commits += 1

    def run_calculator(self, slug, payload):
        self.calculated.append(slug)
        return self.calc["run"](slug, payload)

    def input(self, **fields):
        return self.env["GerarIn"](procedimento_planejado="Procedimento informado para demonstração", **fields)

    def generate(self, **fields):
        return self.env["gerar"](self.input(**fields), self.db, self.user)

    def gupta_payload(self, **fields):
        return {"idade": 60, "status_funcional": "independente", "asa": 2,
                "creatinina_maior_1_5": False, "tipo_procedimento": "hernia", **fields}

    def test_flag_defaults_false_for_existing_clients(self):
        self.assertIs(self.input().gupta_nao_estimado, False)

    def test_other_method_generates_note_without_mica_number_and_persists_flag(self):
        result = self.generate(gupta_nao_estimado=True, gupta=None, rcri={"cirurgia_alto_risco": False})
        self.assertEqual(self.calculated, ["rcri"])
        self.assertIsNone(result["gupta"])
        self.assertTrue(result["gupta_nao_estimado"])
        text = result["rendered_body"]
        self.assertIn("Gupta MICA não estimado", text)
        self.assertIn("sem categoria correspondente validada no modelo", text)
        self.assertIn("Classificação do procedimento informada pelo profissional: Outras (Baixo Risco)", text)
        self.assertNotRegex(text, r"Gupta MICA[^\n]*\d+(?:[.,]\d+)?%")
        self.assertIn("RCRI", text)
        document, audit = self.added
        self.assertTrue(document.variables["gupta_nao_estimado"])
        self.assertEqual(document.variables["gupta"], {})
        self.assertEqual(document.variables["rcri"], {"cirurgia_alto_risco": False})
        self.assertTrue(audit.detail["gupta_nao_estimado"])
        self.assertFalse(audit.detail["tem_gupta"])
        self.assertEqual(self.commits, 1)

    def test_flag_with_any_gupta_payload_rejected_before_calculation_or_write(self):
        for payload in [{}, self.gupta_payload(), {"tipo_procedimento": "outras_baixo_risco"}]:
            with self.subTest(payload=payload):
                with self.assertRaises(HTTPException) as caught:
                    self.generate(gupta_nao_estimado=True, gupta=payload, rcri={"cirurgia_alto_risco": False})
                self.assertEqual(caught.exception.status_code, 422)
                self.assertEqual(self.calculated, [])
                self.assertEqual(self.added, [])
                self.assertEqual(self.commits, 0)

    def test_flag_alone_or_empty_method_is_not_a_calculated_assessment(self):
        for methods in [{}, {"rcri": {}}, {"dasi": {}}]:
            with self.subTest(methods=methods):
                with self.assertRaises(HTTPException) as caught:
                    self.generate(gupta_nao_estimado=True, **methods)
                self.assertEqual(caught.exception.status_code, 422)
                self.assertEqual(self.added, [])
                self.assertEqual(self.commits, 0)

    def test_existing_numeric_gupta_document_does_not_gain_not_estimated_note(self):
        result = self.generate(gupta=self.gupta_payload())
        self.assertEqual(result["gupta"], {"risco_pct": 0.06, "procedimento": "Hérnia"})
        self.assertFalse(result["gupta_nao_estimado"])
        self.assertNotIn("não estimado", result["rendered_body"])
        self.assertNotIn("Outras (Baixo Risco)", result["rendered_body"])
        self.assertEqual(self.calculated, ["gupta-mica"])

    def test_original_21_coefficients_and_numeric_baselines_unchanged(self):
        expected = {
            "hernia": 0.0, "anorretal": -0.16, "aortica": 1.6, "bariatrica": -0.25,
            "encefalica": 1.4, "mama": -1.61, "cardiaca": 1.01, "orl": 0.71,
            "foregut_hpb": 1.39, "vesicula_apendice_adrenal_baco": 0.59,
            "intestinal": 1.14, "pescoco": 0.18, "obstetrica_ginecologica": 0.76,
            "ortopedica": 0.8, "abdome_outro": 1.13, "vascular_periferica": 0.86,
            "pele": 0.54, "coluna": 0.21, "toracica": 0.4, "veias": -1.09, "urologia": -0.26,
        }
        self.assertEqual({key: value[1] for key, value in self.calc["_GUPTA_PROCEDIMENTOS"].items()}, expected)
        result = self.calc["_gupta_mica"](self.gupta_payload(
            idade=80, status_funcional="totalmente_dependente", asa=4,
            creatinina_maior_1_5=True, tipo_procedimento="aortica",
        ))
        self.assertEqual(result, {"risco_pct": 20.42, "procedimento": "Aórtica"})
        with self.assertRaises(KeyError):
            self.calc["_gupta_mica"](self.gupta_payload(tipo_procedimento="outras_baixo_risco"))

    def test_unknown_mica_category_is_rejected_not_silently_approximated(self):
        with self.assertRaises(HTTPException) as caught:
            self.generate(gupta=self.gupta_payload(tipo_procedimento="outras_baixo_risco"))
        self.assertEqual(caught.exception.status_code, 422)
        self.assertEqual(self.added, [])

    def test_registry_cites_primary_tables_and_does_not_authorize_approximation(self):
        calculator = self.calc["REGISTRY"]["gupta-mica"]
        self.assertIn("10.1161/CIRCULATIONAHA.110.015701", calculator.reference)
        self.assertIn("Tabela 1", calculator.reference)
        self.assertIn("Tabela 2", calculator.reference)
        self.assertNotIn("calculadoras de terceiros", calculator.reference)
        self.assertIn("não aproximar automaticamente", calculator.limitations[0])


if __name__ == "__main__":
    unittest.main()
