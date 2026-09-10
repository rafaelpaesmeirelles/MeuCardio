"""Declared editorial metadata is shared by search and Library without moving entities."""
import json
from pathlib import Path

from app.services.document_editorial_taxonomy import DOCUMENT_KIND_SECTIONS, document_section
from test_search_sections import isolated_catalog, document, api_search
from app.services.catalog_search import calculadoras_encontradas


def test_frontend_snapshot_matches_authority_and_neutral_types_do_not_infer_titles():
    root = Path(__file__).resolve().parents[2]
    snapshot = json.loads((root / 'frontend/src/lib/documentEditorialTaxonomy.json').read_text())
    assert snapshot == DOCUMENT_KIND_SECTIONS
    assert document_section('documento') == 'geral'
    assert document_section('estudo') == document_section('revisao') == 'estudo'
    assert document_section('consenso') == 'diretriz'
    assert document_section('desconhecido') == 'geral'


def test_library_and_search_respect_declared_types_and_keep_canonical_front(client, db, criar_usuario):
    rows = [
        document('editorial-trial', 'Editorialsentinela ensaio clínico', 'estudo'),
        document('editorial-consensus', 'Editorialsentinela consenso', 'consenso'),
        document('editorial-guideline', 'Editorialsentinela guideline', 'diretriz'),
        document('editorial-neutral', 'Editorialsentinela miopatia: comentário sobre consenso', 'documento'),
        document('editorial-review', 'Editorialsentinela revisão', 'revisao'),
        document('editorial-hidden', 'Editorialsentinela consenso retido', 'consenso', False),
    ]
    db.add_all(rows); db.commit()
    _, token = criar_usuario(role='admin'); headers = {'Authorization': f'Bearer {token}'}
    result = api_search(client, headers, 'Editorialsentinela')
    assert result['por_secao'] == {'diretriz': 2, 'estudo': 2, 'geral': 1}
    assert result['por_frente'] == {'documento': 5}
    assert all(row['frente'] == 'documento' for row in result['results'])
    for section, count in result['por_secao'].items():
        response = client.get('/api/library/documents', params={'secao': section, 'limit': 1}, headers=headers)
        assert response.status_code == 200, response.text
        body = response.json(); assert body['total'] == count
        assert body['items'][0]['secao'] == section
        all_items = []
        offset = 0
        while offset is not None:
            page = client.get('/api/library/documents', params={'secao': section, 'limit': 1, 'offset': offset}, headers=headers).json()
            all_items += page['items']; offset = page['next_offset']
        assert {row['slug'] for row in all_items} == {row['slug'] for row in result['results'] if row['secao'] == section}
    assert client.get('/api/library/documents?secao=invalid', headers=headers).status_code == 422
    assert client.get('/api/library/documents?secao=diretriz&kind=estudo', headers=headers).json()['total'] == 0
    assert client.get('/api/library/documents?secao=geral&q=miopatia', headers=headers).json()['items'][0]['slug'] == 'editorial-neutral'
    assert client.get('/api/library/documents?q=%25', headers=headers).json()['total'] == 0


def test_calculator_editorial_section_includes_documents_without_changing_identity(client, db, criar_usuario):
    calculators = calculadoras_encontradas('score')
    assert calculators
    # Identical slug across canonical namespaces must remain two separate rows.
    db.add(document(calculators[0]['slug'], 'Score editorial', 'calculadora'))
    db.commit()
    _, token = criar_usuario(role='admin'); headers = {'Authorization': f'Bearer {token}'}
    result = api_search(client, headers, 'score', secao='calculadora', limit=100)
    assert result['por_secao']['calculadora'] == len(calculators) + 1
    assert result['por_frente'] == {'calculadora': len(calculators), 'documento': 1}
    identities = {(row['frente'], row['slug']) for row in result['results']}
    assert len(identities) == len(calculators) + 1
    only_document = api_search(client, headers, 'score', frente='documento', secao='calculadora')
    assert only_document['por_frente'] == {'documento': 1}
    only_tools = api_search(client, headers, 'score', frente='calculadora', secao='calculadora')
    assert only_tools['por_frente'] == {'calculadora': len(calculators)}
    assert api_search(client, headers, 'score', frente='calculadora', secao='geral')['total'] == 0
    boundary = api_search(client, headers, 'score', secao='calculadora', offset=len(calculators)-1, limit=2)
    assert [row['frente'] for row in boundary['results']] == ['calculadora', 'documento']


