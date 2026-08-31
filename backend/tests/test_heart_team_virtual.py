from __future__ import annotations

import inspect
import threading
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.api.heart_team import _dump_opinion, _objective_extract
from app.models.heart_team import HeartTeamOpinion, HeartTeamPatientRecord, _IMMUTABLE, _immutable
from app.services import heart_team as service
from app.services.heart_team_agents import AGENTS, independent_round_inputs, selected_agent_keys
from app.services.heart_team_evidence import (
    DOI_RE, PMID_RE, ReopenedPublication, _title_matches, exact_facts_supported,
    reopen_publication, sanitize_registry_for_persistence, source_catalog,
    structured_facts, validate_claim_support, verify_source_rows,
)
from app.services.heart_team_safety import (
    deterministic_disagreements, emergency_screen, mandatory_opinion_usable,
    normalize_opinion, validate_deidentified,
)


def supported_source(text="Furosemida 40 mg reduziu congestão em N=100; mortalidade não foi avaliada."):
    return {"s1": {"reviewed": True, "text": text}}


def test_feature_flag_default_is_false():
    from app.core.config import Settings
    assert Settings(_env_file=None).heart_team_enabled is False


def test_agent_registry_has_all_mandatory_specialties():
    assert set(AGENTS) == {"coordinator", "heart_failure", "electrophysiology", "imaging", "critical_care", "pharmacology", "evidence", "red_team"}
    assert all(AGENTS[key].mandatory for key in ("coordinator", "evidence", "red_team"))


def test_selected_agents_always_include_evidence_and_red_team():
    assert selected_agent_keys(["imaging"]) == ["imaging", "evidence", "red_team"]


def test_first_round_inputs_are_independent_deep_copies():
    original = {"case": {"symptoms": ["dispneia"]}}
    copies = independent_round_inputs(original, ["imaging", "pharmacology"])
    copies["imaging"]["case"]["symptoms"].append("dor")
    assert copies["pharmacology"] == original
    assert copies["imaging"] is not copies["pharmacology"]


def test_doi_and_pmid_formats_fail_closed():
    assert DOI_RE.fullmatch("10.1000/test.1")
    assert not DOI_RE.fullmatch("doi inventado")
    assert PMID_RE.fullmatch("12345678")
    assert not PMID_RE.fullmatch("PMID-123")


def test_doi_and_pmid_must_cross_same_title():
    assert _title_matches("Heart failure treatment trial", "Heart failure treatment trial: results")
    assert not _title_matches("Heart failure treatment trial", "Unrelated oncology cohort")


def test_external_registry_mismatch_marks_source_unusable():
    rows = [{"id": "s", "title": "Heart trial", "doi": "10.1000/x", "pmid": "123", "reviewed": True}]
    checked = verify_source_rows(rows, opener=lambda **_: None)
    assert checked[0]["reviewed"] is False
    assert "mismatch" in checked[0]["validation"]


def test_external_abstract_overrides_incorrect_local_population_results_and_numbers():
    rows = [{"id": "s", "title": "Heart trial", "doi": "10.1000/x", "pmid": "123", "date": "2024", "text": "Em idosos, N=5000: mortalidade reduziu 99% com 80 mg. Classe I, nível A.", "reviewed": True}]
    publication = ReopenedPublication(title="Heart trial", doi="10.1000/x", pmid="123", date="2023", population="adultos", results="Heart trial. Em adultos, N=100: hospitalização sem diferença com 40 mg.", url="https://doi.org/10.1000/x")
    checked = verify_source_rows(rows, opener=lambda **_: publication)[0]
    assert checked["reviewed"] is False
    assert checked["clinical_claims_authorized"] is False
    assert {"quantities", "sample_sizes", "directions", "classes", "levels", "populations", "outcomes", "date"} <= set(checked["clinical_fact_mismatches"])
    ok, _ = validate_claim_support(rows[0]["text"], ["s"], {"s": checked})
    assert not ok


def test_external_abstract_exact_facts_authorize_claim_against_external_not_local():
    text = "Em adultos, N=100: hospitalização sem diferença com 40 mg em 2023."
    row = {"id": "s", "title": "Heart trial", "doi": "10.1000/x", "pmid": "123", "date": "2023", "text": text, "reviewed": True}
    publication = ReopenedPublication(title="Heart trial", doi="10.1000/x", pmid="123", date="2023", population="adultos", results=f"Heart trial. {text}", url=None)
    checked = verify_source_rows([row], opener=lambda **_: publication)[0]
    assert checked["reviewed"] is True and checked["clinical_claims_authorized"] is True
    assert validate_claim_support("Em adultos, N=100: hospitalização sem diferença com 40 mg em 2023.", ["s"], {"s": checked})[0]


