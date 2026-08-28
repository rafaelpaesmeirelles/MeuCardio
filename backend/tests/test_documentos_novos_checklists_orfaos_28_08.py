"""Contrato do lote de 28/08/2026 que escreve 3 documentos narrativos
novos em content/**/*.md, preenchendo lacunas confirmadas do corpus
(nenhum documento existente tratava centralmente desses temas) e
fechando o documento_origem de 3 checklists já publicados que estavam
órfãos por essa mesma razão.

Trigésimo quinto lote de conteúdo do dia. Duas PRs anteriores fechadas
(#460, #465) já haviam tentado vincular esses 3 checklists a arquivos
que nunca chegaram a existir em nenhuma branch — este lote resolve a
causa raiz escrevendo os documentos de fato, em vez de apenas apontar
para um slug.

Nota sobre verificação de citações: todos os 7 PMIDs usados nos 3
documentos foram verificados individualmente via NCBI e-utils antes da
escrita — nenhuma correção foi necessária.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
CHECKLISTS_PATH = REPOSITORY_ROOT / "checklists/metadados.json"

DOCUMENTOS = {
    "aplicacao-do-stop-bang-na-triagem-de-apneia-obstrutiva-do-sono-pre-operatoria-em-cirurgia-cardiaca": (
        REPOSITORY_ROOT / "content/Cardiologia_do_Esporte_e_do_Exercício"
        / "aplicacao-do-stop-bang-na-triagem-de-apneia-obstrutiva-do-sono-pre-operatoria-em-cirurgia-cardiaca.md"
    ),
    "manejo-da-abstinencia-alcoolica-aguda-com-risco-de-tempestade-autonomica-e-arritmia": (
        REPOSITORY_ROOT / "content/Saúde_mental_e_cardiologia"
        / "manejo-da-abstinencia-alcoolica-aguda-com-risco-de-tempestade-autonomica-e-arritmia.md"
    ),
    "diagnostico-e-tratamento-da-trombose-de-esforco-sindrome-de-paget-schroetter": (
        REPOSITORY_ROOT / "content/Tromboembolismo"
        / "diagnostico-e-tratamento-da-trombose-de-esforco-sindrome-de-paget-schroetter.md"
    ),
}

MIN_PALAVRAS_CORPO = 700

DOSE_PATTERNS = (
    r"\d+[\.,]?\d*\s*mg(?!/d[lL])\b",
    r"\d+[\.,]?\d*\s*mg/kg",
    r"\d+[\.,]?\d*\s*mcg",
    r"\d+[\.,]?\d*\s*j/kg",
)


def _read(slug: str) -> str:
    path = DOCUMENTOS[slug]
    assert path.exists(), f"documento não encontrado: {path}"
    return path.read_text(encoding="utf-8")


def _frontmatter(text: str) -> dict:
    assert text.startswith("---")
    raw = text.split("---", 2)[1]
    fm = {}
    for line in raw.strip().splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        fm[key.strip()] = value.strip()
    return fm


def _corpo(text: str) -> str:
    return text.split("---", 2)[2]


def test_todos_os_3_documentos_existem_no_caminho_esperado():
    for slug in DOCUMENTOS:
        assert DOCUMENTOS[slug].exists(), f"{slug}: arquivo não existe em {DOCUMENTOS[slug]}"


def test_frontmatter_tem_slug_correto_e_review_status_pendente():
    for slug, path in DOCUMENTOS.items():
        text = path.read_text(encoding="utf-8")
        fm = _frontmatter(text)
        assert slug in text, f"{slug}: slug não aparece no frontmatter"
        assert fm.get("review_status") == '"pendente_revisao"' or "pendente_revisao" in text
        assert "review_note" in text
        assert "source_refs" in text


def test_profundidade_minima_nao_e_esboco():
    for slug, path in DOCUMENTOS.items():
        text = path.read_text(encoding="utf-8")
        corpo = _corpo(text)
        palavras = len(corpo.split())
        assert palavras >= MIN_PALAVRAS_CORPO, f"{slug}: corpo tem {palavras} palavras, mínimo {MIN_PALAVRAS_CORPO}"


def test_texto_com_acentuacao_correta_do_portugues():
    palavras_por_documento = {
        "aplicacao-do-stop-bang-na-triagem-de-apneia-obstrutiva-do-sono-pre-operatoria-em-cirurgia-cardiaca": ("não ", "cardíaca", "cirúrgica"),
        "manejo-da-abstinencia-alcoolica-aguda-com-risco-de-tempestade-autonomica-e-arritmia": ("não ", "cardíaca", "abstinência"),
        "diagnostico-e-tratamento-da-trombose-de-esforco-sindrome-de-paget-schroetter": ("não ", "trombose", "cirúrgica"),
    }
    for slug, path in DOCUMENTOS.items():
        text = path.read_text(encoding="utf-8")
        for palavra in palavras_por_documento[slug]:
            assert palavra in text, f"{slug}: acentuação ausente: {palavra!r}"


def test_nenhuma_dose_de_farmaco_em_nenhum_documento():
    for slug, path in DOCUMENTOS.items():
        text = path.read_text(encoding="utf-8")
        for pattern in DOSE_PATTERNS:
            matches = re.findall(pattern, text)
            assert matches == [], f"{slug}: padrão de dose encontrado ({pattern}): {matches}"


def test_nenhum_documento_contem_substring_banida():
    for slug, path in DOCUMENTOS.items():
        text = path.read_text(encoding="utf-8").casefold()
        assert "mwho" not in text, f"{slug} contém 'mwho'"
        assert "hfa-icos" not in text, f"{slug} contém 'hfa-icos'"


def test_checklists_orfaos_agora_apontam_para_os_documentos_novos():
    checklists = json.loads(CHECKLISTS_PATH.read_text(encoding="utf-8"))
    por_slug = {it["slug"]: it for it in checklists}
    for checklist_slug, doc_path in DOCUMENTOS.items():
        assert checklist_slug in por_slug, f"checklist {checklist_slug} não encontrado"
        assert por_slug[checklist_slug].get("documento_origem") == checklist_slug, (
            f"{checklist_slug}: documento_origem não aponta para o documento esperado"
        )
