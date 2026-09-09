"""Incremental RAG refresh limited to the exact reviewed publication package."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter
import hashlib
import json
from pathlib import Path
from threading import Event

from sqlalchemy import select, text
from app.core.config import settings
from app.core.db import SessionLocal, engine
from app.models.content import Document
from app.models.rag import DocumentChunk, KnowledgeChunk
from app.services.rag import indexar_documento, fingerprint_fonte, esta_atualizado
from app.services.rag_multi import indexar_entidade
from app.services.rag_sources import FONTES_POR_TIPO

STOP_REQUESTED = Event()


def process(item, verify_only=False):
    if STOP_REQUESTED.is_set() and not verify_only:
        return None
    kind, slug = item['kind'], item['data']['slug']
    with SessionLocal() as db:
        model = Document if kind == 'documento' else FONTES_POR_TIPO[kind].model
        row = db.execute(select(model).where(model.slug == slug)).scalar_one()
        if not row.published or row.review_status != 'revisado':
            raise ValueError(f'Unpublished/unreviewed source: {kind}:{slug}')
        # A concurrent editorial change must not silently enter this scoped run.
        if any(getattr(row, k) != v for k, v in item['data'].items()):
            raise ValueError(f'Published source differs from approved package: {kind}:{slug}')
        if kind == 'documento':
            title, body = row.title, row.body_md
            query = select(DocumentChunk.content_hash, DocumentChunk.embedding_model).where(DocumentChunk.document_id == row.id)
        else:
            source = FONTES_POR_TIPO[kind]
            title, body = getattr(row, source.titulo_attr), source.texto(row)
            query = select(KnowledgeChunk.content_hash, KnowledgeChunk.embedding_model).where(KnowledgeChunk.entity_type == kind, KnowledgeChunk.entity_id == row.id)
        if verify_only:
            chunks = db.execute(query).all()
            return bool(chunks) and all(esta_atualizado(h, m, fingerprint_fonte(title, body)) for h, m in chunks)
        if kind == 'documento':
            count = indexar_documento(db, row)
        else:
            count = indexar_entidade(db, entity_type=kind, entity_id=row.id, titulo=title, texto=body)
        return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pack', type=Path)
    parser.add_argument('--sha256', required=True)
    args = parser.parse_args()
    raw = args.pack.read_bytes()
    if hashlib.sha256(raw).hexdigest() != args.sha256:
        raise ValueError('Package checksum mismatch')
    pack = json.loads(raw)
    if pack['release_id'] != 'scientific-20260909' or not pack['ready']:
        raise ValueError('Unapproved package')
    if not settings.ai_enabled:
        raise RuntimeError('AI indexing is disabled on this server')
    stats, failures = Counter(), []
    with engine.connect() as lock:
        if not lock.execute(text('SELECT pg_try_advisory_lock(771103090)')).scalar():
            raise RuntimeError('Another RAG backfill is already running')
        try:
            with ThreadPoolExecutor(max_workers=4) as pool:
                futures = {pool.submit(process, item): item for item in pack['items']}
                consecutive_failures = 0
                for future in as_completed(futures):
                    item = futures[future]
                    try:
                        count = future.result()
                        if count is None:
                            stats['deferred'] += 1
                        else:
                            consecutive_failures = 0
                            stats['updated' if count else 'unchanged'] += 1
                            stats['chunks_written'] += count
                    except Exception as error:
                        code = getattr(error, 'code', None)
                        failures.append({'kind':item['kind'], 'slug':item['data']['slug'], 'error_type':type(error).__name__, 'code':code})
                        consecutive_failures += 1
                        if code in ('credit_balance_exhausted', 'insufficient_quota') or consecutive_failures >= 3:
                            STOP_REQUESTED.set()
                    stats['completed'] += 1
                    if stats['completed'] % 25 == 0:
                        print(json.dumps(dict(stats)), flush=True)
            stale = []
            for item in pack['items']:
                try:
                    if not process(item, verify_only=True):
                        stale.append([item['kind'], item['data']['slug']])
                except Exception as error:
                    stale.append([item['kind'], item['data']['slug'], type(error).__name__])
            result = {'pack_sha256':args.sha256, 'records':len(pack['items']), 'stats':dict(stats), 'failures':failures, 'stale':stale}
            Path('/tmp/corvia-scientific-rag-result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
            print(json.dumps(result, ensure_ascii=False), flush=True)
            if failures or stale:
                raise SystemExit(1)
        finally:
            lock.execute(text('SELECT pg_advisory_unlock(771103090)'))


if __name__ == '__main__':
    main()