def test_doi_and_pmid_must_resolve_to_same_publication_identifier(monkeypatch):
    import json
    class Response:
        def __init__(self, *, payload=None, content=b""): self._payload = payload; self.content = content
        def raise_for_status(self): pass
        def json(self): return self._payload
    crossref = {"message": {"title": ["Heart Trial"], "DOI": "10.1000/right", "published": {"date-parts": [[2023]]}, "abstract": "Adults N=100 mortality."}}
    xml = b'''<PubmedArticleSet><PubmedArticle><MedlineCitation><PMID>123</PMID><Article><ArticleTitle>Heart Trial</ArticleTitle><Abstract><AbstractText>Adults N=100 mortality.</AbstractText></Abstract><Journal><JournalIssue><PubDate><Year>2023</Year></PubDate></JournalIssue></Journal></Article></MedlineCitation><PubmedData><ArticleIdList><ArticleId IdType="doi">10.1000/different</ArticleId></ArticleIdList></PubmedData></PubmedArticle></PubmedArticleSet>'''
    def fake_get(url, **_kwargs): return Response(payload=crossref) if "crossref" in url else Response(content=xml)
    monkeypatch.setattr("app.services.heart_team_evidence.httpx.get", fake_get)
    assert reopen_publication(title="Heart Trial", doi="10.1000/right", pmid="123") is None


def test_structured_facts_extract_dose_percent_n_date_class_level():
    facts = structured_facts("Em 2026, N=100 recebeu 80 mg; 50%. Classe II, nível B.")
    assert {"2026"} <= facts["dates"]
    assert "n=100" in facts["sample_sizes"]
    assert {"80mg", "50%"} <= facts["quantities"]
    assert facts["classes"] and facts["levels"]


def test_abstract_100_no_mortality_blocks_claim_5000_99_percent():
    ok, reason = validate_claim_support("Em N=5000, mortalidade caiu 99%", ["s1"], supported_source("Estudo N=100 avaliou congestão; mortalidade não foi avaliada."))
    assert not ok
    assert reason


def test_furosemide_80mg_50_percent_blocked_by_40mg_source():
    ok, reason = validate_claim_support("Furosemida 80 mg reduziu mortalidade em 50%", ["s1"], supported_source())
    assert not ok
    assert "quantities" in reason or "não encontrada" in reason


def test_exact_supported_facts_pass():
    ok, reason = exact_facts_supported("Furosemida 40 mg em N=100", supported_source()["s1"]["text"])
    assert ok and reason is None


def test_population_outcome_and_drug_class_must_match_exact_source():
    ok, reason = exact_facts_supported(
        "Em idosos com doença renal, anticoagulante reduziu AVC",
        "Em adultos com fibrilação atrial, anticoagulante reduziu sangramento",
    )
    assert not ok
    assert reason in {"populations não coincide exatamente com a fonte", "outcomes não coincide exatamente com a fonte"}


def test_source_id_alone_never_authorizes_unrelated_claim():
    ok, _ = validate_claim_support("Apixabana previne AVC", ["s1"], supported_source())
    assert not ok


def test_relevance_ranking_considers_records_beyond_requested_limit():
    irrelevant = [SimpleNamespace(id=i, slug=f"generic-{i}", theme="Geral", statement="Tema genérico", summary="sem relação", reference="ref", guideline_title=f"Genérico {i}", doi=None, year=2020, society="X", source_url=None) for i in range(30)]
    relevant = SimpleNamespace(id=999, slug="amiloidose", theme="Amiloidose", statement="Cardiomiopatia amiloide com cintilografia", summary="amiloidose cardíaca", reference="ref", guideline_title="Amiloidose cardíaca", doi=None, year=2025, society="ESC", source_url=None)
    class Query:
        def __init__(self, rows): self.rows = rows
        def filter(self, *_): return self
        def all(self): return self.rows
    class DB:
        def query(self, model):
            return Query(irrelevant + [relevant] if getattr(model, "__name__", "") == "EvidenceRecord" else [])
    rows = source_catalog(DB(), query="amiloidose cardíaca cintilografia", limit=1)
    assert rows[0]["id"] == "evidence:999"


def test_unreviewed_or_missing_source_is_blocked():
    ok, reason = validate_claim_support("Furosemida 40 mg", ["x"], {"x": {"reviewed": False, "text": "Furosemida 40 mg"}})
    assert not ok and "revisada" in reason


def test_nonnumeric_clinical_assertion_without_source_is_blocked():
    normalized, blocks = normalize_opinion({"summary": "Miocardiopatia hipertrófica é o diagnóstico", "claims": [{"statement": "Miocardiopatia hipertrófica é o diagnóstico", "source_ids": []}], "confidence": "high"}, {})
    assert normalized["summary"] == "evidência insuficiente"
    assert normalized["claims"][0]["validation"] == "blocked"
    assert blocks


