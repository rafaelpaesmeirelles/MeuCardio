import json
import re
from pathlib import Path

from sqlalchemy import Boolean, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from app.commands import publish_preserved_content as command
from app.commands import reconcile_content as reconciliation


class _Base(DeclarativeBase):
    pass


class _Document(_Base):
    __tablename__ = "test_preserved_documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String, unique=True)
    published: Mapped[bool] = mapped_column(Boolean, default=False)
    review_status: Mapped[str | None] = mapped_column(String, nullable=True)


class _Evidence(_Base):
    __tablename__ = "test_preserved_evidence"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String, unique=True)
    published: Mapped[bool] = mapped_column(Boolean, default=False)
    review_status: Mapped[str | None] = mapped_column(String, nullable=True)


class _TrackingSession(Session):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.commits = 0
        self.rollbacks = 0

    def commit(self):
        self.commits += 1
        super().commit()

    def rollback(self):
        self.rollbacks += 1
        super().rollback()


def _session_with(*records) -> _TrackingSession:
    engine = create_engine("sqlite://")
    _Base.metadata.create_all(engine)
    db = _TrackingSession(bind=engine)
    db.add_all(records)
    db.commit()
    db.commits = 0
    return db


def _manifest(path: Path, slugs: set[str]) -> Path:
    path.write_text(
        json.dumps([{"slug": slug, "published": True} for slug in sorted(slugs)]),
        encoding="utf-8",
    )
    return path


def test_publica_preservados_revisados(monkeypatch, tmp_path):
    document_slugs = {f"documentos-atual-{index}" for index in range(3)}
    evidence_slugs = {f"evidencias-atual-{index}" for index in range(2)}
    fronts = {
        "documentos": {
            "model": _Document,
            "path": _manifest(tmp_path / "documentos.json", document_slugs),
        },
        "evidencias": {
            "model": _Evidence,
            "path": _manifest(tmp_path / "evidencias.json", evidence_slugs),
        },
    }
    approvals = {
        "documentos": document_slugs,
        "evidencias": evidence_slugs,
    }
    monkeypatch.setattr(command, "FRONTS", fronts)
    monkeypatch.setattr(reconciliation, "FRONTS", fronts)
    monkeypatch.setattr(
        command,
        "_load_full_corpus_authorization",
        lambda canonical, _sources: (
            {front: set() for front in canonical},
            None,
        ),
    )
    monkeypatch.setattr(command, "_load_editorial_approvals", lambda: approvals)
    db = _session_with(
        *(
            _Document(slug=slug, published=False, review_status="revisado")
            for slug in document_slugs
        ),
        *(
            _Evidence(slug=slug, published=False, review_status="revisado")
            for slug in evidence_slugs
        ),
    )

    try:
        result = command.publish_preserved_reviewed(db)

        assert result["published_total"] == 5
        assert result["published_by_front"] == {"documentos": 3, "evidencias": 2}
        assert result["unpublished_absent"] == {"documentos": 0, "evidencias": 0}
        assert result["unpublished_unreviewed"] == {"documentos": 0, "evidencias": 0}
        assert result["unpublished_ineligible"] == {"documentos": 0, "evidencias": 0}
        assert db.commits == 1
        assert db.rollbacks == 0
        assert all(row.published for row in db.query(_Document).all())
        assert all(row.published for row in db.query(_Evidence).all())
    finally:
        db.close()


def test_dry_run_nao_altera_banco(monkeypatch, tmp_path):
    slugs = {f"atual-{index}" for index in range(4)}
    fronts = {
        "documentos": {
            "model": _Document,
            "path": _manifest(tmp_path / "documentos.json", slugs),
        },
    }
    monkeypatch.setattr(command, "FRONTS", fronts)
    monkeypatch.setattr(reconciliation, "FRONTS", fronts)
    monkeypatch.setattr(
        command,
        "_load_full_corpus_authorization",
        lambda canonical, _sources: (
            {front: set() for front in canonical},
            None,
        ),
    )
    monkeypatch.setattr(
        command,
        "_load_editorial_approvals",
        lambda: {"documentos": slugs},
    )
    db = _session_with(
        *(
            _Document(slug=slug, published=False, review_status="revisado")
            for slug in slugs
        )
    )

    try:
        result = command.publish_preserved_reviewed(db, dry_run=True)

        assert result["published_total"] == 4
        assert result["dry_run"] is True
        assert db.commits == 0
        assert db.rollbacks == 1
        assert all(not row.published for row in db.query(_Document).all())
    finally:
        db.close()


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
