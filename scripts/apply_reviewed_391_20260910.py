"""Import only the frozen 391 corrected drafts, preserving unpublished status.

Default --check reads current rows without writing. --apply-reviewed stores the
reviewed drafts atomically after source guards and an on-host backup. This tool
cannot publish content, run corpus reconciliation, or modify other records.
Run inside the configured backend container with PYTHONPATH=/app.
"""
from __future__ import annotations
import argparse,gzip,hashlib,json,re
from datetime import datetime,timezone
from pathlib import Path
from sqlalchemy import select,text
from app.core.db import SessionLocal
from app.models.content import Document,DocumentRevision
from app.services.canonical_themes import TEMAS_CANONICOS

FIELDS={'slug','title','kind','theme','summary','body_md','tags','source_refs','evidence_level','source_tier','review_status','gaps','published'}
ORIGINAL_FIELDS=(FIELDS-{'published'})|{'version','updated_at'}
LIMITS={'slug':255,'title':500,'kind':50,'theme':80,'evidence_level':40,'source_tier':12,'review_status':40}
RELEASE='scientific-20260910-unpublished'
def serial(v):return v.isoformat() if isinstance(v,datetime) else str(v)
def validate(pack):
 if pack.get('release_id')!=RELEASE or pack.get('expected_count')!=391 or not pack.get('ready_for_reviewed_import'):raise ValueError('Unexpected or incomplete reviewed package')
 items=pack['items'];slugs=[r['data']['slug'] for r in items]
 if len(items)!=391 or len(set(slugs))!=391:raise ValueError('Exactly391 unique frozen documents required')
 for item in items:
  d=item['data'];o=item['original']
  if set(o)!=ORIGINAL_FIELDS or type(o['version']) is not int or o['version']<1 or not isinstance(o['body_md'],str) or not isinstance(o['updated_at'],str):raise ValueError('Incomplete frozen source guard')
  if datetime.fromisoformat(o['updated_at']).tzinfo is None:raise ValueError('Source timestamp must have timezone')
  if item['entity_type']!='documento' or set(d)!=FIELDS or d['slug']!=o['slug']:raise ValueError('Changed identity or field scope')
  if d['published'] is not False or d['review_status']!='revisado' or d['gaps']:raise ValueError('Every draft must be reviewed and unpublished with resolved gaps')
  if d['theme'] not in TEMAS_CANONICOS or not d['body_md'].strip():raise ValueError('Invalid theme/body')
  for k in ['tags','source_refs','gaps']:
   if not isinstance(d[k],list) or any(not isinstance(v,str) for v in d[k]):raise ValueError('Invalid array:'+k)
  for k,n in LIMITS.items():
   v=d[k]
   if v is not None and (not isinstance(v,str) or len(v)>n):raise ValueError('Invalid field:'+k)
  if re.search(r'verifica[çc][ãa]o humana necess[áa]ria|aguardando revis[ãa]o',json.dumps(d,ensure_ascii=False),re.I):raise ValueError('Unresolved review marker')
 return items

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('package',type=Path);p.add_argument('--sha256',required=True)
 a=p.add_mutually_exclusive_group(required=True);a.add_argument('--check',action='store_true');a.add_argument('--apply-reviewed',action='store_true');args=p.parse_args()
 raw=args.package.read_bytes();digest=hashlib.sha256(raw).hexdigest()
 if digest!=args.sha256:raise ValueError('Package checksum mismatch')
 items=validate(json.loads(raw));db=SessionLocal();stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
 try:
  if args.apply_reviewed and not db.execute(text('SELECT pg_try_advisory_xact_lock(39120260910)')).scalar():raise RuntimeError('Reviewed import already running')
  query=select(Document).where(Document.slug.in_([r['data']['slug'] for r in items]))
  if args.apply_reviewed:query=query.with_for_update()
  rows={r.slug:r for r in db.execute(query).scalars()}
  if len(rows)!=391:raise RuntimeError('Source inventory changed')
  changed=[];unchanged=[]
  for item in items:
   d,o=item['data'],item['original'];r=rows[d['slug']]
   if r.published:raise RuntimeError('Source became published: '+r.slug)
   delta=any(getattr(r,k)!=v for k,v in d.items())
   if not delta:
    unchanged.append(r.slug);continue
   for k,v in o.items():
    current=getattr(r,k)
    if k=='updated_at':
     if current!=datetime.fromisoformat(v):raise RuntimeError('Source changed: '+r.slug+':updated_at')
    elif current!=v:raise RuntimeError('Source changed: '+r.slug+':'+k)
   changed.append(item)
  result={'release_id':RELEASE,'package_sha256':digest,'mode':'apply-reviewed' if args.apply_reviewed else 'check','matched':391,'changes':len(changed),'already_matching':len(unchanged),'published':0}
  if args.apply_reviewed:
   backup=Path('/tmp')/f'corvia-391-before-reviewed-{stamp}.json.gz'
   payload={'release_id':RELEASE,'package_sha256':digest,'rows':[{c.key:getattr(r,c.key) for c in Document.__table__.columns} for r in rows.values()]}
   with backup.open('xb') as f:f.write(gzip.compress(json.dumps(payload,ensure_ascii=False,default=serial).encode()))
   for item in changed:
    d=item['data'];r=rows[d['slug']]
    if r.body_md!=d['body_md']:
     db.add(DocumentRevision(document_id=r.id,version=r.version,body_md=r.body_md,author_id=None));r.version+=1
    for k,v in d.items():setattr(r,k,v)
    r.reviewed_by=None;r.reviewed_at=None
   db.flush()
   if any(r.published or r.review_status!='revisado' for r in rows.values()):raise RuntimeError('Review status did not persist')
   db.commit();result['backup']=str(backup)
   (Path('/tmp')/f'corvia-391-reviewed-result-{stamp}.json').write_text(json.dumps(result,indent=2),encoding='utf8')
  else:db.rollback()
  print(json.dumps(result,ensure_ascii=False))
 except BaseException:db.rollback();raise
 finally:db.close()
if __name__=='__main__':main()
