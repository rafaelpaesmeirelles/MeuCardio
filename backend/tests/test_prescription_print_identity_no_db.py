"""Pure print-response contracts; run directly with Python, without conftest.

The real endpoint is compiled from its AST without the route decorator.
Only the literal corporate identity is read from the canonical module; no
application, ORM, database, PDF renderer or patient data are loaded.
"""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "backend/app/api/prescriptions.py"
IDENTITY_SOURCE = ROOT / "backend/app/services/pdf/identidade_institucional.py"


class HTTPException(Exception):
    def __init__(self, status_code, detail):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


def canonical_operator():
    tree = ast.parse(IDENTITY_SOURCE.read_text(encoding="utf-8"))
    assignments = [node for node in tree.body if isinstance(node, ast.Assign)
                   and any(isinstance(target, ast.Name) and target.id == "EMPRESA"
                           for target in node.targets)]
    assert len(assignments) == 1, "EMPRESA must have one canonical definition"
    return ast.literal_eval(assignments[0].value)


def print_endpoint(namespace):
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)
                 and node.name == "dados_para_impressao"]
    assert len(functions) == 1
    functions[0].decorator_list = []
    module = ast.Module(body=functions, type_ignores=[])
    exec(compile(module, str(SOURCE), "exec"), namespace)
    return namespace["dados_para_impressao"]


class PrescriptionPrintIdentityTest(unittest.TestCase):
    def setUp(self):
        self.events = []
        self.prescription_model = object()
        self.prescription = SimpleNamespace(id=-501, patient_id=-901)
        self.user = SimpleNamespace(id=-701, operadora={"cnpj": "NOT-CANONICAL"})
        self.patient = SimpleNamespace(initials="QA", record_number="FICTICIO-901")
        self.company = canonical_operator()
        self.expected_prescription = {"id": -501, "items": []}
        self.expected_doctor = {"full_name": "Profissional demonstrativo"}

        def lookup(model, record_id):
            self.events.append("lookup")
            return self.prescription

        def authorize(patient_id, db, user):
            self.events.append("ownership")
            return self.patient

        def dump(record):
            self.events.append("dump")
            return self.expected_prescription

        def identity(user):
            self.events.append("identity")
            return self.expected_doctor

        self.db = SimpleNamespace(get=Mock(side_effect=lookup))
        self.ownership = Mock(side_effect=authorize)
        self.dump = Mock(side_effect=dump)
        self.identity = Mock(side_effect=identity)
        self.endpoint = print_endpoint({
            "Prescription": self.prescription_model,
            "Session": object,
            "Depends": lambda dependency: None,
            "get_db": object(),
            "current_user": object(),
            "HTTPException": HTTPException,
            "patient_for_user": self.ownership,
            "_dump": self.dump,
            "document_identity": self.identity,
            "EMPRESA": self.company,
        })

    def test_authorized_response_copies_canonical_operator_after_ownership_check(self):
        expected_company = canonical_operator()
        response = self.endpoint(-501, self.db, self.user)

        self.db.get.assert_called_once_with(self.prescription_model, -501)
        self.ownership.assert_called_once_with(-901, self.db, self.user)
        self.dump.assert_called_once_with(self.prescription)
        self.identity.assert_called_once_with(self.user)
        self.assertEqual(self.events, ["lookup", "ownership", "dump", "identity"])
        self.assertEqual(response["prescricao"], self.expected_prescription)
        self.assertEqual(response["paciente"], {"initials": "QA", "record_number": "FICTICIO-901"})
        self.assertEqual(response["medico"], self.expected_doctor)
        self.assertEqual(response["operadora"], expected_company)
        self.assertIsNot(response["operadora"], self.company)
        self.assertEqual(set(response), {"prescricao", "paciente", "medico", "operadora"})

        response["operadora"]["cnpj"] = "CHANGED-IN-RESPONSE-ONLY"
        self.assertEqual(self.company, expected_company)
        second_response = self.endpoint(-501, self.db, self.user)
        self.assertEqual(second_response["operadora"], expected_company)
        self.assertIsNot(second_response["operadora"], response["operadora"])

    def test_missing_prescription_is_404_without_lookup_of_patient_or_identity(self):
        self.db.get.side_effect = None
        self.db.get.return_value = None

        with self.assertRaises(HTTPException) as raised:
            self.endpoint(-999, self.db, self.user)

        self.assertEqual(raised.exception.status_code, 404)
        self.assertEqual(raised.exception.detail, "Prescrição não encontrada.")
        self.db.get.assert_called_once_with(self.prescription_model, -999)
        self.ownership.assert_not_called()
        self.dump.assert_not_called()
        self.identity.assert_not_called()

    def test_denied_patient_ownership_propagates_without_serializing_any_document(self):
        denied = HTTPException(status_code=404, detail="Paciente não encontrado.")
        self.ownership.side_effect = denied

        with self.assertRaises(HTTPException) as raised:
            self.endpoint(-501, self.db, self.user)

        self.assertIs(raised.exception, denied)
        self.db.get.assert_called_once_with(self.prescription_model, -501)
        self.ownership.assert_called_once_with(-901, self.db, self.user)
        self.dump.assert_not_called()
        self.identity.assert_not_called()
        self.assertEqual(self.company, canonical_operator())


if __name__ == "__main__":
    unittest.main()
