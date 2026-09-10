"""Exercise the actual manifest function with isolated collaborators.

These are focused function-contract tests, not HTTP/API or database integration.
The production get_entity eligibility call is retained and its rejection is
verified; no application setup, paid providers, or database sessions are loaded.
"""
import ast
import re
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import quote
import pytest

SOURCE_KEY = 'a' * 64
ENTITY_TYPE = 'publicacao_original'
BASE = '/api/scientific-reading/' + ENTITY_TYPE + '/' + SOURCE_KEY + '/sources/' + SOURCE_KEY


def manifest_function(asset, *, reject_entity=False):
    path = Path(__file__).parents[1] / 'app/services/scientific_reading.py'
    node = next(item for item in ast.parse(path.read_text()).body if isinstance(item, ast.FunctionDef) and item.name == 'reading_manifest')
    calls = []
    def get_entity(db, entity_type, slug):
        calls.append((entity_type, slug))
        if reject_entity: raise LookupError('published source is not eligible')
        return SimpleNamespace(slug=SOURCE_KEY)
    query = SimpleNamespace(filter=lambda *args: SimpleNamespace(all=lambda: [asset]))
    db = SimpleNamespace(query=lambda *args: query)
    ns = {'quote': quote, 're': re, 'get_entity': get_entity,
          'entity_sources': lambda *args: [{'key': SOURCE_KEY, 'doi': '10.36660/abc.20250621', 'url': 'https://doi.org/10.36660/abc.20250621'}],
          'ScientificPublicationAsset': SimpleNamespace(source_key=SimpleNamespace(in_=lambda keys: keys)),
          'editorial_summary': lambda row: None}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])), str(path), 'exec'), ns)
    return lambda: ns['reading_manifest'](db, ENTITY_TYPE, SOURCE_KEY), calls


@pytest.mark.parametrize('source_format,media,suffix,read_variant', [
    ('jats_xml', 'application/xml', 'xml', 'original-text'),
    ('pdf', 'application/pdf', 'pdf', 'original-text'),
])
def test_native_pt_manifest_uses_original_and_publisher_summary_without_ai_translation(source_format, media, suffix, read_variant):
    asset = SimpleNamespace(source_key=SOURCE_KEY, original_storage_key='original.bin', translated_storage_key=None,
        license_url='https://creativecommons.org/licenses/by/4.0/', source_sha256='b'*64, status='original_ready',
        coverage={'source_format': source_format, 'native_pt': True, 'complete_text': False},
        summary_pt='Resumo em português publicado pelos autores.', reason='Original editorial disponível.',
        progress={'summary_origin': 'publisher_abstract', 'title': 'Publicação original', 'authors': ['Autor A']}, pmcid=None)
    if source_format == 'pdf':
        asset.progress['original_text'] = {'storage_key': 'text.bin', 'sha256': 'c'*64, 'source_sha256': asset.source_sha256, 'source_format': 'pdf'}
    run, calls = manifest_function(asset)
    result = run()
    assert calls == [(ENTITY_TYPE, SOURCE_KEY)]
    source = result['sources'][0]
    assert source['original']['media_type'] == media
    assert source['original']['read_url'] == BASE + '/' + read_variant
    assert source['original']['url'] == BASE + '/original'
    assert source['original']['filename'].endswith('.' + suffix)
    assert source['translation_pt']['status'] == 'original_pt'
    assert source['translation_pt']['url'] is None
    assert source['translation_pt']['coverage']['complete_text'] is False
    assert source['summary_pt'] == {'status': 'available', 'text': asset.summary_pt, 'origin': 'publisher_abstract'}
    assert source['provenance']['model'] is None
    assert result['summary_pt']['status'] == 'unavailable'


def test_native_manifest_does_not_bypass_existing_entity_eligibility():
    run, calls = manifest_function(None, reject_entity=True)
    with pytest.raises(LookupError, match='not eligible'): run()
    assert calls == [(ENTITY_TYPE, SOURCE_KEY)]


def test_pdf_without_verified_text_keeps_download_available_without_text_read_url():
    asset = SimpleNamespace(source_key=SOURCE_KEY, original_storage_key='original.bin', translated_storage_key=None,
        license_url='https://creativecommons.org/licenses/by/4.0/', source_sha256='b'*64, status='original_ready',
        coverage={'source_format': 'pdf', 'native_pt': True, 'complete_text': False},
        summary_pt=None, reason='Original em PDF disponível.', progress={}, pmcid=None)
    run, _ = manifest_function(asset)
    source = run()['sources'][0]
    assert source['original']['status'] == 'available'
    assert source['original']['url'] == BASE + '/original'
    assert source['original']['media_type'] == 'application/pdf'
    assert source['original']['read_url'] is None
    assert source['translation_pt']['url'] is None
    assert source['summary_pt']['status'] == 'unavailable'
