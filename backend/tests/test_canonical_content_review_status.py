"""Garante status editorial explícito sem confundir corpus canônico com publicação.

O repositório pode preservar verbetes em `pendente_revisao` para revisão
editorial posterior. A fronteira de segurança de publicação fica na
reconciliação: apenas `review_status=revisado` é publicado e qualquer registro
que deixe de estar revisado é despublicado.

A exceção estreita usada durante a RC de lançamento (dez medicamentos
conhecidos, aprovados nominalmente) foi fechada em 12/08/2026, depois da
validação científica completa dos dez contra fonte primária (bula/rótulo/
PubMed) — ver `review_note` de cada um em `medicamentos/metadados.json`. Os lotes
Tudo com Tudo pendentes foram revisados em 28/08/2026. As allowlists ficam
vazias: qualquer novo status diferente de `revisado` quebra o gate e exige
decisão editorial explícita.
"""

from __future__ import annotations

import json
from pathlib import Path
import re

from app.services.disease_manifest import load_disease_records


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
        # Lote de aprofundamento Tudo com Tudo de 29/08/2026: ficha
        # planejamento-parto-cardiopatia-fetal passou de completeness=
        # basico (só catalogação) para completo. Mantida pendente_revisao
        # (não autoaprovada) — gate canônico deste arquivo falhará
        # intencionalmente até revisão humana, política vigente desde
        # 28/08/2026.
        "planejamento-parto-cardiopatia-fetal",
    },
}
PENDENTES_MARKDOWN_AVC: set[str] = set()


def _records(relative_path: str) -> list[dict]:
    path = REPOSITORY_ROOT / relative_path
    if relative_path == "doencas/metadados.json":
        return load_disease_records(path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(payload, list)
    return payload


def test_manifestos_canonicos_so_tem_pendencias_explicitamente_aprovadas_para_rc():
    invalidos: list[str] = []
    pendentes_encontrados: set[str] = set()
    for relative_path in MANIFESTS:
        for record in _records(relative_path):
            status = record.get("review_status")
            identifier = record.get("slug") or record.get("title") or record.get("titulo")
            if status == "revisado":
                continue
            if relative_path == "medicamentos/metadados.json" and status == "revisado" and identifier in PENDENTES_MEDICAMENTOS_RC:
                pendentes_encontrados.add(str(identifier)); continue
            if status == "revisado" and identifier in PENDENTES_LOTES_TUDO_COM_TUDO.get(relative_path, set()):
                pendentes_encontrados.add(f"{relative_path}:{identifier}"); continue
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
    for path in sorted((REPOSITORY_ROOT / "content").rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        frontmatter = text.split("---", 2)[1] if text.startswith("---") else ""
        match = re.search(r"^review_status:\s*['\"]?([^'\"\n]+)", frontmatter, re.MULTILINE)
        relative_path = str(path.relative_to(REPOSITORY_ROOT))
        if match is None: sem_status.append(relative_path)
        elif match.group(1).strip() != "revisado":
            if match.group(1).strip() == "revisado" and relative_path in PENDENTES_MARKDOWN_AVC:
                pendentes_permitidos.add(relative_path)
            else: pendentes.append(f"{relative_path}:{match.group(1).strip()}")
    assert sem_status == []
    assert pendentes == []
    assert pendentes_permitidos == PENDENTES_MARKDOWN_AVC
