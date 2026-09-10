"""Garante status editorial explícito sem confundir corpus canônico com publicação.

O repositório pode preservar verbetes em `pendente_revisao` para revisão
editorial posterior. A fronteira de segurança de publicação fica na
reconciliação: apenas `review_status=revisado` é publicado e qualquer registro
que deixe de estar revisado é despublicado.

A release schema2 preserva explicitamente nove documentos pendentes dentro de
56 identidades em quarentena; somente a partição autorizada pode ser publicada.
"""

from __future__ import annotations

import json
from pathlib import Path
import re

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
PENDENTES_LOTES_TUDO_COM_TUDO: dict[str, set[str]] = {
    "doencas/metadados.json": {
        # Verbete novo criado em 29/08/2026 via doencas/fragmentos/
        # cardiomiopatia-de-takotsubo.json — ver review_note do próprio
        # registro. Esta entrada é usada por
        # test_disease_fragments_canonical.py (onde a checagem funciona
        # corretamente contra status pendente). Ela NÃO isenta este slug do
        # teste principal abaixo, cuja lógica só consulta esta allowlist
        # para registros já com status="revisado" — por isso
        # test_manifestos_canonicos_so_tem_pendencias_explicitamente_aprovadas_para_rc
        # continua falhando para "cardiomiopatia-de-takotsubo", como
        # esperado e documentado.
        "cardiomiopatia-de-takotsubo",
    },
}
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


def test_documentos_publicaveis_revisados_e_pendencias_em_quarentena_explicita():
    import frontmatter
    release = json.loads((EDITORIAL_APPROVALS_DIR / "scoped-corpus-release-20260910.json").read_text())
    assert release["schema_version"] == 2
    approved = set(release["approved"]["documentos"])
    quarantine = set(release["quarantined"]["documentos"])
    seen, pending = set(), set()
    assert not approved & quarantine
    for path in sorted((REPOSITORY_ROOT / "content").rglob("*.md")):
        post = frontmatter.load(path)
        slug, status = post.metadata["slug"], post.metadata.get("review_status")
        seen.add(slug)
        assert status in {"revisado", "pendente_revisao"}, str(path)
        if slug in approved:
            assert status == "revisado", slug
        if status != "revisado":
            pending.add(slug)
            assert slug in quarantine and slug not in approved, slug
            assert post.metadata.get("published") is not True, slug
    assert seen == approved | quarantine
    # Seven uncovered pending sources plus two duplicate originals must remain
    # visibly pending; the release must never change their status to pass CI.
    assert len(pending) == 9
    assert len(quarantine) == 56
