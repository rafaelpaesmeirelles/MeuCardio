"""Regressões focadas da busca e navegação do Guia de Doenças."""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("POSTGRES_HOST", "localhost")
os.environ.setdefault("POSTGRES_PORT", "5432")
os.environ.setdefault("POSTGRES_USER", "meucardio_test")
os.environ.setdefault("POSTGRES_PASSWORD", "test")
os.environ.setdefault("POSTGRES_DB", "meucardio_test")
os.environ.setdefault("STORAGE_ENCRYPTION_KEY", "MDEyMzQ1Njc4OTAxMjM0NTY3ODkwMTIzNDU2Nzg5MDE=")
os.environ.setdefault("JWT_SECRET", "chave-de-teste-nao-usar-em-producao")
os.environ.setdefault("ADMIN_EMAIL", "admin@teste.local")
os.environ.setdefault("ADMIN_PASSWORD", "admin-teste-123")

from sqlalchemy.dialects import postgresql

from app.api.specialty_guides import (
    _disease_search_predicate,
    _escaped_like_term,
    _normalize_search_term,
    list_disease_facets,
)


ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "frontend/src/pages/GuiaDoencas.tsx"
DETAIL = ROOT / "frontend/src/pages/GuiaDoenca.tsx"
LIBRARY_API = ROOT / "backend/app/api/library.py"


class _FakeQuery:
    def __init__(self):
        self.filters: list[object] = []

    def filter(self, *expressions):
        self.filters.extend(expressions)
        return self

    def group_by(self, *_):
        return self

    def order_by(self, *_):
        return self

    def all(self):
        return []


class _FakeSession:
    def __init__(self):
        self.queries: list[_FakeQuery] = []

    def query(self, *_):
        query = _FakeQuery()
        self.queries.append(query)
        return query


def _compiled(expression: object) -> str:
    return str(expression.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}))


def test_busca_normaliza_acentos_slug_e_wildcards_sem_extensao():
    assert _normalize_search_term("  Hipertensão-ARTERIAL  ") == "hipertensao arterial"
    assert _escaped_like_term(r"100%_HAS") == r"%100\% has%"

    sql = _compiled(_disease_search_predicate("hipertensão"))
    assert "unaccent" not in sql.casefold()
    assert "translate(" in sql.casefold()
    for field in (
        "slug", "name", "aliases", "tags", "epidemiology", "presentation",
        "diagnostic_approach", "differentials", "tests", "red_flags",
    ):
        assert f"specialty_diseases.{field}" in sql


def test_facetas_aplicam_filtro_cruzado_de_area_e_categoria():
    session = _FakeSession()
    result = list_disease_facets(
        area="geral",
        category="hipertensao",
        db=session,
    )

    assert result == {"areas": [], "categories": []}
    assert len(session.queries) == 2
    area_filters = " ".join(_compiled(item) for item in session.queries[0].filters)
    category_filters = " ".join(_compiled(item) for item in session.queries[1].filters)
    assert "specialty_diseases.category = 'hipertensao'" in area_filters
    assert "specialty_diseases.area = 'geral'" in category_filters


def test_catalogo_sincroniza_url_e_descarta_filtros_invisiveis():
    source = CATALOG.read_text(encoding="utf-8")

    assert 'const serializedParams = params.toString()' in source
    assert 'setQ(params.get("q") || "")' in source
    assert 'setParams(nextParams, { replace: true })' in source
    assert 'nextParams.delete("area")' in source
    assert 'nextParams.delete("category")' in source
    assert 'nextParams.delete("cyanosis")' in source
    assert '`/specialty-guides/disease-facets${search ? `?${search}` : ""}`' in source
    assert 'onChange={(event) => updateAreaFilter(event.target.value)}' in source


def test_detalhe_preserva_estado_trivalente_e_exibe_mensagens_e_rotulos():
    source = DETAIL.read_text(encoding="utf-8")

    assert 'event.target.value === "" ? undefined : event.target.value === "true"' in source
    assert "if (value === undefined) delete next[question.id]" in source
    assert 'setAssessment(null);\n    setContext(next);' in source
    assert 'title="Orientações do assistente" items={assessment.messages}' in source
    assert 'geral: "Cardiologia do adulto"' in source
    assert "{labelArea(disease.area)} · {labelCategory(disease.category)}" in source


def test_catalogo_da_biblioteca_aponta_para_rota_canonica():
    source = LIBRARY_API.read_text(encoding="utf-8")

    assert '("doencas_especializadas", "Guia de Doenças", "/doencas", SpecialtyDisease)' in source
    assert '"/guias-doencas", SpecialtyDisease' not in source
