"""Regressão direcionada dos seis loaders do release científico."""

from __future__ import annotations

import json
import importlib
import inspect
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from sqlalchemy import Boolean, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from app.api.admin import (
    DecisaoRevisao,
    PublicacaoConteudo,
    publicar_conteudo,
    revisar,
)
from app.commands import reconcile_content as reconciliation
from app.commands.reconcile_content import _canonical_publication_intents
from app.models.patient_material import PatientMaterial
from app.models.study import ScientificStudy
from app.services import (
    carregar_casos_clinicos,
    carregar_checklists,
    carregar_doencas_especializadas,
    carregar_drugs,
    carregar_emergencia,
    carregar_estudos,
    carregar_evidencias,
    carregar_exames,
    carregar_galeria,
    carregar_material_paciente,
    carregar_triagem_sintomas,
    carregar_trilhas,
    importer,
)
from app.services.scientific_loader_safety import (
    combined_review_note,
    enforce_safe_publication,
)
from migrations.versions import f89s20260901_scientific_loader_metadata as metadata_migration


class _PublicationBase(DeclarativeBase):
    pass


class _PublicationRecord(_PublicationBase):
    __tablename__ = "publication_safety_fixture"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String, unique=True)
    review_status: Mapped[str | None] = mapped_column(String, nullable=True)
    published: Mapped[bool] = mapped_column(Boolean)


@pytest.fixture(autouse=True)
def _banco_limpo():
    """Este módulo usa sessões falsas e não precisa do PostgreSQL da suíte."""
    yield


class _Query:
    def __init__(self, existing):
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

    def rollback(self):
        pass

    def close(self):
        pass


LOADERS = (
    (
        carregar_estudos,
        {
            "slug": "estudo-loader-safe",
            "title": "Estudo seguro",
            "study_type": "ensaio_clinico",
            "journal": "Journal",
            "year": 2026,
            "pmid": "12345678",
            "url": "https://example.test/study",
            "summary": "Resumo",
            "key_findings": "Achados",
            "clinical_implications": "Implicações",
            "theme": "Teste",
        },
    ),
    (
        carregar_evidencias,
        {
            "slug": "evidencia-loader-safe",
            "statement": "Recomendação",
            "recommendation_class": "I",
            "evidence_level": "A",
            "society": "SBC",
            "year": 2026,
            "guideline_title": "Diretriz",
            "reference": "Referência verificável",
            "source_url": "https://example.test/evidence",
            "theme": "Teste",
        },
    ),
    (
        carregar_casos_clinicos,
        {
            "slug": "caso-loader-safe",
            "titulo": "Caso seguro",
            "tema": "Teste",
            "enunciado": "Vinheta",
            "pergunta": "Conduta?",
            "opcoes": ["A", "B"],
            "resposta_correta": 0,
            "explicacao": "Explicação",
            "source_refs": ["PMID:12345678"],
        },
    ),
    (
        carregar_checklists,
        {
            "slug": "checklist-loader-safe",
            "condicao": "Condição",
            "source_refs": ["PMID:12345678"],
            "itens": [{"id": "um", "origem_secao": "Diretriz"}],
        },
    ),
    (
        carregar_material_paciente,
        {
            "slug": "material-loader-safe",
            "titulo": "Material seguro",
            "tema": "Teste",
            "secoes": [],
            "source_refs": ["PMID:12345678"],
        },
    ),
    (
        carregar_trilhas,
        {
            "slug": "trilha-loader-safe",
            "titulo": "Trilha segura",
            "tema": "Teste",
            "etapas": [],
        },
    ),
    (
        carregar_exames,
        {
            "slug": "exame-loader-safe",
            "name": "Exame seguro",
            "category": "laboratorial",
            "what_it_measures": "Marcador",
            "indications": "Indicação",
            "interpretation": "Interpretação",
            "theme": "Teste",
            "source_refs": ["PMID:12345678"],
        },
    ),
    (
        carregar_drugs,
        {
            "slug": "medicamento-loader-safe",
            "generic_name": "Medicamento seguro",
            "drug_class": "Classe terapêutica",
            "references": ["PMID:12345678"],
        },
    ),
    (
        carregar_doencas_especializadas,
        {
            "slug": "doenca-loader-safe",
            "name": "Doença segura",
            "area": "geral",
            "category": "Teste",
            "summary": "Resumo",
            "source_refs": ["PMID:12345678"],
        },
    ),
    (
        carregar_triagem_sintomas,
        {
            "slug": "triagem-loader-safe",
            "name": "Triagem segura",
            "areas": ["geral"],
            "summary": "Resumo",
            "questions": [],
            "rules": [],
            "source_refs": ["PMID:12345678"],
        },
    ),
)