def test_supported_claim_is_preserved():
    registry = {"s1": {"reviewed": True, "text": "Congestão clínica melhorou com furosemida 40 mg."}}
    normalized, blocks = normalize_opinion({"summary": "Congestão clínica melhorou com furosemida 40 mg.", "claims": [{"statement": "Congestão clínica melhorou com furosemida 40 mg", "source_ids": ["s1"], "position": "support"}], "confidence": "moderate"}, registry)
    assert not blocks
    assert normalized["claims"][0]["validation"] == "verified"


def test_one_verified_claim_cannot_authorize_unrelated_narrative_sections():
    registry = {"s1": {"reviewed": True, "text": "Congestão melhorou com furosemida 40 mg."}}
    normalized, blocks = normalize_opinion({"summary": "Congestão melhorou com furosemida 40 mg", "therapeutic_options": ["Amiodarona 400 mg reduz mortalidade 80%"], "claims": [{"statement": "Congestão melhorou com furosemida 40 mg", "source_ids": ["s1"], "position": "support"}], "confidence": "moderate"}, registry)
    assert normalized["therapeutic_options"] == ["evidência insuficiente"]
    assert blocks


def test_external_abstract_never_persisted():
    cleaned = sanitize_registry_for_persistence([{"id": "s", "external_abstract": "copyright", "external_text": "raw", "title": "T"}])
    assert cleaned == [{"id": "s", "title": "T"}]


@pytest.mark.parametrize("value,kind", [
    ("CPF 123.456.789-00", "cpf"), ("email a@b.com", "email"), ("fone 11999998888", "telefone"),
    ("Paciente: Maria da Silva", "nome"), ("CNS 123456789012345", "cns"),
    ("RG: 12.345.678-9", "rg"), ("Data de nascimento: 01/02/1980", "nascimento"),
    ("Endereço: Rua das Flores, 10", "endereco"), ("Prontuário: ABC-1234", "prontuario"),
])
def test_pii_detection(value, kind):
    assert kind in validate_deidentified({"case_text": value})


def test_emergency_screen_flags_but_does_not_diagnose():
    risk = emergency_screen({"symptoms": ["dor torácica em curso", "instável"]})
    assert risk["level"] == "emergency_possible"
    assert "protocolo" in risk["notice"]


def test_mandatory_agent_insufficient_is_unusable():
    assert not mandatory_opinion_usable("evidence", {"summary": "evidência insuficiente", "confidence": "insufficient", "source_ids": []})
    assert not mandatory_opinion_usable("red_team", {"summary": "x", "confidence": "high", "source_ids": ["s"], "safety_blocks": ["bad"]})


def test_opposing_agents_always_create_disagreement():
    opinions = [
        {"agent_key": "imaging", "content": {"claims": [{"statement": "Realizar ressonância", "position": "support"}]}},
        {"agent_key": "critical_care", "content": {"claims": [{"statement": "Realizar ressonância", "position": "oppose"}]}},
    ]
    result = deterministic_disagreements(opinions)
    assert len(result) == 1
    assert {p["position"] for p in result[0]["positions"]} == {"support", "oppose"}


def test_dump_opinion_exposes_round_name_and_legacy_alias():
    row = SimpleNamespace(id=1, agent_key="imaging", round_name="independent", content={}, source_ids=[], confidence="low", model_name="m", created_at=None)
    assert _dump_opinion(row)["round_name"] == _dump_opinion(row)["round"]


def test_pdf_objective_extraction_uses_installed_pymupdf():
    import fitz
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), "ECG: ritmo sinusal 70 bpm")
    payload = document.tobytes()
    document.close()
    extracted = _objective_extract(payload, "application/pdf")
    assert extracted["type"] == "pdf_text"
    assert extracted["pages"] == 1
    assert "ritmo sinusal" in extracted["text"]


def test_image_attachment_is_never_silently_ignored_without_report(monkeypatch):
    monkeypatch.setattr(service.settings, "ai_clinical_multimodal_enabled", False)
    case = SimpleNamespace(id=1, owner_id=3, input_data={})
    descriptor = {"id": 1, "kind": "upload", "reference_id": None, "media_type": "image/png", "size_bytes": 100, "sha256": "a", "objective_extract": {"type": "image", "width": 100, "height": 100}}
    with pytest.raises(service.HeartTeamSafetyError, match="não pode ser ignorado"):
        service._enrich_visual_attachments(SimpleNamespace(), case, [descriptor], object())


