"""Garante status editorial explícito sem confundir corpus canônico com publicação.

O repositório pode preservar verbetes em `pendente_revisao` para revisão
editorial posterior. A fronteira de segurança de publicação fica na
reconciliação: apenas `review_status=revisado` é publicado e qualquer registro
que deixe de estar revisado é despublicado.

A release schema2 define a partição exata vigente. A quantidade de pendências
pode mudar em uma nova aprovação; a barreira de quarentena não pode mudar.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
import pytest

from app.services.disease_manifest import load_disease_records
from app.services.carregar_triagem_sintomas import load_triage_records


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
MANIFESTS = (
    "galeria/metadados.json", "exames/metadados.json", "evidencias/metadados.json",
    "estudos/metadados.json", "medicamentos/metadados.json", "checklists/metadados.json",
    "trilhas/metadados.json", "material-paciente/metadados.json", "emergencia/metadados.json",
    "casos-clinicos/metadados.json", "doencas/metadados.json", "triagem-sintomas/metadados.json",
)
PENDENTES_MEDICAMENTOS_RC: set[str] = set()
PENDENTES_LOTES_TUDO_COM_TUDO: dict[str, set[str]] = {}
PENDENTES_MARKDOWN_AVC: set[str] = set()
EDITORIAL_APPROVALS_DIR = REPOSITORY_ROOT / "editorial-approvals"


def _approved_by_front() -> dict[str, set[str]]:
    approvals: dict[str, set[str]] = {}
    if not EDITORIAL_APPROVALS_DIR.exists():
        return approvals
    for path in sorted(EDITORIAL_APPROVALS_DIR.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("decision") != "approved_for_publication":
            continue
        for front, slugs in (payload.get("fronts") or {}).items():
            approvals.setdefault(front, set()).update(slugs)
    return approvals


PATH_TO_FRONT = {
    "evidencias/metadados.json": "evidencias",
    "estudos/metadados.json": "estudos",
    "checklists/metadados.json": "checklists",
    "trilhas/metadados.json": "trilhas",
    "material-paciente/metadados.json": "material_paciente",
    "emergencia/metadados.json": "emergencia",
    "casos-clinicos/metadados.json": "casos_clinicos",
    "doencas/metadados.json": "doencas_especializadas",
    "triagem-sintomas/metadados.json": "triagem_sintomas",
}


def _records(relative_path: str) -> list[dict]:
    path = REPOSITORY_ROOT / relative_path
    if relative_path == "doencas/metadados.json":
        return load_disease_records(path)
    if relative_path == "triagem-sintomas/metadados.json":
        return load_triage_records(path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(payload, list)
    return payload


def test_manifestos_canonicos_so_tem_pendencias_explicitamente_aprovadas_para_rc():
    invalidos: list[str] = []
    pendentes_encontrados: set[str] = set()
    approved = _approved_by_front()
    for relative_path in MANIFESTS:
        for record in _records(relative_path):
            status = record.get("review_status")
            identifier = record.get("slug") or record.get("title") or record.get("titulo")
            if status == "revisado":
                continue
            front = PATH_TO_FRONT.get(relative_path)
            if front and identifier in approved.get(front, set()):
                continue
            invalidos.append(f"{relative_path}:{identifier}:{status}")
    assert invalidos == []
    pendentes_esperados = set(PENDENTES_MEDICAMENTOS_RC)
    pendentes_esperados.update(f"{path}:{slug}" for path, slugs in PENDENTES_LOTES_TUDO_COM_TUDO.items() for slug in slugs)
    assert pendentes_encontrados == pendentes_esperados


def test_manifesto_nao_marca_como_publicado_um_registro_pendente():
    conflitos: list[str] = []
    for relative_path in MANIFESTS:
        for record in _records(relative_path):
            if record.get("review_status") != "revisado" and record.get("published") is True:
                identifier = record.get("slug") or record.get("title") or record.get("titulo")
                conflitos.append(f"{relative_path}:{identifier}")
    assert conflitos == []


def _assert_document_partition(records, approved, quarantine):
    seen, pending = set(), set()
    assert not approved & quarantine
    for path, metadata in records:
        slug, status = metadata["slug"], metadata.get("review_status")
        assert slug not in seen, slug
        seen.add(slug)
        assert status in {"revisado", "pendente_revisao"}, str(path)
        if slug in approved:
            assert status == "revisado", slug
        if status != "revisado":
            pending.add(slug)
            assert slug in quarantine and slug not in approved, slug
            assert metadata.get("published") is not True, slug
    assert seen == approved | quarantine
    return pending


def test_documentos_publicaveis_revisados_e_pendencias_em_quarentena_explicita():
    import frontmatter
    release = json.loads((EDITORIAL_APPROVALS_DIR / "scoped-corpus-release-20260910.json").read_text())
    assert release["schema_version"] == 2
    records = [(path, frontmatter.load(path).metadata)
               for path in sorted((REPOSITORY_ROOT / "content").rglob("*.md"))]
    _assert_document_partition(records, set(release["approved"]["documentos"]),
                               set(release["quarantined"]["documentos"]))


def test_partition_retains_pending_and_reviewed_quarantine_without_publication():
    records = [
        ("approved.md", {"slug": "approved", "review_status": "revisado"}),
        ("pending.md", {"slug": "pending", "review_status": "pendente_revisao", "published": False}),
        ("duplicate.md", {"slug": "duplicate", "review_status": "revisado", "published": False}),
    ]
    assert _assert_document_partition(records, {"approved"}, {"pending", "duplicate"}) == {"pending"}
    assert records[1][1]["review_status"] == "pendente_revisao"
    assert records[1][1]["published"] is False


@pytest.mark.parametrize("approved,quarantine,published", [
    ({"pending"}, set(), False), (set(), set(), False),
    (set(), {"pending"}, True), ({"pending"}, {"pending"}, False),
])
def test_partition_rejects_pending_approval_missing_scope_or_publication(approved, quarantine, published):
    with pytest.raises(AssertionError):
        _assert_document_partition([("pending.md", {"slug": "pending", "review_status": "pendente_revisao",
                                                   "published": published})], approved, quarantine)
