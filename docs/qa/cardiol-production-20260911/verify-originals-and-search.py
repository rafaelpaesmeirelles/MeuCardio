import hashlib,json
from sqlalchemy import text
from app.core.db import SessionLocal
from app.models.scientific_publication_asset import ScientificPublicationAsset as Asset
from app.services.scientific_publication_catalog import public_asset_query
from app.services.scientific_reading import reading_manifest
from app.api.scientific_reading import artifact
from app.api.search import search
from app.services.calculators import REGISTRY
from pathlib import Path
manifest=json.loads(Path('/tmp/corvia926-release/import-manifest.json').read_text())
dois=[d['doi'] for d in manifest['documents']]
report={'verification':'postdeployment-read-only','paid_calls':0,'items':[],'search':[]}
with SessionLocal() as db:
 db.execute(text('SET TRANSACTION READ ONLY'))
 db.execute(text("SET LOCAL statement_timeout = '30s'"))
 eligible=public_asset_query(db).filter(Asset.doi.in_(dois)).all()
 assert len(eligible)==13, 'Not every original is eligible in the public catalog'
 for a in eligible:
  m=reading_manifest(db,'publicacao_original',a.source_key);s=m['sources'][0]
  original=artifact('publicacao_original',a.source_key,a.source_key,'original',db,None)
  readable=artifact('publicacao_original',a.source_key,a.source_key,'original-text',db,None)
  assert hashlib.sha256(original.body).hexdigest()==a.source_sha256
  assert s['translation_pt']['status']=='original_pt' and s['translation_pt']['url'] is None
  assert s['original']['read_url'].endswith('/original-text') and readable.status_code==200
  assert a.status=='original_ready' and not a.translated_storage_key
  report['items'].append({'doi':a.doi,'asset_id':a.id,'status':a.status,'original_bytes':len(original.body),'readable_bytes':len(readable.body),'original_sha256':a.source_sha256,'summary_available':bool(a.summary_pt),'attempts':a.attempts,'readable':True})
 for doi in ['10.36660/abc.20250615','10.36660/abc.20250618','10.36660/abc.20260565']:
  result=search(q=doi,frente=None,secao=None,limit=100,offset=0,db=db,_=None)
  a=next(x for x in eligible if x.doi==doi)
  found=any(x['frente']=='publicacao_original' and x['slug']==a.source_key for x in result['results'])
  assert found, 'Original not found by DOI: '+doi
  report['search'].append({'doi':doi,'found_original':found,'results':len(result['results'])})
 report['calculators']={slug:REGISTRY[slug].status for slug in ('framingham-global','framingham-imc','prevent','score2','score2-op','score2-diabetes','sbc-risco-cardiovascular')}
 db.rollback()
print(json.dumps(report,ensure_ascii=False,indent=2))