def test_multimodal_provider_receives_visual_bytes_and_enriches_agent_context(monkeypatch):
    row = SimpleNamespace(id=1, case_id=8, owner_id=3, storage_key="file.bin", kind="upload", reference_id=None, objective_extract={})
    class Query:
        def filter(self, *_): return self
        def first(self): return row
    class DB:
        def query(self, _): return Query()
        def commit(self): pass
    captured = {}
    class Provider:
        def analisar_arquivo_clinico(self, **kwargs):
            captured.update(kwargs)
            return SimpleNamespace(texto='{"image_quality":"adequate","objective_observations":["ritmo regular visível"],"unreadable_elements":[],"limitations":[]}', tokens_entrada=10, tokens_saida=20, modelo="vision-clinical")
    monkeypatch.setattr(service.settings, "ai_clinical_multimodal_enabled", True)
    monkeypatch.setattr(service.settings, "ai_clinical_data_controls_approved", True)
    monkeypatch.setattr(service, "ler", lambda *_args, **_kwargs: b"sanitized-image-bytes")
    monkeypatch.setattr(service, "_reserve_call", lambda *_args, **_kwargs: SimpleNamespace(reserved_micros=100, agent_key="multimodal_extractor", phase="attachment_extract"))
    monkeypatch.setattr(service, "_reconcile_call", lambda *_args, **_kwargs: None)
    descriptor = {"id": 1, "kind": "upload", "reference_id": None, "media_type": "image/png", "size_bytes": 16, "sha256": "a", "objective_extract": {"type": "image"}}
    enriched = service._enrich_visual_attachments(DB(), SimpleNamespace(id=8, owner_id=3, reserved_cost_micros=0), [descriptor], Provider())
    assert captured["conteudo"] == b"sanitized-image-bytes"
    assert enriched[0]["objective_extract"]["multimodal_extract"]["objective_observations"] == ["ritmo regular visível"]
    # This exact descriptor is included in the context passed to independent agents.
    isolated = independent_round_inputs({"attachments": enriched}, ["imaging"])
    assert "ritmo regular" in str(isolated["imaging"]["attachments"])


def test_patient_context_is_actually_merged_into_snapshot():
    merged = service._merge_patient_context({"case_text": "Caso livre"}, "CONTEXTO LONGITUDINAL\n- hipertensão")
    snapshot = service.build_snapshot(merged)
    assert "hipertensão" in snapshot["case_text"]
    assert snapshot["patient_context_imported"] is True


def test_patient_import_denies_cross_tenant_profile():
    class Query:
        def filter(self, *_): return self
        def first(self): return None
    class DB:
        def query(self, _): return Query()
    with pytest.raises(service.HeartTeamSafetyError, match="este assinante"):
        service._import_patient_context(DB(), owner_id=9, patient_id=77, authorized=True)


def test_clinical_file_sanitizer_blocks_direct_identifier_before_storage(monkeypatch):
    import io
    from PIL import Image
    from app.services.ia import clinical_file_sanitizer as sanitizer
    monkeypatch.setattr(sanitizer, "_ocr", lambda _data: "Paciente: Maria da Silva CPF 123.456.789-09")
    image = io.BytesIO(); Image.new("RGB", (32, 32), "white").save(image, format="PNG")
    with pytest.raises(sanitizer.UnsafeClinicalFile, match="identificador"):
        sanitizer.sanitize_clinical_file(image.getvalue(), "image/png")


def test_clinical_file_sanitizer_blocks_pdf_text_identifier_before_provider():
    import fitz
    from app.services.ia.clinical_file_sanitizer import UnsafeClinicalFile, sanitize_clinical_file
    document = fitz.open(); page = document.new_page(); page.insert_text((72, 72), "Paciente: Maria da Silva CPF: 123.456.789-09")
    payload = document.tobytes(); document.close()
    with pytest.raises(UnsafeClinicalFile, match="identificador"):
        sanitize_clinical_file(payload, "application/pdf")


def test_canonical_file_sanitizer_detects_labeled_name_with_particle():
    from app.services.ia.clinical_file_sanitizer import contains_identifier
    assert contains_identifier("Paciente: Maria da Silva")


def test_heart_upload_persists_only_sanitized_bytes_contract():
    from app.api.heart_team import upload_attachments
    source = inspect.getsource(upload_attachments)
    assert "sanitize_clinical_file(source, media_type)" in source
    assert "guardar(sanitized" in source
    assert "source_sha256" in source and "sanitized_sha256" in source
    assert "guardar(source" not in source