def _write_manifest(tmp_path, slug, payload):
    path = tmp_path / f"{slug}.json"
    path.write_text(json.dumps([payload], ensure_ascii=False), encoding="utf-8")
    return str(path)


@pytest.mark.parametrize("module,payload", LOADERS)
def test_loader_nunca_publica_registro_novo(module, payload, monkeypatch, tmp_path):
    session = _Session()
    monkeypatch.setattr(module, "SessionLocal", lambda: session)
    manifest = {**payload, "review_status": "revisado", "published": True}

    result = module.carregar(_write_manifest(tmp_path, payload["slug"], manifest))

    assert result["novos"] == 1
    assert session.added[0].published is False
    assert session.added[0].review_status == "revisado"
    assert session.commits == 1


@pytest.mark.parametrize("module,payload", LOADERS)
def test_loader_despublica_quando_revisao_volta_a_pendente(
    module, payload, monkeypatch, tmp_path
):
    existing = SimpleNamespace(
        slug=payload["slug"],
        published=True,
        review_status="revisado",
        version=1,
    )
    session = _Session(existing)
    monkeypatch.setattr(module, "SessionLocal", lambda: session)
    manifest = {
        **payload,
        "review_status": "pendente_revisao",
        "published": True,
        "review_note": "Aguardando revisão independente.",
        "fonte_producao": "lote científico 2026-09-01",
    }

    result = module.carregar(_write_manifest(tmp_path, payload["slug"], manifest))

    assert result["atualizados"] == 1
    assert existing.review_status == "pendente_revisao"
    assert existing.published is False
    assert session.commits == 1

    if module is carregar_evidencias:
        assert "Aguardando revisão independente." in existing.review_note
        assert "Proveniência de produção" in existing.review_note
        assert existing.reference == "Referência verificável"
    elif module in (carregar_casos_clinicos, carregar_checklists, carregar_trilhas):
        assert "Aguardando revisão independente." in existing.revisao
        assert "Proveniência de produção" in existing.revisao
    elif module is carregar_material_paciente:
        assert existing.fontes == ["PMID:12345678"]
        assert existing.review_note == "Aguardando revisão independente."
        assert existing.fonte_producao == "lote científico 2026-09-01"
    elif module is carregar_estudos:
        assert existing.pmid == "12345678"
        assert existing.url == "https://example.test/study"
        assert existing.review_note == "Aguardando revisão independente."
        assert existing.fonte_producao == "lote científico 2026-09-01"


@pytest.mark.parametrize("module,payload", LOADERS)
def test_loader_nunca_promove_update_privado_com_published_true(
    module, payload, monkeypatch, tmp_path
):
    existing = SimpleNamespace(
        slug=payload["slug"],
        published=False,
        review_status="revisado",
        version=1,
    )
    session = _Session(existing)
    monkeypatch.setattr(module, "SessionLocal", lambda: session)

    module.carregar(
        _write_manifest(
            tmp_path,
            payload["slug"],
            {**payload, "review_status": "revisado", "published": True},
        )
    )

    assert existing.published is False


@pytest.mark.parametrize("module,payload", LOADERS)
def test_loader_aplica_quarentena_false_antes_do_commit(
    module, payload, monkeypatch, tmp_path
):
    existing = SimpleNamespace(
        slug=payload["slug"],
        published=True,
        review_status="revisado",
        version=1,
    )
    session = _Session(existing)
    monkeypatch.setattr(module, "SessionLocal", lambda: session)

    module.carregar(
        _write_manifest(
            tmp_path,
            payload["slug"],
            {**payload, "review_status": "revisado", "published": False},
        )
    )

    assert existing.published is False
    assert session.commits == 1


