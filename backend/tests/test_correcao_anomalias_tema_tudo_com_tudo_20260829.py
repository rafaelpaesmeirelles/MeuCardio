"""Regressão da auditoria de 29/08/2026 ao mecanismo "Tudo com Tudo"
(`app/services/related_content.py`).

A auditoria encontrou 3 registros com `theme`/`tema` fora do vocabulário
canônico de 30 temas — cada um era um silo de 1 item, invisível ao
cruzamento de conteúdo relacionado (`GET /api/relacionados?tema=...`)
porque o casamento nesse mecanismo é por STRING EXATA, sem normalização.
Ver `docs/correcao-anomalias-tema-tudo-com-tudo-2026-08-29.md` para o
relato completo.

Este teste não sobe banco nem API — lê os manifestos/arquivos de conteúdo
diretamente do disco, no mesmo espírito de `test_rc605_canonical_disease_
inventory.py` e da família `test_aprofundamento_*`, e trava o valor
corrigido de cada um dos 3 registros para prevenir regressão futura
(reversão acidental, merge conflituoso, etc.).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def _theme_from_markdown_front_matter(path: Path) -> str:
    texto = path.read_text(encoding="utf-8")
    m = re.search(r'^theme:\s*"([^"]+)"', texto, re.MULTILINE)
    assert m, f"campo theme não encontrado no front-matter de {path}"
    return m.group(1)


def _patient_material_by_slug(slug: str) -> dict:
    caminho = REPOSITORY_ROOT / "material-paciente" / "metadados.json"
    registros = json.loads(caminho.read_text(encoding="utf-8"))
    for item in registros:
        if item.get("slug") == slug:
            return item
    raise AssertionError(f"slug {slug!r} não encontrado em {caminho}")


def test_documento_cardiorrenal_usa_tema_insuficiencia_cardiaca():
    """esc-2026-doenca-cardiovascular-e-doenca-renal-cronica-stamp-on-ckd
    tinha theme = "Cardiorrenal" (fora do vocabulário canônico, uso único
    no repositório) — corrigido para "Insuficiência cardíaca"."""
    caminho = (
        REPOSITORY_ROOT
        / "content"
        / "Cardiorrenal"
        / "esc-2026-doenca-cardiovascular-e-doenca-renal-cronica-stamp-on-ckd.md"
    )
    assert caminho.is_file()
    assert _theme_from_markdown_front_matter(caminho) == "Insuficiência cardíaca"


def test_documento_reabilitacao_cardiaca_usa_tema_prevencao_e_lipidios():
    """esc-2026-reabilitacao-cardiaca-sintese-pratica-corvia tinha
    theme = "Reabilitação cardíaca" (fora do vocabulário canônico, uso
    único no repositório) — corrigido para "Prevenção e lipídios", mesmo
    tema já usado pelo documento irmão sobre o mesmo assunto,
    reabilitacao-cardiaca-e-prescricao-de-exercicio-na-prevencao-
    secundaria.md."""
    caminho = (
        REPOSITORY_ROOT
        / "content"
        / "Reabilitação_cardíaca"
        / "esc-2026-reabilitacao-cardiaca-sintese-pratica-corvia.md"
    )
    assert caminho.is_file()
    assert _theme_from_markdown_front_matter(caminho) == "Prevenção e lipídios"

    irmao = (
        REPOSITORY_ROOT
        / "content"
        / "Prevenção_e_lipídios"
        / "reabilitacao-cardiaca-e-prescricao-de-exercicio-na-prevencao-secundaria.md"
    )
    assert irmao.is_file()
    assert _theme_from_markdown_front_matter(irmao) == "Prevenção e lipídios"


def test_material_paciente_colapso_subito_usa_tema_terapia_intensiva():
    """colapso-subito-como-reconhecer-parada-e-usar-o-dea tinha
    tema = "Emergências cardiovasculares" (fora do vocabulário canônico,
    uso único no repositório) — corrigido para "Terapia intensiva", o
    mesmo tema do documento-mãe (documento_slug) e dos outros 13 materiais
    de parada cardíaca/UTI."""
    item = _patient_material_by_slug("colapso-subito-como-reconhecer-parada-e-usar-o-dea")
    assert item["tema"] == "Terapia intensiva"

    documento_mae = (
        REPOSITORY_ROOT
        / "content"
        / "Terapia_intensiva"
        / f"{item['documento_slug']}.md"
    )
    assert documento_mae.is_file()
    assert _theme_from_markdown_front_matter(documento_mae) == "Terapia intensiva"


def test_nenhum_dos_tres_temas_anomalos_sobrevive_no_corpus():
    """Os 3 valores de tema que causavam os silos não devem mais aparecer
    em lugar nenhum do corpus — nem em content/, nem em material-paciente/
    metadados.json."""
    temas_removidos = {"Cardiorrenal", "Reabilitação cardíaca", "Emergências cardiovasculares"}

    for caminho in (REPOSITORY_ROOT / "content").glob("**/*.md"):
        m = re.search(r'^theme:\s*"([^"]+)"', caminho.read_text(encoding="utf-8"), re.MULTILINE)
        if m:
            assert m.group(1) not in temas_removidos, f"{caminho} ainda usa tema anômalo {m.group(1)!r}"

    registros = json.loads(
        (REPOSITORY_ROOT / "material-paciente" / "metadados.json").read_text(encoding="utf-8")
    )
    for item in registros:
        tema = item.get("tema")
        assert tema not in temas_removidos, f"{item.get('slug')} ainda usa tema anômalo {tema!r}"