def test_heart_team_rbac_requires_approved_medical_profile_and_crm():
    physician = SimpleNamespace(is_active=True, investidor=False, role="medico", status="aprovado", profession="Médico cardiologista", council_name="CRM", council_number="123", council_state="SP", crm=None)
    investor = SimpleNamespace(**{**physician.__dict__, "investidor": True})
    reader = SimpleNamespace(**{**physician.__dict__, "role": "leitor"})
    admin_without_crm = SimpleNamespace(**{**physician.__dict__, "role": "admin", "council_number": None, "crm": None})
    assert service.is_heart_team_physician(physician)
    assert not service.is_heart_team_physician(investor)
    assert not service.is_heart_team_physician(reader)
    assert not service.is_heart_team_physician(admin_without_crm)


def test_patient_provenance_is_append_only_and_has_no_clinical_recommendation_fields():
    assert HeartTeamPatientRecord in _IMMUTABLE
    columns = set(HeartTeamPatientRecord.__table__.columns.keys())
    assert {"case_id", "patient_profile_id", "reviewer_id", "decision", "final_hash", "provenance"} <= columns
    assert not ({"diagnosis", "treatment", "prescription", "recommendation"} & columns)
    from app.api.heart_team import final_review
    assert "HeartTeamPatientRecord" in inspect.getsource(final_review)
    timeline_source = (Path(__file__).parents[1] / "app/api/patient_timeline.py").read_text()
    assert "HeartTeamPatientRecord.owner_id == user.id" in timeline_source
    assert "apoio_ia_heart_team" in timeline_source


def test_draft_patch_cannot_forge_patient_provenance_or_attachments():
    from app.api.heart_team import patch_case, final_review
    patch_source = inspect.getsource(patch_case)
    for protected in ("source_patient_id", "source_patient_authorized", "patient_context_imported", "attachments"):
        assert protected in patch_source
    final_source = inspect.getsource(final_review)
    assert "PatientProfile.owner_id == user.id" in final_source
    assert "não pertence a este assinante" in final_source


def test_cache_key_changes_for_attachment_hash_type_and_extract():
    case = SimpleNamespace(owner_id=1, selected_agents=["imaging"])
    snapshot = {"age": 60}
    base = {"sha256": "a", "media_type": "image/png", "size_bytes": 1, "kind": "upload", "reference_id": None, "objective_extract": {"width": 1}}
    key = service._cache_key(case, snapshot, [base])
    assert key != service._cache_key(case, snapshot, [{**base, "sha256": "b"}])
    assert key != service._cache_key(case, snapshot, [{**base, "media_type": "application/pdf"}])
    assert key != service._cache_key(case, snapshot, [{**base, "objective_extract": {"width": 2}}])


def test_cache_key_changes_for_pipeline_or_model(monkeypatch):
    case = SimpleNamespace(owner_id=1, selected_agents=["imaging"])
    first = service._cache_key(case, {}, [])
    monkeypatch.setattr(service.settings, "heart_team_clinical_model", "other")
    assert first != service._cache_key(case, {}, [])


def test_cache_key_is_tenant_scoped():
    first = service._cache_key(SimpleNamespace(owner_id=1, selected_agents=["imaging"]), {"age": 60}, [])
    second = service._cache_key(SimpleNamespace(owner_id=2, selected_agents=["imaging"]), {"age": 60}, [])
    assert first != second


def test_tudo_com_tudo_uses_only_real_reviewed_graph_links(monkeypatch):
    graph = {"grupos": [{"tipo": "medicamento", "itens": [
        {"slug": "sacubitril-valsartana", "titulo": "Sacubitril/valsartana", "rota": "/medicamentos?slug=sacubitril-valsartana", "relation_type": "recommended_by", "review_status": "revisado", "confidence": "explicit", "provenance_type": "editorial"},
        {"slug": "filler", "titulo": "Não revisado", "rota": "/medicamentos?slug=filler", "relation_type": "same_theme", "review_status": "pendente_revisao", "confidence": "derived", "provenance_type": "structured_metadata"},
    ]}]}
    monkeypatch.setattr(service, "relacionados_de", lambda *_args, **_kwargs: graph)
    related = service.resolve_related_content(object(), [{"id": "evidence:1", "entity_type": "evidencia", "slug": "hf-guideline", "route": "/evidencias/hf-guideline", "theme": "Insuficiência Cardíaca", "title": "Diretriz IC", "reviewed": True}])
    assert any(item["href"] == "/medicamentos?slug=sacubitril-valsartana" for item in related)
    assert any(item["href"].startswith("/trilhas/timeline?tema=") for item in related)
    assert not any(item.get("slug") == "filler" for item in related)


def test_tudo_com_tudo_returns_empty_without_cited_or_reviewed_relation(monkeypatch):
    monkeypatch.setattr(service, "relacionados_de", lambda *_args, **_kwargs: None)
    assert service.resolve_related_content(object(), []) == []
    assert service.resolve_related_content(object(), [{"id": "x", "entity_type": "evidencia", "slug": "x", "route": "/evidencias/x", "reviewed": False}]) == []