@pytest.mark.parametrize(
    "module,payload",
    (
        (carregar_estudos, LOADERS[0][1]),
        (carregar_material_paciente, LOADERS[4][1]),
    ),
)
def test_loader_persiste_metadados_operacionais_em_registro_novo(
    module, payload, monkeypatch, tmp_path
):
    session = _Session()
    monkeypatch.setattr(module, "SessionLocal", lambda: session)
    manifest = {
        **payload,
        "review_note": "Aguardando revisão independente.",
        "fonte_producao": "lote científico versionado",
    }

    result = module.carregar(_write_manifest(tmp_path, payload["slug"], manifest))

    assert result["novos"] == 1
    assert session.added[0].review_note == "Aguardando revisão independente."
    assert session.added[0].fonte_producao == "lote científico versionado"


@pytest.mark.parametrize(
    "module,payload",
    (
        (carregar_estudos, LOADERS[0][1]),
        (carregar_material_paciente, LOADERS[4][1]),
    ),
)
def test_loader_preserva_metadados_operacionais_quando_fonte_legada_os_omite(
    module, payload, monkeypatch, tmp_path
):
    existing = SimpleNamespace(
        slug=payload["slug"],
        published=False,
        review_status="pendente_revisao",
        review_note="Revisão humana anterior.",
        fonte_producao="lote auditado anterior",
        version=1,
    )
    session = _Session(existing)
    monkeypatch.setattr(module, "SessionLocal", lambda: session)

    result = module.carregar(_write_manifest(tmp_path, payload["slug"], payload))

    assert result["atualizados"] == 1
    assert existing.review_note == "Revisão humana anterior."
    assert existing.fonte_producao == "lote auditado anterior"


def test_material_preserva_fontes_quando_aliases_estao_ausentes(monkeypatch, tmp_path):
    payload = {
        key: value
        for key, value in LOADERS[4][1].items()
        if key not in {"fontes", "source_refs"}
    }
    existing = SimpleNamespace(
        slug=payload["slug"],
        published=False,
        review_status="revisado",
        review_note=None,
        fonte_producao=None,
        fontes=["PMID:12345678"],
        version=1,
    )
    session = _Session(existing)
    monkeypatch.setattr(carregar_material_paciente, "SessionLocal", lambda: session)

    carregar_material_paciente.carregar(
        _write_manifest(tmp_path, payload["slug"], payload)
    )

    assert existing.fontes == ["PMID:12345678"]


def test_estudo_preserva_metadados_quando_fonte_traz_null(monkeypatch, tmp_path):
    payload = {
        **LOADERS[0][1],
        "summary": None,
        "review_note": None,
        "fonte_producao": None,
    }
    existing = SimpleNamespace(
        slug=payload["slug"],
        published=False,
        review_status="revisado",
        summary="Resumo científico anterior.",
        review_note="Revisão humana anterior.",
        fonte_producao="lote auditado anterior",
    )
    session = _Session(existing)
    monkeypatch.setattr(carregar_estudos, "SessionLocal", lambda: session)

    carregar_estudos.carregar(_write_manifest(tmp_path, payload["slug"], payload))

    assert existing.review_note == "Revisão humana anterior."
    assert existing.fonte_producao == "lote auditado anterior"
    assert existing.summary == "Resumo científico anterior."


@pytest.mark.parametrize(
    "module,payload,field",
    (
        (carregar_evidencias, LOADERS[1][1], "review_note"),
        (carregar_casos_clinicos, LOADERS[2][1], "revisao"),
        (carregar_checklists, LOADERS[3][1], "revisao"),
        (carregar_trilhas, LOADERS[5][1], "revisao"),
    ),
)
def test_loader_de_campo_unico_preserva_proveniencia_quando_nota_muda(
    module, payload, field, monkeypatch, tmp_path
):
    existing = SimpleNamespace(
        slug=payload["slug"],
        published=False,
        review_status="revisado",
        version=1,
        **{
            field: (
                "Revisão anterior.\n\n"
                "Proveniência de produção: lote auditado anterior"
            )
        },
    )
    session = _Session(existing)
    monkeypatch.setattr(module, "SessionLocal", lambda: session)
    manifest = {**payload, "review_note": "Revisão atualizada."}

    module.carregar(_write_manifest(tmp_path, payload["slug"], manifest))

    assert getattr(existing, field) == (
        "Revisão atualizada.\n\n"
        "Proveniência de produção: lote auditado anterior"
    )


def test_campo_unico_preserva_nota_quando_so_proveniencia_muda():
    existing = "Revisão anterior.\n\nProveniência de produção: lote anterior"

    assert combined_review_note(
        {"fonte_producao": "lote atual"}, existing=existing
    ) == "Revisão anterior.\n\nProveniência de produção: lote atual"


