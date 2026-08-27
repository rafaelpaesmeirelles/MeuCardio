"""Garante status editorial explícito sem confundir corpus canônico com publicação.

O repositório pode preservar verbetes em `pendente_revisao` para revisão
editorial posterior. A fronteira de segurança de publicação fica na
reconciliação: apenas `review_status=revisado` é publicado e qualquer registro
que deixe de estar revisado é despublicado.

A exceção estreita usada durante a RC de lançamento (dez medicamentos
conhecidos, aprovados nominalmente) foi fechada em 12/08/2026, depois da
validação científica completa dos dez contra fonte primária (bula/rótulo/
PubMed) — ver `review_note` de cada um em `medicamentos/metadados.json`. A
allowlist `PENDENTES_MEDICAMENTOS_RC` continua vazia de propósito. As
allowlists `PENDENTES_LOTE_*` abaixo são fechadas nos slugs de lotes
auditáveis específicos (produção assistida, `fonte_producao` explícito,
`review_note` com pendência de revisão humana declarada) — permitem que o PR
preserve a decisão humana sem publicar conteúdo novo; qualquer outro pendente
continua quebrando o gate.
"""

from __future__ import annotations

import json
from pathlib import Path
import re


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
MANIFESTS = (
    "galeria/metadados.json",
    "exames/metadados.json",
    "evidencias/metadados.json",
    "estudos/metadados.json",
    "medicamentos/metadados.json",
    "checklists/metadados.json",
    "trilhas/metadados.json",
    "material-paciente/metadados.json",
    "emergencia/metadados.json",
    "casos-clinicos/metadados.json",
    "doencas/metadados.json",
    "triagem-sintomas/metadados.json",
)
PENDENTES_MEDICAMENTOS_RC: set[str] = set()
PENDENTES_LOTE_ISQUEMIA_MESENTERICA_AGUDA: dict[str, set[str]] = {
    "evidencias/metadados.json": {
        "ima-dor-abdominal-desproporcional-assumir-ima-ate-provar-o-contrario-wses-2022",
        "ima-angiotomografia-urgente-independente-da-funcao-renal-esvs-2025",
        "ima-revascularizacao-endovascular-primeira-linha-oclusao-arterial-esvs-2025",
    },
    "checklists/metadados.json": {"primeira-hora-na-suspeita-de-isquemia-mesenterica-aguda"},
    "trilhas/metadados.json": {
        "trilha-suspeita-de-isquemia-mesenterica-aguda-do-reconhecimento-a-decisao-de-revascularizacao"
    },
    "material-paciente/metadados.json": {
        "dor-abdominal-subita-e-intensa-quando-procurar-a-emergencia"
    },
    "doencas/metadados.json": {"isquemia-mesenterica-aguda-cardioembolica"},
    "triagem-sintomas/metadados.json": {"dor-abdominal-aguda-desproporcional-ao-exame"},
}
PENDENTES_MARKDOWN_ISQUEMIA_MESENTERICA_AGUDA = {
    "content/Aorta_e_doença_arterial_periférica/isquemia-mesenterica-aguda-origem-cardioembolica-reconhecimento-e-primeira-hora.md",
    "content/Aorta_e_doença_arterial_periférica/fluxograma-suspeita-de-isquemia-mesenterica-aguda-primeira-hora.md",
}


def test_manifestos_canonicos_so_tem_pendencias_explicitamente_aprovadas_para_rc():
    invalidos: list[str] = []
    pendentes_encontrados: set[str] = set()
    for relative_path in MANIFESTS:
        records = json.loads((REPOSITORY_ROOT / relative_path).read_text(encoding="utf-8"))
        for record in records:
            status = record.get("review_status")
            identifier = record.get("slug") or record.get("title") or record.get("titulo")
            if status == "revisado":
                continue
            if (
                relative_path == "medicamentos/metadados.json"
                and status == "pendente_revisao"
                and identifier in PENDENTES_MEDICAMENTOS_RC
            ):
                pendentes_encontrados.add(str(identifier))
                continue
            if (
                status == "pendente_revisao"
                and identifier in PENDENTES_LOTE_ISQUEMIA_MESENTERICA_AGUDA.get(relative_path, set())
            ):
                pendentes_encontrados.add(f"{relative_path}:{identifier}")
                continue
            invalidos.append(f"{relative_path}:{identifier}:{status}")

    assert invalidos == []
    pendentes_esperados = set(PENDENTES_MEDICAMENTOS_RC)
    pendentes_esperados.update(
        f"{path}:{slug}"
        for path, slugs in PENDENTES_LOTE_ISQUEMIA_MESENTERICA_AGUDA.items()
        for slug in slugs
    )
    assert pendentes_encontrados == pendentes_esperados


def test_manifesto_nao_marca_como_publicado_um_registro_pendente():
    conflitos: list[str] = []
    for relative_path in MANIFESTS:
        records = json.loads((REPOSITORY_ROOT / relative_path).read_text(encoding="utf-8"))
        for record in records:
            if record.get("review_status") != "revisado" and record.get("published") is True:
                identifier = record.get("slug") or record.get("title") or record.get("titulo")
                conflitos.append(f"{relative_path}:{identifier}")

    assert conflitos == []


def test_todos_os_documentos_markdown_estao_revisados():
    pendentes: list[str] = []
    pendentes_permitidos: set[str] = set()
    sem_status: list[str] = []
    for path in sorted((REPOSITORY_ROOT / "content").rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        frontmatter = text.split("---", 2)[1] if text.startswith("---") else ""
        match = re.search(r"^review_status:\s*['\"]?([^'\"\n]+)", frontmatter, re.MULTILINE)
        relative_path = str(path.relative_to(REPOSITORY_ROOT))
        if match is None:
            sem_status.append(relative_path)
        elif match.group(1).strip() != "revisado":
            if (
                match.group(1).strip() == "pendente_revisao"
                and relative_path in PENDENTES_MARKDOWN_ISQUEMIA_MESENTERICA_AGUDA
            ):
                pendentes_permitidos.add(relative_path)
            else:
                pendentes.append(f"{relative_path}:{match.group(1).strip()}")

    assert sem_status == []
    assert pendentes == []
    assert pendentes_permitidos == PENDENTES_MARKDOWN_ISQUEMIA_MESENTERICA_AGUDA