def test_immutable_records_raise_on_mutation_hook():
    with pytest.raises(ValueError, match="imutáveis"):
        _immutable(None, None, None)


def test_provider_contract_accepts_explicit_heart_team_output_cap():
    from app.services.ia.provedor import ProvedorAnthropic, ProvedorIA, ProvedorOpenAI
    for cls in (ProvedorIA, ProvedorOpenAI, ProvedorAnthropic):
        assert "max_output_tokens" in inspect.signature(cls.responder).parameters


def test_openai_heart_team_model_and_output_cap_are_applied():
    from app.services.ia.provedor import ProvedorOpenAI
    captured = {}
    class Completions:
        def create(self, **kwargs):
            captured.update(kwargs)
            return SimpleNamespace(usage=SimpleNamespace(prompt_tokens=1, completion_tokens=2), choices=[SimpleNamespace(message=SimpleNamespace(content="{}"), finish_reason="stop")])
    provider = object.__new__(ProvedorOpenAI)
    provider._modelo = "gpt-4o-mini"
    provider._cliente = SimpleNamespace(chat=SimpleNamespace(completions=Completions()))
    provider.responder("system", [{"role": "user", "content": "x"}], modelo="gpt-5.6-sol", max_output_tokens=777)
    assert captured["model"] == "gpt-5.6-sol"
    assert captured["max_completion_tokens"] == 777


def test_pipeline_has_no_simulated_provider_fallback():
    source = inspect.getsource(service.HeartTeamOrchestrator.analyze)
    assert "simulad" not in source.lower()
    assert "awaiting_review" in source
    assert "completed" not in source


def test_cache_purge_is_independent_command_and_admin_endpoint():
    root = Path(__file__).parents[1]
    assert (root / "app/commands/purge_expired_heart_team_cache.py").exists()
    api_source = (root / "app/api/heart_team.py").read_text()
    assert '"/retention/purge"' in api_source


def test_http_analysis_is_durable_202_and_worker_is_wired():
    from app.api.heart_team import analyze
    api_source = inspect.getsource(analyze)
    worker_source = (Path(__file__).parents[1] / "app/services/whatsapp_heart_team_worker.py").read_text()
    assert "enqueue_analysis_job" in api_source
    assert "analyze_case_by_id" not in api_source
    assert getattr(analyze, "__name__", "") == "analyze"
    assert "process_pending_analysis_jobs" in worker_source
    root = Path(__file__).parents[2]
    assert "whatsapp-heart-team-worker:" in (root / "docker-compose.prod.yml").read_text()
    assert 'app.services.whatsapp_heart_team_worker' in (root / "docker-compose.prod.yml").read_text()


def test_enqueue_analysis_is_idempotent_for_same_case(monkeypatch):
    existing = SimpleNamespace(id=91, case_id=7, owner_id=3, actor_id=3, status="queued")
    case = SimpleNamespace(id=7, owner_id=3, status="queued")
    class Query:
        def __init__(self, model): self.model = model
        def filter(self, *_): return self
        def with_for_update(self): return self
        def first(self):
            return case if getattr(self.model, "__name__", "") == "HeartTeamCase" else existing
    class DB:
        def query(self, model): return Query(model)
        def add(self, _): raise AssertionError("idempotent enqueue must not add another job")
    monkeypatch.setattr(service, "enabled", lambda: None)
    monkeypatch.setattr(service, "ensure_heart_team_physician", lambda *_: None)
    job = service.enqueue_analysis_job(DB(), case_id=7, owner_id=3, actor_id=3, confirm_deidentified=True, confirm_medical_review=True)
    assert job is existing


def test_worker_recovery_is_fail_closed_after_partial_analysis():
    source = inspect.getsource(service.process_pending_analysis_jobs)
    assert 'case.status == "queued"' in source
    assert '"lease_recovered_pre_analysis"' in source
    assert '"lease_lost_partial_quarantined"' in source
    assert "case.result = {}" in source
    job_source = inspect.getsource(service.process_analysis_job)
    assert 'failed_case.status = "failed"' in job_source
    assert "failed_case.result = {}" in job_source


def test_expired_cache_purge_deletes_without_running_analysis():
    class Query:
        def filter(self, *_): return self
        def delete(self, **_): return 3
    class DB:
        def __init__(self): self.committed = False
        def query(self, _): return Query()
        def commit(self): self.committed = True
    db = DB()
    assert service.purge_expired_cache(db) == 3
    assert db.committed