@pytest.mark.parametrize(
    "module,payload",
    (
        (carregar_doencas_especializadas, LOADERS[8][1]),
        (carregar_triagem_sintomas, LOADERS[9][1]),
    ),
)
def test_doenca_e_triagem_preservam_nota_e_proveniencia_em_null(
    module, payload, monkeypatch, tmp_path
):
    existing = SimpleNamespace(
        slug=payload["slug"],
        published=False,
        review_status="revisado",
        review_note=(
            "Revisão anterior.\n\n"
            "Proveniência de produção: lote auditado anterior"
        ),
        version=1,
    )
    session = _Session(existing)
    monkeypatch.setattr(module, "SessionLocal", lambda: session)

    module.carregar(
        _write_manifest(
            tmp_path,
            payload["slug"],
            {
                **payload,
                "review_status": "revisado",
                "review_note": None,
                "fonte_producao": None,
            },
        )
    )

    assert existing.review_note == (
        "Revisão anterior.\n\n"
        "Proveniência de produção: lote auditado anterior"
    )


def _gallery_payload(*, published=True, review_status="revisado"):
    return {
        "slug": "imagem-loader-safe",
        "title": "Imagem segura",
        "modality": "ECG",
        "theme": "Teste",
        "findings": "Achado",
        "file_path": "imagem.png",
        "source_name": "Fonte",
        "source_url": "https://example.test/image",
        "license": "CC0",
        "attribution": "Fonte",
        "review_status": review_status,
        "published": published,
    }


@pytest.mark.parametrize(
    "existing,source,expected",
    (
        (None, _gallery_payload(published=True), False),
        (
            SimpleNamespace(slug="imagem-loader-safe", published=False, review_status="revisado"),
            _gallery_payload(published=True),
            False,
        ),
        (
            SimpleNamespace(slug="imagem-loader-safe", published=True, review_status="revisado"),
            _gallery_payload(published=False),
            False,
        ),
        (
            SimpleNamespace(slug="imagem-loader-safe", published=True, review_status="revisado"),
            {key: value for key, value in _gallery_payload().items() if key != "published"}
            | {"review_status": "pendente_revisao"},
            False,
        ),
    ),
)
def test_galeria_e_fail_closed(existing, source, expected, monkeypatch, tmp_path):
    (tmp_path / "imagem.png").write_bytes(b"imagem")
    manifest = tmp_path / "galeria.json"
    manifest.write_text(json.dumps([source]), encoding="utf-8")
    session = _Session(existing)
    monkeypatch.setattr(carregar_galeria, "SessionLocal", lambda: session)
    monkeypatch.setattr(carregar_galeria, "GALERIA_DIR", tmp_path)

    carregar_galeria.carregar(str(manifest))

    record = session.added[0] if existing is None else existing
    assert record.published is expected
    assert session.commits == 1


class _EmergencyDocumentQuery:
    def all(self):
        return [("documento-seguro", True, "revisado")]


class _EmergencySession(_Session):
    def query(self, *entities):
        if len(entities) == 3:
            return _EmergencyDocumentQuery()
        return _Query(self.existing)


def _emergency_payload(*, published=True, review_status="revisado"):
    return {
        "slug": "emergencia-loader-safe",
        "titulo": "Emergência segura",
        "documento_slug": "documento-seguro",
        "review_status": review_status,
        "published": published,
    }


@pytest.mark.parametrize(
    "existing,source,expected",
    (
        (None, _emergency_payload(published=True), False),
        (
            SimpleNamespace(slug="emergencia-loader-safe", published=False, review_status="revisado"),
            _emergency_payload(published=True),
            False,
        ),
        (
            SimpleNamespace(slug="emergencia-loader-safe", published=True, review_status="revisado"),
            _emergency_payload(published=False),
            False,
        ),
        (
            SimpleNamespace(slug="emergencia-loader-safe", published=True, review_status="revisado"),
            {key: value for key, value in _emergency_payload().items() if key != "published"}
            | {"review_status": "pendente_revisao"},
            False,
        ),
    ),
)
def test_emergencia_e_fail_closed(existing, source, expected, monkeypatch, tmp_path):
    session = _EmergencySession(existing)
    monkeypatch.setattr(carregar_emergencia, "SessionLocal", lambda: session)

    carregar_emergencia.carregar(
        _write_manifest(tmp_path, source["slug"], source)
    )

    record = session.added[0] if existing is None else existing
    assert record.published is expected
    assert session.commits == 1


