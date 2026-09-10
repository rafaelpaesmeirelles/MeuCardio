"""Retained vectors and candidates selected before quarantine confer no access."""
import pytest

from app.models.content import Document
from app.models.evidence import EvidenceRecord
from app.models.rag import KnowledgeChunk
from app.services import rag, rag_multi


class FakeEmbedding:
    def embeddings(self, texts):
        return [[0.01] * 1536 for _ in texts]


def evidence():
    return EvidenceRecord(slug="quarantine-rag-evidence", statement="Sentinelaquarentena evidência clínica.",
                          summary="Resumo de teste.", recommendation_class="I", evidence_level="A",
                          society="Sociedade de teste", year=2024, guideline_title="Diretriz de teste",
                          reference="Referência de teste", theme="Cardiologia", review_status="revisado", published=True)


def test_direct_chunk_resolution_rechecks_publication_without_deleting_vector(db, monkeypatch):
    monkeypatch.setattr(rag_multi, "obter_provedor_embeddings", lambda: FakeEmbedding())
    row = evidence(); db.add(row); db.commit()
    rag_multi.indexar_tipo(db, "evidencia", apenas_pendentes=False)
    chunk = db.query(KnowledgeChunk).filter(KnowledgeChunk.entity_type == "evidencia", KnowledgeChunk.entity_id == row.id).first()
    assert chunk and chunk.id in rag_multi.resolver_trechos_multi(db, [chunk.id])
    row.published = False; db.commit()
    assert db.get(KnowledgeChunk, chunk.id) is not None
    assert rag_multi.resolver_trechos_multi(db, [chunk.id]) == {}


@pytest.mark.parametrize("kind,indexed", [("documento", True), ("documento", False), ("evidencia", False)])
def test_quarantine_during_embedding_removes_already_selected_candidates(db, monkeypatch, kind, indexed):
    if kind == "documento":
        row = Document(slug="quarantine-rag-document", title="Sentinelaquarentena documento clínico",
                       kind="documento", theme="Cardiologia", body_md="## Conteúdo\nSentinelaquarentena conteúdo clínico.",
                       source_tier="A", review_status="revisado", published=True)
    else:
        row = evidence()
    db.add(row); db.commit()
    if indexed:
        rag.indexar_documento(db, row, provedor=FakeEmbedding())
    original_lexical = rag_multi.buscar_lexico_multi
    lexical_candidates = []
    def capture_lexical(*args, **kwargs):
        items = original_lexical(*args, **kwargs)
        lexical_candidates.extend(items)
        return items
    monkeypatch.setattr(rag_multi, "buscar_lexico_multi", capture_lexical)
    class QuarantineWhileEmbedding:
        def embeddings(self, texts):
            row.published = False
            db.commit()
            raise RuntimeError("Fake embedding unavailable after quarantine")
    monkeypatch.setattr(rag, "obter_provedor_embeddings", lambda: QuarantineWhileEmbedding())
    results = rag.recuperar(db, "Sentinelaquarentena")
    if not indexed:
        assert any(item["slug"] == row.slug for item in lexical_candidates)
    assert all(item["slug"] != row.slug for item in results)
    assert row.published is False
