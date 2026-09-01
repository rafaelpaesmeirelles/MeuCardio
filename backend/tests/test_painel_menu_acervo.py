import re
from pathlib import Path

import pytest

from app.commands import publish_preserved_content as command


@pytest.fixture(autouse=True)
def _banco_limpo():
    """Este módulo valida contratos puros e não precisa do PostgreSQL global."""
    yield


class _Session:
    def __init__(self):
        self.rollbacks = 0

    def rollback(self):
        self.rollbacks += 1


def test_publica_preservados_revisados(monkeypatch):
    monkeypatch.setattr(command, "FRONTS", {
        "documentos": {"model": object, "path": "/documentos"},
        "evidencias": {"model": object, "path": "/evidencias.json"},
    })
    monkeypatch.setattr(command, "_ensure_source", lambda front, path: path)
    monkeypatch.setattr(
        command,
        "_canonical_source_slugs",
        lambda front, source: {
            f"{front}-atual",
            f"{front}-quarentena",
            f"{front}-legado",
        },
    )
    monkeypatch.setattr(
        command,
        "_canonical_publication_intents",
        lambda front, source: {
            f"{front}-atual": True,
            f"{front}-quarentena": False,
            f"{front}-legado": None,
        },
    )
    monkeypatch.setattr(
        command,
        "_load_editorial_approvals",
        lambda: {
            "documentos": {"documentos-atual", "documentos-quarentena"},
            "evidencias": {"evidencias-atual", "evidencias-quarentena"},
        },
    )
    captured = {}

    def synchronize(db, canonical_slugs, **kwargs):
        captured.update({"db": db, "canonical": canonical_slugs, **kwargs})
        return (
            {"documentos": 3, "evidencias": 2},
            {"documentos": 1, "evidencias": 0},
            {"documentos": 0, "evidencias": 1},
            {"documentos": 2, "evidencias": 2},
        )

    monkeypatch.setattr(command, "_synchronize_publication", synchronize)
    db = _Session()
    result = command.publish_preserved_reviewed(db)

    assert result["published_total"] == 5
    assert result["published_by_front"] == {"documentos": 3, "evidencias": 2}
    assert result["unpublished_absent"] == {"documentos": 1, "evidencias": 0}
    assert result["unpublished_unreviewed"] == {"documentos": 0, "evidencias": 1}
    assert result["unpublished_ineligible"] == {"documentos": 2, "evidencias": 2}
    assert db.rollbacks == 0
    assert captured["db"] is db
    assert captured["publish_reviewed"] is True
    assert captured["dry_run"] is False
    assert captured["publication_intents"]["documentos"]["documentos-quarentena"] is False


def test_dry_run_nao_altera_banco(monkeypatch):
    monkeypatch.setattr(command, "FRONTS", {
        "documentos": {"model": object, "path": "/documentos"},
    })
    monkeypatch.setattr(command, "_ensure_source", lambda front, path: path)
    monkeypatch.setattr(command, "_canonical_source_slugs", lambda front, source: {"atual"})
    monkeypatch.setattr(
        command, "_canonical_publication_intents", lambda front, source: {"atual": True}
    )
    monkeypatch.setattr(
        command, "_load_editorial_approvals", lambda: {"documentos": {"atual"}}
    )
    captured = {}

    def synchronize(_db, _canonical, **kwargs):
        captured.update(kwargs)
        return (
            {"documentos": 4},
            {"documentos": 1},
            {"documentos": 2},
            {"documentos": 3},
        )

    monkeypatch.setattr(command, "_synchronize_publication", synchronize)
    db = _Session()
    result = command.publish_preserved_reviewed(db, dry_run=True)

    assert result["published_total"] == 4
    assert captured["dry_run"] is True
    assert db.rollbacks == 0


def test_publicador_preservado_rejeita_aprovacao_orfa(monkeypatch):
    monkeypatch.setattr(command, "FRONTS", {
        "documentos": {"model": object, "path": "/documentos"},
    })
    monkeypatch.setattr(command, "_ensure_source", lambda front, path: path)
    monkeypatch.setattr(command, "_canonical_source_slugs", lambda front, source: {"atual"})
    monkeypatch.setattr(
        command, "_canonical_publication_intents", lambda front, source: {"atual": True}
    )
    monkeypatch.setattr(
        command,
        "_load_editorial_approvals",
        lambda: {"documentos": {"atual", "ausente"}},
    )
    monkeypatch.setattr(
        command,
        "_synchronize_publication",
        lambda *_args, **_kwargs: pytest.fail("não deve sincronizar approval órfã"),
    )
    db = _Session()

    with pytest.raises(RuntimeError, match="slugs ausentes"):
        command.publish_preserved_reviewed(db)

    assert db.rollbacks == 1


def test_publicador_preservado_usa_a_politica_integral_do_reconcile():
    source = Path(command.__file__).read_text(encoding="utf-8")
    assert "_canonical_publication_intents" in source
    assert "_load_editorial_approvals" in source
    assert "_validate_editorial_approvals" in source
    assert "_synchronize_publication" in source
    assert "unpublished_absent" in source
    assert "unpublished_unreviewed" in source
    assert "unpublished_ineligible" in source


def test_ordem_do_menu_alerta_e_deploy():
    root = Path(__file__).resolve().parents[2]
    shell = (root / "frontend/src/components/ShellClinicalOSLaunch.tsx").read_text(encoding="utf-8")
    painel = (root / "frontend/src/pages/PainelClinicalOS.tsx").read_text(encoding="utf-8")
    clinical_css = (root / "frontend/src/styles/clinical-os.css").read_text(encoding="utf-8")
    emergencia_css = (root / "frontend/src/styles/emergencia.css").read_text(encoding="utf-8")
    deploy = (root / "deploy.sh").read_text(encoding="utf-8")

    # A ordem do Clinical OS legado continua protegida como fallback; a
    # navegação canônica visível é certificada separadamente no inventário.
    assert shell.index('id: "decisao"') < shell.index('id: "pratica"')
    assert shell.index('id: "pratica"') < shell.index('id: "conhecimento"')
    assert shell.index('id: "conhecimento"') < shell.index('id: "comunicacao"')
    assert shell.index('id: "comunicacao"') < shell.index('id: "gestao"')
    assert 'secao.id !== "gestao"' in shell
    assert '{ to: "/admin", rotulo: "Administração"' in shell
    assert '{ to: "/fila-telediagnostico", rotulo: "Fila de telediagnóstico"' in shell

    assert "Acervo de produção abaixo do inventário certificado" not in painel
    # O botão publicado usa hoje o seletor específico `cos-emergency-fab`;
    # o teste anterior ainda exigia a classe removida `cos-emergency`.
    assert 'className="cos-emergency-fab"' in shell
    assert ".cos-emergency" in clinical_css
    assert ".emerg-atalho {" not in clinical_css
    assert len(re.findall(r"(?m)^\.emerg-atalho\s*\{", emergencia_css)) == 1
    assert "padding: 0.8rem 1.15rem" in emergencia_css
    assert "app.commands.publish_preserved_content" in deploy
