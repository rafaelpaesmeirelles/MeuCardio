import hashlib
import pytest
from fastapi import HTTPException
from app.models.content import Document
from app.models.scientific_publication_asset import ScientificPublicationAsset as Asset
from app.services.scientific_reading import source_identity, reading_manifest
from app.services.scientific_publication_library import publication_queue_status
from app.api.scientific_reading import artifact


def test_original_is_read_inside_platform_from_stored_xml_without_translation(db,monkeypatch):
    doi='10.1000/corvia.original.reader';source=source_identity(doi)
    body='Original English scientific results and limitations are presented here, without translating the source. ' * 8
    xml=('<article xmlns:xlink="http://www.w3.org/1999/xlink"><front><article-meta><article-id pub-id-type="doi">'+doi+'</article-id><title-group><article-title>Original clinical article</article-title></title-group><permissions><license xlink:href="https://creativecommons.org/licenses/by/4.0/"><license-p>Attribution required</license-p></license></permissions></article-meta></front><body><p>'+body+'</p></body></article>').encode()
    doc=Document(slug='qa-original-reader',title='Síntese editorial',kind='estudo',theme='Geral',body_md='Outra camada',source_refs=[doi],published=True)
    asset=Asset(source_key=source['key'],doi=doi,source_url=source['url'],status='downloaded',license_url='https://creativecommons.org/licenses/by/4.0/',source_sha256=hashlib.sha256(xml).hexdigest(),original_storage_key='stored-only',progress={},coverage={'complete_text':False,'scope':'full_article_text','figures':'captions_only'})
    db.add_all([doc,asset]);db.commit()
    reads=[]
    monkeypatch.setattr('app.api.scientific_reading.cofre.ler',lambda key,id,**kw:reads.append((key,id)) or xml)
    try:
        manifest=reading_manifest(db,'documento',doc.slug)
        original=manifest['sources'][0]['original']
        assert original['read_url'].endswith('/original-text') and original['coverage']['complete_text']
        assert manifest['sources'][0]['translation_pt']['status']!='available'
        response=artifact('documento',doc.slug,source['key'],'original-text',db,None)
        assert body.strip().encode() in response.body and doi.encode() in response.body and b'creativecommons.org' in response.body
        assert response.media_type.startswith('text/plain') and reads==[('stored-only',asset.id)]
        monkeypatch.setattr('app.api.scientific_reading.cofre.ler',lambda *a,**kw:b'other stored content')
        with pytest.raises(HTTPException) as error:artifact('documento',doc.slug,source['key'],'original-text',db,None)
        assert error.value.status_code==503
    finally:
        db.rollback();db.delete(asset);db.delete(doc);db.commit()


def test_active_ai_processing_is_not_counted_as_failure(db):
    before=publication_queue_status(db)
    asset=Asset(source_key='d'*64,doi='10.1000/qa.processing',source_url='https://doi.org/10.1000/qa.processing',status='ai_processing',progress={},coverage={})
    db.add(asset);db.commit()
    try:
        during=publication_queue_status(db)
        assert during['processing']==before['processing']+1
        assert during['failed']==before['failed']
        asset.status='cost_unknown';db.commit()
        after=publication_queue_status(db)
        assert after['failed']==before['failed']+1 and after['reconciliation_pending']==before['reconciliation_pending']+1
    finally:
        db.rollback();db.delete(asset);db.commit()

def test_original_asset_manifest_and_favorite_require_current_public_origin(db,criar_usuario):
    from app.api import favorites
    from app.models.favorite import Favorite
    user,_=criar_usuario(role='admin')
    doi='10.1000/corvia.public.asset.favorite';source=source_identity(doi)
    doc=Document(slug='qa-original-public-provenance',title='Public reference',kind='documento',theme='Geral',body_md='Editorial',source_refs=[doi],published=True)
    asset=Asset(source_key=source['key'],doi=doi,source_url=source['url'],status='downloaded',license_url='https://creativecommons.org/licenses/by/4.0/',source_sha256='e'*64,original_storage_key='public-source.bin',progress={'title':'Licensed original'},coverage={'complete_text':False})
    db.add_all([doc,asset]);db.commit()
    try:
        manifest=reading_manifest(db,'publicacao_original',source['key'])
        assert manifest['slug']==source['key'] and manifest['summary_pt']['text'] is None
        assert manifest['sources'][0]['original']['read_url'].endswith('/original-text')
        added=favorites.adicionar(favorites.NovoFavorito(item_type='publicacao_original',item_slug=source['key']),db,user)
        again=favorites.adicionar(favorites.NovoFavorito(item_type='publicacao_original',item_id=asset.id),db,user)
        assert added['id']==again['id']
        row=favorites.listar(db,user)[0]
        assert row['url']=='/intelligence?fonte='+source['key']
        assert row['reading']=={'entity_type':'publicacao_original','slug':source['key']}
        doc.published=False;db.commit()
        with pytest.raises(HTTPException) as error:reading_manifest(db,'publicacao_original',source['key'])
        assert error.value.status_code==404
        row=favorites.listar(db,user)[0]
        assert row['title']=='Conteúdo indisponível' and row['reading'] is None
    finally:
        db.rollback();db.query(Favorite).filter(Favorite.user_id==user.id).delete();db.delete(asset);db.delete(doc);db.commit()
