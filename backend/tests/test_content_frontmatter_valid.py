from pathlib import Path

import frontmatter
import pytest


ROOT = Path(__file__).resolve().parents[2]
CONTENT = ROOT / "content"


def test_all_markdown_frontmatter_is_parseable():
    """Falha com o caminho exato quando um documento quebra o reconciliador.

    O reconciliador percorre todo o corpus Markdown antes de publicar. Um único
    frontmatter YAML inválido interrompe a rodada inteira; este gate deixa o
    diagnóstico local e explícito em vez de expor apenas a linha do parser.
    """
    for md in sorted(CONTENT.rglob("*.md")):
        try:
            frontmatter.load(md)
        except Exception as exc:  # pragma: no cover - só executa no corpus inválido
            pytest.fail(f"Frontmatter YAML inválido em {md.relative_to(ROOT)}: {exc}")
