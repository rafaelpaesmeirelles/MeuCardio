"""Execute actual interaction consumers without database/router dependencies."""
import ast
import json
from pathlib import Path
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[2]
GRAPH = ROOT / "backend/app/services/knowledge_graph.py"
API = ROOT / "backend/app/api/drugs.py"


def tree(path):
    return ast.parse(path.read_text(encoding="utf-8"))


def execute(nodes, env, path):
    future = ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0)
    module = ast.fix_missing_locations(ast.Module(body=[future, *nodes], type_ignores=[]))
    exec(compile(module, str(path), "exec"), env)


def fixtures():
    records = json.loads((ROOT / "medicamentos/interacoes.json").read_text(encoding="utf-8"))
    negative = next(x for x in records if x["slug"] == "rivaroxabana-digoxina")
    assert negative["interaction_present"] is False
    positive = next(x for x in records if len(x.get("farmacos", [])) == 2
                    and x.get("review_status") == "revisado"
                    and x.get("interaction_present") is not False)
    return negative, positive


def graph_loop():
    function = next(n for n in tree(GRAPH).body if isinstance(n, ast.FunctionDef)
                    and n.name == "_registrar_referencias_explicitas")
    return next(n for n in function.body if isinstance(n, ast.For)
                and isinstance(n.target, ast.Name) and n.target.id == "interacao")


class InteractionAbsenceTests(unittest.TestCase):
    def test_graph_real_loop_keeps_positive_and_ignores_negative(self):
        negative, positive = fixtures()
        calls = []
        env = {
            "interacoes": [negative, positive], "db": None, "lote": None,
            "criadas": 0, "nao_resolvidas": [],
            "_no": lambda types, slug: (types, slug),
            "_registrar_relacao_estruturada": lambda *args, **kwargs: (calls.append(kwargs) or 1),
        }
        execute([graph_loop()], env, GRAPH)
        self.assertEqual(env["criadas"], 1)
        self.assertEqual(env["nao_resolvidas"], [])
        self.assertEqual(calls[0]["extra"]["registro"], positive["slug"])
        self.assertEqual(calls[0]["relation_type"], "interacts_with")
        self.assertEqual(calls[0]["review_status"], "revisado")
        self.assertEqual(calls[0]["confidence"], "explicit")

    def test_api_real_loop_keeps_positive_without_negative_alert(self):
        negative, positive = fixtures()
        loop = next(n for n in ast.walk(tree(API)) if isinstance(n, ast.For)
                    and isinstance(n.iter, ast.Call) and isinstance(n.iter.func, ast.Name)
                    and n.iter.func.id == "_interacoes_curadas")
        selected = set(negative["farmacos"] + positive["farmacos"])
        env = {
            "_interacoes_curadas": lambda: [negative, positive],
            "selecionados": selected, "nome": {slug: slug for slug in selected},
            "verificadas": [], "avisos_de_classe": [],
        }
        execute([loop], env, API)
        self.assertEqual([x["slug"] for x in env["verificadas"]], [positive["slug"]])
        self.assertEqual(env["avisos_de_classe"], [])

    def test_real_cleanup_rejects_removed_pair_preserves_manual_decisions(self):
        negative, positive = fixtures()
        names = {"_relacao_pertence_ao_backfill", "_rejeitar_relacoes_automaticas_ausentes"}
        assignments = {"_PRODUTOR_BACKFILL", "_ASSINATURAS_AUTOMATICAS_LEGADAS"}
        nodes = [n for n in tree(GRAPH).body
                 if (isinstance(n, ast.FunctionDef) and n.name in names)
                 or (isinstance(n, ast.Assign) and any(isinstance(t, ast.Name)
                     and t.id in assignments for t in n.targets))]
        env = {}
        execute(nodes, env, GRAPH)
        def relation(record, status="revisado", manual=False):
            return SimpleNamespace(
                extra={"campo": "medicamentos/interacoes.json.farmacos", "registro": record["slug"]},
                relation_type="interacts_with", review_status=status,
                source_entity=SimpleNamespace(entity_type="medicamento"),
                target_entity=SimpleNamespace(entity_type="medicamento"),
                evidence_source=("editorial/manual" if manual else "medicamentos/interacoes.json#"+record["slug"]),
                provenance_type="editorial", confidence="explicit",
            )
        removed = relation(negative)
        desired = relation(positive)
        human_rejected = relation(negative, status="rejeitado")
        manual = relation(negative, manual=True)
        batch = SimpleNamespace(existentes={"removed": removed, "positive": desired,
                                            "human": human_rejected, "manual": manual},
                                desejadas={"positive"})
        cleanup = env["_rejeitar_relacoes_automaticas_ausentes"]
        self.assertEqual(cleanup(batch), 1)
        self.assertEqual(removed.review_status, "rejeitado")
        self.assertEqual(removed.extra["_inactive_reason"], "source_removed")
        self.assertEqual(desired.review_status, "revisado")
        self.assertEqual(manual.review_status, "revisado")
        self.assertNotIn("_inactive_reason", human_rejected.extra)
        self.assertEqual(cleanup(batch), 0)


if __name__ == "__main__":
    unittest.main()