def test_migration_is_reversible_and_db_immutable():
    migration = Path(__file__).parents[1] / "migrations/versions/f87h20260831_heart_team_virtual.py"
    source = migration.read_text()
    assert 'down_revision = "f86d20260829"' in source
    assert "heart_team_reject_mutation" in source
    assert "def downgrade" in source


def test_cost_reservation_uses_postgres_advisory_lock():
    source = inspect.getsource(service._reserve_call)
    assert "pg_advisory_xact_lock" in source
    assert "monthly_cost_ceiling" in source


def test_concurrent_cost_reservation_allows_only_one_under_shared_ceiling(monkeypatch):
    shared_lock = threading.Lock()
    cases = [SimpleNamespace(id=1, owner_id=7, reserved_cost_micros=0), SimpleNamespace(id=2, owner_id=7, reserved_cost_micros=0)]

    class Query:
        def __init__(self, expression): self.expression = str(expression)
        def filter(self, *_args): return self
        def scalar(self):
            if "heart_team_cost_ledger" in self.expression: return 0
            return sum(case.reserved_cost_micros for case in cases)

    class LockedDB:
        bind = SimpleNamespace(dialect=SimpleNamespace(name="postgresql"))
        def __init__(self): self.locked = False
        def execute(self, *_args, **_kwargs): shared_lock.acquire(); self.locked = True
        def query(self, expression): return Query(expression)
        def add(self, _row): pass
        def commit(self):
            if self.locked: self.locked = False; shared_lock.release()
        def refresh(self, _row): pass

    reserve = service._estimate_cost_micros(1, 2200)
    monkeypatch.setattr(service.settings, "heart_team_monthly_cost_ceiling_micros", reserve + 1)
    outcomes = []
    def run(case):
        db = LockedDB()
        try:
            service._reserve_call(db, case, agent_key="x", phase="independent", input_chars=1)
            outcomes.append("ok")
        except service.HeartTeamBudgetExceeded:
            outcomes.append("blocked")
            if db.locked: db.commit()
    threads = [threading.Thread(target=run, args=(case,)) for case in cases]
    for thread in threads: thread.start()
    for thread in threads: thread.join(timeout=2)
    assert sorted(outcomes) == ["blocked", "ok"]


def test_final_review_requires_all_suggestions_and_dual_confirmation():
    from app.api.heart_team import final_review
    source = inspect.getsource(final_review)
    assert "medical_responsibility_confirmed" in source
    assert "human_decisions_confirmed" in source
    assert "reviewed != len(suggestions)" in source
    assert "HeartTeamFinalReview" in source


class FakeDB:
    def __init__(self): self.added = []
    def add(self, row): self.added.append(row)
    def commit(self): pass
    def refresh(self, _): pass


def usable(agent_key):
    return {"summary": f"Parecer {agent_key}", "final_consensus": f"Consenso {agent_key}", "claims": [{"statement": "Achado respaldado", "source_ids": ["s1"], "position": "support"}], "source_ids": ["s1"], "confidence": "moderate", "safety_blocks": [], "limitations": [], "alerts": [], "differential_diagnoses": [], "additional_tests": [], "therapeutic_options": [], "safety": []}


def test_cached_result_recreates_reviewable_suggestions():
    db = FakeDB(); case = SimpleNamespace(id=1)
    service._materialize_suggestions(db, case, {"additional_tests": ["Ecocardiograma"], "therapeutic_options": ["evidência insuficiente"], "safety": []})
    assert len(db.added) == 1
    assert db.added[0].category == "additional_tests"


def test_cached_bundle_replays_all_immutable_opinions_and_models():
    db = FakeDB(); case = SimpleNamespace(id=22)
    cached_opinions = []
    for agent, round_name, model in (("imaging", "independent", "clinical-a"), ("imaging", "contestation", "clinical-a"), ("coordinator", "consensus", "clinical-b")):
        content = usable(agent)
        cached_opinions.append({"agent_key": agent, "round_name": round_name, "content": content, "position": {"claims": []}, "source_ids": ["s1"], "confidence": "moderate", "content_hash": service.content_hash(content), "model_name": model, "tokens_input": 10, "tokens_output": 20})
    service._materialize_cached_opinions(db, case, cached_opinions)
    assert [(row.agent_key, row.round_name) for row in db.added] == [("imaging", "independent"), ("imaging", "contestation"), ("coordinator", "consensus")]
    assert {row.model_name for row in db.added} == {"clinical-a", "clinical-b"}
    assert all(row.content_hash == service.content_hash(row.content) for row in db.added)


def test_cached_bundle_rejects_modified_opinion_hash():
    db = FakeDB(); case = SimpleNamespace(id=23)
    with pytest.raises(service.HeartTeamSafetyError, match="Integridade"):
        service._materialize_cached_opinions(db, case, [{"agent_key": "evidence", "round_name": "independent", "content": usable("evidence"), "content_hash": "tampered"}])


