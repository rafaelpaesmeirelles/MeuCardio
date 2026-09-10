"""Sequential, metered RAG indexing of only the approved scientific-20260910 pack.

Run inside the backend container with PYTHONPATH=/app:
  python /tmp/index_scientific_release_20260910.py PACK --sha256 HASH --check
  python /tmp/index_scientific_release_20260910.py PACK --sha256 HASH --apply

--check uses READ ONLY transactions, does not call the provider or wallet, and
reports exact-source guards plus fingerprint/model/chunk completeness. --apply
shares the global RAG lock, skips current entries before entering ai_operation,
and calls the existing metered indexers sequentially. There are no item retries.
Quota, credit, budget and accounting errors stop the run immediately; other
failures stop after at most three failures in total. Reports contain only public
typed slugs, hashes, counts and sanitized error identifiers, never source text.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re

from sqlalchemy import select, text
from app.core.config import settings
from app.core.db import SessionLocal, engine
from app.models.content import Document
from app.models.clinical_case import ClinicalCase
from app.models.patient_material import PatientMaterial
from app.models.rag import DocumentChunk, KnowledgeChunk
from app.services.ai_wallet import AIWalletError
from app.services.ia.usage_control import AIUsageError
from app.services.rag import (
    EmbeddingDimensionError, dividir, esta_atualizado, fingerprint_fonte,
    indexar_documento, verificar_dimensao_embedding,
)
from app.services.rag_multi import indexar_entidade
from app.services.rag_sources import FONTES_POR_TIPO

RELEASE_ID = 'scientific-20260910'
LOCK_ID = 771103090  # app.commands.reindex_rag_completo_20260902._LOCK_KEY
MODELS = {'documento': Document, 'caso_clinico': ClinicalCase,
          'material_paciente': PatientMaterial}
EXPECTED_COUNTS = {'documento': 395, 'caso_clinico': 2, 'material_paciente': 1}
FORBIDDEN = {'id', 'reviewed_by', 'reviewed_at', 'created_at', 'updated_at',
             'version', 'search_vector', 'author_id', 'human_by'}
MAX_FAILURES = 3


class SourceGuardError(RuntimeError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def now():
    return datetime.now(timezone.utc).isoformat()


def identity(item):
    return item['kind'], item['data']['slug']


def read_pack(path, expected_sha):
    raw = path.read_bytes()
    if not re.fullmatch(r'[0-9a-fA-F]{64}', expected_sha):
        raise ValueError('Invalid SHA256 argument')
    if hashlib.sha256(raw).hexdigest() != expected_sha.lower():
        raise ValueError('Package checksum mismatch')
    pack = json.loads(raw)
    if (pack.get('release_id') != RELEASE_ID or pack.get('ready') is not True
            or pack.get('errors') or pack.get('pending_source_indices')):
        raise ValueError('Unapproved package')
    items = pack.get('items') or []
    if Counter(i['kind'] for i in items) != EXPECTED_COUNTS:
        raise ValueError('Expected exactly 395 documents, two cases and one patient material')
    if len({identity(i) for i in items}) != 398:
        raise ValueError('Duplicate typed identities')
    for item in items:
        kind, data = item['kind'], item['data']
        columns = MODELS[kind].__table__.columns
        if set(data) - set(columns.keys()) or set(data) & FORBIDDEN:
            raise ValueError(f'Forbidden or unknown fields: {kind}:{data.get("slug")}')
        if data.get('published') is not True or data.get('review_status') != 'revisado':
            raise ValueError(f'Not published and reviewed: {kind}:{data.get("slug")}')
        required = ({'title', 'body_md', 'kind', 'theme'} if kind == 'documento'
                    else {'titulo', 'enunciado', 'pergunta', 'opcoes', 'resposta_correta', 'explicacao'}
                    if kind == 'caso_clinico' else {'titulo', 'secoes', 'tema'})
        if not required.issubset(data):
            raise ValueError(f'Incomplete indexing source: {kind}:{data["slug"]}')
    return items


def inspect_item(db, item, *, lock_row=False):
    kind, slug = identity(item)
    query = select(MODELS[kind]).where(MODELS[kind].slug == slug)
    if lock_row:
        # Keep this exact public source stable until its chunks commit. Do not
        # wait behind a concurrent editor or silently index a newer revision.
        query = query.with_for_update(read=True, nowait=True)
    row = db.execute(query.execution_options(populate_existing=True)).scalar_one_or_none()
    if row is None:
        raise SourceGuardError('source_missing')
    if not row.published or row.review_status != 'revisado':
        raise SourceGuardError('source_unpublished_or_unreviewed')
    if any(getattr(row, field) != value for field, value in item['data'].items()):
        raise SourceGuardError('source_differs_from_approved_package')
    if kind == 'documento':
        title, body = row.title, row.body_md
        chunks_query = select(DocumentChunk.ordem, DocumentChunk.content_hash,
                              DocumentChunk.embedding_model).where(DocumentChunk.document_id == row.id)
    else:
        source = FONTES_POR_TIPO[kind]
        title, body = getattr(row, source.titulo_attr), source.texto(row)
        chunks_query = select(KnowledgeChunk.ordem, KnowledgeChunk.content_hash,
                              KnowledgeChunk.embedding_model).where(
                                  KnowledgeChunk.entity_type == kind, KnowledgeChunk.entity_id == row.id)
    fingerprint = fingerprint_fonte(title, body)
    expected_chunks = len(dividir(body or ''))
    if expected_chunks == 0:
        raise SourceGuardError('empty_indexable_source')
    chunks = db.execute(chunks_query).all()
    complete = (len(chunks) == expected_chunks
                and sorted(c[0] for c in chunks) == list(range(expected_chunks)))
    current = complete and all(esta_atualizado(c[1], c[2], fingerprint) for c in chunks)
    status = {'kind': kind, 'slug': slug, 'status': 'current' if current else 'pending',
              'fingerprint': fingerprint, 'chunks': len(chunks), 'expected_chunks': expected_chunks}
    return row, title, body, status


def safe_error(error):
    code = getattr(error, 'code', None)
    code = code if isinstance(code, str) and re.fullmatch(r'[A-Za-z0-9_.-]{1,100}', code) else None
    status = getattr(error, 'status_code', None)
    return {'error_type': type(error).__name__, 'code': code,
            'http_status': status if isinstance(status, int) else None}


def stop_reason(error):
    seen = set()
    while error is not None and id(error) not in seen:
        seen.add(id(error))
        if isinstance(error, SourceGuardError):
            return 'source_guard_failed'
        if isinstance(error, EmbeddingDimensionError):
            return 'embedding_configuration_error'
        if isinstance(error, (AIWalletError, AIUsageError)):
            return 'wallet_budget_or_usage_control'
        codes = [getattr(error, 'code', None)]
        body = getattr(error, 'body', None)
        if isinstance(body, dict):
            codes.append(body.get('code'))
            if isinstance(body.get('error'), dict):
                codes.append(body['error'].get('code'))
        if any(c in {'credit_balance_exhausted', 'insufficient_quota',
                     'billing_hard_limit_reached', 'budget_exceeded',
                     'monthly_budget_exceeded', 'quota_exceeded', 'rate_limit_exceeded'}
               for c in codes if isinstance(c, str)):
            return 'provider_quota_or_budget'
        if getattr(error, 'status_code', None) in (401, 402, 403, 429):
            return 'provider_access_quota_or_rate_limit'
        error = error.__cause__ or error.__context__
    return None


def scan(items):
    states = []
    # Explicit SQL read-only: even an accidental flush would be rejected.
    with SessionLocal() as db:
        db.execute(text('SET TRANSACTION READ ONLY'))
        verificar_dimensao_embedding(db)
        for item in items:
            try:
                states.append(inspect_item(db, item)[3])
            except SourceGuardError as error:
                kind, slug = identity(item)
                states.append({'kind': kind, 'slug': slug, 'status': 'guard_failed', **safe_error(error)})
        db.rollback()
    return states


def process(item):
    with SessionLocal() as db:
        row, title, body, before = inspect_item(db, item, lock_row=True)
        if before['status'] == 'current':
            db.rollback()
            return 0, before
        # These are the original ai_operation-decorated functions. The wallet,
        # catalog_index cost center, reservations and settlement remain active.
        # Force only this confirmed pending item: the library's fast path checks
        # one chunk and would otherwise miss an incomplete or mixed chunk set.
        if item['kind'] == 'documento':
            count = indexar_documento(db, row, forcar=True)
        else:
            count = indexar_entidade(db, entity_type=item['kind'], entity_id=row.id,
                                     titulo=title, texto=body, forcar=True)
        # The service commits its chunks. Refresh rather than trusting the ORM
        # identity cache if a queued editorial writer ran immediately afterward.
        after = inspect_item(db, item)[3]
        if after['status'] != 'current':
            raise SourceGuardError('index_not_current_after_write')
        db.rollback()
        return count, after


def save_report(path, report):
    report['updated_at'] = now()
    states = report['states']
    report['pending'] = [{'kind': s['kind'], 'slug': s['slug'], 'reason': s.get('code') or s['status']}
                         for s in states if s['status'] != 'current']
    report['counts'] = dict(Counter(s['status'] for s in states))
    report['pending_by_type'] = dict(Counter(s['kind'] for s in report['pending']))
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f'.{os.getpid()}.next')
    temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pack', type=Path)
    parser.add_argument('--sha256', required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check', action='store_true')
    mode.add_argument('--apply', action='store_true')
    parser.add_argument('--result', type=Path)
    args = parser.parse_args()
    items = read_pack(args.pack, args.sha256)
    report_path = args.result or Path(f'/tmp/corvia-scientific-20260910-rag-{"check" if args.check else "result"}.json')
    if report_path.resolve() == args.pack.resolve():
        raise ValueError('Result must not overwrite the approved package')
    report = {'release_id': RELEASE_ID, 'pack_sha256': args.sha256.lower(), 'records': len(items),
              'mode': 'check' if args.check else 'apply', 'started_at': now(), 'complete': False,
              'embedding_model': settings.openai_embedding_model, 'ai_enabled': bool(settings.ai_enabled),
              'lock_id': LOCK_ID, 'stats': {}, 'failures': [], 'stop_reason': None,
              'states': [{'kind': k, 'slug': s, 'status': 'not_checked'} for k, s in map(identity, items)]}
    save_report(report_path, report)
    lock = None
    acquired = False
    stats = Counter()
    exit_code = 0
    try:
        if args.apply:
            if not settings.ai_enabled:
                report['stop_reason'] = 'ai_disabled'
                return 2
            lock = engine.connect()
            acquired = bool(lock.execute(text('SELECT pg_try_advisory_lock(:key)'), {'key': LOCK_ID}).scalar())
            lock.commit()  # session lock persists without an idle transaction
            if not acquired:
                report['stop_reason'] = 'global_rag_lock_busy'
                return 3
        report['states'] = scan(items)
        save_report(report_path, report)
        if any(s['status'] == 'guard_failed' for s in report['states']):
            report['stop_reason'] = 'source_guard_failed'
            return 2
        if args.check:
            report['complete'] = not report['pending']
            return 0
        for index, item in enumerate(items):
            if report['states'][index]['status'] == 'current':
                stats['already_current'] += 1
                continue
            try:
                count, state = process(item)
                report['states'][index] = state
                stats['indexed' if count else 'already_current'] += 1
                stats['chunks_written'] += count
            except Exception as error:
                kind, slug = identity(item)
                failure = {'kind': kind, 'slug': slug, **safe_error(error)}
                report['failures'].append(failure)
                report['states'][index] = {**failure, 'status': 'failed'}
                stats['failed'] += 1
                report['stop_reason'] = stop_reason(error)
                if not report['stop_reason'] and stats['failed'] >= MAX_FAILURES:
                    report['stop_reason'] = 'three_failures_limit'
            stats['attempted'] += 1
            report['stats'] = dict(stats)
            save_report(report_path, report)
            if report['stop_reason']:
                break
            if stats['attempted'] % 25 == 0:
                print(json.dumps({'progress': dict(stats), 'remaining': len(report['pending'])}), flush=True)
        # Final read-only accounting also covers unattempted entries after a stop.
        report['states'] = scan(items)
        report['complete'] = all(s['status'] == 'current' for s in report['states'])
        exit_code = 1 if report['failures'] or not report['complete'] else 0
    except KeyboardInterrupt:
        report['stop_reason'] = 'operator_interrupted'
        exit_code = 130
    except Exception as error:
        report['stop_reason'] = stop_reason(error) or 'operational_error'
        report['fatal_error'] = safe_error(error)
        exit_code = 2
    finally:
        if lock is not None:
            try:
                if acquired:
                    lock.execute(text('SELECT pg_advisory_unlock(:key)'), {'key': LOCK_ID})
                    lock.commit()
            except Exception as error:
                # Never return a connection holding the session lock to the pool.
                lock.invalidate()
                report['lock_release_error'] = safe_error(error)
            finally:
                lock.close()
        report['stats'] = dict(stats)
        report['finished_at'] = now()
        save_report(report_path, report)
        print(json.dumps({'release_id': RELEASE_ID, 'mode': report['mode'],
                          'counts': report['counts'], 'stats': report['stats'],
                          'pending': report['pending'], 'failures': report['failures'],
                          'stop_reason': report['stop_reason'], 'report': str(report_path)},
                         ensure_ascii=False), flush=True)
    return exit_code


if __name__ == '__main__':
    raise SystemExit(main())
