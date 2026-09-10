import json
import pytest
from app.services import scientific_publication_library as lib
from app.services.scientific_reading import normalize_doi, source_identity

DOI = '10.1000/corvia.fulltext'
def article(body='<p>A complete scientific article has results and limitations. Participants received 5 mg versus 10 mg with 95% CI; this text is long enough to distinguish a complete body from an abstract. The clinical findings, protocol, results, and observations are described here in detail for a complete text extraction rather than an abstract alone.</p>', license='https://creativecommons.org/licenses/by/4.0/', doi=DOI):
    return f'<article xmlns:xlink="http://www.w3.org/1999/xlink"><front><article-meta><article-id pub-id-type="doi">{doi}</article-id><title-group><article-title>Scientific publication</article-title></title-group><contrib-group><contrib contrib-type="author"><name><surname>Author</surname><given-names>AB</given-names></name></contrib></contrib-group><permissions><license xlink:href="{license}"><license-p>Attribution required</license-p></license></permissions></article-meta></front><body>{body}</body><back><ref-list><ref>Reference 1</ref></ref-list></back></article>'.encode()

def test_fulltext_requires_exact_identity_and_reusable_license():
    parsed = lib.parse_fulltext(article(), DOI)
    assert parsed['coverage']['complete_text'] is True
    assert 'Reference 1' in parsed['text'] and parsed['license_url'].endswith('/by/4.0/')
    assert parsed['authors'] and DOI in parsed['attribution']
    for xml in [article(doi='10.1000/different'), article(license='https://creativecommons.org/licenses/by-nc/4.0/'), article(body='<abstract>Not a full article</abstract>')]:
        with pytest.raises(lib.SourceUnavailable): lib.parse_fulltext(xml, DOI)

def test_tables_and_superscripts_preserve_numeric_structure():
    xml = article().replace(b'</body>', b'<table-wrap><table><tr><td>5</td><td>10</td></tr></table></table-wrap><p>10<sup>2</sup>; H<sub>2</sub>O</p></body>')
    parsed = lib.parse_fulltext(xml, DOI)
    assert '5\t\t10' in parsed['text'] and '510' not in parsed['text']
    assert '10^(2)' in parsed['text'] and 'H_(2)O' in parsed['text']

def test_unsupported_math_and_entity_encoding_fail_closed():
    for xml in [article().replace(b'</body>', b'<inline-formula>10 squared</inline-formula></body>'), article().decode().encode('utf-16'), b'<!DOCTYPE article [<!ENTITY payload "hello">]>' + article()]:
        with pytest.raises(lib.SourceUnavailable): lib.parse_fulltext(xml, DOI)

def test_doi_citation_delimiters_do_not_change_identity():
    assert normalize_doi('(https://doi.org/10.1056/NEJMoa2115998).') == '10.1056/nejmoa2115998'
    assert normalize_doi('10.1016/S0140-6736(22)01950-8') == '10.1016/s0140-6736(22)01950-8'
    assert source_identity(DOI)['key'] == source_identity('https://doi.org/' + DOI)['key']
    assert source_identity('javascript:alert(1)') is None

def test_translation_requires_all_segments_and_preserves_numbers():
    source = ('Clinical outcomes 10 mg with 95% CI require faithful translation. ' * 12)
    segments = lib._segments(source)
    assert ''.join(segments) == source
    result = {'segments': [{'id': i, 'translation_pt': s} for i,s in enumerate(segments)], 'summary_pt': 'Resumo do artigo.'}
    assert lib.validate_translation(source, result)[1] == 'Resumo do artigo.'
    wrong = json.loads(json.dumps(result)); wrong['segments'].pop()
    with pytest.raises(lib.SourceUnavailable): lib.validate_translation(source, wrong)
    wrong = json.loads(json.dumps(result)); wrong['segments'][0]['translation_pt'] = wrong['segments'][0]['translation_pt'].replace('10 mg', '100 mg')
    with pytest.raises(lib.SourceUnavailable): lib.validate_translation(source, wrong)
    wrong = json.loads(json.dumps(result)); wrong['segments'][0]['id'] = 99
    with pytest.raises(lib.SourceUnavailable): lib.validate_translation(source, wrong)

def test_download_only_official_api_and_never_redirects(monkeypatch):
    with pytest.raises(ValueError): lib._download('https://127.0.0.1/secrets')
    with pytest.raises(ValueError): lib._download('/../secrets')

