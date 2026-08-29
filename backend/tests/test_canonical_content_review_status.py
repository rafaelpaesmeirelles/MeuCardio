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
# Lote "science overnight" de 29/08/2026 (branch claude/science-overnight-20260829,
# sem merge): 11 verbetes novos em doencas/fragmentos/ produzidos por pesquisa
# científica autônoma, com review_status=pendente_revisao por instrução explícita
# do Rafael (nunca promover automaticamente a revisado). Rastreados aqui apenas
# para test_disease_fragments_canonical.py (PENDENTES_DOENCAS) — não afeta e não
# tenta contornar o gate principal desta suíte, que continua corretamente
# quebrando para qualquer status != revisado até revisão editorial humana.
PENDENTES_LOTES_TUDO_COM_TUDO: dict[str, set[str]] = {
    "doencas/metadados.json": {
        "flutter-atrial-adulto",
        "wolff-parkinson-white",
        "bloqueio-de-ramo",
        "hematoma-intramural-aortico-e-ulcera-penetrante",
        "doenca-renovascular-e-displasia-fibromuscular",
        "aortopatias-geneticas-do-adulto",
        "coracao-de-atleta-versus-cardiomiopatia-hipertrofica",
        "avaliacao-pre-participacao-esportiva",
        "avaliacao-cardiovascular-perioperatoria",
        "insuficiencia-cardiaca-pediatrica",
        "transplante-cardiaco-pediatrico",
        "aconselhamento-genetico-cardiovascular",
        "morte-subita-cardiaca-no-esporte-causas-e-prevencao",
        "pericardite-pediatrica",
        "obesidade-pediatrica-e-coracao",
    },
}
PENDENTES_MARKDOWN_AVC: set[str] = set()


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
