"""Real PostgreSQL checks for acquired-original discovery, without clinical writes."""
import hashlib
import pytest
from sqlalchemy import text
from app.models.content import Document
from app.models.study import ScientificStudy
from app.models.guideline import Guideline, GuidelineLink
from app.models.scientific_publication_asset import ScientificPublicationAsset as Asset
from app.services.scientific_publication_catalog import public_asset_query
from app.services.catalog_search import PAGE_SQL, SQL, INTERNAL_OVERRIDE_SQL_PATTERN, INTERNAL_MARKER_SQL_PATTERN, literal_like

PREFIX = 'qa-originalcatalog-'

@pytest.fixture(autouse=True)
def cleanup(db):
    def clear():
        db.rollback()
        db.query(GuidelineLink).filter(GuidelineLink.origem == 'qa-original').delete(synchronize_session=False)
        db.query(Document).filter(Document.slug.like(PREFIX+'%')).delete(synchronize_session=False)
        db.query(ScientificStudy).filter(ScientificStudy.slug.like(PREFIX+'%')).delete(synchronize_session=False)
        db.query(Guideline).filter(Guideline.slug.like(PREFIX+'%')).delete(synchronize_session=False)
        db.query(Asset).filter(Asset.doi.like('10.9999/qa-originalcatalog%')).delete(synchronize_session=False)
        db.commit()
    clear(); yield; clear()


def original(db, suffix, title='Originalsentinela bibliographic title', source=True):
    doi = '10.9999/qa-originalcatalog' + suffix
    asset = Asset(source_key=hashlib.sha256(('doi:'+doi).encode()).hexdigest(), doi=doi,
        source_url='https://doi.org/'+doi, original_storage_key='synthetic-encrypted-key', source_sha256='a'*64,
        license_url='https://creativecommons.org/licenses/by/4.0/', status='downloaded',
        progress={'title':title,'authors':['Bibliographic Author']}, coverage={}, summary_pt='Do not index inventedclinicalsentinel')
    db.add(asset)
    guideline = None
    if source:
        guideline=Guideline(slug=PREFIX+suffix, org='CROSSREF', titulo=title, ano=2026, doi=doi, url='https://doi.org/'+doi, detection_status='detected')
        db.add(guideline)
    db.flush()
    return asset, guideline


def query(db, q='Originalsentinela', **kwargs):
    params={'q':q,'q_like':literal_like(q),'frente':None,'secao':None,'limit':100,'offset':0,
        'internal_override_pattern':INTERNAL_OVERRIDE_SQL_PATTERN,'internal_marker_pattern':INTERNAL_MARKER_SQL_PATTERN,**kwargs}
    return db.execute(PAGE_SQL, params).mappings().one()


def test_acquired_original_requires_current_public_origin_license_identity(db):
    asset,_=original(db,'-unbound',source=False)
    assert public_asset_query(db).filter(Asset.id==asset.id).first() is None
    doc=Document(slug=PREFIX+'source',title='A public guide',kind='modulo',theme='Teste',body_md='Public source',source_refs=[asset.doi],published=False)
    db.add(doc);db.flush()
    assert public_asset_query(db).filter(Asset.id==asset.id).first() is None
    doc.published=True;db.flush()
    assert public_asset_query(db).filter(Asset.id==asset.id).one().id==asset.id
    for field,value in [('license_url','https://creativecommons.org/licenses/by-nc/4.0/'),('source_sha256','bad'),('source_key','b'*64),('original_storage_key',''),('status','blocked_identity')]:
        previous=getattr(asset,field);setattr(asset,field,value);db.flush()
        assert public_asset_query(db).filter(Asset.id==asset.id).first() is None
        setattr(asset,field,previous);db.flush()
    assert doc.review_status=='pendente_revisao'  # acquisition never claims review


def test_citing_guide_does_not_hide_original_and_exact_study_identity_dedupes(db):
    cited,_=original(db,'-cited')
    represented,_=original(db,'-own')
    prefix,_=original(db,'-own-longer')
    db.add(Document(slug=PREFIX+'guide',title='Atrial guide',kind='diretriz',theme='Teste',body_md='Editorial',source_refs=[cited.doi],published=True))
    db.add(ScientificStudy(slug=PREFIX+'study',title='Identidade traduzida',study_type='ensaio_clinico',journal='Teste',year=2026,summary='Editorial',key_findings='Achado',clinical_implications='Contexto',theme='Teste',doi=represented.doi,review_status='revisado',published=True))
    db.flush();page=query(db)
    originals={r['slug'] for r in page['results'] if r['frente']=='publicacao_original'}
    assert cited.source_key in originals and prefix.source_key in originals
    assert represented.source_key not in originals
    assert any(r['frente']=='estudo' and r['slug']==PREFIX+'study' for r in page['results'])


def test_explicit_summary_link_keeps_original_english_title_discoverable(db):
    asset,guideline=original(db,'-summary',title='Originalsentinela English source article')
    doc=Document(slug=PREFIX+'summary',title='Síntese em português',kind='documento',theme='Teste',body_md='Texto editorial',source_refs=[asset.doi],published=True,review_status='revisado')
    db.add(doc);db.flush()
    db.add(GuidelineLink(guideline_id=guideline.id,item_type='intelligence_document',item_id=doc.id,origem='qa-original',confirmado=True));db.flush()
    page=query(db,'English source article')
    assert [(r['frente'],r['slug']) for r in page['results']]==[('documento',doc.slug)]
    assert doc.title=='Síntese em português' and doc.body_md=='Texto editorial'


def test_original_section_counts_pagination_and_rag_exclusion(db):
    for suffix in ['-page-a','-page-b','-page-c']: original(db,suffix)
    page=query(db,secao='publicacao_original',limit=1,offset=1)
    assert len(page['results'])==1 and page['por_frente']=={'publicacao_original':3} and page['por_secao']=={'publicacao_original':3}
    assert query(db,secao='diretriz')['results']==[]
    assert query(db,q='inventedclinicalsentinel')['results']==[]
    params={'q':'Originalsentinela','q_like':'%originalsentinela%','frente':None,'limit':100,'offset':0,
        'internal_override_pattern':INTERNAL_OVERRIDE_SQL_PATTERN,'internal_marker_pattern':INTERNAL_MARKER_SQL_PATTERN}
    assert db.execute(SQL,params).mappings().all()==[]
