"""Contrato do lote de FECHAMENTO DE LACUNA Tudo com Tudo de 28/08/2026 —
ficha já existente miocardite-pediatrica (área cardiopediatria) em
doencas/metadados.json.

Trigésimo lote de conteúdo do dia, quarto desta natureza (após
doenca-de-kawasaki PR #642, estenose-aortica-tavi-idoso PR #643 e
trombose-associada-cancer PR #644): não é aprofundamento de conteúdo
clínico. A ficha já estava completeness=completo, com todo o conteúdo
clínico integral e review_status=revisado — mas related_document_slugs e
patient_material_slug estavam None.

O lote não altera nenhum campo de conteúdo clínico pré-existente — apenas
adiciona os 4 related_document_slugs e o patient_material_slug, ambos
verificados por leitura real dos documentos candidatos e do
material-paciente/metadados.json.

Nota sobre colisão: uma suspeita inicial de colisão com a PR #568
("novo verbete-hub de Miocardite geral") foi descartada via
`gh pr diff 568 | grep '"slug": "miocardite-pediatrica"'`, que retornou
0 ocorrências do slug exato.

Este arquivo também espelha, em test_disease_fragments_canonical.py, a
mesma correção de allowlist já aprovada pelo Rafael no PR #606, pois esta
branch parte de origin/main antes dessa correção.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DOENCAS_PATH = REPOSITORY_ROOT / "doencas/metadados.json"
SLUG = "miocardite-pediatrica"

PASTAS_NAO_DOCUMENTO = ("Farmacologia", "Calculadoras", "Exames")

TERMOS_TEMA = ("miocardite",)

DOCUMENTOS_COMPARTILHADOS_COM_OUTRAS_FICHAS: set[str] = {
    "miocardite-fulminante-pediatrica-e-choque-cardiogenico",
    "miocardite-pos-vacina-de-mrna-em-adolescentes-incidencia-comparacao-com-covid-19-e-vigilancia-atual",
    "miocardite-aguda-pediatrica-diagnostico-suporte-hemodinamico-e-ecmo",
}


def _load_doencas() -> dict[str, dict]:
    items = json.loads(DOENCAS_PATH.read_text(encoding="utf-8"))
    return {item["slug"]: item for item in items}


def _all_document_paths() -> dict[str, Path]:
    result: dict[str, Path] = {}
    for path in (REPOSITORY_ROOT / "content").rglob("*.md"):
        text = path.read_text(encoding="utf-8", errors="replace")
        slug = None
        if text.startswith("---"):
            frontmatter = text.split("---", 2)[1]
            match = re.search(r'^slug:\s*["\']?([^"\'\n]+)', frontmatter, re.MULTILINE)
            if match:
                slug = match.group(1).strip()
        result[slug or path.stem] = path
    return result


def test_ficha_continua_existindo_com_mesmo_slug():
    doencas = _load_doencas()
    assert SLUG in doencas


def test_marcacao_editorial_correta():
    item = _load_doencas()[SLUG]
    assert item.get("fonte_producao") == "claude"
    assert item.get("review_status") == "pendente_revisao"
    assert item.get("completeness") == "completo"
    assert item.get("area") == "cardiopediatria"
    assert item.get("review_note")
    assert item.get("version") == 2, "fechamento de lacuna deveria incrementar version de 1 para 2"


def test_catalogacao_e_conteudo_clinico_preexistente_preservados():
    item = _load_doencas()[SLUG]
    assert item.get("name") == "Miocardite pediátrica"
    assert "miocardite na criança" in (item.get("aliases") or [])
    assert item.get("category") == "doenca_miocardica"
    assert item.get("prevalence_rank") == 3
    # conteúdo clínico não deve ter sido tocado por este lote
    assert item.get("treatment_summary"), "treatment_summary pré-existente não deveria ter sido removido"
    assert len(item.get("assistant_rules") or []) >= 4, "assistant_rules pré-existentes não deveriam ter sido removidas"


def test_vinculos_tudo_com_tudo_resolvem_e_sao_documentos_narrativos():
    item = _load_doencas()[SLUG]
    documentos = _all_document_paths()

    related = item.get("related_document_slugs") or []
    assert 3 <= len(related) <= 7, "regra Tudo com Tudo pede entre 3 e 7 links"

    nao_resolvidos = [slug for slug in related if slug not in documentos]
    assert nao_resolvidos == [], f"related_document_slugs aponta para documento inexistente: {nao_resolvidos}"

    fora_de_escopo = [
        slug for slug in related
        if any(pasta in str(documentos[slug]) for pasta in PASTAS_NAO_DOCUMENTO)
    ]
    assert fora_de_escopo == [], f"related_document_slugs aponta para fora do escopo permitido: {fora_de_escopo}"

    assert len(related) == len(set(related)), "related_document_slugs contém duplicatas"


def test_related_document_slugs_mencionam_miocardite():
    item = _load_doencas()[SLUG]
    documentos = _all_document_paths()
    for slug in item.get("related_document_slugs") or []:
        texto = documentos[slug].read_text(encoding="utf-8", errors="replace").casefold()
        assert any(termo in texto for termo in TERMOS_TEMA), (
            f"{slug}: documento vinculado não menciona miocardite no texto"
        )


def test_documentos_compartilhados_sao_os_esperados_e_documentados():
    item = _load_doencas()[SLUG]
    doencas = _load_doencas()
    related = set(item.get("related_document_slugs") or [])

    compartilhados_encontrados = set()
    for outro_slug, outro_item in doencas.items():
        if outro_slug == SLUG:
            continue
        outros_related = set(outro_item.get("related_document_slugs") or [])
        compartilhados_encontrados |= (related & outros_related)

    inesperados = compartilhados_encontrados - DOCUMENTOS_COMPARTILHADOS_COM_OUTRAS_FICHAS
    assert inesperados == set(), (
        f"sobreposição não documentada com outra ficha: {inesperados}"
    )


def test_patient_material_slug_resolve():
    item = _load_doencas()[SLUG]
    material = item.get("patient_material_slug")
    assert material == "miocardite-inflamacao-do-musculo-do-coracao-e-recuperacao"
    materiais = {
        x["slug"]
        for x in json.loads((REPOSITORY_ROOT / "material-paciente/metadados.json").read_text(encoding="utf-8"))
    }
    assert material in materiais, f"patient_material_slug aponta para material inexistente: {material}"
