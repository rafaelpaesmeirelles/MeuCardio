"""Pure selection contracts; clinical indication is never inferred from a tag."""
from types import SimpleNamespace

import pytest

from app.services import search_relevance as relevance
from app.services.catalog_search import DISEASE_SQL, PAGE_SQL, SQL


def test_registered_plural_aliases_match_whole_normalized_tags_only():
    disease = SimpleNamespace(name="Estenose mitral", slug="estenose-mitral",
                              aliases=["Estenoses mitrais", "Mitral stenosis", "EM reumática"])
    phrases = relevance.disease_identity_phrases(disease)
    assert {"estenose mitral", "estenoses mitrais", "mitral stenosis", "em reumatica"} == set(phrases)
    assert "mitral" not in phrases and "em" not in phrases
    sql = str(relevance.REVIEWED_TAG_MATCHES_SQL)
    assert sql.count("review_status = 'revisado'") == len(relevance.TAGGED_FRONTS)
    assert sql.count("published = true") == len(relevance.TAGGED_FRONTS)
    assert "= ANY" in sql and "LIKE" not in sql


def test_rag_keeps_original_bind_contract_and_global_order_has_no_front_round_robin():
    # SQLAlchemy's internal parser records a phantom "spac" for POSIX
    # [[:space:]], already present in the originals catalogue. The compiler
    # preserves that regex literally; only compiled params are actual binds.
    assert set(SQL.compile().params) == {"q", "q_like", "frente", "limit", "offset",
                                        "internal_override_pattern", "internal_marker_pattern"}
    assert "PARTITION BY frente" not in str(DISEASE_SQL)
    for query in (DISEASE_SQL, PAGE_SQL):
        assert "AS relevance_order" in str(query)
        assert query._bindparams["candidate_metadata"].value == "{}"
        assert query._bindparams["calculator_candidates"].value == "[]"


@pytest.mark.parametrize("role", ["direct", "conditional", "comparison", "mention"])
def test_curated_roles_keep_conditions_and_sources_without_synthetic_results(monkeypatch, role):
    disease = SimpleNamespace(name="Estenose mitral", slug="estenose-mitral",
                              aliases=[], published=True)
    context = "Aplicável apenas quando há fibrilação atrial; não estender a todas as valvopatias."
    monkeypatch.setattr(relevance, "clinical_profiles", lambda: {disease.slug: {"items": [{
        "frente": "medicamento", "slug": "varfarina", "role": role, "priority": 100,
        "context": context, "relation_type": "associated_with",
        "evidence_sources": ["https://doi.org/10.1056/NEJMoa2209051"],
    }]}})
    db = SimpleNamespace(execute=lambda *_: SimpleNamespace(mappings=lambda: []))
    metadata = relevance.disease_search_metadata(db, disease, {})
    item = metadata["medicamento:varfarina"]
    assert item["clinical_role"] == role and item["clinical_context"] == context
    assert item["relation_type"] == "associated_with" and item["priority"] == 100
    assert item["match_reasons"][-1]["source"] == "clinical_profile"
    assert item["match_reasons"][-1]["evidence_sources"]
    assert "title" not in item  # final catalogue must supply a published row
    disease.published = False
    assert relevance.disease_search_metadata(db, disease, {}) == {}
