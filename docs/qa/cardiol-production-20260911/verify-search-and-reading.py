import json
from sqlalchemy import text
from app.core.db import SessionLocal
from app.api.search import search
from app.services.scientific_reading import reading_manifest
from app.services.scientific_publication_catalog import public_asset_query
from app.models.scientific_publication_asset import ScientificPublicationAsset as Asset
from app.services.calculators import REGISTRY
report={'verification':'production search and bibliographic reader access','search':[]}
with SessionLocal() as db:
 db.execute(text('SET TRANSACTION READ ONLY'))
 db.execute(text("SET LOCAL statement_timeout = '30s'"))
 for doi,front in [('10.36660/abc.20250618','publicacao_original'),('10.36660/abc.20260565',None)]:
  a=public_asset_query(db).filter(Asset.doi==doi).one()
  result=search(q=doi,frente=front,secao=None,limit=100,offset=0,db=db,_=None)
  found=any(x['frente']=='publicacao_original' and x['slug']==a.source_key for x in result['results'])
  assert found, {'doi':doi,'total':result['total'],'results':result['results']}
  report['search'].append({'doi':doi,'front':front,'found_original':found,'total':result['total']})
 doi='10.36660/abc.20250618'
 m=reading_manifest(db,'documento','diretriz-brasileira-de-fibrilacao-atrial-2025-sbc-sobrac')
 sources=[s for s in m['sources'] if s.get('doi')==doi]
 assert sources, m
 assert any(s['original']['read_url'] and s['translation_pt']['status']=='original_pt' for s in sources)
 report['fa_first_page_document']={'slug':'diretriz-brasileira-de-fibrilacao-atrial-2025-sbc-sobrac','original_readable_via_source':True}
 report['calculators']={slug:REGISTRY[slug].status for slug in ('framingham-global','framingham-imc','prevent','score2','score2-op','score2-diabetes','sbc-risco-cardiovascular')}
 db.rollback()
print(json.dumps(report,ensure_ascii=False,indent=2))
