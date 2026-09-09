"""Publish the fixed, reviewed September 9 release, without corpus reconciliation.

Run inside the backend container with its installed application:
  python /tmp/publish_scientific_release_20260909.py PACK --sha256 HASH --check
  python /tmp/publish_scientific_release_20260909.py PACK --sha256 HASH --apply

The owner authorized this exact review/publication in the originating task.
No patient models, human reviewer identity, pruning, or unrelated drafts are used.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import re
import sys

from sqlalchemy import select, text
from app.core.db import SessionLocal
from app.models.content import Document, DocumentRevision
from app.models.study import ScientificStudy
from app.models.evidence import EvidenceRecord
from app.models.clinical_case import ClinicalCase
from app.models.lab_test import LabTest
from app.models.study_track import StudyTrack
from app.models.patient_material import PatientMaterial
from app.services.canonical_themes import TEMAS_CANONICOS
from app.services.knowledge_graph import registrar_entidade, registrar_relacao

MODELS = {'documento': Document, 'estudo': ScientificStudy,
          'evidencia': EvidenceRecord, 'caso_clinico': ClinicalCase,
          'exame': LabTest, 'trilha': StudyTrack, 'material_paciente': PatientMaterial}
FORBIDDEN = {'id', 'reviewed_by', 'reviewed_at', 'created_at', 'updated_at',
             'version', 'search_vector', 'author_id'}
RELEASE_ID = 'scientific-20260909'

def serial(value):
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)

def validate_item(kind, data):
    model = MODELS[kind]
    columns = {c.key: c for c in model.__table__.columns}
    unknown = set(data) - set(columns)
    if unknown or set(data) & FORBIDDEN:
        raise ValueError(f'{kind}:{data.get("slug")}: forbidden/unknown fields {unknown | (set(data) & FORBIDDEN)}')
    if data.get('review_status') != 'revisado' or data.get('published') is not True:
        raise ValueError('Every packaged record must be explicitly reviewed and approved.')
    if data.get('theme', data.get('tema')) not in TEMAS_CANONICOS:
        raise ValueError(f'Noncanonical theme: {kind}:{data["slug"]}')
    for name, column in columns.items():
        value = data.get(name)
        if name not in data:
            if not column.nullable and column.default is None and not column.primary_key and name not in FORBIDDEN:
                raise ValueError(f'Missing required field {kind}:{data["slug"]}:{name}')
            continue
        if value is None and not column.nullable:
            raise ValueError(f'Null required field {kind}:{data["slug"]}:{name}')
        limit = getattr(column.type, 'length', None)
        if limit and isinstance(value, str) and len(value) > limit:
            raise ValueError(f'Field too long {kind}:{data["slug"]}:{name} ({len(value)}>{limit})')
    raw = json.dumps(data, ensure_ascii=False)
    if re.search(r'verifica[çc][ãa]o humana necess[áa]ria|aguardando revis[ãa]o', raw, re.I):
        raise ValueError(f'Unresolved review marker: {kind}:{data["slug"]}')
    if kind == 'caso_clinico':
        choices = data.get('opcoes') or []
        answer = data.get('resposta_correta')
        if len(choices) < 2 or not isinstance(answer, int) or not 0 <= answer < len(choices):
            raise ValueError(f'Invalid case answer: {data["slug"]}')
    if kind == 'trilha':
        stages = data.get('etapas') or []
        identities = {(s.get('item_type'), s.get('item_slug')) for s in stages}
        if not stages or len(identities) != len(stages) or any(not s.get('por_que') for s in stages):
            raise ValueError(f'Invalid track stages: {data["slug"]}')
    if kind == 'exame' and data['category'] not in ('laboratorial', 'metodo_grafico', 'imagem'):
        raise ValueError(f'Invalid exam category: {data["slug"]}')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pack', type=Path)
    parser.add_argument('--sha256', required=True)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--check', action='store_true')
    action.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    raw = args.pack.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != args.sha256:
        raise ValueError('Package checksum mismatch.')
    pack = json.loads(raw)
    if pack.get('release_id') != RELEASE_ID:
        raise ValueError('Unexpected release ID.')
    if not pack.get('ready') or pack.get('pending_source_indices') or pack.get('errors'):
        raise ValueError('The package has not passed its complete review and relationship audit.')
    keys = [(r['kind'], r['data']['slug']) for r in pack['items']]
    if len(keys) != len(set(keys)):
        raise ValueError('Duplicate typed identities in release.')
    for r in pack['items']:
        validate_item(r['kind'], r['data'])
    db = SessionLocal()
    stats = Counter()
    now = datetime.now(timezone.utc)
    stamp = now.strftime('%Y%m%d-%H%M%S')
    backup_path = Path('/tmp') / f'corvia-scientific-before-{stamp}.json.gz'
    result_path = Path('/tmp') / f'corvia-scientific-result-{stamp}.json'
    try:
        if not db.execute(text('SELECT pg_try_advisory_xact_lock(90920261800)')).scalar():
            raise RuntimeError('Another publication of this release is in progress.')
        existing = {}
        backups = []
        for kind, model in MODELS.items():
            slugs = [slug for k, slug in keys if k == kind]
            if not slugs:
                continue
            for row in db.execute(select(model).where(model.slug.in_(slugs)).with_for_update()).scalars():
                existing[(kind, row.slug)] = row
                backups.append({'kind':kind, 'data':{c.key:getattr(row,c.key) for c in model.__table__.columns}})
        # Backup stays on the production host; it includes only these scientific rows.
        backup_payload = {'release_id':RELEASE_ID, 'pack_sha256':digest, 'created_at':now,
                          'previous_records':backups, 'new_record_keys':[list(k) for k in keys if k not in existing]}
        if args.apply:
            with backup_path.open('xb') as output:
                output.write(gzip.compress(json.dumps(backup_payload, ensure_ascii=False, default=serial).encode()))
            print(json.dumps({'backup':str(backup_path),'previous_records':len(backups)},ensure_ascii=False),flush=True)
        records = dict(existing)
        for item in pack['items']:
            kind, data = item['kind'], item['data']
            key = (kind, data['slug'])
            record = records.get(key)
            if record is None:
                record = MODELS[kind](**data)
                db.add(record)
                records[key] = record
                stats[f'{kind}:created'] += 1
            else:
                changed = any(getattr(record,k) != v for k,v in data.items())
                if kind == 'documento' and record.body_md != data['body_md']:
                    db.add(DocumentRevision(document_id=record.id, version=record.version,
                                            body_md=record.body_md, author_id=None))
                    record.version += 1
                if kind == 'material_paciente' and changed:
                    record.version += 1
                if changed and hasattr(record, 'reviewed_by'):
                    record.reviewed_by = None  # never attribute a new revision to an old human reviewer
                if changed and hasattr(record, 'reviewed_at'):
                    record.reviewed_at = None
                for k,v in data.items():
                    setattr(record,k,v)
                stats[f'{kind}:updated' if changed else f'{kind}:unchanged'] += 1
        db.flush()

        def resolve(kind, slug):
            key = (kind,slug)
            row = records.get(key)
            if row is None:
                if kind not in MODELS:
                    raise ValueError(f'Unmanaged reference type: {kind}:{slug}')
                row = db.execute(select(MODELS[kind]).where(MODELS[kind].slug==slug)).scalar_one_or_none()
                if row is None or not row.published:
                    raise ValueError(f'Reference is not published: {kind}:{slug}')
                records[key] = row
            return row

        for item in pack['items']:
            k,d=item['kind'],item['data']
            if k=='trilha':
                for e in d['etapas']:
                    resolve(e['item_type'],e['item_slug'])
            if k=='evidencia':
                for f,t in [('study_slug','estudo'),('document_slug','documento')]:
                    if d.get(f):resolve(t,d[f])
            if k=='material_paciente' and d.get('documento_slug'):
                resolve('documento',d['documento_slug'])
        entities={}
        def node(kind,slug):
            key=(kind,slug)
            if key not in entities:
                row=resolve(kind,slug)
                entity_type='fluxograma' if kind=='documento' and row.kind=='fluxograma' else kind
                title=getattr(row,'title',None) or getattr(row,'titulo',None) or getattr(row,'name',None) or getattr(row,'statement',slug)[:250]
                entities[key]=registrar_entidade(db,entity_type=entity_type,canonical_id=row.id,slug=slug,title=title)
            return entities[key]
        covered=set()
        for edge in pack['relations']:
            source=node(edge['source_type'],edge['source_slug'])
            target=node(edge['target_type'],edge['target_slug'])
            relation=registrar_relacao(db,source=source,target=target,
                relation_type=edge['relation_type'],provenance_type='imported',confidence='explicit',
                review_status='revisado',relevance_score=0.95,
                evidence_source=f'{RELEASE_ID}:{digest}',
                extra={'release_id':RELEASE_ID,'pack_sha256':digest,'clinical_reason':edge['reason'],
                       'review_method':'Revisão editorial e bibliográfica assistida por Codex; publicação autorizada pelo proprietário.'})
            if relation is not None and relation.review_status!='rejeitado':
                if relation.review_status != 'revisado':
                    # Promote only this exact, now verified and traceable relationship.
                    relation.review_status = 'revisado'
                    relation.provenance_type = 'imported'
                    relation.confidence = 'explicit'
                    relation.evidence_source = f'{RELEASE_ID}:{digest}'
                    relation.extra = {**(relation.extra or {}), 'release_id':RELEASE_ID,
                                      'pack_sha256':digest, 'clinical_reason':edge['reason'],
                                      'review_method':'Revisão editorial e bibliográfica assistida por Codex; publicação autorizada pelo proprietário.'}
                covered.add((edge['source_type'],edge['source_slug']))
                covered.add((edge['target_type'],edge['target_slug']))
                stats['verified_relations']+=1
        missing=set(keys)-covered
        if missing:
            raise ValueError(f'Records without an active explicit relationship: {sorted(missing)}')
        db.flush()
        for kind,slug in keys:
            record=records[(kind,slug)]
            if not record.published or record.review_status!='revisado':
                raise ValueError(f'Publication did not persist in transaction: {kind}:{slug}')
        result={'release_id':RELEASE_ID,'pack_sha256':digest,'mode':'apply' if args.apply else 'check',
                'records':len(keys),'source_files':pack['source_count'],'stats':dict(stats),
                'unlinked':0,'backup':str(backup_path) if args.apply else None,
                'completed_at':datetime.now(timezone.utc).isoformat()}
        if args.apply:
            db.commit()
            result_path.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        else:
            db.rollback()
        print(json.dumps(result,ensure_ascii=False),flush=True)
    except BaseException:
        db.rollback()
        raise
    finally:
        db.close()

if __name__=='__main__':
    main()
