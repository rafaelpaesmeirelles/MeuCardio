"""Correção coordenada de 03/09/2026 (seção "arquitetura de deploy"): reescrito
depois que `reconcile_content._reindexar_rag_pendente` foi removida.

`reconcile()` NUNCA MAIS chama o provedor de embeddings — publicar/reconciliar
tem que ser rápido e determinístico porque roda dentro da janela em que o
Caddy está fechado (`deploy.sh`). A indexação RAG é responsabilidade exclusiva
de `app.commands.reindex_rag_completo_20260902`, disparado pelo `deploy.sh`
DEPOIS que o tráfego já reabriu (ver `deploy.sh`, seção "Indexação RAG
incremental").

Este arquivo cobre as duas pontas: (1) `reconcile()` continua sem indexar nada
mesmo quando há conteúdo novo publicado; (2) o comando de backfill indexa
documento + frente multi corretamente e é idempotente."""

import pytest
import json
from sqlalchemy import text

from app.commands.reconcile_content import reconcile
from app.commands import reconcile_content as reconciliation
from app.commands.reindex_rag_completo_20260902 import rodar
from app.core.config import settings
from app.models.content import Document
from app.models.evidence import EvidenceRecord
from app.models.rag import DocumentChunk, KnowledgeChunk
from app.services.corpus_release_authorization import (
    FULL_CORPUS_DECISION, FULL_CORPUS_SCOPE, build_front_fingerprint, corpus_inventory_sha256,
)
from _editorial_fixtures import write_empty_editorial_registry


class _ProvedorFake:
    def embeddings(self, textos):
        vetores = []
        for texto in textos:
            semente = sum(ord(c) for c in texto) % 997
            vetores.append([((semente + i) % 997) / 997 for i in range(1536)])
        return vetores


@pytest.fixture(autouse=True)
def _acervo_limpo(db):
    tabelas = "documents, document_chunks, evidence_records, knowledge_chunks, rag_reindex_runs"
    db.execute(text(f"TRUNCATE {tabelas} RESTART IDENTITY CASCADE"))
    db.commit()
    yield
    db.execute(text(f"TRUNCATE {tabelas} RESTART IDENTITY CASCADE"))
    db.commit()


def test_reconcile_nunca_chama_rag(db, monkeypatch, tmp_path):
    """Invariante da seção "arquitetura de deploy": reconcile() não pode
    depender do provedor de embeddings. Se qualquer caminho de código dentro
    de reconcile() chamar obter_provedor_embeddings, este teste explode —
    nenhum fake é instalado de propósito."""

    def _explode():
        raise AssertionError("reconcile() chamou obter_provedor_embeddings() — regressão da seção 2")

    monkeypatch.setattr("app.services.rag.obter_provedor_embeddings", _explode)
    monkeypatch.setattr("app.services.rag_multi.obter_provedor_embeddings", _explode)
    # Explicit schema-1 test release: keep the actual authorization/hash checks
    # and never inherit the changing production schema-2 manifest or corpus.
    from collections import defaultdict
    source = tmp_path / "content"
    source.mkdir()
    slug = "reconcile-nao-indexa-teste"
    (source / "fixture.md").write_text(
        f"---\nslug: {slug}\ntitle: Documento de teste\nkind: documento\ntheme: Farmacologia\n"
        "source_tier: A\nreview_status: revisado\npublished: true\n---\n## Seção\nConteúdo de teste do documento.\n")
    fronts = {"documentos": {"path": str(source), "model": Document, "minimum": 1, "loader": None}}
    fingerprint = {"documentos": build_front_fingerprint(source, {slug}, {slug: "revisado"})}
    authorization = tmp_path / "test-release.json"
    authorization.write_text(json.dumps({"schema_version": 1, "release": "isolated-rag-contract",
        "decision": FULL_CORPUS_DECISION, "scope": FULL_CORPUS_SCOPE,
        "approval_basis": "Synthetic test fixture only; no real content or publication authorization.",
        "expected_total": 1, "inventory_sha256": corpus_inventory_sha256(fingerprint), "fronts": fingerprint}))
    monkeypatch.setattr(reconciliation, "FRONTS", fronts)
    editorial_registry = write_empty_editorial_registry(tmp_path)
    # Schema 1 resolves its preferred evidence ledger below REPOSITORY_ROOT;
    # overriding only the fallback path still selects the real repository.
    monkeypatch.setattr(reconciliation, "REPOSITORY_ROOT", tmp_path)
    monkeypatch.setattr(reconciliation, "EDITORIAL_KIND_REGISTRY_PATH", editorial_registry)
    monkeypatch.setattr(reconciliation, "_load_editorial_approvals", lambda: defaultdict(set))
    monkeypatch.setattr(reconciliation, "_load_controlled_substances", lambda _db: {})
    monkeypatch.setattr(reconciliation, "_migrate_study_track_progress", lambda _db: 0)
    monkeypatch.setattr(reconciliation, "backfill_mesmo_tema", lambda _db: {})

    db.add(Document(
        slug="reconcile-nao-indexa-teste", title="Documento de teste", kind="documento",
        theme="Farmacologia", body_md="## Seção\nConteúdo de teste do documento.",
        source_tier="A", review_status="revisado", published=True,
    ))
    db.commit()

    resultado = reconcile(publish_reviewed=False, allow_partial=True, authorization_path=authorization)

    assert resultado["rag"]["status"] == "nao_executado_aqui"
    metadata = resultado["loads"]["editorial_metadata"]
    assert metadata["registry_sha256"] == reconciliation.load_editorial_registry(editorial_registry)["registry_sha256"]
    assert metadata["canonical_claims_checked"] == 0 and metadata["materialized"] == 0
    assert db.query(DocumentChunk).count() == 0


