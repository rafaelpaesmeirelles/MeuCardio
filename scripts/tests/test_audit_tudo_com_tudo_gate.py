from __future__ import annotations

from contextlib import redirect_stdout
from importlib.util import module_from_spec, spec_from_file_location
import io
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]


def _load_auditor():
    spec = spec_from_file_location(
        "audit_tudo_com_tudo_gate_tests",
        ROOT / "scripts" / "audit_tudo_com_tudo.py",
    )
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


AUDITOR = _load_auditor()


class AuditTudoComTudoGateTests(unittest.TestCase):
    def test_reference_issue_distinguishes_missing_from_wrong_type(self):
        slugs = {
            "documento": {"doc-certo"},
            "fluxograma": set(),
            "estudo": {"estudo-no-campo-errado"},
        }

        self.assertIsNone(AUDITOR._reference_issue(
            field="EvidenceRecord.document_slug",
            source="evidencia-ok",
            target="doc-certo",
            allowed=("documento", "fluxograma"),
            slugs=slugs,
        ))

        wrong_type = AUDITOR._reference_issue(
            field="EvidenceRecord.document_slug",
            source="evidencia-tipo-errado",
            target="estudo-no-campo-errado",
            allowed=("documento", "fluxograma"),
            slugs=slugs,
        )
        self.assertEqual(wrong_type, {
            "field": "EvidenceRecord.document_slug",
            "source": "evidencia-tipo-errado",
            "target": "estudo-no-campo-errado",
            "reason": "wrong_target_type",
            "allowed_types": ["documento", "fluxograma"],
            "actual_types": ["estudo"],
        })

        missing = AUDITOR._reference_issue(
            field="Document.body_md.link",
            source="doc-origem",
            target="doc-ausente",
            allowed=("documento", "fluxograma"),
            slugs=slugs,
        )
        self.assertIsNotNone(missing)
        self.assertEqual(missing["reason"], "missing_target")
        self.assertEqual(missing["actual_types"], [])

    def test_evidence_study_reference_requires_unique_typed_target_and_matching_pmid(self):
        ready = {"published": True, "review_status": "revisado"}
        slugs = {
            "documento": {"alvo-tipo-errado"},
            "estudo": {
                "estudo-certo", "estudo-pmid-divergente", "estudo-sem-pmid",
                "estudo-duplicado",
            },
        }
        studies_by_slug = {
            "estudo-certo": [{
                "slug": "estudo-certo", "pmid": 12345, **ready,
            }],
            "estudo-pmid-divergente": [{
                "slug": "estudo-pmid-divergente", "pmid": "99999", **ready,
            }],
            "estudo-sem-pmid": [{"slug": "estudo-sem-pmid", **ready}],
            "estudo-duplicado": [
                {"slug": "estudo-duplicado", "pmid": "12345", **ready},
                {"slug": "estudo-duplicado", "pmid": "12345", **ready},
            ],
        }

        self.assertIsNone(AUDITOR._evidence_study_issue(
            {"slug": "evidencia-ok", "study_slug": "estudo-certo", "pmid": " 12345 "},
            slugs=slugs,
            studies_by_slug=studies_by_slug,
        ))
        self.assertIsNone(AUDITOR._evidence_study_issue(
            {"slug": "evidencia-sem-pmid", "study_slug": "estudo-sem-pmid"},
            slugs=slugs,
            studies_by_slug=studies_by_slug,
        ))

        missing = AUDITOR._evidence_study_issue(
            {"slug": "evidencia-ausente", "study_slug": "estudo-ausente"},
            slugs=slugs,
            studies_by_slug=studies_by_slug,
        )
        self.assertEqual(missing["reason"], "missing_target")

        empty = AUDITOR._evidence_study_issue(
            {"slug": "evidencia-vazia", "study_slug": ""},
            slugs=slugs,
            studies_by_slug=studies_by_slug,
        )
        self.assertEqual(empty["reason"], "missing_target")

        wrong_type = AUDITOR._evidence_study_issue(
            {"slug": "evidencia-tipo", "study_slug": "alvo-tipo-errado"},
            slugs=slugs,
            studies_by_slug=studies_by_slug,
        )
        self.assertEqual(wrong_type["reason"], "wrong_target_type")
        self.assertEqual(wrong_type["actual_types"], ["documento"])

        mismatch = AUDITOR._evidence_study_issue(
            {
                "slug": "evidencia-pmid-divergente",
                "study_slug": "estudo-pmid-divergente",
                "pmid": "12345",
            },
            slugs=slugs,
            studies_by_slug=studies_by_slug,
        )
        self.assertEqual(mismatch["reason"], "pmid_mismatch")
        self.assertEqual(mismatch["source_pmid"], "12345")
        self.assertEqual(mismatch["target_pmid"], "99999")

        missing_pmid = AUDITOR._evidence_study_issue(
            {
                "slug": "evidencia-pmid-sem-alvo",
                "study_slug": "estudo-sem-pmid",
                "pmid": "12345",
            },
            slugs=slugs,
            studies_by_slug=studies_by_slug,
        )
        self.assertEqual(missing_pmid["reason"], "target_pmid_missing")

        ambiguous = AUDITOR._evidence_study_issue(
            {
                "slug": "evidencia-ambigua",
                "study_slug": "estudo-duplicado",
                "pmid": "12345",
            },
            slugs=slugs,
            studies_by_slug=studies_by_slug,
        )
        self.assertEqual(ambiguous["reason"], "ambiguous_target")
        self.assertEqual(ambiguous["matching_studies"], 2)

    def test_editorial_gate_preserves_explicit_false_without_mutating_record(self):
        record = {
            "slug": "conteudo-revisado-nao-publicado",
            "review_status": "revisado",
            "published": False,
            "review_note": "Revisão editorial concluída.",
        }
        snapshot = dict(record)

        self.assertEqual(AUDITOR._editorial_issues("estudo", [record]), [])
        self.assertEqual(record, snapshot)
        self.assertEqual(AUDITOR._publication_flags([record]), {
            "true": 0,
            "false": 1,
            "missing": 0,
            "invalid": 0,
        })

    def test_editorial_gate_blocks_pending_published_and_contradictory_note(self):
        issues = AUDITOR._editorial_issues("evidencia", [
            {
                "slug": "publicado-sem-revisao",
                "review_status": "pendente_revisao",
                "published": True,
            },
            {
                "slug": "status-contradiz-nota",
                "review_status": "revisado",
                "published": False,
                "review_note": "Artigo integral e revisão independente pendentes.",
            },
            {
                "slug": "nota-nova-nao-apaga-pendencia-antiga",
                "review_status": "revisado",
                "published": False,
                "review_note": "Estrutura conferida.",
                "revisao": "Aguardando revisão editorial independente.",
            },
            {
                "slug": "sem-aval-explicito",
                "review_status": "revisado",
                "published": False,
                "revisao": "Este item ainda não carrega aval clínico individual.",
            },
        ])

        self.assertEqual([issue["reason"] for issue in issues], [
            "published_without_review_or_approval",
            "reviewed_with_pending_review_note",
            "reviewed_with_pending_review_note",
            "reviewed_with_pending_review_note",
        ])

    def test_editorial_gate_blocks_explicitly_incomplete_methodological_review(self):
        records = [
            {
                "slug": "revisao-generica-pendente",
                "review_status": "revisado",
                "published": False,
                "review_note": (
                    "Achado de estudo baseado no abstract/XML PubMed; "
                    "revisão pendente."
                ),
            },
            {
                "slug": "revisao-independente-obrigatoria",
                "review_status": "revisado",
                "published": False,
                "review_note": (
                    "Registro e artigo integral não conferidos; "
                    "revisão independente obrigatória."
                ),
            },
            {
                "slug": "somente-abstract-sem-revisao-completa",
                "review_status": "revisado",
                "published": False,
                "review_note": (
                    "Síntese limitada ao abstract PubMed; "
                    "artigo integral não conferido."
                ),
            },
        ]

        issues = AUDITOR._editorial_issues("estudo", records)

        self.assertEqual(
            [issue["identifier"] for issue in issues],
            [record["slug"] for record in records],
        )
        self.assertTrue(all(
            issue["reason"] == "reviewed_with_pending_review_note"
            for issue in issues
        ))

    def test_editorial_gate_preserves_legitimate_methodological_cautions(self):
        records = [
            {
                "slug": "revisao-independente-documentada",
                "review_status": "revisado",
                "published": False,
                "review_note": (
                    "Revisão independente Codex: PMID/DOI, números do abstract, "
                    "estrutura e segurança clínica verificados em 2026-08-30; "
                    "artigo integral não conferido."
                ),
            },
            {
                "slug": "revisao-clinica-concluida",
                "review_status": "revisado",
                "published": False,
                "review_note": (
                    "Revisão editorial e clínica concluída em 2026-08-30 "
                    "contra XML/abstract PubMed; artigo integral não conferido."
                ),
            },
            {
                "slug": "cautela-sem-pendencia-editorial",
                "review_status": "revisado",
                "published": False,
                "review_note": (
                    "Achado de estudo, não recomendação nem classe oficial; "
                    "generalização clínica limitada."
                ),
            },
        ]

        self.assertEqual(AUDITOR._editorial_issues("estudo", records), [])

    def test_editorial_gate_allows_and_counts_unpublished_quarantine(self):
        records = [
            {
                "slug": "pendente-explicitamente-retido",
                "review_status": "pendente_revisao",
                "published": False,
            },
            {
                "slug": "rejeitado-sem-flag",
                "review_status": "rejeitado",
            },
        ]

        self.assertEqual(AUDITOR._editorial_issues("estudo", records), [])
        self.assertEqual(AUDITOR._editorial_quarantine("estudo", records), [
            {
                "kind": "estudo",
                "identifier": "pendente-explicitamente-retido",
                "review_status": "pendente_revisao",
                "published": False,
            },
            {
                "kind": "estudo",
                "identifier": "rejeitado-sem-flag",
                "review_status": "rejeitado",
                "published": "missing",
            },
        ])

    def test_versioned_approval_allows_published_pending_record(self):
        record = {
            "slug": "aprovado-em-manifesto",
            "review_status": "pendente_revisao",
            "published": True,
        }

        self.assertEqual(AUDITOR._editorial_issues(
            "evidencia",
            [record],
            approved={"aprovado-em-manifesto"},
        ), [])

    def test_versioned_approval_loader_maps_front_to_auditor_kind(self):
        with tempfile.TemporaryDirectory() as directory:
            approvals = Path(directory) / "editorial-approvals"
            approvals.mkdir()
            (approvals / "batch.json").write_text(json.dumps({
                "decision": "approved_for_publication",
                "fronts": {
                    "documentos": ["doc-aprovado"],
                    "evidencias": ["evidencia-aprovada"],
                },
            }), encoding="utf-8")

            loaded = AUDITOR._load_editorial_approvals(Path(directory))

        self.assertEqual(loaded["documento_markdown"], {"doc-aprovado"})
        self.assertEqual(loaded["evidencia"], {"evidencia-aprovada"})

    def test_editorial_gate_blocks_invalid_status_and_publication_flag(self):
        record = {
            "slug": "metadados-invalidos",
            "review_status": "quase_revisado",
            "published": "false",
        }

        self.assertEqual(
            [
                issue["reason"]
                for issue in AUDITOR._editorial_issues("evidencia", [record])
            ],
            ["invalid_review_status", "invalid_published_flag"],
        )
        self.assertEqual(AUDITOR._publication_flags([record]), {
            "true": 0,
            "false": 0,
            "missing": 0,
            "invalid": 1,
        })

    def test_frontmatter_reads_published_false_and_pending_status(self):
        with tempfile.TemporaryDirectory() as directory:
            document = Path(directory) / "documento.md"
            document.write_text(
                "---\n"
                "slug: documento-seguro\n"
                "review_status: pendente_revisao\n"
                "published: false\n"
                "---\n"
                "# Documento\n",
                encoding="utf-8",
            )

            metadata, body = AUDITOR._frontmatter(document)

        self.assertEqual(metadata["slug"], "documento-seguro")
        self.assertEqual(metadata["review_status"], "pendente_revisao")
        self.assertIs(metadata["published"], False)
        self.assertIn("# Documento", body)

    def test_frontmatter_preserves_invalid_published_value_for_gate(self):
        with tempfile.TemporaryDirectory() as directory:
            document = Path(directory) / "documento.md"
            document.write_text(
                "---\n"
                "slug: documento-invalido\n"
                "review_status: revisado\n"
                "published: talvez\n"
                "---\n"
                "# Documento\n",
                encoding="utf-8",
            )

            metadata, _body = AUDITOR._frontmatter(document)

        self.assertEqual(metadata["published"], "talvez")

    def test_gate_summary_counts_markdown_and_issue_reasons(self):
        result = {
            "broken_references": [
                {"field": "Document.body_md.link", "reason": "missing_target"},
                {"field": "EvidenceRecord.document_slug", "reason": "wrong_target_type"},
            ],
            "editorial_issues": [
                {"reason": "invalid_review_status"},
                {"reason": "reviewed_with_pending_review_note"},
            ],
        }

        self.assertEqual(AUDITOR._gate_summary(result), {
            "passed": False,
            "blocker_count": 4,
            "reference_blockers": 2,
            "editorial_blockers": 2,
            "broken_markdown_links": 1,
            "reference_reasons": {
                "missing_target": 1,
                "wrong_target_type": 1,
            },
            "editorial_reasons": {
                "invalid_review_status": 1,
                "reviewed_with_pending_review_note": 1,
            },
        })

    def test_strict_release_requires_every_item_reviewed_and_published(self):
        records = [
            {
                "slug": "pronto",
                "review_status": "revisado",
                "published": True,
            },
            {
                "slug": "pendente",
                "review_status": "pendente_revisao",
                "published": False,
            },
            {
                "slug": "revisado-nao-publicado",
                "review_status": "revisado",
                "published": False,
            },
            {
                "slug": "sem-flags",
            },
        ]

        issues = AUDITOR._strict_release_issues("evidencia", records)

        self.assertEqual([issue["identifier"] for issue in issues], [
            "pendente", "revisado-nao-publicado", "sem-flags",
        ])
        self.assertEqual(issues[0]["blockers"], ["not_reviewed", "not_published"])
        self.assertEqual(issues[1]["blockers"], ["not_published"])
        self.assertEqual(issues[2]["published"], "missing")

    def test_strict_release_manifest_checks_only_the_approved_batch(self):
        records_by_kind = {
            "evidencia": [
                {
                    "slug": "evidencia-pronta",
                    "review_status": "revisado",
                    "published": True,
                },
                {
                    "slug": "evidencia-retida",
                    "review_status": "revisado",
                    "published": False,
                },
                {
                    "slug": "evidencia-legada-fora-do-lote",
                    "review_status": "pendente_revisao",
                    "published": False,
                },
            ],
            "estudo": [{"slug": "estudo-legado-sem-flags"}],
        }
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / "release.json"
            manifest.write_text(json.dumps({
                "decision": "approved_for_publication",
                "fronts": {
                    "evidencias": ["evidencia-pronta", "evidencia-retida"],
                },
            }), encoding="utf-8")

            issues, metadata = AUDITOR._strict_release_manifest_issues(
                manifest, records_by_kind
            )

        self.assertEqual(metadata["decision"], "approved_for_publication")
        self.assertEqual(metadata["item_count"], 2)
        self.assertEqual(metadata["fronts"], {"evidencias": 2})
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]["identifier"], "evidencia-retida")
        self.assertEqual(issues[0]["front"], "evidencias")
        self.assertEqual(issues[0]["blockers"], ["not_published"])

    def test_strict_release_manifest_rejects_invalid_scope_or_approval(self):
        invalid_payloads = {
            "sem_decisao": {"fronts": {"evidencias": ["evidencia"]}},
            "frente_desconhecida": {
                "decision": "approved_for_publication",
                "fronts": {"cursos": ["evidencia"]},
            },
            "slug_duplicado": {
                "decision": "approved_for_publication",
                "fronts": {"evidencias": ["evidencia", "evidencia"]},
            },
            "lote_vazio": {
                "decision": "approved_for_publication",
                "fronts": {"evidencias": []},
            },
        }
        with tempfile.TemporaryDirectory() as directory:
            for name, payload in invalid_payloads.items():
                with self.subTest(name=name):
                    manifest = Path(directory) / f"{name}.json"
                    manifest.write_text(json.dumps(payload), encoding="utf-8")
                    with self.assertRaises(ValueError):
                        AUDITOR._strict_release_manifest_issues(manifest, {})

    def test_strict_release_manifest_rejects_missing_wrong_and_ambiguous_targets(self):
        records_by_kind = {
            "evidencia": [
                {
                    "slug": "evidencia-ambigua",
                    "review_status": "revisado",
                    "published": True,
                },
                {
                    "slug": "evidencia-ambigua",
                    "review_status": "revisado",
                    "published": True,
                },
            ],
            "estudo": [{
                "slug": "slug-no-tipo-errado",
                "review_status": "revisado",
                "published": True,
            }],
        }
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / "release.json"
            manifest.write_text(json.dumps({
                "decision": "approved_for_publication",
                "fronts": {
                    "evidencias": [
                        "evidencia-ausente",
                        "slug-no-tipo-errado",
                        "evidencia-ambigua",
                    ],
                },
            }), encoding="utf-8")

            issues, _metadata = AUDITOR._strict_release_manifest_issues(
                manifest, records_by_kind
            )

        self.assertEqual(
            {issue["identifier"]: issue["blockers"] for issue in issues},
            {
                "evidencia-ausente": ["missing_target"],
                "slug-no-tipo-errado": ["wrong_target_type"],
                "evidencia-ambigua": ["ambiguous_target"],
            },
        )

    def test_strict_release_cli_is_explicit_and_does_not_change_generic_mode(self):
        result = {
            "broken_references": [],
            "editorial_issues": [],
            "release_readiness_issues": [{
                "reason": "release_item_not_ready",
                "blockers": ["not_reviewed", "not_published"],
            }],
        }
        original = AUDITOR.audit
        AUDITOR.audit = lambda **_kwargs: dict(result)
        generic_output = io.StringIO()
        strict_output = io.StringIO()
        try:
            with redirect_stdout(generic_output):
                generic_exit = AUDITOR.main([])
            with redirect_stdout(strict_output):
                strict_exit = AUDITOR.main(["--strict-release"])
        finally:
            AUDITOR.audit = original

        generic_gate = json.loads(generic_output.getvalue())["gate"]
        strict_gate = json.loads(strict_output.getvalue())["gate"]
        self.assertEqual(generic_exit, 0)
        self.assertIs(generic_gate["passed"], True)
        self.assertNotIn("strict_release", generic_gate)
        self.assertEqual(strict_exit, 1)
        self.assertIs(strict_gate["passed"], False)
        self.assertIs(strict_gate["strict_release"], True)
        self.assertEqual(strict_gate["release_blockers"], 1)
        self.assertEqual(strict_gate["release_reasons"], {
            "not_published": 1,
            "not_reviewed": 1,
        })

    def test_strict_release_manifest_cli_is_explicit_and_reports_scope(self):
        result = {
            "broken_references": [],
            "editorial_issues": [],
            "release_readiness_issues": [],
            "release_manifest": {"item_count": 174},
        }
        calls = []
        original = AUDITOR.audit
        AUDITOR.audit = lambda **kwargs: calls.append(kwargs) or dict(result)
        output = io.StringIO()
        manifest = Path("release-evidences.json")
        try:
            with redirect_stdout(output):
                exit_code = AUDITOR.main([
                    "--strict-release-manifest", str(manifest),
                ])
        finally:
            AUDITOR.audit = original

        gate = json.loads(output.getvalue())["gate"]
        self.assertEqual(calls, [{"strict_release_manifest": manifest}])
        self.assertEqual(exit_code, 0)
        self.assertIs(gate["passed"], True)
        self.assertIs(gate["strict_release"], True)
        self.assertEqual(gate["strict_release_manifest"], str(manifest))
        self.assertEqual(gate["release_manifest_items"], 174)

    def test_main_returns_failure_for_blockers(self):
        result = {
            "broken_references": [
                {"field": "Document.body_md.link", "reason": "missing_target"},
            ],
            "editorial_issues": [],
        }
        result["gate"] = AUDITOR._gate_summary(result)
        original = AUDITOR.audit
        AUDITOR.audit = lambda: result
        output = io.StringIO()
        try:
            with redirect_stdout(output):
                exit_code = AUDITOR.main()
        finally:
            AUDITOR.audit = original

        self.assertEqual(exit_code, 1)
        self.assertIs(json.loads(output.getvalue())["gate"]["passed"], False)

    def test_main_fails_closed_when_audit_crashes(self):
        def fail():
            raise ValueError("manifesto inválido")

        original = AUDITOR.audit
        AUDITOR.audit = fail
        output = io.StringIO()
        try:
            with redirect_stdout(output):
                exit_code = AUDITOR.main()
        finally:
            AUDITOR.audit = original

        payload = json.loads(output.getvalue())
        self.assertEqual(exit_code, 2)
        self.assertIs(payload["gate"]["passed"], False)
        self.assertEqual(payload["error"]["type"], "ValueError")


if __name__ == "__main__":
    unittest.main()