def _write_markdown(tmp_path, metadata):
    front_matter = "\n".join(f"{key}: {json.dumps(value)}" for key, value in metadata.items())
    path = tmp_path / "documento.md"
    path.write_text(f"---\n{front_matter}\n---\n\nConteúdo seguro.\n", encoding="utf-8")
    return path


@pytest.mark.parametrize(
    "existing,metadata,expected",
    (
        (None, {"published": True, "review_status": "revisado"}, False),
        (
            SimpleNamespace(slug="documento", body_md="Conteúdo seguro.", version=1,
                            published=False, review_status="revisado"),
            {"published": True, "review_status": "revisado"},
            False,
        ),
        (
            SimpleNamespace(slug="documento", body_md="Conteúdo seguro.", version=1,
                            published=True, review_status="revisado"),
            {"published": False, "review_status": "revisado"},
            False,
        ),
        (
            SimpleNamespace(slug="documento", body_md="Conteúdo seguro.", version=1,
                            published=True, review_status="revisado"),
            {"review_status": "pendente_revisao"},
            False,
        ),
    ),
)
def test_importador_markdown_e_fail_closed(existing, metadata, expected, monkeypatch, tmp_path):
    _write_markdown(tmp_path, {"slug": "documento", "title": "Documento", **metadata})
    session = _Session(existing)
    monkeypatch.setattr(importer, "SessionLocal", lambda: session)

    importer.import_directory(str(tmp_path))

    record = session.added[0] if existing is None else existing
    assert record.published is expected
    assert session.commits == 1


def test_todos_loaders_incrementais_aplicam_guarda_antes_do_commit():
    for front, config in reconciliation.FRONTS.items():
        if config["loader"] is None:
            function = importer.import_directory
        else:
            module = importlib.import_module(f"app.services.{config['loader']}")
            function = module.carregar
        source = inspect.getsource(function)
        assert "enforce_safe_publication" in source, front
        assert source.index("enforce_safe_publication") < source.rindex("db.commit"), front


def test_loaders_da_rota_admin_sao_os_mesmos_do_reconcile():
    from app.api import admin as admin_api

    for front, (_path, loader, _model) in admin_api.FRENTES.items():
        assert front in reconciliation.FRONTS
        assert reconciliation.FRONTS[front]["loader"] == loader


def test_modelos_persistem_metadados_editoriais():
    assert {"review_note", "fonte_producao"} <= set(
        ScientificStudy.__table__.columns.keys()
    )
    assert {"review_note", "fonte_producao"} <= set(
        PatientMaterial.__table__.columns.keys()
    )


def test_migration_falha_se_tabela_esperada_estiver_ausente(monkeypatch):
    class MissingInspector:
        def has_table(self, _table):
            return False

    monkeypatch.setattr(metadata_migration.op, "get_bind", lambda: object())
    monkeypatch.setattr(metadata_migration.sa, "inspect", lambda _bind: MissingInspector())

    with pytest.raises(RuntimeError, match="expected table is missing: scientific_studies"):
        metadata_migration.upgrade()


def test_migration_upgrade_e_idempotente_quando_colunas_ja_existem(monkeypatch):
    class ExistingInspector:
        def has_table(self, _table):
            return True

        def get_columns(self, _table):
            return [
                {"name": "review_note", "type": metadata_migration.sa.Text(),
                 "nullable": True, "comment": None},
                {"name": "fonte_producao", "type": metadata_migration.sa.Text(),
                 "nullable": True, "comment": None},
            ]

    additions = []
    monkeypatch.setattr(metadata_migration.op, "get_bind", lambda: object())
    monkeypatch.setattr(metadata_migration.sa, "inspect", lambda _bind: ExistingInspector())
    monkeypatch.setattr(
        metadata_migration.op,
        "add_column",
        lambda table, column: additions.append((table, column.name)),
    )

    metadata_migration.upgrade()

    assert additions == []


