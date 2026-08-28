"""Contrato do fechamento de lacunas Tudo com Tudo de 28/08/2026.

O lote inicial encontrou 8 checklists sem documento_origem. Cinco foram
vinculados a documentos centrais já existentes. Os três restantes (STOP-Bang
pré-operatório, abstinência alcoólica aguda e síndrome de Paget-Schroetter)
receberam documentos narrativos dedicados no PR #651 e, desde então, também
devem possuir vínculo explícito e resolvível.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
CHECKLISTS_PATH = REPOSITORY_ROOT / "checklists/metadados.json"

PASTAS_NAO_DOCUMENTO = ("Farmacologia", "Calculadoras", "Exames")

VINCULOS_ESPERADOS = {
    "avaliacao-cardiovascular-do-usuario-recreativo-de-esteroides-anabolizantes-androgenicos": "esteroides-anabolizantes-androgenicos-e-risco-cardiovascular",
    "manejo-agudo-de-fibrilacao-atrial-induzida-por-alcool-holiday-heart-syndrome": "sindrome-do-coracao-em-ferias-e-fibrilacao-atrial-induzida-por-alcool",
    "controle-da-hipertensao-sistolica-isolada-no-muito-idoso-com-vigilancia-de-hipotensao-ortostatica-iatrogenica": "hipertensao-sistolica-isolada-e-meta-pressorica-no-muito-idoso-hyvet-sprint-e-step",
    "decisao-entre-valvuloplastia-por-balao-percutanea-e-cirurgia-na-estenose-mitral-reumatica-cronica-grave": "estenose-mitral-diagnostico-e-manejo-esc-eacts-2025",
    "envolvimento-cardiaco-na-sindrome-inflamatoria-multissistemica-pediatrica-mis-c-avaliacao-e-seguimento": "mis-c-com-disfuncao-miocardica-e-choque",
    "aplicacao-do-stop-bang-na-triagem-de-apneia-obstrutiva-do-sono-pre-operatoria-em-cirurgia-cardiaca": "aplicacao-do-stop-bang-na-triagem-de-apneia-obstrutiva-do-sono-pre-operatoria-em-cirurgia-cardiaca",
    "manejo-da-abstinencia-alcoolica-aguda-com-risco-de-tempestade-autonomica-e-arritmia": "manejo-da-abstinencia-alcoolica-aguda-com-risco-de-tempestade-autonomica-e-arritmia",
    "diagnostico-e-tratamento-da-trombose-de-esforco-sindrome-de-paget-schroetter": "diagnostico-e-tratamento-da-trombose-de-esforco-sindrome-de-paget-schroetter",
}


def _load_checklists() -> dict[str, dict]:
    items = json.loads(CHECKLISTS_PATH.read_text(encoding="utf-8"))
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


def test_checklists_existem_com_mesmo_slug():
    checklists = _load_checklists()
    for slug in VINCULOS_ESPERADOS:
        assert slug in checklists, f"checklist {slug} não encontrado"


def test_documento_origem_atribuido_corretamente():
    checklists = _load_checklists()
    for checklist_slug, doc_esperado in VINCULOS_ESPERADOS.items():
        assert checklists[checklist_slug].get("documento_origem") == doc_esperado


def test_documento_origem_resolve_e_esta_no_escopo_permitido():
    checklists = _load_checklists()
    documentos = _all_document_paths()
    for checklist_slug, doc_esperado in VINCULOS_ESPERADOS.items():
        assert doc_esperado in documentos, f"{doc_esperado} não resolve no corpus"
        path = documentos[doc_esperado]
        assert not any(pasta in str(path) for pasta in PASTAS_NAO_DOCUMENTO), (
            f"{doc_esperado} está fora do escopo permitido: {path}"
        )


def test_documento_origem_menciona_tema_central_do_checklist():
    checklists = _load_checklists()
    documentos = _all_document_paths()
    termos_por_checklist = {
        "avaliacao-cardiovascular-do-usuario-recreativo-de-esteroides-anabolizantes-androgenicos": ("esteroide", "anabolizante"),
        "manejo-agudo-de-fibrilacao-atrial-induzida-por-alcool-holiday-heart-syndrome": ("holiday heart", "álcool"),
        "controle-da-hipertensao-sistolica-isolada-no-muito-idoso-com-vigilancia-de-hipotensao-ortostatica-iatrogenica": ("hipertensão sistólica isolada",),
        "decisao-entre-valvuloplastia-por-balao-percutanea-e-cirurgia-na-estenose-mitral-reumatica-cronica-grave": ("estenose mitral",),
        "envolvimento-cardiaco-na-sindrome-inflamatoria-multissistemica-pediatrica-mis-c-avaliacao-e-seguimento": ("mis-c",),
        "aplicacao-do-stop-bang-na-triagem-de-apneia-obstrutiva-do-sono-pre-operatoria-em-cirurgia-cardiaca": ("stop-bang", "apneia obstrutiva"),
        "manejo-da-abstinencia-alcoolica-aguda-com-risco-de-tempestade-autonomica-e-arritmia": ("abstinência alcoólica", "tempestade autonômica"),
        "diagnostico-e-tratamento-da-trombose-de-esforco-sindrome-de-paget-schroetter": ("paget-schroetter", "trombose de esforço"),
    }
    for checklist_slug, termos in termos_por_checklist.items():
        doc_slug = checklists[checklist_slug]["documento_origem"]
        texto = documentos[doc_slug].read_text(encoding="utf-8", errors="replace").casefold()
        assert any(termo in texto for termo in termos), (
            f"{doc_slug}: documento vinculado a {checklist_slug} não menciona termos centrais {termos}"
        )


def test_todos_os_oito_checklists_tem_documento_origem_real():
    """Os três antigos deferidos foram fechados pelo PR #651; nenhum dos oito
    checklists auditados deve voltar a ficar órfão ou apontar para slug inexistente."""
    checklists = _load_checklists()
    documentos = _all_document_paths()
    for checklist_slug, doc_slug in VINCULOS_ESPERADOS.items():
        assert checklists[checklist_slug].get("documento_origem") == doc_slug
        assert doc_slug in documentos