def test_orchestrator_actually_uses_isolated_first_round_inputs(monkeypatch):
    db = FakeDB()
    case = SimpleNamespace(id=9, owner_id=1, created_by_id=1, status="draft", input_data={"age": 55, "sex": "F", "symptoms": ["dispneia"], "medications": ["x"], "allergies": ["nenhuma"]}, selected_agents=["imaging", "evidence", "red_team"], risk_classification={}, structured_case={}, missing_data=[], started_at=None, finished_at=None, input_hash=None, result={}, reserved_cost_micros=0, model_versions={}, tokens_input=0, tokens_output=0, estimated_cost_micros=0)
    first_inputs = []
    def fake_call(_db, _case, **kwargs):
        if kwargs["round_name"] == "independent": first_inputs.append(kwargs["message"])
        return {"agent_key": kwargs["agent_key"], "round_name": kwargs["round_name"], "content": usable(kwargs["agent_key"]), "source_ids": ["s1"], "confidence": "moderate"}
    monkeypatch.setattr(service, "enabled", lambda: None)
    monkeypatch.setattr(service, "_enforce_case_limits", lambda *_: None)
    monkeypatch.setattr(service, "attachment_descriptors", lambda *_: [])
    monkeypatch.setattr(service, "source_catalog", lambda *_args, **_kwargs: [{"id": "s1", "title": "x", "text": "Achado respaldado", "reviewed": True}])
    monkeypatch.setattr(service, "verify_source_rows", lambda rows: rows)
    monkeypatch.setattr(service, "purge_expired_cache", lambda *_: 0)
    monkeypatch.setattr(service, "_cache_get", lambda *_: None)
    monkeypatch.setattr(service, "_cache_put", lambda *_: None)
    monkeypatch.setattr(service, "resolve_related_content", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(service, "_knowledge_graph_fingerprint", lambda *_args, **_kwargs: "graph-v1")
    monkeypatch.setattr(service, "_call", fake_call)
    monkeypatch.setattr(service, "audit_event", lambda *_args, **_kwargs: None)
    service.HeartTeamOrchestrator(db, provider=object()).analyze(case, actor_id=1)
    assert len(first_inputs) == 3
    assert len({id(value) for value in first_inputs}) == 3
    assert all("opinions" not in value for value in first_inputs)
    first_inputs[0]["case"]["symptoms"].append("dor")
    assert first_inputs[1]["case"]["symptoms"] == ["dispneia"]
    assert case.status == "awaiting_review"


def test_mandatory_evidence_failure_never_reaches_awaiting_review(monkeypatch):
    db = FakeDB()
    case = SimpleNamespace(id=10, owner_id=1, created_by_id=1, status="draft", input_data={"age": 55, "sex": "F", "symptoms": ["dispneia"], "medications": ["x"], "allergies": ["nenhuma"]}, selected_agents=["imaging", "evidence", "red_team"], risk_classification={}, structured_case={}, missing_data=[], started_at=None, finished_at=None, input_hash=None, result={}, reserved_cost_micros=0, model_versions={}, tokens_input=0, tokens_output=0, estimated_cost_micros=0)
    def fake_call(_db, _case, **kwargs):
        content = usable(kwargs["agent_key"])
        if kwargs["agent_key"] == "evidence": content = {"summary": "evidência insuficiente", "claims": [], "source_ids": [], "confidence": "insufficient", "safety_blocks": []}
        return {"agent_key": kwargs["agent_key"], "round_name": kwargs["round_name"], "content": content, "source_ids": content.get("source_ids", []), "confidence": content.get("confidence")}
    monkeypatch.setattr(service, "enabled", lambda: None); monkeypatch.setattr(service, "_enforce_case_limits", lambda *_: None)
    monkeypatch.setattr(service, "attachment_descriptors", lambda *_: []); monkeypatch.setattr(service, "source_catalog", lambda *_args, **_kwargs: [{"id": "s1", "title": "x", "text": "Achado respaldado", "reviewed": True}]); monkeypatch.setattr(service, "verify_source_rows", lambda rows: rows)
    monkeypatch.setattr(service, "purge_expired_cache", lambda *_: 0); monkeypatch.setattr(service, "_cache_get", lambda *_: None); monkeypatch.setattr(service, "_call", fake_call); monkeypatch.setattr(service, "audit_event", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(service, "resolve_related_content", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(service, "_knowledge_graph_fingerprint", lambda *_args, **_kwargs: "graph-v1")
    service.HeartTeamOrchestrator(db, provider=object()).analyze(case, actor_id=1)
    assert case.status == "unusable"
    assert case.result == {}
