"""Contrato do lote de fechamento de lacuna Tudo com Tudo de 28/08/2026 —
5 checklists de checklists/metadados.json com documento_origem vazio,
agora vinculados a documentos narrativos reais e centrais já publicados
em content/**/*.md.

Descoberto ao auditar todo checklists/metadados.json em busca de
documento_origem vazio (8 registros encontrados). Para 5 deles, foi
confirmado por leitura real do documento candidato que ele trata
centralmente do mesmo tema clínico do checklist (mesmas referências
primárias, mesmo escopo). Para os outros 3 (STOP-Bang pré-operatório,
abstinência alcoólica aguda, síndrome de Paget-Schroetter), nenhum
documento genuinamente central foi encontrado no corpus — permanecem
com documento_origem vazio, sem fabricar vínculo fraco. Duas PRs
anteriores fechadas (#460, #465) já haviam tentado vincular esses 3
(e outros) a arquivos que nunca chegaram a existir em nenhuma branch —
referências quebradas, provável motivo do fechamento dessas PRs.
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
}

# Estes 3 permanecem sem documento_origem deliberadamente — corpus não
# tem documento central sobre o tema (verificado por busca ampla e
# leitura), não é uma omissão a corrigir neste lote.
DEFERIDOS_SEM_DOCUMENTO_ORIGEM = {
    "aplicacao-do-stop-bang-na-triagem-de-apneia-obstrutiva-do-sono-pre-operatoria-em-cirurgia-cardiaca",
    "manejo-da-abstinencia-alcoolica-aguda-com-risco-de-tempestade-autonomica-e-arritmia",
    "diagnostico-e-tratamento-da-trombose-de-esforco-sindrome-de-paget-schroetter",
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
    # termos mínimos por checklist, extraídos do próprio slug/tema
    termos_por_checklist = {
        "avaliacao-cardiovascular-do-usuario-recreativo-de-esteroides-anabolizantes-androgenicos": ("esteroide", "anabolizante"),
        "manejo-agudo-de-fibrilacao-atrial-induzida-por-alcool-holiday-heart-syndrome": ("holiday heart", "álcool"),
        "controle-da-hipertensao-sistolica-isolada-no-muito-idoso-com-vigilancia-de-hipotensao-ortostatica-iatrogenica": ("hipertensão sistólica isolada",),
        "decisao-entre-valvuloplastia-por-balao-percutanea-e-cirurgia-na-estenose-mitral-reumatica-cronica-grave": ("estenose mitral",),
        "envolvimento-cardiaco-na-sindrome-inflamatoria-multissistemica-pediatrica-mis-c-avaliacao-e-seguimento": ("mis-c",),
    }
    for checklist_slug, termos in termos_por_checklist.items():
        doc_slug = checklists[checklist_slug]["documento_origem"]
        texto = documentos[doc_slug].read_text(encoding="utf-8", errors="replace").casefold()
        assert any(termo in texto for termo in termos), (
            f"{doc_slug}: documento vinculado a {checklist_slug} não menciona termos centrais {termos}"
        )


def test_checklists_deferidos_permanecem_sem_documento_origem_fabricado():
    """Confirma que os 3 checklists sem candidato real no corpus não
    foram forçados com um vínculo fraco — permanecem vazios, aguardando
    documento narrativo dedicado em lote futuro."""
    checklists = _load_checklists()
    for slug in DEFERIDOS_SEM_DOCUMENTO_ORIGEM:
        assert slug in checklists, f"checklist {slug} não encontrado"
        assert not checklists[slug].get("documento_origem"), (
            f"{slug} não deveria ter documento_origem preenchido neste lote"
        )
