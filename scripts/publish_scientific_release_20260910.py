"""Publish only the frozen, independently reviewed scientific-20260910 package.

PACK requires ready=true and exactly 398 items (395 documents, two cases,
one patient material). Each item contains kind, data and source_expected.
source_expected is null for a record absent from the source snapshot, otherwise
an object containing every data field plus updated_at and version when present.
Additional real model columns are compared too. Datetimes are compared in UTC.
An existing row already equal to every packaged data field is an idempotent retry.

--check uses a PostgreSQL READ ONLY transaction and always rolls back: no flush,
sequence allocation, content/graph write, revision, or durable backup is made.
--apply repeats all preconditions under row locks, writes a scoped backup, then
publishes content and explicit TCT edges in one transaction. No corpus reconciliation,
human reviewer attribution, pruning, or unrelated draft publication is performed.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
import gzip
import hashlib
import json
import os
from pathlib import Path
import re

from sqlalchemy import DateTime, select, text, tuple_
from app.core.db import SessionLocal
from app.models.content import Document, DocumentRevision
from app.models.study import ScientificStudy
from app.models.evidence import EvidenceRecord
from app.models.clinical_case import ClinicalCase
from app.models.lab_test import LabTest
from app.models.study_track import StudyTrack
from app.models.patient_material import PatientMaterial
from app.models.knowledge import KnowledgeEntity, KnowledgeRelation
from app.services.canonical_themes import TEMAS_CANONICOS
from app.services.knowledge_graph import registrar_entidade, registrar_relacao
from app.services.knowledge_relation_policy import validar_relacao_clinica

MODELS = {'documento': Document, 'estudo': ScientificStudy,
          'evidencia': EvidenceRecord, 'caso_clinico': ClinicalCase,
          'exame': LabTest, 'trilha': StudyTrack, 'material_paciente': PatientMaterial}
FORBIDDEN = {'id', 'reviewed_by', 'reviewed_at', 'created_at', 'updated_at',
             'version', 'search_vector', 'author_id'}
RELEASE_ID = 'scientific-20260910'
EXPECTED_COUNTS = {'documento': 395, 'caso_clinico': 2, 'material_paciente': 1}
LOCK_ID = 90920261800  # Shared with the previous scoped scientific publisher.
REVIEW_METHOD = 'Revisão editorial e bibliográfica assistida por Codex; publicação autorizada pelo proprietário.'


def serial(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    raise TypeError(f'Cannot serialize {type(value).__name__}')


def normalized(value, column):
    if value is not None and isinstance(column.type, DateTime):
        if isinstance(value, str):
            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
        if not isinstance(value, datetime):
            raise ValueError(f'Invalid datetime for {column.key}')
        if column.type.timezone and value.tzinfo is None:
            raise ValueError(f'Timezone missing for {column.key}')
        return value.astimezone(timezone.utc) if value.tzinfo else value
    return value


def fields_equal(row, values):
    columns = row.__table__.columns
    return all(normalized(getattr(row, field), columns[field]) == normalized(value, columns[field])
               for field, value in values.items())


def row_data(row):
    return {column.key: getattr(row, column.key) for column in row.__table__.columns}


def validate_expected(item):
    if 'source_expected' not in item:
        raise ValueError(f'Missing source_expected: {item["data"]["slug"]}')
    expected = item['source_expected']
    if expected is None:
        return
    if not isinstance(expected, dict):
        raise ValueError('source_expected must be an object or null')
    columns = MODELS[item['kind']].__table__.columns
    unknown = set(expected) - set(columns.keys())
    required = set(item['data']) | ({'updated_at', 'version'} & set(columns.keys()))
    if unknown or required - set(expected):
        raise ValueError(f'Incomplete/unknown source guard {item["data"]["slug"]}: missing={sorted(required-set(expected))}, unknown={sorted(unknown)}')
    if expected['slug'] != item['data']['slug']:
        raise ValueError('Source identity differs from packaged identity')
    for field, value in expected.items():
        normalized(value, columns[field])


def guard_source(item, row):
    # A successful previous application changed timestamps/version. Only exact
    # packaged data permits retry without the original snapshot precondition.
    if row is not None and fields_equal(row, item['data']):
        return 'unchanged'
    expected = item['source_expected']
    if row is None:
        if expected is not None:
            raise ValueError(f'Source disappeared: {item["kind"]}:{item["data"]["slug"]}')
        return 'created'
    if expected is None:
        raise ValueError(f'Unexpected existing source: {item["kind"]}:{item["data"]["slug"]}')
    if not fields_equal(row, expected):
        columns = row.__table__.columns
        changed = [field for field, value in expected.items()
                   if normalized(getattr(row, field), columns[field]) != normalized(value, columns[field])]
        raise ValueError(f'Concurrent source change: {item["kind"]}:{row.slug}: {changed}')
    return 'updated'


def node_type(kind, data):
    return 'fluxograma' if kind == 'documento' and data.get('kind') == 'fluxograma' else kind


def relation_extra(digest, edge):
    return {'release_id': RELEASE_ID, 'pack_sha256': digest,
            'clinical_reason': edge['reason'], 'review_method': REVIEW_METHOD}

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
    if kind == 'documento' and (not data.get('body_md', '').strip() or data.get('gaps')):
        raise ValueError(f'Empty body or unresolved gaps: {data["slug"]}')
    if kind == 'material_paciente' and (not data.get('documento_slug') or not data.get('secoes')):
        raise ValueError(f'Patient material needs sections and its technical document: {data["slug"]}')
    if kind == 'caso_clinico':
        choices = data.get('opcoes') or []
        answer = data.get('resposta_correta')
        if len(choices) < 2 or type(answer) is not int or not 0 <= answer < len(choices):
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
    parser.add_argument('--backup-dir', type=Path, default=Path('/tmp'))
    args = parser.parse_args()
    raw = args.pack.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != args.sha256.lower():
        raise ValueError('Package checksum mismatch.')
    pack = json.loads(raw)
    if pack.get('release_id') != RELEASE_ID or pack.get('ready') is not True:
        raise ValueError('Unexpected or unapproved release.')
    if pack.get('pending_source_indices') or pack.get('errors'):
        raise ValueError('Package still has unresolved review findings.')
    if not isinstance(pack.get('items'), list) or not isinstance(pack.get('relations'), list):
        raise ValueError('items and relations must be lists.')
    counts = Counter(item['kind'] for item in pack['items'])
    if dict(counts) != EXPECTED_COUNTS or len(pack['items']) != 398:
        raise ValueError(f'Unexpected release composition: {dict(counts)}')
    items = {(item['kind'], item['data']['slug']): item for item in pack['items']}
    if len(items) != len(pack['items']):
        raise ValueError('Duplicate typed identities.')
    for item in items.values():
        validate_item(item['kind'], item['data'])
        validate_expected(item)
    edges, seen_edges = [], set()
    for edge in pack['relations']:
        identity = (edge['source_type'], edge['source_slug'], edge['target_type'],
                    edge['target_slug'], edge['relation_type'])
        if not isinstance(edge.get('reason'), str) or not edge['reason'].strip():
            raise ValueError('Every relationship needs its reviewed clinical reason.')
        source, target = identity[:2], identity[2:4]
        if source == target or not ({source, target} & set(items)):
            raise ValueError(f'Unscoped/self relationship: {identity}')
        if source[0] not in MODELS or target[0] not in MODELS:
            raise ValueError(f'Unmanaged reference type: {identity}')
        if identity not in seen_edges:
            seen_edges.add(identity)
            edges.append(edge)
    db = SessionLocal()
    now = datetime.now(timezone.utc)
    stamp = now.strftime('%Y%m%d-%H%M%S-%f')
    backup_path = args.backup_dir / f'corvia-{RELEASE_ID}-before-{stamp}.json.gz'
    result_path = args.backup_dir / f'corvia-{RELEASE_ID}-result-{stamp}.json'
    try:
        if args.check:
            db.execute(text('SET TRANSACTION READ ONLY'))
        if not db.execute(text('SELECT pg_try_advisory_xact_lock(:key)'), {'key': LOCK_ID}).scalar():
            raise RuntimeError('Another scoped scientific publication is in progress.')
        existing = {}
        reference_keys = set(items)
        for edge in edges:
            reference_keys.update({(edge['source_type'], edge['source_slug']),
                                   (edge['target_type'], edge['target_slug'])})
        for item in items.values():
            if item['kind'] == 'material_paciente':
                reference_keys.add(('documento', item['data']['documento_slug']))
        for kind in sorted({key[0] for key in reference_keys}):
            model = MODELS[kind]
            slugs = sorted(slug for key_kind, slug in reference_keys if key_kind == kind)
            query = select(model).where(model.slug.in_(slugs)).order_by(model.slug)
            if args.apply:
                query = query.with_for_update()
            for row in db.execute(query).scalars():
                existing[(kind, row.slug)] = row
        stats = Counter()
        outcomes = {}
        for key, item in items.items():
            outcomes[key] = guard_source(item, existing.get(key))
            stats[f'{key[0]}:{outcomes[key]}'] += 1
        projected = {key: item['data'] for key, item in items.items()}
        anchors = set()
        for key in reference_keys:
            row = existing.get(key)
            if key not in items:
                if row is None or row.published is not True or row.review_status != 'revisado':
                    raise ValueError(f'Reference is not currently published and reviewed: {key}')
                projected[key] = row_data(row)
            if row is not None and row.published is True and row.review_status == 'revisado':
                anchors.add(key)
        evidence_source = f'{RELEASE_ID}:{digest}'
        covered, adjacency = set(), defaultdict(set)
        for edge in edges:
            source = (edge['source_type'], edge['source_slug'])
            target = (edge['target_type'], edge['target_slug'])
            validar_relacao_clinica(
                source_type=node_type(source[0], projected[source]),
                target_type=node_type(target[0], projected[target]),
                relation_type=edge['relation_type'], relevance_score=0.95,
                provenance_type='imported', confidence='explicit', review_status='revisado',
                evidence_source=evidence_source, extra=relation_extra(digest, edge))
            covered.update({source, target})
            adjacency[source].add(target)
            adjacency[target].add(source)
        if set(items) - covered:
            raise ValueError(f'Records without an explicit relationship: {sorted(set(items)-covered)}')
        visited = set()
        for key in items:
            if key in visited:
                continue
            component, todo = set(), [key]
            while todo:
                current = todo.pop()
                if current in component:
                    continue
                component.add(current)
                todo.extend(adjacency[current] - component)
            visited |= component
            if not component & anchors:
                raise ValueError(f'Release component without a currently published anchor: {sorted(component)}')

        # Capture only graph rows this package may change; reject previously
        # rejected edges rather than silently reviving editorial rejections.
        entity_keys = {(node_type(key[0], projected[key]), row.id): key
                       for key, row in existing.items()}
        entities_before, entity_by_content, relations_before = [], {}, []
        if entity_keys:
            query = select(KnowledgeEntity).where(
                tuple_(KnowledgeEntity.entity_type, KnowledgeEntity.canonical_id).in_(sorted(entity_keys)))
            if args.apply:
                query = query.with_for_update()
            for entity in db.execute(query).scalars():
                entities_before.append(row_data(entity))
                key = entity_keys[(entity.entity_type, entity.canonical_id)]
                entity_by_content[key] = entity
        relation_keys = set()
        for edge in edges:
            source = entity_by_content.get((edge['source_type'], edge['source_slug']))
            target = entity_by_content.get((edge['target_type'], edge['target_slug']))
            if source is not None and target is not None:
                relation_keys.add((source.id, target.id, edge['relation_type']))
        if relation_keys:
            query = select(KnowledgeRelation).where(tuple_(
                KnowledgeRelation.source_entity_id, KnowledgeRelation.target_entity_id,
                KnowledgeRelation.relation_type).in_(sorted(relation_keys)))
            if args.apply:
                query = query.with_for_update()
            for relation in db.execute(query).scalars():
                if relation.review_status == 'rejeitado':
                    raise ValueError(f'Explicit edge was previously rejected: relation_id={relation.id}')
                relations_before.append(row_data(relation))
        result = {'release_id': RELEASE_ID, 'pack_sha256': digest,
                  'mode': 'apply' if args.apply else 'check', 'records': len(items),
                  'source_files': pack.get('source_count', len(items)), 'stats': dict(stats),
                  'verified_relations': len(edges), 'unlinked': 0,
                  'backup': str(backup_path) if args.apply else None}
        if args.check:
            db.rollback()
            result['completed_at'] = datetime.now(timezone.utc).isoformat()
            result['durable_writes'] = 0
            print(json.dumps(result, ensure_ascii=False), flush=True)
            return

        backup = {'release_id': RELEASE_ID, 'pack_sha256': digest, 'created_at': now,
                  'previous_records': [{'kind': key[0], 'data': row_data(existing[key])}
                                       for key in sorted(items) if key in existing],
                  'new_record_keys': [list(key) for key in sorted(items) if key not in existing],
                  'previous_graph_entities': entities_before,
                  'previous_graph_relations': relations_before,
                  'planned_relations': edges}
        args.backup_dir.mkdir(parents=True, exist_ok=True)
        with backup_path.open('xb') as output:
            output.write(gzip.compress(json.dumps(backup, ensure_ascii=False, default=serial).encode()))
            output.flush()
            os.fsync(output.fileno())
        print(json.dumps({'backup': str(backup_path), 'previous_records': len(backup['previous_records'])}), flush=True)
        records = dict(existing)
        for key, item in items.items():
            data = item['data']
            if outcomes[key] == 'unchanged':
                continue
            row = records.get(key)
            if row is None:
                row = MODELS[key[0]](**data)
                db.add(row)
                records[key] = row
            else:
                if key[0] == 'documento' and row.body_md != data['body_md']:
                    db.add(DocumentRevision(document_id=row.id, version=row.version,
                                            body_md=row.body_md, author_id=None))
                    row.version += 1
                if key[0] == 'material_paciente':
                    row.version += 1
                if hasattr(row, 'reviewed_by'):
                    row.reviewed_by = None
                if hasattr(row, 'reviewed_at'):
                    row.reviewed_at = None
                for field, value in data.items():
                    setattr(row, field, value)
        db.flush()
        entities = {}
        def node(kind, slug):
            key = (kind, slug)
            if key not in entities:
                row = records[key]
                title = (getattr(row, 'title', None) or getattr(row, 'titulo', None)
                         or getattr(row, 'name', None) or getattr(row, 'statement', slug)[:250])
                entities[key] = registrar_entidade(db, entity_type=node_type(kind, projected[key]),
                                                   canonical_id=row.id, slug=slug, title=title)
            return entities[key]
        for edge in edges:
            source = node(edge['source_type'], edge['source_slug'])
            target = node(edge['target_type'], edge['target_slug'])
            relation = registrar_relacao(
                db, source=source, target=target, relation_type=edge['relation_type'],
                provenance_type='imported', confidence='explicit', review_status='revisado',
                relevance_score=0.95, evidence_source=evidence_source,
                extra=relation_extra(digest, edge))
            if relation is None or relation.review_status == 'rejeitado':
                raise ValueError('Relationship unavailable or rejected during application.')
            if relation.review_status != 'revisado':
                relation.review_status = 'revisado'
                relation.provenance_type = 'imported'
                relation.confidence = 'explicit'
                relation.evidence_source = evidence_source
                relation.extra = {**(relation.extra or {}), **relation_extra(digest, edge)}
        db.flush()
        for key, item in items.items():
            if not fields_equal(records[key], item['data']):
                raise ValueError(f'Applied record differs from exact approved data: {key}')
        db.commit()
        result['completed_at'] = datetime.now(timezone.utc).isoformat()
        result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
        print(json.dumps(result, ensure_ascii=False), flush=True)
    except BaseException:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == '__main__':
    main()