def test_migration_marca_como_proprias_as_colunas_que_cria(monkeypatch):
    class EmptyInspector:
        def has_table(self, _table):
            return True

        def get_columns(self, _table):
            return []

    additions = []
    monkeypatch.setattr(metadata_migration.op, "get_bind", lambda: object())
    monkeypatch.setattr(metadata_migration.sa, "inspect", lambda _bind: EmptyInspector())
    monkeypatch.setattr(
        metadata_migration.op,
        "add_column",
        lambda table, column: additions.append((table, column)),
    )

    metadata_migration.upgrade()

    assert len(additions) == len(metadata_migration.TABLES) * len(metadata_migration.COLUMNS)
    assert all(column.nullable is True for _table, column in additions)
    assert all(
        column.comment == metadata_migration.OWNER_COMMENT
        for _table, column in additions
    )


def test_migration_rejeita_coluna_preexistente_com_formato_incompativel(monkeypatch):
    class IncompatibleInspector:
        def has_table(self, _table):
            return True

        def get_columns(self, _table):
            return [
                {"name": "review_note", "type": metadata_migration.sa.String(255),
                 "nullable": True, "comment": None},
            ]

    monkeypatch.setattr(metadata_migration.op, "get_bind", lambda: object())
    monkeypatch.setattr(
        metadata_migration.sa, "inspect", lambda _bind: IncompatibleInspector()
    )

    with pytest.raises(RuntimeError, match="incompatible pre-existing column"):
        metadata_migration.upgrade()


def test_migration_downgrade_preserva_colunas_preexistentes_sem_marca(monkeypatch):
    class ExistingInspector:
        def has_table(self, _table):
            return True

        def get_columns(self, _table):
            return [
                {"name": "review_note", "type": metadata_migration.sa.Text(),
                 "nullable": True, "comment": None},
                {"name": "fonte_producao", "type": metadata_migration.sa.Text(),
                 "nullable": True, "comment": None},
            ]

    removals = []
    monkeypatch.setattr(metadata_migration.op, "get_bind", lambda: object())
    monkeypatch.setattr(
        metadata_migration.sa, "inspect", lambda _bind: ExistingInspector()
    )
    monkeypatch.setattr(
        metadata_migration.op,
        "drop_column",
        lambda table, column: removals.append((table, column)),
    )

    metadata_migration.downgrade()

    assert removals == []


def test_quarentena_false_despublica_sem_permitir_promocao_inversa():
    published = SimpleNamespace(review_status="revisado", published=True)
    enforce_safe_publication(published, {"published": False}, is_new=False)
    assert published.published is False

    unpublished = SimpleNamespace(review_status="revisado", published=False)
    enforce_safe_publication(unpublished, {"published": True}, is_new=False)
    assert unpublished.published is False

    approved = SimpleNamespace(review_status="revisado", published=True)
    enforce_safe_publication(approved, {"published": True}, is_new=False)
    assert approved.published is True


def test_manifesto_legado_sem_published_preserva_existente_sem_promover_novo():
    legacy_published = SimpleNamespace(review_status="revisado", published=True)
    enforce_safe_publication(legacy_published, {}, is_new=False)
    assert legacy_published.published is True

    legacy_unpublished = SimpleNamespace(review_status="revisado", published=False)
    enforce_safe_publication(legacy_unpublished, {}, is_new=False)
    assert legacy_unpublished.published is False

    new_record = SimpleNamespace(review_status="revisado", published=None)
    enforce_safe_publication(new_record, {}, is_new=True)
    assert new_record.published is False


def test_intencao_canonica_distingue_publicacao_quarentena_e_legado(tmp_path):
    manifest = tmp_path / "metadados.json"
    manifest.write_text(
        json.dumps(
            [
                {"slug": "publicar", "published": True},
                {"slug": "quarentena", "published": False},
                {"slug": "legado"},
            ]
        ),
        encoding="utf-8",
    )

    assert _canonical_publication_intents("teste", manifest) == {
        "publicar": True,
        "quarentena": False,
        "legado": None,
    }


def test_intencao_canonica_rejeita_published_nao_booleano(tmp_path):
    manifest = tmp_path / "metadados.json"
    manifest.write_text(
        json.dumps([{"slug": "invalido", "published": "false"}]),
        encoding="utf-8",
    )

    with pytest.raises(RuntimeError, match="published deve ser booleano"):
        _canonical_publication_intents("teste", manifest)


