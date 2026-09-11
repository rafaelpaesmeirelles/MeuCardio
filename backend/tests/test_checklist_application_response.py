"""Pure response contract: run directly with Python, never import app/DB/conftest."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest


SOURCE = Path(__file__).resolve().parents[1] / "app/api/checklists.py"


class _Field:
    def __init__(self, name):
        self.name = name

    def __eq__(self, value):
        return self.name, value


class _HTTPException(Exception):
    def __init__(self, status_code, detail):
        self.status_code = status_code
        self.detail = detail


def application_response(run, checklist, user_id):
    """Execute the real endpoint/helper AST against read-only in-memory rows."""
    tree = ast.parse(SOURCE.read_text())
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)
                 and node.name in {"_pendencias", "ver_aplicacao"}]
    assert len(functions) == 2
    for node in functions:
        node.decorator_list = []
        node.args.defaults = []
        node.returns = None
        for argument in node.args.args:
            argument.annotation = None

    run_model = SimpleNamespace(id=_Field("run_id"), user_id=_Field("owner_id"))
    checklist_model = SimpleNamespace(id=_Field("checklist_id"))
    filters = []

    class Query:
        def __init__(self, model):
            self.model = model

        def filter(self, *expressions):
            filters.append(expressions)
            self.expressions = dict(expressions)
            return self

        def first(self):
            if self.model is run_model:
                if run and self.expressions == {"run_id": run.id, "owner_id": run.user_id}:
                    return run
                return None
            assert self.model is checklist_model
            return checklist if checklist and self.expressions == {"checklist_id": checklist.id} else None

    namespace = {"DischargeChecklistRun": run_model, "DischargeChecklist": checklist_model,
                 "HTTPException": _HTTPException}
    exec(compile(ast.fix_missing_locations(ast.Module(body=functions, type_ignores=[])),
                 str(SOURCE), "exec"), namespace)
    response = namespace["ver_aplicacao"](
        run.id if run else -940, SimpleNamespace(query=Query), SimpleNamespace(id=user_id),
    )
    return response, namespace["_pendencias"], filters


class ChecklistApplicationResponseTest(unittest.TestCase):
    def rows(self, marked=None, finalized=None):
        items = [{"id": "demo-1", "texto": "Item demonstrativo A", "obrigatorio": True},
                 {"id": "demo-2", "texto": "Item demonstrativo B", "obrigatorio": False}]
        run = SimpleNamespace(id=-940, user_id=-990, checklist_id=-941,
                              identificacao_livre="APLICAÇÃO FICTÍCIA — QA", itens_no_momento=items,
                              marcados=marked, observacoes="Sem dados clínicos", finalizado_em=finalized)
        checklist = SimpleNamespace(id=-941, slug="modelo-demonstrativo", condicao="Demonstração",
                                    theme="Interface", scope_type="doenca", documento_origem=None)
        return run, checklist

    def test_empty_marks_are_always_an_id_list(self):
        for marks in (None, []):
            with self.subTest(marks=marks):
                run, checklist = self.rows(marks)
                payload, _, _ = application_response(run, checklist, run.user_id)
                self.assertEqual(payload["marcados"], [])
                self.assertEqual(payload["total"], 2)
                self.assertEqual(payload["faltando_obrigatorios"], 1)

    def test_marked_snapshot_ids_and_other_fields_are_preserved(self):
        for marks in (["demo-1"], ["demo-1", "demo-2"]):
            with self.subTest(marks=marks):
                run, checklist = self.rows(marks, "2026-09-11T12:00:00Z")
                payload, _, filters = application_response(run, checklist, run.user_id)
                self.assertEqual(payload["marcados"], marks)
                self.assertEqual(payload["itens"], run.itens_no_momento)
                self.assertEqual(payload["finalizado_em"], run.finalizado_em)
                self.assertEqual(payload["observacoes"], run.observacoes)
                self.assertEqual(payload["identificacao"], run.identificacao_livre)
                self.assertEqual(payload["checklist"], checklist.slug)
                self.assertEqual(payload["faltando_obrigatorios"], 0)
                self.assertEqual(len(payload["faltando"]), 2 - len(marks))
                self.assertEqual(filters[0], (("run_id", run.id), ("owner_id", run.user_id)))

    def test_summary_helper_keeps_its_existing_numeric_counter(self):
        run, checklist = self.rows(["demo-1"])
        _, pending, _ = application_response(run, checklist, run.user_id)
        self.assertEqual(pending(run.itens_no_momento, run.marcados)["marcados"], 1)

    def test_other_owner_still_cannot_read_application(self):
        run, checklist = self.rows(["demo-1"])
        with self.assertRaises(_HTTPException) as raised:
            application_response(run, checklist, user_id=-999)
        self.assertEqual(raised.exception.status_code, 404)

    def test_missing_checklist_preserves_historical_snapshot(self):
        run, _ = self.rows(["demo-1"])
        payload, _, _ = application_response(run, None, run.user_id)
        self.assertIsNone(payload["checklist"])
        self.assertEqual(payload["itens"], run.itens_no_momento)
        self.assertEqual(payload["marcados"], ["demo-1"])


if __name__ == "__main__":
    unittest.main()
