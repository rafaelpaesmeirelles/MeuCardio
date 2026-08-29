from types import SimpleNamespace

from app.services import guideline_clinical_update as clinical
from app.services import guideline_clinical_update_runtime as runtime


def guideline(slug="esc-2026-heart-failure"):
    return SimpleNamespace(
        slug=slug,
        ano=2026,
        published_at=None,
        url="https://doi.org/10.1000/test",
        doi="10.1000/test",
        org="ESC",
        titulo="Documento científico de teste",
        tema="Cardiologia",
    )


def substantive_summary():
    return " ".join([
        "A publicação compara recomendações contemporâneas para terapia antiarrítmica em diferentes cardiomiopatias.",
        "A seleção farmacológica deve ser orientada pelo fenótipo, função ventricular, substrato cicatricial e tipo de arritmia.",
        "Betabloqueadores e amiodarona aparecem como opções recorrentes em cardiopatia estrutural, enquanto fármacos classe I têm uso restrito.",
        "O objetivo predominante é reduzir sintomas, carga arrítmica e terapias de CDI, sem substituir estratificação de morte súbita, ablação ou terapia por dispositivo quando indicadas.",
        "A força da evidência varia entre os fenótipos e permanece mais limitada em cardiomiopatia dilatada e ventricular esquerda não dilatada.",
    ] * 3)


def test_plain_override_is_marked_and_removable_without_touching_other_updates():
    first = guideline("primeira")
    second = guideline("segunda")
    impact = {"override_pt": "Nova orientação confirmada.", "source_url": "https://doi.org/10.1000/test"}
    block_a = runtime._plain_override(first, impact)
    block_b = runtime._plain_override(second, impact)
    text = f"{block_b}\n\n{block_a}\n\nConteúdo histórico preservado."

    stripped = runtime._strip_plain_override(text, "primeira")

    assert "corvia-intelligence:primeira:plain:start" not in stripped
    assert "corvia-intelligence:segunda:plain:start" in stripped
    assert "Conteúdo histórico preservado." in stripped


def test_already_applied_is_scoped_by_guideline_and_item_type():
    target = SimpleNamespace(
        body_md="<!-- corvia-intelligence:g1:start -->\ntexto\n<!-- corvia-intelligence:g1:end -->",
        summary="",
        treatment_summary="",
        notes={},
        resumo="",
    )
    assert runtime._already_applied(target, "document", "g1") is True
    assert runtime._already_applied(target, "document", "g2") is False


def test_drug_update_is_idempotent_per_guideline():
    target = SimpleNamespace(notes={"corvia_intelligence_updates": [
        {"guideline_slug": "g1", "change": "mudança"}
    ]})
    assert runtime._already_applied(target, "drug", "g1") is True
    assert runtime._already_applied(target, "drug", "g2") is False


def test_only_trusted_scientific_hosts_are_accepted():
    allowed = ["doi.org", "escardio.org", "portal.cardiol.br"]
    assert clinical._trusted_url("https://doi.org/10.1093/example", allowed) is True
    assert clinical._trusted_url("https://www.escardio.org/guidelines/test", allowed) is True
    assert clinical._trusted_url("https://evil.example/escardio.org/guideline", allowed) is False


def test_analysis_schema_requires_explicit_source_support_flag():
    change = clinical.ANALYSIS_SCHEMA["properties"]["key_changes"]["items"]
    assert "explicit_in_source" in change["required"]
    assert "source_url" in change["required"]


def test_fallback_analysis_is_never_publishable():
    analysis = {
        "summary_pt": (
            "Identidade bibliográfica confirmada. Não foi possível recuperar o resumo ou texto integral "
            "nas fontes oficiais permitidas. Por isso não foi possível verificar recomendações específicas. "
        ) * 8,
        "source_urls_seen": ["https://www.escardio.org/guidelines/test"],
        "key_changes": [],
        "limitations": [
            "Não foi possível recuperar o texto integral.",
            "Não foi possível confirmar recomendações.",
        ],
    }
    assert runtime._analysis_publishable(guideline(), analysis) is False


def test_metadata_only_doi_or_pubmed_never_unlocks_publication():
    analysis = {
        "summary_pt": substantive_summary(),
        "source_urls_seen": [
            "https://doi.org/10.1000/test",
            "https://pubmed.ncbi.nlm.nih.gov/12345678/",
        ],
        "key_changes": [{"explicit_in_source": True}],
        "limitations": [],
    }
    assert runtime._analysis_publishable(guideline(), analysis) is False


def test_substantive_analysis_with_original_source_is_publishable():
    analysis = {
        "summary_pt": substantive_summary(),
        "source_urls_seen": ["https://www.escardio.org/guidelines/test"],
        "key_changes": [{"explicit_in_source": True}],
        "limitations": [],
        "original_source_accessed": True,
    }
    assert runtime._analysis_publishable(guideline(), analysis) is True


def test_springer_full_text_is_allowed_as_original_source():
    original = clinical.TRUSTED_DOMAINS
    try:
        runtime._install_source_domains()
        assert runtime._is_primary_content_url(
            guideline(),
            "https://link.springer.com/article/10.1007/s11886-026-02405-0",
        ) is True
    finally:
        clinical.TRUSTED_DOMAINS = original


def test_fallback_document_detector_catches_bibliographic_placeholder():
    doc = SimpleNamespace(
        summary=(
            "Identidade bibliográfica confirmada. Não foi possível recuperar o texto integral "
            "e não foi possível verificar recomendações específicas."
        ),
        body_md=(
            "Não foi possível recuperar o texto integral. Não foi possível verificar as recomendações. "
            "Não foi possível confirmar doses ou critérios."
        ),
    )
    assert runtime._document_looks_like_fallback(doc) is True


def test_runtime_install_replaces_core_helpers_with_source_original_guards(monkeypatch):
    original_plain = clinical._plain_override
    original_strip = clinical._strip_plain_override
    original_apply = clinical._apply_override
    original_summary = clinical._ensure_summary_document
    original_analyze = clinical._analyze_source
    original_domains = clinical.TRUSTED_DOMAINS

    runtime.install_runtime_guards()
    assert clinical._plain_override is runtime._plain_override
    assert clinical._strip_plain_override is runtime._strip_plain_override
    assert clinical._apply_override is runtime._guarded_apply_override
    assert clinical._ensure_summary_document is runtime._ensure_summary_published
    assert clinical._analyze_source is runtime._analyze_source_from_original
    assert "springer.com" in clinical.TRUSTED_DOMAINS

    monkeypatch.setattr(clinical, "_plain_override", original_plain)
    monkeypatch.setattr(clinical, "_strip_plain_override", original_strip)
    monkeypatch.setattr(clinical, "_apply_override", original_apply)
    monkeypatch.setattr(clinical, "_ensure_summary_document", original_summary)
    monkeypatch.setattr(clinical, "_analyze_source", original_analyze)
    monkeypatch.setattr(clinical, "TRUSTED_DOMAINS", original_domains)
