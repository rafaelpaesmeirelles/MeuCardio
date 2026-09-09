"""Read-only paired RAG retrieval audit; paid embedding requires --compare.

Run inside an isolated process using the application's runtime/configuration.
The caller may overlay candidate catalog code in that process before calling
audit(). No production source file, content row, chunk, or conversation changes.
Only the 16 synthetic fixture queries are sent in one embedding request.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import logging
import math
from pathlib import Path
import statistics
import sys
import time


FIXTURE_SHA256 = "80d2b45d94b0bee4d914aa365ab5f30793a4731ee444258d8418ed0c34c166ea"


def validate_cases(cases: list[dict], fixture_sha256: str) -> None:
    if fixture_sha256 != FIXTURE_SHA256:
        raise ValueError("Fixture differs from the reference frozen before comparison")
    if len(cases) != 16 or len({c["id"] for c in cases}) != 16:
        raise ValueError("Exactly 16 unique frozen cases are required")
    if Counter(c["group"] for c in cases) != {"exact": 8, "paraphrase": 8}:
        raise ValueError("Expected eight exact queries and eight paraphrases")
    for case in cases:
        if not isinstance(case["query"], str) or not 1 <= len(case["query"]) <= 200:
            raise ValueError("Invalid bounded synthetic query")
        if not 2 <= len(case["required_any"]) <= 4:
            raise ValueError("Invalid reference alternatives")
        if any(not key.startswith("documento:") for key in case["required_any"]):
            raise ValueError("This frozen sample contains document labels only")


def safe_error(exc: Exception) -> dict:
    # Exception messages/HTTP bodies can contain configuration or provider
    # details. Keep only bounded structured classification, never API keys.
    code = getattr(exc, "code", None)
    return {
        "type": type(exc).__name__,
        "status_code": getattr(exc, "status_code", None),
        "code": str(code)[:80] if isinstance(code, (str, int)) else None,
    }


def preflight(db, cases: list[dict], rag, settings) -> dict:
    from sqlalchemy import select, text
    from app.models.content import Document
    from app.models.rag import DocumentChunk

    keys = sorted({key for c in cases for key in c["required_any"]})
    slugs = [key.split(":", 1)[1] for key in keys]
    rows = db.execute(select(
        Document.id, Document.slug, Document.title, Document.body_md,
        Document.published, Document.review_status,
    ).where(Document.slug.in_(slugs))).all()
    by_slug = {row.slug: row for row in rows}
    ids = [row.id for row in rows]
    chunks = db.execute(select(
        DocumentChunk.document_id, DocumentChunk.content_hash,
        DocumentChunk.embedding_model,
        DocumentChunk.embedding.is_not(None).label("has_vector"),
    ).where(DocumentChunk.document_id.in_(ids))).all() if ids else []
    by_id: dict[int, list] = {}
    for chunk in chunks:
        by_id.setdefault(chunk.document_id, []).append(chunk)
    records = []
    for key, slug in zip(keys, slugs):
        doc = by_slug.get(slug)
        if doc is None:
            records.append({"key": key, "exists": False, "published": False,
                            "eligible": False, "index_state": "MISSING_SOURCE"})
            continue
        fingerprint = rag.fingerprint_fonte(doc.title, doc.body_md)
        doc_chunks = by_id.get(doc.id, [])
        states = Counter(rag.classificar_chunk(
            chunk.content_hash, chunk.embedding_model, fingerprint,
        ) if chunk.has_vector else "MISSING_VECTOR" for chunk in doc_chunks)
        verified = states.get(rag.CURRENT_VERIFIED, 0)
        legacy = states.get(rag.LEGACY_UNVERIFIED, 0)
        records.append({
            "key": key, "exists": True, "published": bool(doc.published),
            "eligible": bool(doc.published), "review_status": doc.review_status,
            "title": doc.title, "source_fingerprint": fingerprint,
            "chunk_count": len(doc_chunks), "chunk_states": dict(states),
            "index_state": "CURRENT_VERIFIED" if verified else (
                "LEGACY_UNVERIFIED" if legacy else "STALE_OR_MISSING"),
            "has_usable_semantic_chunk": bool(verified or legacy),
        })
    dimensions = [dict(row) for row in db.execute(text(
        "SELECT c.relname AS table_name, a.atttypmod AS vector_dimension "
        "FROM pg_attribute a JOIN pg_class c ON c.oid=a.attrelid "
        "WHERE c.relname IN ('document_chunks','knowledge_chunks') "
        "AND a.attname='embedding' AND a.attnum>0 AND NOT a.attisdropped"
    )).mappings()]
    return {
        "references": records,
        "eligible_count": sum(r["eligible"] for r in records),
        "ineligible_keys": [r["key"] for r in records if not r["eligible"]],
        "semantic_ready_count": sum(bool(r.get("has_usable_semantic_chunk"))
                                    and r["eligible"] for r in records),
        "schema_dimensions": dimensions,
        "configured_model": settings.openai_embedding_model,
        "configured_dimension": settings.embedding_dim,
        "publication_policy": "Only published labels enter metric denominators; labels are never replaced",
        "index_policy": "Missing/stale chunks remain retrieval gaps; publication eligibility does not require embeddings",
    }


class LexicalOnlyProvider:
    def __init__(self):
        self.calls = 0

    def embeddings(self, _texts):
        self.calls += 1
        raise RuntimeError("Intentional lexical-only audit provider")


class CachedQueryProvider:
    def __init__(self, query: str, vector: list[float]):
        self.query, self.vector, self.calls = query, vector, 0

    def embeddings(self, texts):
        self.calls += 1
        if texts != [self.query]:
            raise RuntimeError("Unexpected embedding request in bounded retrieval audit")
        return [self.vector]


class RetrievalLogCapture(logging.Handler):
    def __init__(self):
        super().__init__(logging.WARNING)
        self.events = []

    def emit(self, record):
        if record.name.startswith("corvia.rag"):
            self.events.append({"logger": record.name, "level": record.levelname,
                                "message": record.getMessage()[:240]})


def identity(row: dict) -> str:
    kind = {"document": "documento", "fluxograma": "documento",
            "protocolo_emergencia": "emergencia"}.get(
                row.get("entity_type", "documento"), row.get("entity_type", "documento"))
    return f"{kind}:{row.get('slug', '')}"


def score_rows(rows: list[dict], case: dict, eligible_keys: set[str], k: int) -> dict:
    keys = [identity(row) for row in rows]
    ranked = keys[:k]
    references = set(case["required_any"]) & eligible_keys
    hits = references & set(ranked)
    first = next((i for i, key in enumerate(ranked, 1) if key in references), None)
    required_all = set(case.get("required_all", [])) & eligible_keys
    sources = [{
        "rank": index, "key": identity(row), "title": row.get("titulo"),
        "section": row.get("secao"), "route": row.get("rota"),
        "review_status": row.get("review_status"),
        "content_excerpt": str(row.get("conteudo") or "")[:600],
    } for index, row in enumerate(rows, 1)]
    return {
        "raw_result_count": len(rows), "unique_identity_count": len(set(keys)),
        "duplicate_count": len(keys) - len(set(keys)),
        "duplicate_identities": {key: n for key, n in Counter(keys).items() if n > 1},
        "unique_typed_identities": list(dict.fromkeys(keys)),
        "top_k_raw_identities": ranked, "eligible_reference_count": len(references),
        "ineligible_references": sorted(set(case["required_any"]) - eligible_keys),
        "matched_references": sorted(hits),
        "hit_at_k": int(bool(hits)) if references else None,
        "first_reference_rank": first,
        "reciprocal_rank_at_k": (1 / first if first else 0.0) if references else None,
        "partial_label_recall_at_k": len(hits) / len(references) if references else None,
        "required_all_satisfied": required_all <= set(ranked) if required_all else None,
        "source_pages": [{"offset": offset, "limit": k,
                          "next_offset": offset + k if offset + k < len(sources) else None,
                          "items": sources[offset:offset + k]}
                         for offset in range(0, len(sources), k)],
    }


def retrieve_mode(db, rag, case: dict, provider, eligible: set[str], k: int, mode: str) -> dict:
    previous = rag.obter_provedor_embeddings
    capture = RetrievalLogCapture()
    logger = logging.getLogger()
    logger.addHandler(capture)
    started = time.perf_counter()
    try:
        rag.obter_provedor_embeddings = lambda: provider
        # A query timeout must not poison subsequent paired trials. Savepoints
        # change no data and preserve the outer read-only repeatable snapshot.
        with db.begin_nested():
            rows = rag.recuperar(db, case["query"])
        result = score_rows(rows, case, eligible, k)
        events = capture.events
        expected_warning = "Provedor de embeddings indisponível na recuperação"
        unexpected = [event for event in events if not (
            mode == "lexical" and expected_warning in event["message"])]
        result.update({"status": "degraded" if unexpected else "ok",
                       "diagnostics": events, "embedding_provider_calls": provider.calls})
        if provider.calls != 1:
            result["status"] = "blocked_provider_not_used_as_expected"
        if mode == "hybrid" and any(expected_warning in event["message"] for event in events):
            result["status"] = "blocked_semantic_fallback"
        return result
    except Exception as exc:
        return {"status": "failed", "error": safe_error(exc),
                "embedding_provider_calls": provider.calls, "diagnostics": capture.events}
    finally:
        rag.obter_provedor_embeddings = previous
        logger.removeHandler(capture)
        # Return dictionaries above are updated through a local timing wrapper.
        provider.elapsed_seconds = round(time.perf_counter() - started, 6)


def summarize(results: list[dict]) -> dict:
    summaries = {}
    for group in ("all", "exact", "paraphrase"):
        selected = [row for row in results if group == "all" or row["group"] == group]
        paired = [row for row in selected
                  if all((row.get(mode) or {}).get("status") == "ok" for mode in ("lexical", "hybrid"))
                  and row["lexical"].get("hit_at_k") is not None
                  and row["hybrid"].get("hit_at_k") is not None]
        summary = {"requested_cases": len(selected), "valid_paired_cases": len(paired)}
        for mode in ("lexical", "hybrid"):
            rows = [row[mode] for row in paired]
            summary[mode] = {
                "hit_at_k": statistics.mean(r["hit_at_k"] for r in rows) if rows else None,
                "mrr_at_k": statistics.mean(r["reciprocal_rank_at_k"] for r in rows) if rows else None,
                "partial_label_recall_at_k": statistics.mean(r["partial_label_recall_at_k"] for r in rows) if rows else None,
                "median_retrieval_seconds": statistics.median(r["retrieval_seconds"] for r in rows) if rows else None,
                "mean_retrieval_seconds": statistics.mean(r["retrieval_seconds"] for r in rows) if rows else None,
                "duplicate_total": sum(r["duplicate_count"] for r in rows),
            }
        summary["hybrid_only_hits"] = [r["id"] for r in paired if r["hybrid"]["hit_at_k"] > r["lexical"]["hit_at_k"]]
        summary["lexical_only_hits"] = [r["id"] for r in paired if r["lexical"]["hit_at_k"] > r["hybrid"]["hit_at_k"]]
        summaries[group] = summary
    return summaries


def lexical_baseline(cases: list[dict], fixture_sha256: str, *, previous_report: dict | None = None,
                     max_elapsed_seconds: int = 600) -> dict:
    """Measure current lexical fallback without constructing any real provider.

    A prior blocked embedding report is retained verbatim in its fields. This
    separate run obtains a new repeatable snapshot and repeats preflight; the
    previous closed transaction's snapshot is not claimed to remain current.
    """
    validate_cases(cases, fixture_sha256)
    if previous_report is not None and previous_report.get("status") != "blocked_embedding_provider":
        raise ValueError("Only a blocked embedding attempt may be augmented by this baseline")
    from sqlalchemy import text
    from app.core.config import settings
    from app.core.db import SessionLocal
    from app.services import rag

    report = json.loads(json.dumps(previous_report)) if previous_report is not None else {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "lexical_only_completed", "fixture_sha256": fixture_sha256,
        "query_count": len(cases), "embedding_batch": {"attempts": 0},
        "database_writes": False, "chat_generation_calls": 0,
        "precision_note": "Not calculated: unlabelled results are not automatically irrelevant",
    }
    if report.get("fixture_sha256") != fixture_sha256:
        raise ValueError("Prior report belongs to a different reference fixture")
    started = time.monotonic()
    k = min(8, int(settings.ai_top_k))
    if k < 1:
        raise ValueError("Configured ai_top_k must be positive")
    report.update(evaluation_k=k, configured_ai_top_k=settings.ai_top_k, results=[])
    report["lexical_baseline_started_at"] = datetime.now(timezone.utc).isoformat()
    report["lexical_baseline_embedding_network_calls"] = 0
    with SessionLocal() as db:
        db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY"))
        db.execute(text("SET LOCAL statement_timeout = '20s'"))
        report["lexical_baseline_snapshot"] = db.execute(text("SELECT txid_current_snapshot()::text")).scalar_one()
        report["lexical_baseline_preflight"] = preflight(db, cases, rag, settings)
        eligible = {row["key"] for row in report["lexical_baseline_preflight"]["references"] if row["eligible"]}
        for index, case in enumerate(cases):
            record = {"id": case["id"], "query": case["query"], "group": case["group"],
                      "pair_id": case.get("pair_id"), "required_any": case["required_any"],
                      "hybrid": None, "execution_order": ["lexical"]}
            if time.monotonic() - started > max_elapsed_seconds:
                record["lexical"] = {"status": "not_run_time_budget"}
            else:
                provider = LexicalOnlyProvider()
                record["lexical"] = retrieve_mode(db, rag, case, provider, eligible, k, "lexical")
                record["lexical"]["retrieval_seconds"] = provider.elapsed_seconds
            report["results"].append(record)
            print(json.dumps({"completed_case": index + 1, "case_id": case["id"],
                              "mode": "lexical_only", "status": record["lexical"]["status"]}),
                  file=sys.stderr, flush=True)
    summaries = {}
    for group in ("all", "exact", "paraphrase"):
        selected = [row for row in report["results"] if group == "all" or row["group"] == group]
        valid = [row["lexical"] for row in selected if row["lexical"].get("status") == "ok"
                 and row["lexical"].get("hit_at_k") is not None]
        summaries[group] = {
            "requested_cases": len(selected), "valid_cases": len(valid),
            "hit_at_k": statistics.mean(row["hit_at_k"] for row in valid) if valid else None,
            "mrr_at_k": statistics.mean(row["reciprocal_rank_at_k"] for row in valid) if valid else None,
            "partial_label_recall_at_k": statistics.mean(row["partial_label_recall_at_k"] for row in valid) if valid else None,
            "median_retrieval_seconds": statistics.median(row["retrieval_seconds"] for row in valid) if valid else None,
            "duplicate_total": sum(row["duplicate_count"] for row in valid),
        }
    report["lexical_baseline_summary"] = summaries
    report["lexical_baseline_status"] = ("completed" if summaries["all"]["valid_cases"] == len(cases)
                                         else "completed_with_limitations")
    report["lexical_baseline_elapsed_seconds"] = round(time.monotonic() - started, 3)
    report["comparison_note"] = "Hybrid was not executed; no semantic contribution estimate can be derived from this lexical baseline"
    report["summary"] = summarize(report["results"])
    return report


def audit(cases: list[dict], fixture_sha256: str, *, compare: bool = False,
          max_elapsed_seconds: int = 600) -> dict:
    """Default is preflight only; caller must explicitly select paid comparison."""
    validate_cases(cases, fixture_sha256)
    from sqlalchemy import text
    from app.core.config import settings
    from app.core.db import SessionLocal
    from app.services import rag

    started = time.monotonic()
    k = min(8, int(settings.ai_top_k))
    if k < 1:
        raise ValueError("Configured ai_top_k must be positive")
    report = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "preflight_only", "fixture_sha256": fixture_sha256,
        "query_count": len(cases), "evaluation_k": k,
        "configured_ai_top_k": settings.ai_top_k,
        "method": "rag.recuperar real; provider unavailable vs precomputed query vector",
        "scope": "Agent-labeled sample of document retrieval, not exhaustive clinical certification",
        "latency_scope": "Retrieval excludes the single embedding batch; its latency is reported separately",
        "precision_note": "Not calculated: unlabelled results are not automatically irrelevant",
        "duplicates_note": "Metrics use raw first-k positions; deduplication does not hide consumed slots",
        "database_writes": False, "chat_generation_calls": 0, "embedding_batch": {"attempts": 0},
        "results": [],
    }
    with SessionLocal() as db:
        db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY"))
        db.execute(text("SET LOCAL statement_timeout = '20s'"))
        report["snapshot"] = db.execute(text("SELECT txid_current_snapshot()::text")).scalar_one()
        try:
            report["preflight"] = preflight(db, cases, rag, settings)
            rag.verificar_dimensao_embedding(db)
        except Exception as exc:
            report.update(status="blocked_preflight", error=safe_error(exc))
            return report
        if not compare:
            return report
        if settings.ai_embedding_provider != "openai" or not settings.openai_api_key:
            report["status"] = "blocked_embedding_configuration"
            return report
        if not report["preflight"]["eligible_count"]:
            report["status"] = "blocked_no_eligible_labels"
            return report
        batch_started = time.perf_counter()
        batch = report["embedding_batch"]
        batch.update(attempts=1, input_count=len(cases), max_retries=0, timeout_seconds=20,
                     requested_model=settings.openai_embedding_model)
        try:
            from openai import OpenAI
            # Match production model/default dimensions; do not silently change
            # its vector space by selecting a different model or dimensions.
            with OpenAI(api_key=settings.openai_api_key, max_retries=0, timeout=20.0) as client:
                response = client.embeddings.create(model=settings.openai_embedding_model,
                                                    input=[case["query"] for case in cases])
            data = sorted(response.data, key=lambda row: row.index)
            if [row.index for row in data] != list(range(len(cases))):
                raise ValueError("Provider returned an incomplete embedding batch")
            vectors = [row.embedding for row in data]
            if any(len(vector) != settings.embedding_dim or not all(math.isfinite(x) for x in vector)
                   for vector in vectors):
                raise ValueError("Provider embedding dimensions or values are incompatible")
            usage = response.usage
            batch.update(status="ok", returned_model=response.model,
                         dimension=settings.embedding_dim,
                         usage={"prompt_tokens": usage.prompt_tokens, "total_tokens": usage.total_tokens},
                         vector_count=len(vectors))
        except Exception as exc:
            batch.update(status="blocked", error=safe_error(exc))
            report["status"] = "blocked_embedding_provider"
            return report
        finally:
            batch["latency_seconds"] = round(time.perf_counter() - batch_started, 6)
        eligible = {row["key"] for row in report["preflight"]["references"] if row["eligible"]}
        for index, (case, vector) in enumerate(zip(cases, vectors)):
            record = {"id": case["id"], "query": case["query"], "group": case["group"],
                      "pair_id": case.get("pair_id"), "required_any": case["required_any"]}
            # Alternate order to reduce warm-cache bias between modes.
            order = ("lexical", "hybrid") if index % 2 == 0 else ("hybrid", "lexical")
            record["execution_order"] = list(order)
            for mode in order:
                if time.monotonic() - started > max_elapsed_seconds:
                    record[mode] = {"status": "not_run_time_budget"}
                    continue
                provider = LexicalOnlyProvider() if mode == "lexical" else CachedQueryProvider(case["query"], vector)
                record[mode] = retrieve_mode(db, rag, case, provider, eligible, k, mode)
                record[mode]["retrieval_seconds"] = provider.elapsed_seconds
            report["results"].append(record)
        report["summary"] = summarize(report["results"])
        report["status"] = ("completed" if report["summary"]["all"]["valid_paired_cases"] == len(cases)
                            else "completed_with_limitations")
        report["elapsed_seconds"] = round(time.monotonic() - started, 3)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, default=Path("scripts/fixtures/ai_retrieval_cases.json"))
    parser.add_argument("--output", default="docs/ai-contribution-20260909.json")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--compare", action="store_true", help="Send one paid embedding batch for the 16 synthetic queries")
    modes.add_argument("--lexical-only", action="store_true", help="Run the lexical baseline with zero embedding network calls")
    parser.add_argument("--previous-report", type=Path, help="Preserve a previous blocked embedding report when adding a lexical baseline")
    parser.add_argument("--max-elapsed-seconds", type=int, default=600)
    args = parser.parse_args()
    raw = args.fixture.read_bytes()
    if args.previous_report and not args.lexical_only:
        parser.error("--previous-report requires --lexical-only")
    if args.lexical_only:
        previous = json.loads(args.previous_report.read_text()) if args.previous_report else None
        report = lexical_baseline(json.loads(raw), hashlib.sha256(raw).hexdigest(), previous_report=previous,
                                  max_elapsed_seconds=args.max_elapsed_seconds)
    else:
        report = audit(json.loads(raw), hashlib.sha256(raw).hexdigest(), compare=args.compare,
                       max_elapsed_seconds=args.max_elapsed_seconds)
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output == "-":
        print(rendered, end="")
    else:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered)
        print(json.dumps({"status": report["status"], "output": str(output)}, ensure_ascii=False))
    return 0 if report["status"] in {"preflight_only", "completed", "completed_with_limitations", "lexical_only_completed"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