def test_reindex_rag_completo_indexa_documento_e_frente_multi(db, monkeypatch):
    monkeypatch.setattr(settings, "ai_enabled", True)
    monkeypatch.setattr("app.services.rag.obter_provedor_embeddings", lambda: _ProvedorFake())
    monkeypatch.setattr("app.services.rag_multi.obter_provedor_embeddings", lambda: _ProvedorFake())

    db.add(Document(
        slug="reindex-rag-documento-teste", title="Documento de teste", kind="documento",
        theme="Farmacologia", body_md="## Seção\nConteúdo de teste do documento.",
        source_tier="A", review_status="revisado", published=True,
    ))
    db.add(EvidenceRecord(
        slug="reindex-rag-evidencia-teste", statement="Statement de teste.",
        summary="Resumo.", recommendation_class="I", evidence_level="A",
        society="Sociedade de teste", year=2024, guideline_title="Diretriz de teste",
        reference="Referência de teste", theme="Farmacologia",
        review_status="revisado", published=True,
    ))
    db.commit()

    resultado, exit_code = rodar()

    assert exit_code == 0
    assert resultado["por_frente"]["documento"]["documentos"] == 1
    assert resultado["por_frente"]["evidencia"]["entidades"] == 1
    assert db.query(DocumentChunk).count() > 0
    assert db.query(KnowledgeChunk).filter(KnowledgeChunk.entity_type == "evidencia").count() > 0
    # Uma linha de auditoria por execução, com contadores e exit_code.
    from app.models.rag import RagReindexRun
    runs = db.query(RagReindexRun).all()
    assert len(runs) == 1
    assert runs[0].exit_code == 0
    assert runs[0].falhas == 0
    assert runs[0].backlog_restante == 0


def test_reindex_rag_completo_e_idempotente(db, monkeypatch):
    """Segunda chamada não reprocessa quem já tem chunk em dia — content_hash."""
    monkeypatch.setattr(settings, "ai_enabled", True)
    monkeypatch.setattr("app.services.rag.obter_provedor_embeddings", lambda: _ProvedorFake())
    monkeypatch.setattr("app.services.rag_multi.obter_provedor_embeddings", lambda: _ProvedorFake())

    db.add(EvidenceRecord(
        slug="reindex-rag-idempotente-teste", statement="Statement de teste.",
        summary="Resumo.", recommendation_class="I", evidence_level="A",
        society="Sociedade de teste", year=2024, guideline_title="Diretriz de teste",
        reference="Referência de teste", theme="Farmacologia",
        review_status="revisado", published=True,
    ))
    db.commit()

    primeiro, exit1 = rodar()
    segundo, exit2 = rodar()

    assert exit1 == 0 and exit2 == 0
    assert primeiro["por_frente"]["evidencia"]["entidades"] == 1
    assert segundo["por_frente"]["evidencia"]["entidades"] == 0  # já em dia, nenhuma chamada de rede


