"""Garante status editorial explícito sem confundir corpus canônico com publicação.

O repositório pode preservar verbetes em `pendente_revisao` para revisão
editorial posterior. A fronteira de segurança de publicação fica na
reconciliação: apenas `review_status=revisado` é publicado e qualquer registro
que deixe de estar revisado é despublicado.

Os lotes Tudo com Tudo pendentes anteriores foram revisados. Qualquer novo
status diferente de revisado quebra o gate e exige decisão editorial explícita.
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
        # Lote vincular Tudo com Tudo de 29/08/2026: ficha já completa
        # persistencia-canal-arterial tinha apenas 1 related_document_slug
        # (abaixo do piso); 5 vínculos adicionados após verificação.
        # Mantido pendente_revisao (não autoaprovado) — gate canônico deste
        # arquivo falhará intencionalmente até revisão humana, consistente
        # com a política vigente desde 28/08/2026.
        "persistencia-canal-arterial",
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


def test_todos_os_documentos_markdown_estao_revisados():
    pendentes: list[str] = []; pendentes_permitidos: set[str] = set(); sem_status: list[str] = []
    approved_docs = _approved_by_front().get("documentos", set())
    for path in sorted((REPOSITORY_ROOT / "content").rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        frontmatter = text.split("---", 2)[1] if text.startswith("---") else ""
        match = re.search(r"^review_status:\s*['\"]?([^'\"\n]+)", frontmatter, re.MULTILINE)
        relative_path = str(path.relative_to(REPOSITORY_ROOT))
        if match is None: sem_status.append(relative_path)
        elif match.group(1).strip() != "revisado":
            slug_match = re.search(r'^slug:\s*[\'\"]?([^\'\"\n]+)', frontmatter, re.MULTILINE)
            slug = slug_match.group(1).strip() if slug_match else ""
            if slug in approved_docs:
                continue
            pendentes.append(f"{relative_path}:{match.group(1).strip()}")
    assert sem_status == []
    assert pendentes == []
    assert pendentes_permitidos == PENDENTES_MARKDOWN_AVC