def test_formal_studies_are_visible_as_guidance_without_promoting_trial_titles(client, db, criar_usuario):
    from app.models.study import ScientificStudy
    for slug, title, kind, published in [
        ('sepsis-task-force', 'Editorialsentinela definição de sepse', 'consenso', True),
        ('consensus-trial', 'Editorialsentinela CONSENSUS ensaio', 'ensaio_clinico', True),
        ('oster-review', 'Editorialsentinela revisão para guideline', 'revisao_sistematica', True),
        ('hidden-statement', 'Editorialsentinela consenso oculto', 'consenso', False),
    ]:
        db.add(ScientificStudy(slug=slug, title=title, study_type=kind, journal='Teste', year=2026,
            summary='Resumo sintético', key_findings='Achado', clinical_implications='Contexto',
            theme='Teste', published=published))
    db.commit()
    _, token = criar_usuario(role='admin'); headers = {'Authorization': f'Bearer {token}'}
    result = api_search(client, headers, 'Editorialsentinela')
    assert result['por_secao'] == {'diretriz': 1, 'estudo': 2}
    assert result['por_frente'] == {'estudo': 3}
    formal = api_search(client, headers, 'Editorialsentinela', secao='diretriz')
    assert [(x['frente'], x['slug']) for x in formal['results']] == [('estudo', 'sepsis-task-force')]
    listing = client.get('/api/studies?secao=diretriz&q=Editorialsentinela', headers=headers)
    assert listing.status_code == 200, listing.text
    assert [(x['slug'], x['secao']) for x in listing.json()['items']] == [('sepsis-task-force', 'diretriz')]
    assert client.get('/api/studies?secao=diretriz&study_type=ensaio_clinico', headers=headers).json()['total'] == 0
    assert client.get('/api/studies?secao=invalid', headers=headers).status_code == 422


def test_library_search_matches_literal_symbols_and_subscript_digits(client, db, criar_usuario):
    for slug, title in [
        ('percent', '100% de conteúdo'), ('wildcard', '1000 de conteúdo'),
        ('underscore', 'A_B marcador'), ('letter', 'ACB marcador'),
        ('bang', 'Alerta! clínico'), ('subscript', 'CHA₂DS₂-VASc'),
    ]:
        db.add(document(slug, title, 'documento'))
    db.commit()
    _, token = criar_usuario(role='admin'); headers = {'Authorization': f'Bearer {token}'}
    for query, expected in [('100%', 'percent'), ('A_B', 'underscore'), ('Alerta!', 'bang'), ('CHA2DS2', 'subscript'), ('CHA₂DS₂', 'subscript')]:
        response = client.get('/api/library/documents', params={'q': query}, headers=headers)
        assert response.status_code == 200, response.text
        assert [row['slug'] for row in response.json()['items']] == [expected]


def test_study_pages_tie_break_identical_titles_by_stable_identity(client, db, criar_usuario):
    from sqlalchemy import event
    from app.models.study import ScientificStudy
    for slug in ('third', 'first', 'second'):
        db.add(ScientificStudy(slug=slug, title='Mesmo título', study_type='consenso', journal='Teste', year=2026,
            summary='Resumo', key_findings='Achado', clinical_implications='Contexto', theme='Teste', published=True))
    db.commit()
    _, token = criar_usuario(role='admin'); headers = {'Authorization': f'Bearer {token}'}
    statements = []
    def capture(connection, cursor, statement, parameters, context, executemany):
        if 'ORDER BY scientific_studies.title' in statement:
            statements.append(statement)
    event.listen(db.bind, 'before_cursor_execute', capture)
    try:
        pages = [client.get('/api/studies', params={'secao': 'diretriz', 'limit': 1, 'offset': offset}, headers=headers).json() for offset in range(3)]
    finally:
        event.remove(db.bind, 'before_cursor_execute', capture)
    assert [page['items'][0]['slug'] for page in pages] == ['third', 'first', 'second']
    assert all(page['total'] == 3 for page in pages)
    assert statements and all('ORDER BY scientific_studies.title, scientific_studies.id' in statement for statement in statements)