def test_reindex_rag_recusa_segunda_execucao_concorrente(db, monkeypatch):
    """Achado do revisor adversarial de deploy/rollback em 03/09/2026: nada
    impedia duas execuções do backfill rodarem ao mesmo tempo (deploy.sh
    dispara em background; um operador podia rodar de novo manualmente
    achando que a primeira não tinha disparado). Simula o lock já ocupado
    por outra sessão — a segunda chamada tem que desistir rápido, com exit
    code próprio, sem tocar em nada."""
    from sqlalchemy import text as sqltext

    from app.commands.reindex_rag_completo_20260902 import _LOCK_KEY

    monkeypatch.setattr(settings, "ai_enabled", True)
    monkeypatch.setattr(
        "app.services.rag.obter_provedor_embeddings",
        lambda: (_ for _ in ()).throw(AssertionError("não devia chegar a chamar o provedor")),
    )

    obtido = db.execute(sqltext("SELECT pg_try_advisory_lock(:k)"), {"k": _LOCK_KEY}).scalar()
    assert obtido is True
    try:
        resultado, exit_code = rodar()
        assert exit_code == 3
        assert "execução" in resultado["erro"].lower()
    finally:
        db.execute(sqltext("SELECT pg_advisory_unlock(:k)"), {"k": _LOCK_KEY})
        db.commit()


def test_reindex_rag_recusa_rodar_com_ia_desligada(db, monkeypatch):
    """Achado da investigação original de 03/09/2026: o comando gastava
    crédito mesmo com AI_ENABLED=false, sem guarda nenhuma."""
    monkeypatch.setattr(settings, "ai_enabled", False)
    monkeypatch.setattr(
        "app.services.rag.obter_provedor_embeddings",
        lambda: (_ for _ in ()).throw(AssertionError("não devia chegar a chamar o provedor")),
    )

    resultado, exit_code = rodar()

    assert exit_code == 4
    assert "ai_enabled=false" in resultado["erro"].lower()


def test_reindex_rag_dry_run_funciona_mesmo_com_ia_desligada(db, monkeypatch):
    """--dry-run é só leitura — precisa continuar útil mesmo com IA desligada,
    para preparar/estimar o backfill antes de ligar."""
    monkeypatch.setattr(settings, "ai_enabled", False)

    resultado, exit_code = rodar(dry_run=True)

    assert exit_code == 0
    assert "preflight" in resultado


def test_reindex_rag_dry_run_nao_chama_provedor_nem_escreve(db, monkeypatch):
    def _explode():
        raise AssertionError("--dry-run chamou o provedor de embeddings")

    monkeypatch.setattr("app.services.rag.obter_provedor_embeddings", _explode)
    monkeypatch.setattr("app.services.rag_multi.obter_provedor_embeddings", _explode)

    db.add(EvidenceRecord(
        slug="reindex-rag-dry-run-teste", statement="Statement de teste.",
        summary="Resumo.", recommendation_class="I", evidence_level="A",
        society="Sociedade de teste", year=2024, guideline_title="Diretriz de teste",
        reference="Referência de teste", theme="Farmacologia",
        review_status="revisado", published=True,
    ))
    db.commit()

    resultado, exit_code = rodar(dry_run=True)

    assert exit_code == 0
    assert resultado["preflight"]["total_pendentes"] >= 1
    assert db.query(KnowledgeChunk).count() == 0
    from app.models.rag import RagReindexRun
    assert db.query(RagReindexRun).count() == 0  # dry-run não grava linha de execução real