def test_translation_preserves_signs_and_comparators():
    source = 'The effect was -2.5 mg and threshold ≤5 with 95% confidence.'
    for translated in [source.replace('-2.5', '2.5'), source.replace('≤5', '>5')]:
        with pytest.raises(lib.SourceUnavailable):
            lib.validate_translation(source, {'segments': [{'id': 0, 'translation_pt': translated}], 'summary_pt': 'Resumo.'})

def test_shared_seed_continues_and_manifest_never_labels_synthesis_translation(db, monkeypatch):
    from app.models.content import Document
    from app.models.scientific_publication_asset import ScientificPublicationAsset as Asset
    from app.services.scientific_reading import reading_manifest
    prefix = 'qa-scientific-reading-20260910'
    dois = ['10.1000/corvia.qa.seed1', '10.1000/corvia.qa.seed2']
    keys = [source_identity(d)['key'] for d in dois]
    docs = [Document(slug=prefix+str(i), title='QA reading '+str(i), kind='estudo', theme='Geral', summary='Resumo editorial existente', body_md='Síntese não é tradução integral.', source_refs=[doi], published=True) for i,doi in enumerate(dois)]
    try:
        db.add_all(docs); db.commit()
        monkeypatch.setattr(lib, 'MODELS', {'documento': Document})
        original_query = lib.published_query
        monkeypatch.setattr(lib, 'published_query', lambda session, model: original_query(session, model).filter(model.slug.like(prefix+'%')))
        assert lib.seed_publication_queue(db, limit=1)['inserted'] == 1
        assert lib.seed_publication_queue(db, limit=1)['inserted'] == 1
        assert db.query(Asset).filter(Asset.source_key.in_(keys)).count() == 2
        manifest = reading_manifest(db, 'documento', docs[0].slug)
        assert manifest['summary_pt']['text'] == 'Resumo editorial existente'
        assert manifest['sources'][0]['translation_pt']['status'] == 'pending'
        assert manifest['sources'][0]['original']['status'] == 'source_only'
        assert manifest['sources'][0]['translation_pt']['url'] is None
        docs[0].published = False; db.commit()
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as error: reading_manifest(db, 'documento', docs[0].slug)
        assert error.value.status_code == 404
    finally:
        db.rollback()
        db.query(Asset).filter(Asset.source_key.in_(keys)).delete(synchronize_session=False)
        db.query(Document).filter(Document.slug.like(prefix+'%')).delete(synchronize_session=False)
        db.commit()

def test_shared_download_requires_public_source_binding(db, monkeypatch):
    from app.models.content import Document
    from app.models.scientific_publication_asset import ScientificPublicationAsset as Asset
    from app.api.scientific_reading import artifact
    from fastapi import HTTPException
    source = source_identity('10.1000/corvia.qa.binding')
    unrelated = source_identity('10.1000/corvia.qa.unrelated')
    doc = Document(slug='qa-scientific-download-binding', title='QA', kind='estudo', theme='Geral', body_md='Editorial', source_refs=[source['doi']], published=True)
    asset = Asset(source_key=source['key'], doi=source['doi'], source_url=source['url'], status='ready', license_url='https://creativecommons.org/licenses/by/4.0/', source_sha256='a'*64, original_storage_key='original', translated_storage_key='translation', coverage={'complete_text':True}, progress={})
    try:
        db.add_all([doc,asset]); db.commit()
        monkeypatch.setattr('app.api.scientific_reading.cofre.ler', lambda *a,**kw:b'texto cientifico')
        response = artifact('documento',doc.slug,source['key'],'translation',db,None)
        assert response.body == b'texto cientifico' and response.headers['x-content-type-options'] == 'nosniff'
        with pytest.raises(HTTPException) as error: artifact('documento',doc.slug,unrelated['key'],'original',db,None)
        assert error.value.status_code == 404
        asset.coverage={'complete_text':False};db.commit()
        with pytest.raises(HTTPException):artifact('documento',doc.slug,source['key'],'translation',db,None)
    finally:
        db.rollback();db.delete(asset);db.delete(doc);db.commit()

def test_shared_reader_requires_authentication_without_ai_plan_gate():
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from app.api.scientific_reading import router
    app = FastAPI(); app.include_router(router)
    with TestClient(app) as client:
        response = client.get('/api/scientific-reading/documento/unpublished')
        assert response.status_code == 401

def test_private_extraction_does_not_silently_truncate(monkeypatch):
    monkeypatch.setattr(lib.translator, 'MAX_EXTRACTED_CHARS', 10)
    with pytest.raises(ValueError, match='Nenhum texto foi truncado'):
        lib.translator.extract_text(b'long scientific text', 'text/plain')
