"""Regressões do vínculo tipado entre evidência e estudo científico."""

from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from app.api.evidence import _card, _detail
from app.models.evidence import EvidenceRecord
from app.services import carregar_evidencias
from migrations.versions import f90s20260901_evidence_study_slug as migration


@pytest.fixture(autouse=True)
def _banco_limpo():
    """Estes contratos usam sessões falsas e não dependem de PostgreSQL."""
    yield


class _Query:
    def __init__(self, existing=None):
        self.existing = existing

    def filter(self, *_args, **_kwargs):
        return self

    def first(self):
        return self.existing


class _Session:
    def __init__(self, existing=None):
        self.existing = existing
        self.added = []
        self.commits = 0

    def query(self, _model):
        return _Query(self.existing)

    def add(self, record):
        self.added.append(record)

    def commit(self):
        self.commits += 1

    def close(self):
        pass


def _evidence_payload(**overrides):
    return {
        "slug": "evidencia-com-estudo",
        "statement": "Recomendação clínica.",
        "recommendation_class": "I",
        "evidence_level": "A",
        "society": "SBC",
        "year": 2026,
        "guideline_title": "Diretriz",
        "reference": "PMID:12345678",
        "theme": "Teste",
        "review_status": "revisado",
        "published": False,
        "study_slug": "estudo-clinico-canonico",
        **overrides,
    }


def test_model_declares_nullable_indexed_study_slug():
    column = EvidenceRecord.__table__.columns["study_slug"]

    assert column.nullable is True
    assert column.index is True
    assert column.type.length == 255


def test_loader_persiste_study_slug_pela_lista_de_colunas(monkeypatch, tmp_path):
    session = _Session()
    monkeypatch.setattr(carregar_evidencias, "SessionLocal", lambda: session)
    manifest = tmp_path / "evidencias.json"
    manifest.write_text(
        json.dumps([_evidence_payload()], ensure_ascii=False), encoding="utf-8"
    )

    result = carregar_evidencias.carregar(str(manifest))

    assert result == {"novos": 1, "atualizados": 0}
    assert session.added[0].study_slug == "estudo-clinico-canonico"
    assert session.added[0].published is False
    assert session.commits == 1
    assert "study_slug" in carregar_evidencias._COLUNAS


def test_loader_atualiza_study_slug_em_evidencia_existente(monkeypatch, tmp_path):
    existing = SimpleNamespace(
        slug="evidencia-com-estudo",
        study_slug="estudo-anterior",
        review_status="revisado",
        review_note=None,
        published=False,
    )
    session = _Session(existing)
    monkeypatch.setattr(carregar_evidencias, "SessionLocal", lambda: session)
    manifest = tmp_path / "evidencias.json"
    manifest.write_text(
        json.dumps([_evidence_payload()], ensure_ascii=False), encoding="utf-8"
    )

    result = carregar_evidencias.carregar(str(manifest))

    assert result == {"novos": 0, "atualizados": 1}
    assert existing.study_slug == "estudo-clinico-canonico"
    assert existing.published is False
    assert session.commits == 1


def test_detail_expoe_vinculo_clinico_sem_ampliar_card_ou_metadados_editoriais():
    evidence = EvidenceRecord(
        **_evidence_payload(),
        review_note="Nota editorial interna.",
    )

    detail = _detail(evidence)

    assert detail["study_slug"] == "estudo-clinico-canonico"
    assert "study_slug" not in _card(evidence)
    assert "review_note" not in detail
    assert "fonte_producao" not in detail


def test_migration_is_linear_after_f89_and_fails_when_table_is_missing(monkeypatch):
    assert migration.down_revision == "f89s20260901"

    class MissingInspector:
        def has_table(self, _table):
            return False

    monkeypatch.setattr(migration.op, "get_bind", lambda: object())
    monkeypatch.setattr(migration.sa, "inspect", lambda _bind: MissingInspector())

    with pytest.raises(RuntimeError, match="expected table is missing: evidence_records"):
        migration.upgrade()