def test_reconcile_exige_true_revisao_e_aprovacao_sem_promover_legado(monkeypatch):
    engine = create_engine("sqlite://")
    _PublicationBase.metadata.create_all(engine)
    db = Session(engine)
    db.add_all(
        [
            _PublicationRecord(slug="publicar", review_status="revisado", published=False),
            _PublicationRecord(slug="quarentena", review_status="revisado", published=True),
            _PublicationRecord(slug="sem-aprovacao", review_status="revisado", published=True),
            _PublicationRecord(slug="legado-publico", review_status="revisado", published=True),
            _PublicationRecord(slug="legado-novo", review_status="revisado", published=False),
            _PublicationRecord(slug="sem-revisao", review_status="pendente", published=True),
            _PublicationRecord(slug="ausente", review_status="revisado", published=True),
        ]
    )
    db.commit()
    monkeypatch.setattr(
        reconciliation,
        "FRONTS",
        {"teste": {"model": _PublicationRecord}},
    )
    canonical = {
        "publicar",
        "quarentena",
        "sem-aprovacao",
        "legado-publico",
        "legado-novo",
        "sem-revisao",
    }

    result = reconciliation._synchronize_publication(
        db,
        {"teste": canonical},
        publish_reviewed=True,
        approved_slugs={"teste": {"publicar", "quarentena", "sem-revisao"}},
        publication_intents={
            "teste": {
                "publicar": True,
                "quarentena": False,
                "sem-aprovacao": True,
                "legado-publico": None,
                "legado-novo": None,
                "sem-revisao": True,
            }
        },
    )

    state = {
        row.slug: row.published
        for row in db.query(_PublicationRecord).order_by(_PublicationRecord.slug)
    }
    assert state == {
        "ausente": False,
        "legado-novo": False,
        "legado-publico": True,
        "publicar": True,
        "quarentena": False,
        "sem-aprovacao": False,
        "sem-revisao": False,
    }
    assert result == (
        {"teste": 1},
        {"teste": 1},
        {"teste": 1},
        {"teste": 2},
    )
    db.close()


def test_reconcile_dry_run_reverte_publicacao_e_despublicacoes(monkeypatch):
    engine = create_engine("sqlite://")
    _PublicationBase.metadata.create_all(engine)
    db = Session(engine)
    db.add_all(
        [
            _PublicationRecord(slug="publicar", review_status="revisado", published=False),
            _PublicationRecord(slug="quarentena", review_status="revisado", published=True),
            _PublicationRecord(slug="revogado", review_status="revisado", published=True),
            _PublicationRecord(slug="legado", review_status="revisado", published=True),
            _PublicationRecord(slug="sem-revisao", review_status="pendente", published=True),
            _PublicationRecord(slug="revisao-nula", review_status=None, published=True),
            _PublicationRecord(slug="ausente", review_status="revisado", published=True),
        ]
    )
    db.commit()
    monkeypatch.setattr(
        reconciliation,
        "FRONTS",
        {"teste": {"model": _PublicationRecord}},
    )

    result = reconciliation._synchronize_publication(
        db,
        {
            "teste": {
                "publicar",
                "quarentena",
                "revogado",
                "legado",
                "sem-revisao",
                "revisao-nula",
            }
        },
        publish_reviewed=True,
        approved_slugs={
            "teste": {"publicar", "quarentena", "sem-revisao", "revisao-nula"}
        },
        publication_intents={
            "teste": {
                "publicar": True,
                "quarentena": False,
                "revogado": True,
                "legado": None,
                "sem-revisao": True,
                "revisao-nula": True,
            }
        },
        dry_run=True,
    )

    assert result == (
        {"teste": 1},
        {"teste": 1},
        {"teste": 2},
        {"teste": 2},
    )
    state = {
        row.slug: row.published
        for row in db.query(_PublicationRecord).order_by(_PublicationRecord.slug)
    }
    assert state == {
        "ausente": True,
        "legado": True,
        "publicar": False,
        "quarentena": True,
        "revisao-nula": True,
        "revogado": True,
        "sem-revisao": True,
    }
    db.close()


