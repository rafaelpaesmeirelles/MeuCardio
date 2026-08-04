from pathlib import Path

from app.commands import publish_preserved_content as command


class _Field:
    __hash__ = object.__hash__

    def is_(self, value):
        return ("is", value)

    def __eq__(self, value):
        return ("eq", value)


class _Model:
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
        "documentos": {"model": _Model},
        "evidencias": {"model": _Model},
    })
    db = _Session([3, 2])
    result = command.publish_preserved_reviewed(db)

    assert result["published_total"] == 5
    assert result["published_by_front"] == {"documentos": 3, "evidencias": 2}
    assert db.commits == 1
    assert db.rollbacks == 0
    assert all(query.updated for query in db.queries)
    assert all(len(query.filters) == 2 for query in db.queries)


def test_dry_run_nao_altera_banco(monkeypatch):
    monkeypatch.setattr(command, "FRONTS", {"documentos": {"model": _Model}})
    db = _Session([4])
    result = command.publish_preserved_reviewed(db, dry_run=True)

    assert result["published_total"] == 4
    assert db.commits == 0
    assert db.rollbacks == 1
    assert not db.queries[0].updated


def test_ordem_do_menu_alerta_e_deploy():
    root = Path(__file__).resolve().parents[2]
    shell = (root / "frontend/src/components/Shell.tsx").read_text(encoding="utf-8")
    painel = (root / "frontend/src/pages/Painel.tsx").read_text(encoding="utf-8")
    css = (root / "frontend/src/styles/shell.css").read_text(encoding="utf-8")
    deploy = (root / "deploy.sh").read_text(encoding="utf-8")

    assert ': [PAINEL, ...NAV_BASE, INDICADORES, CONTA];' in shell
    assert "INDICADORES,\n        ADMIN,\n        CONTA," in shell
    assert shell.index("PAINEL,\n        ...NAV_BASE") < shell.index("{ to: \"/fila-telediagnostico\"")
    assert "Acervo de produção abaixo do inventário certificado" not in painel
    assert 'className="emerg-atalho"' in shell
    assert ".emerg-atalho" in css
    assert "app.commands.publish_preserved_content" in deploy