def test_migration_adds_nullable_column_and_non_unique_index(monkeypatch):
    class EmptyInspector:
        def has_table(self, table):
            return table == "evidence_records"

        def get_columns(self, _table):
            return []

        def get_indexes(self, _table):
            return []

    additions = []
    indexes = []
    monkeypatch.setattr(migration.op, "get_bind", lambda: object())
    monkeypatch.setattr(migration.sa, "inspect", lambda _bind: EmptyInspector())
    monkeypatch.setattr(
        migration.op,
        "add_column",
        lambda table, column: additions.append((table, column)),
    )
    monkeypatch.setattr(
        migration.op,
        "create_index",
        lambda name, table, columns, unique: indexes.append(
            (name, table, columns, unique)
        ),
    )

    migration.upgrade()

    assert len(additions) == 1
    table, column = additions[0]
    assert table == "evidence_records"
    assert column.name == "study_slug"
    assert column.nullable is True
    assert column.type.length == 255
    assert column.comment == migration.OWNER_COMMENT
    assert indexes == [(
        "ix_evidence_records_study_slug",
        "evidence_records",
        ["study_slug"],
        False,
    )]


def test_migration_is_idempotent_when_column_and_index_exist(monkeypatch):
    class ExistingInspector:
        def has_table(self, _table):
            return True

        def get_columns(self, _table):
            return [{
                "name": "study_slug",
                "type": migration.sa.String(length=255),
                "nullable": True,
                "comment": None,
            }]

        def get_indexes(self, _table):
            return [{
                "name": "ix_evidence_records_study_slug",
                "column_names": ["study_slug"],
                "unique": False,
            }]

    additions = []
    indexes = []
    monkeypatch.setattr(migration.op, "get_bind", lambda: object())
    monkeypatch.setattr(migration.sa, "inspect", lambda _bind: ExistingInspector())
    monkeypatch.setattr(migration.op, "add_column", additions.append)
    monkeypatch.setattr(migration.op, "create_index", indexes.append)

    migration.upgrade()

    assert additions == []
    assert indexes == []


def test_migration_rejects_incompatible_existing_column(monkeypatch):
    class IncompatibleInspector:
        def has_table(self, _table):
            return True

        def get_columns(self, _table):
            return [{
                "name": "study_slug",
                "type": migration.sa.String(length=120),
                "nullable": True,
                "comment": None,
            }]

        def get_indexes(self, _table):
            return []

    monkeypatch.setattr(migration.op, "get_bind", lambda: object())
    monkeypatch.setattr(migration.sa, "inspect", lambda _bind: IncompatibleInspector())

    with pytest.raises(RuntimeError, match="incompatible pre-existing column"):
        migration.upgrade()


def test_migration_rejects_incompatible_existing_index(monkeypatch):
    class IncompatibleInspector:
        def has_table(self, _table):
            return True

        def get_columns(self, _table):
            return [{
                "name": "study_slug",
                "type": migration.sa.String(length=255),
                "nullable": True,
                "comment": None,
            }]

        def get_indexes(self, _table):
            return [{
                "name": "ix_evidence_records_study_slug",
                "column_names": ["slug"],
                "unique": False,
            }]

    monkeypatch.setattr(migration.op, "get_bind", lambda: object())
    monkeypatch.setattr(migration.sa, "inspect", lambda _bind: IncompatibleInspector())

    with pytest.raises(RuntimeError, match="incompatible pre-existing index"):
        migration.upgrade()


def test_migration_downgrade_preserves_unowned_column_and_index(monkeypatch):
    class PreexistingInspector:
        def has_table(self, _table):
            return True

        def get_columns(self, _table):
            return [{
                "name": "study_slug",
                "type": migration.sa.String(length=255),
                "nullable": True,
                "comment": None,
            }]

        def get_indexes(self, _table):
            return [{
                "name": "ix_evidence_records_study_slug",
                "column_names": ["study_slug"],
                "unique": False,
            }]

    removals = []
    monkeypatch.setattr(migration.op, "get_bind", lambda: object())
    monkeypatch.setattr(migration.sa, "inspect", lambda _bind: PreexistingInspector())
    monkeypatch.setattr(migration.op, "drop_index", lambda *args, **kwargs: removals.append(args))
    monkeypatch.setattr(migration.op, "drop_column", lambda *args, **kwargs: removals.append(args))

    migration.downgrade()

    assert removals == []