def test_reconcile_fecha_publicacao_inelegivel_antes_de_loader_parcial(monkeypatch):
    events = []

    class PreflightSession:
        def commit(self):
            events.append("preflight:commit")

        def rollback(self):
            events.append("preflight:rollback")

        def close(self):
            events.append("preflight:close")

    monkeypatch.setattr(
        reconciliation,
        "FRONTS",
        {
            "primeira": {"path": "/primeira", "model": object, "loader": "primeira"},
            "segunda": {"path": "/segunda", "model": object, "loader": "segunda"},
        },
    )
    monkeypatch.setattr(
        reconciliation,
        "_prepare_front",
        lambda front, _config: (
            front,
            {f"{front}-atual"},
            {f"{front}-atual": False},
        ),
    )
    monkeypatch.setattr(
        reconciliation,
        "_load_editorial_approvals",
        lambda: {"primeira": set(), "segunda": set()},
    )
    monkeypatch.setattr(
        reconciliation,
        "_load_full_corpus_authorization",
        lambda canonical, _sources: (
            {front: set() for front in canonical},
            None,
        ),
    )
    monkeypatch.setattr(
        reconciliation,
        "_validate_editorial_approvals",
        lambda *_args, **_kwargs: {"primeira": 0, "segunda": 0},
    )
    monkeypatch.setattr(reconciliation, "SessionLocal", PreflightSession)

    def synchronize(_db, _canonical, **kwargs):
        events.append(f"sync:{kwargs['publish_reviewed']}:{kwargs['commit']}")
        zeros = {"primeira": 0, "segunda": 0}
        return zeros, zeros, zeros, zeros

    monkeypatch.setattr(reconciliation, "_synchronize_publication", synchronize)
    monkeypatch.setattr(
        reconciliation,
        "arquivar_entidades_de_conteudo_despublicado",
        lambda _db, *, commit: events.append(f"graph:{commit}"),
    )

    def load(front, _config, *, prepared):
        events.append(f"load:{front}")
        if front == "segunda":
            raise RuntimeError("falha tardia")
        return {}, prepared[1], prepared[2]

    monkeypatch.setattr(reconciliation, "_load_front", load)

    with pytest.raises(RuntimeError, match="falha tardia"):
        reconciliation.reconcile()

    assert events == [
        "sync:False:False",
        "graph:False",
        "preflight:commit",
        "preflight:close",
        "load:primeira",
        "load:segunda",
    ]


@pytest.mark.parametrize(
    "publication_request,detail",
    [
        (
            PublicacaoConteudo(frente="estudos", slugs=None),
            "informe os slugs aprovados explicitamente",
        ),
        (
            PublicacaoConteudo(
                frente="estudos",
                slugs=["estudo-loader-safe"],
                somente_revisados=False,
            ),
            "Conteúdo pendente não pode ser publicado",
        ),
    ],
)
def test_publicacao_admin_exige_selecao_e_revisao_explicitas(publication_request, detail):
    with pytest.raises(HTTPException, match=detail) as error:
        publicar_conteudo(publication_request, db=object(), user=SimpleNamespace(id=1))

    assert error.value.status_code == 422


def test_revisao_documento_bloqueia_publicacao_pendente():
    document = SimpleNamespace(
        slug="documento-pendente",
        published=False,
        review_status="pendente_revisao",
        source_tier="A",
        gaps=[],
    )
    session = _Session(document)

    with pytest.raises(HTTPException, match="Conteúdo pendente não pode ser publicado") as error:
        revisar(
            document.slug,
            DecisaoRevisao(publicar=True),
            db=session,
            user=SimpleNamespace(id=1),
        )

    assert error.value.status_code == 422
    assert document.published is False
    assert session.added == []
    assert session.commits == 0


def test_revisao_documento_publica_quando_revisado():
    document = SimpleNamespace(
        slug="documento-revisado",
        published=False,
        review_status="revisado",
        source_tier="A",
        gaps=[],
    )
    session = _Session(document)

    result = revisar(
        document.slug,
        DecisaoRevisao(publicar=True),
        db=session,
        user=SimpleNamespace(id=1),
    )

    assert result == {
        "slug": document.slug,
        "published": True,
        "review_status": "revisado",
    }
    assert document.published is True
    assert session.commits == 1


def test_revisao_documento_permite_despublicar_pendente():
    document = SimpleNamespace(
        slug="documento-pendente-publicado",
        published=True,
        review_status="pendente_revisao",
        source_tier="A",
        gaps=[],
    )
    session = _Session(document)

    result = revisar(
        document.slug,
        DecisaoRevisao(publicar=False),
        db=session,
        user=SimpleNamespace(id=1),
    )

    assert result == {
        "slug": document.slug,
        "published": False,
        "review_status": "pendente_revisao",
    }
    assert document.published is False
    assert session.commits == 1
