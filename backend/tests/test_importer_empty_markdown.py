"""Protege o diagnóstico de documentos Markdown sem corpo."""

import pytest

from app.commands.reconcile_content import _assert_no_rejections
from app.services import importer


class _DbSemUso:
    def close(self):
        return None

    def rollback(self):
        return None


def test_importador_reporta_markdown_vazio_e_reconciliador_bloqueia(tmp_path, monkeypatch):
    arquivo = tmp_path / "somente-front-matter.md"
    arquivo.write_text(
        "---\n"
        "title: Documento sem corpo\n"
        "slug: documento-sem-corpo\n"
        "review_status: revisado\n"
        "---\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(importer, "SessionLocal", lambda: _DbSemUso())

    resultado = importer.import_directory(str(tmp_path))

    assert resultado["novos"] == 0
    assert resultado["atualizados"] == 0
    assert resultado["inalterados"] == 0
    assert resultado["vazios"] == [
        "somente-front-matter.md (arquivo sem corpo Markdown; ignorado)"
    ]
    with pytest.raises(RuntimeError, match="somente-front-matter.md"):
        _assert_no_rejections("documentos", resultado)
