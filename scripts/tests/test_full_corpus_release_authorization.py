"""Testes focados da autorização integral do corpus científico."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from app.services.corpus_release_authorization import (  # noqa: E402
    FULL_CORPUS_DECISION,
    FULL_CORPUS_SCOPE,
    build_front_fingerprint,
    corpus_inventory_sha256,
    resolve_publication_policy,
    validate_full_corpus_authorization,
    validate_full_corpus_publication,
)


FRONT_SOURCES = {
    "documentos": ("content", None),
    "galeria": ("galeria/metadados.json", "galeria"),
    "exames": ("exames/metadados.json", "exames"),
    "evidencias": ("evidencias/metadados.json", "evidencias"),
    "estudos": ("estudos/metadados.json", "estudos"),
    "medicamentos": ("medicamentos/metadados.json", "medicamentos"),
    "checklists": ("checklists/metadados.json", "checklists"),
    "casos_clinicos": ("casos-clinicos/metadados.json", "casos-clinicos"),
    "trilhas": ("trilhas/metadados.json", "trilhas"),
    "material_paciente": ("material-paciente/metadados.json", "material-paciente"),
    "emergencia": ("emergencia/metadados.json", "emergencia"),
    "doencas_especializadas": ("doencas/metadados.json", "doencas"),
    "triagem_sintomas": ("triagem-sintomas/metadados.json", "triagem-sintomas"),
}


def _audit_module():
    spec = importlib.util.spec_from_file_location(
        "full_corpus_release_auditor",
        ROOT / "scripts" / "audit_tudo_com_tudo.py",
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _repository_inventory():
    auditor = _audit_module()
    canonical_slugs = {}
    fingerprints = {}
    for front, (source_relative, loader_name) in FRONT_SOURCES.items():
        source = ROOT / source_relative
        if front == "documentos":
            records = []
            for path in sorted(source.rglob("*.md")):
                metadata, _body = auditor._frontmatter(path)
                records.append((metadata.get("slug") or path.stem, metadata))
        else:
            records = [
                (str(item["slug"]), item)
                for item in auditor._load(loader_name)
            ]
        slugs = {slug for slug, _metadata in records}
        statuses = {
            slug: metadata.get("review_status")
            for slug, metadata in records
        }
        canonical_slugs[front] = slugs
        fingerprint_source = (
            source.parent
            if front in {"doencas_especializadas", "triagem_sintomas"}
            else source
        )
        fingerprints[front] = build_front_fingerprint(
            fingerprint_source,
            slugs,
            statuses,
        )
    return canonical_slugs, fingerprints


def _manifest(fingerprints, *, expected_total, inventory_sha256):
    return {
        "schema_version": 1,
        "release": "teste",
        "decision": FULL_CORPUS_DECISION,
        "scope": FULL_CORPUS_SCOPE,
        "approval_basis": "Aprovação explícita de teste.",
        "expected_total": expected_total,
        "inventory_sha256": inventory_sha256,
        "fronts": fingerprints,
    }


class FullCorpusReleaseAuthorizationTests(unittest.TestCase):
    def test_manifesto_real_vincula_exatamente_11581_revisados(self):
        canonical, fingerprints = _repository_inventory()

        authorized, metadata = validate_full_corpus_authorization(
            ROOT / "editorial-approvals" / "full-corpus-release-20260905.json",
            canonical_slugs=canonical,
            fingerprints=fingerprints,
        )

        self.assertEqual(sum(map(len, authorized.values())), 11_581)
        self.assertEqual(metadata["authorized_total"], 11_581)
        self.assertEqual(set(authorized), set(FRONT_SOURCES))
        self.assertTrue(all(
            fingerprint["count"] == fingerprint["reviewed_count"]
            for fingerprint in fingerprints.values()
        ))

    def test_alteracao_de_fonte_invalida_autorizacao(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "metadados.json"
            source.write_text('[{"slug":"canonico"}]', encoding="utf-8")
            canonical = {"teste": {"canonico"}}
            statuses = {"canonico": "revisado"}
            fingerprints = {
                "teste": build_front_fingerprint(source, canonical["teste"], statuses)
            }
            manifest = _manifest(
                fingerprints,
                expected_total=1,
                inventory_sha256=corpus_inventory_sha256(fingerprints),
            )
            path = root / "release.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            source.write_text('[{"slug":"canonico","novo":true}]', encoding="utf-8")
            changed = {
                "teste": build_front_fingerprint(source, canonical["teste"], statuses)
            }

            with self.assertRaisesRegex(RuntimeError, "não corresponde"):
                validate_full_corpus_authorization(
                    path,
                    canonical_slugs=canonical,
                    fingerprints=changed,
                )

    def test_item_nao_revisado_fecha_publicacao(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "metadados.json"
            source.write_text('[{"slug":"canonico"}]', encoding="utf-8")
            canonical = {"teste": {"canonico"}}
            fingerprints = {
                "teste": build_front_fingerprint(
                    source,
                    canonical["teste"],
                    {"canonico": "pendente_revisao"},
                )
            }
            manifest = _manifest(
                fingerprints,
                expected_total=1,
                inventory_sha256=corpus_inventory_sha256(fingerprints),
            )
            path = root / "release.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "item não revisado"):
                validate_full_corpus_authorization(
                    path,
                    canonical_slugs=canonical,
                    fingerprints=fingerprints,
                )

    def test_autorizacao_devolve_so_canonico_e_nunca_historico(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "metadados.json"
            source.write_text('[{"slug":"canonico"}]', encoding="utf-8")
            canonical = {"teste": {"canonico"}}
            fingerprints = {
                "teste": build_front_fingerprint(
                    source,
                    canonical["teste"],
                    {"canonico": "revisado"},
                )
            }
            manifest = _manifest(
                fingerprints,
                expected_total=1,
                inventory_sha256=corpus_inventory_sha256(fingerprints),
            )
            path = root / "release.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")

            authorized, _metadata = validate_full_corpus_authorization(
                path,
                canonical_slugs=canonical,
                fingerprints=fingerprints,
            )

            self.assertEqual(authorized, {"teste": {"canonico"}})
            self.assertNotIn("historico", authorized["teste"])

    def test_override_integral_e_fail_closed_ficam_restritos_ao_canonico(self):
        eligible, ineligible = resolve_publication_policy(
            {"integral", "quarentena", "sem-aprovacao"},
            {
                "integral": False,
                "quarentena": False,
                "sem-aprovacao": True,
            },
            {"integral", "quarentena"},
            {"integral"},
        )

        self.assertEqual(eligible, {"integral"})
        self.assertEqual(ineligible, {"quarentena", "sem-aprovacao"})
        with self.assertRaisesRegex(RuntimeError, "não canônico"):
            resolve_publication_policy(
                {"canonico"},
                {"canonico": False},
                {"canonico"},
                {"canonico", "historico"},
            )

    def test_gate_final_exige_total_e_contagens_por_frente(self):
        authorization = {
            "authorized_total": 3,
            "fronts": {"documentos": 2, "evidencias": 1},
        }
        validate_full_corpus_publication(
            {
                "published_total": 3,
                "fronts": {
                    "documentos": {"published": 2},
                    "evidencias": {"published": 1},
                },
            },
            authorization,
        )

        with self.assertRaisesRegex(RuntimeError, "Publicação integral incompleta"):
            validate_full_corpus_publication(
                {
                    "published_total": 2,
                    "fronts": {
                        "documentos": {"published": 2},
                        "evidencias": {"published": 0},
                    },
                },
                authorization,
            )


if __name__ == "__main__":
    unittest.main()
