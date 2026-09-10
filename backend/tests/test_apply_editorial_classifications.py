"""Real CLI transactions against the isolated QA database; no provider/network calls."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid

import pytest
from sqlalchemy import text

from app.core.db import SessionLocal
from app.models.content import Document
from app.models.guideline import Guideline, GuidelineLink

SCOPE = 'editorial_metadata_only_no_publication_authorization'
CAS_FIELDS = (
    'id', 'slug', 'title', 'kind', 'theme', 'tags', 'source_refs',
    'evidence_level', 'source_tier', 'review_status', 'published', 'version',
    'body_sha256', 'summary_sha256', 'title_sha256', 'source_metadata_sha256',
)


def _sha(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def _json_hash(value):
    return _sha(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False))


def _snapshot(row):
    expected = {key: row[key] for key in CAS_FIELDS if not key.endswith('_sha256')}
    expected.update(body_sha256=_sha(row['body_md'] or ''),
                    summary_sha256=_sha(row['summary'] or ''),
                    title_sha256=_sha(row['title'] or ''),
                    source_metadata_sha256=_json_hash({key: row[key] for key in
                        ('source_refs', 'source_tier', 'evidence_level')}))
    expected['cas_metadata_sha256'] = _json_hash(expected)
    return expected


def _write_ledger(directory, entries):
    claims = {entry['evidence_id']: {
        **{key: entry[key] for key in ('entity_type', 'slug', 'field', 'old_value', 'new_value', 'source_sha256')},
        'decision_basis': 'confirmed_publication_genre',
        'rationale': 'Synthetic bibliographic fixture; not clinical content.',
        'evidence': [{'url': entry['source_identity']['url'], 'type': 'test_fixture'}],
    } for entry in entries}
    evidence_path = directory / 'evidence.json'
    evidence_path.write_text(json.dumps({'schema_version': 1, 'scope': SCOPE, 'claims': claims}, ensure_ascii=False))
    registry = {'schema_version': 1, 'scope': SCOPE, 'decision_id': 'test-editorial-cli',
                'runtime_cas_fields': list(CAS_FIELDS), 'evidence_file': evidence_path.name,
                'evidence_sha256': hashlib.sha256(evidence_path.read_bytes()).hexdigest(),
                'entries': entries}
    path = directory / 'registry.json'
    path.write_text(json.dumps(registry, ensure_ascii=False))
    return path


@pytest.fixture
def runtime_ledger(tmp_path):
    # A shared fixture must never accidentally target the deployment database.
    assert os.environ.get('POSTGRES_DB', '').startswith('corvia_editorial_20260910_')
    marker = 'editorial-cli-' + uuid.uuid4().hex
    ids, guideline_ids, entries, before = [], [], [], {}
    with SessionLocal() as db:
        for number, target in enumerate(('estudo', 'revisao')):
            g = Guideline(slug=f'{marker}-{number}', org='TEST',
                titulo=f'Publicação sintética {number}: classificação, não conteúdo clínico',
                ano=2026, doi=f'10.0000/{marker}.{number}', url=f'https://example.test/{marker}/{number}',
                source_fingerprint=_sha(f'{marker}-source-{number}'), detection_status='analisada')
            db.add(g)
            db.flush()
            doc = Document(slug='corvia-intelligence-' + g.slug, title=f'Título íntegro {number}',
                kind='diretriz', theme='Fibrilação atrial', summary='Resumo sintético sem recomendação.',
                body_md='# Corpo imutável\n\nAcentuação: ação.\n```text\nintacto\n```',
                tags=['fixture', 'classificação'], source_refs=[g.url, 'https://doi.org/' + g.doi],
                evidence_level=None, source_tier='A', review_status='revisado' if number else 'pendente_revisao',
                published=bool(number), version=7)
            db.add(doc)
            db.flush()
            link = GuidelineLink(guideline_id=g.id, item_type='intelligence_document', item_id=doc.id,
                origem='intelligence', confirmado=True)
            db.add(link)
            db.flush()
            row = dict(db.execute(text('SELECT * FROM documents WHERE id=:id'), {'id': doc.id}).mappings().one())
            identity = {key: getattr(g, key) for key in ('slug', 'org', 'titulo', 'ano', 'doi', 'url', 'source_fingerprint')}
            entry = {'entity_type': 'documento', 'slug': doc.slug, 'field': 'kind', 'origin': 'intelligence_summary',
                     'old_value': 'diretriz', 'new_value': target, 'source_identity': identity,
                     'source_sha256': _json_hash(identity), 'evidence_id': f'fixture-{number}',
                     'expected_guideline_id': g.id, 'expected_link_id': link.id, 'expected': _snapshot(row)}
            ids.append(doc.id)
            guideline_ids.append(g.id)
            entries.append(entry)
            before[doc.id] = row
        db.commit()
    path = _write_ledger(tmp_path, entries)
    yield {'path': path, 'entries': entries, 'before': before, 'ids': ids}
    with SessionLocal() as db:
        db.execute(text("DELETE FROM audit_logs WHERE action IN ('editorial_kind_reclassified', 'editorial_kind_verified') AND entity_id LIKE :pattern"),
                   {'action': 'editorial_kind_reclassified', 'pattern': 'corvia-intelligence-' + marker + '%'})
        db.execute(text('DELETE FROM guideline_links WHERE guideline_id = ANY(:ids)'), {'ids': guideline_ids})
        db.execute(text('DELETE FROM documents WHERE id = ANY(:ids)'), {'ids': ids})
        db.execute(text('DELETE FROM guidelines WHERE id = ANY(:ids)'), {'ids': guideline_ids})
        db.commit()


def _cli(path, *, apply=False, check_read_only=False):
    args = ['--registry', str(path)] + (['--apply'] if apply else [])
    if check_read_only:
        # Invoke the actual main/parser with a probe of the actual transaction.
        code = '''from app.commands import apply_editorial_classifications as cli
from sqlalchemy import text
original = cli.plan_runtime_classifications
def probe(db, *args, **kwargs):
    assert db.execute(text("SHOW transaction_read_only")).scalar_one() == "on"
    return original(db, *args, **kwargs)
cli.plan_runtime_classifications = probe
cli.main()
'''
        command = [sys.executable, '-c', code, *args]
    else:
        command = [sys.executable, '-m', 'app.commands.apply_editorial_classifications', *args]
    return subprocess.run(command, capture_output=True, text=True, timeout=30, check=False)


def _success(result):
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout.strip().splitlines()[-1])


def _rows_and_audits(ledger):
    with SessionLocal() as db:
        rows = {r['id']: dict(r) for r in db.execute(text('SELECT * FROM documents WHERE id = ANY(:ids)'),
                       {'ids': ledger['ids']}).mappings()}
        audits = [dict(r) for r in db.execute(text("SELECT * FROM audit_logs WHERE action IN ('editorial_kind_reclassified', 'editorial_kind_verified') AND entity_id = ANY(:slugs) ORDER BY id"),
                    {'action': 'editorial_kind_reclassified', 'slugs': [e['slug'] for e in ledger['entries']]}).mappings()]
    return rows, audits


def test_dry_run_real_cli_is_read_only_and_leaves_no_audit(runtime_ledger):
    result = _success(_cli(runtime_ledger['path'], check_read_only=True))
    rows, audits = _rows_and_audits(runtime_ledger)
    assert result['mode'] == 'dry_run_read_only'
    assert result['planned_changes'] == 2 and result['changed'] == 0
    assert rows == runtime_ledger['before']
    assert audits == []


def test_apply_changes_only_kind_and_audits_each_change(runtime_ledger):
    result = _success(_cli(runtime_ledger['path'], apply=True))
    rows, audits = _rows_and_audits(runtime_ledger)
    assert result['changed'] == 2
    assert result['publication_changed'] is result['clinical_content_changed'] is False
    for entry in runtime_ledger['entries']:
        row = rows[entry['expected']['id']]
        assert row['kind'] == entry['new_value']
        assert {k: v for k, v in row.items() if k != 'kind'} == {
            k: v for k, v in runtime_ledger['before'][row['id']].items() if k != 'kind'}
    assert len(audits) == 2
    assert {a['entity_id'] for a in audits} == {e['slug'] for e in runtime_ledger['entries']}
    for audit in audits:
        assert audit['user_id'] is None
        assert audit['detail']['publication_changed'] is False
        assert audit['detail']['scope'] == SCOPE
        assert audit['detail']['old_kind'] == 'diretriz'
        entry = next(e for e in runtime_ledger['entries'] if e['slug'] == audit['entity_id'])
        assert audit['detail']['new_kind'] == entry['new_value']
        assert audit['detail']['body_sha256'] == entry['expected']['body_sha256']
        assert audit['detail']['source_sha256'] == entry['source_sha256']


def test_second_apply_is_idempotent_without_duplicate_audit(runtime_ledger):
    _success(_cli(runtime_ledger['path'], apply=True))
    before, audits_before = _rows_and_audits(runtime_ledger)
    result = _success(_cli(runtime_ledger['path'], apply=True))
    after, audits_after = _rows_and_audits(runtime_ledger)
    assert result['changed'] == 0 and result['retained_or_already_applied'] == 2
    assert before == after and audits_before == audits_after
    assert len(audits_after) == 2


@pytest.mark.parametrize('tamper', ['second_claim', 'second_snapshot'])
def test_second_tampered_claim_aborts_whole_batch(runtime_ledger, tamper):
    path = runtime_ledger['path']
    registry = json.loads(path.read_text())
    if tamper == 'second_claim':
        # A valid value for the field, but not the exact reviewed claim.
        registry['entries'][1]['new_value'] = 'documento'
        expected_error = 'does not prove this exact claim'
    else:
        # Internally valid hash, but reviewed bytes no longer match the actual second row.
        expected = registry['entries'][1]['expected']
        expected['body_sha256'] = _sha('tampered content')
        expected['cas_metadata_sha256'] = _json_hash({key: expected[key] for key in CAS_FIELDS})
        expected_error = 'content/metadata changed since review'
    path.write_text(json.dumps(registry, ensure_ascii=False))
    result = _cli(path, apply=True)
    assert result.returncode != 0 and expected_error in result.stderr
    rows, audits = _rows_and_audits(runtime_ledger)
    assert rows == runtime_ledger['before']
    assert audits == []


def _refresh_body(ledger, *, set_target_kind=False):
    entry = ledger['entries'][0]
    with SessionLocal() as db:
        db.execute(text('UPDATE documents SET body_md=:body, summary=:summary, version=version+1'
                        + (', kind=:kind' if set_target_kind else '') + ' WHERE id=:id'),
            {'id': entry['expected']['id'], 'body': '# Revisão futura legítima\nTexto preservado na reexecução.',
             'summary': 'Resumo revisto posteriormente.', 'kind': entry['new_value']})
        db.commit()


def test_audited_completion_accepts_later_body_refresh_as_noop(runtime_ledger):
    _success(_cli(runtime_ledger['path'], apply=True))
    _refresh_body(runtime_ledger)
    before, audits_before = _rows_and_audits(runtime_ledger)
    result = _success(_cli(runtime_ledger['path'], apply=True))
    after, audits_after = _rows_and_audits(runtime_ledger)
    assert result['changed'] == result['completion_markers_recorded'] == 0
    assert result['already_completed'] == 2
    assert before == after and audits_before == audits_after
    assert all(a['detail']['document_id'] in runtime_ledger['ids'] for a in audits_after)
    assert all(a['detail']['document_slug'] == a['entity_id'] for a in audits_after)


def test_target_kind_without_matching_audit_still_requires_original_snapshot(runtime_ledger):
    _refresh_body(runtime_ledger, set_target_kind=True)
    before, audits_before = _rows_and_audits(runtime_ledger)
    result = _cli(runtime_ledger['path'], apply=True)
    assert result.returncode != 0 and 'content/metadata changed since review' in result.stderr
    after, audits_after = _rows_and_audits(runtime_ledger)
    assert before == after and audits_before == audits_after == []


@pytest.mark.parametrize('drift', ['source', 'kind', 'audit_binding'])
def test_completion_audit_never_bypasses_identity_or_kind_drift(runtime_ledger, drift):
    _success(_cli(runtime_ledger['path'], apply=True))
    entry = runtime_ledger['entries'][0]
    with SessionLocal() as db:
        if drift == 'source':
            db.execute(text('UPDATE guidelines SET doi=:doi WHERE id=:id'),
                {'doi': '10.0000/different-source', 'id': entry['expected_guideline_id']})
        elif drift == 'kind':
            db.execute(text("UPDATE documents SET kind='protocolo' WHERE id=:id"),
                {'id': entry['expected']['id']})
        else:
            # A similar historical audit must not excuse a body that no longer matches.
            detail = db.execute(text('SELECT detail FROM audit_logs WHERE entity_id=:slug'),
                                {'slug': entry['slug']}).scalar_one()
            detail['evidence_sha256'] = '0' * 64
            db.execute(text('UPDATE audit_logs SET detail=CAST(:detail AS jsonb) WHERE entity_id=:slug'),
                       {'detail': json.dumps(detail), 'slug': entry['slug']})
        db.commit()
    if drift == 'audit_binding':
        _refresh_body(runtime_ledger)
    before, audits_before = _rows_and_audits(runtime_ledger)
    result = _cli(runtime_ledger['path'], apply=True)
    assert result.returncode != 0
    expected_error = {'source': 'publication identity changed', 'kind': 'kind changed since review',
                      'audit_binding': 'content/metadata changed since review'}[drift]
    assert expected_error in result.stderr
    after, audits_after = _rows_and_audits(runtime_ledger)
    assert before == after and audits_before == audits_after


def test_retained_classification_records_one_idempotent_completion(runtime_ledger):
    entries = runtime_ledger['entries']
    entries[1]['new_value'] = entries[1]['old_value']
    _write_ledger(runtime_ledger['path'].parent, entries)
    first = _success(_cli(runtime_ledger['path'], apply=True))
    before, audits_before = _rows_and_audits(runtime_ledger)
    assert first['changed'] == 1 and first['completion_markers_recorded'] == 2
    assert len(audits_before) == 2
    assert {a['action'] for a in audits_before} == {'editorial_kind_reclassified', 'editorial_kind_verified'}
    retained = next(a for a in audits_before if a['action'] == 'editorial_kind_verified')
    assert retained['detail']['document_id'] == entries[1]['expected']['id']
    assert retained['detail']['old_kind'] == retained['detail']['new_kind'] == 'diretriz'
    second = _success(_cli(runtime_ledger['path'], apply=True))
    after, audits_after = _rows_and_audits(runtime_ledger)
    assert second['changed'] == second['completion_markers_recorded'] == 0
    assert second['already_completed'] == 2
    assert before == after and audits_before == audits_after
