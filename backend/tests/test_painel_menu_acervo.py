import re
from pathlib import Path

from app.commands import publish_preserved_content as command


class _Field:
    __hash__ = object.__hash__

    def is_(self, value):
        return ("is", value)

    def in_(self, values):
        return ("in", frozenset(values))

    def __eq__(self, value):
        return ("eq", value)


class _Model:
    slug = _Field()
    published = _Field()
    review_status = _Field()


class _Query:
    def __init__(self, amount):
        self.amount = amount
        self.filters = []
        self.updated = False

    def filter(self, *conditions):
        self.filters.extend(conditions)
        return self

    def count(self):
        return self.amount

    def update(self, values, synchronize_session=False):
        assert values.get(_Model.published) is True
        assert synchronize_session is False
        self.updated = True
        return self.amount


class _Session:
    def __init__(self, amounts):
        self.amounts = iter(amounts)
        self.queries = []
        self.commits = 0
        self.rollbacks = 0

    def query(self, model):
        assert model is _Model
        query = _Query(next(self.amounts))
        self.queries.append(query)
        return query

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1


def test_publica_preservados_revisados(monkeypatch):
    monkeypatch.setattr(command, "FRONTS", {
        "documentos": {"model": _Model, "path": "/documentos"},
        "evidencias": {"model": _Model, "path": "/evidencias.json"},
    })
    monkeypatch.setattr(command, "_ensure_source", lambda front, path: path)
    monkeypatch.setattr(
        command,
        "_canonical_source_slugs",
        lambda front, source: {f"{front}-atual"},
    )
    db = _Session([3, 2])
    result = command.publish_preserved_reviewed(db)

    assert result["published_total"] == 5
    assert result["published_by_front"] == {"documentos": 3, "evidencias": 2}
    assert db.commits == 1
    assert db.rollbacks == 0
    assert all(query.updated for query in db.queries)
    assert all(len(query.filters) == 3 for query in db.queries)
    assert db.queries[0].filters[0] == ("in", frozenset({"documentos-atual"}))
    assert db.queries[1].filters[0] == ("in", frozenset({"evidencias-atual"}))


def test_dry_run_nao_altera_banco(monkeypatch):
    monkeypatch.setattr(command, "FRONTS", {
        "documentos": {"model": _Model, "path": "/documentos"},
    })
    monkeypatch.setattr(command, "_ensure_source", lambda front, path: path)
    monkeypatch.setattr(command, "_canonical_source_slugs", lambda front, source: {"atual"})
    db = _Session([4])
    result = command.publish_preserved_reviewed(db, dry_run=True)

    assert result["published_total"] == 4
    assert db.commits == 0
    assert db.rollbacks == 1
    assert not db.queries[0].updated


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
