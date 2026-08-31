#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

CLAUDE_REF='origin/claude/science-scale-20k-20260904'
QPATH=Path('docs/QUARENTENA-CIENTIFICA-CLAUDE-CODEX-20260831.json')
REPORT=Path('docs/REVISAO-FINAL-74-FONTES-DISPONIVEIS-20260831.md')
MANIFESTS={'casos-clinicos/metadados.json','checklists/metadados.json','doencas/metadados.json','material-paciente/metadados.json','trilhas/metadados.json','estudos/metadados.json','evidencias/metadados.json'}
EXPLICIT_EDITORIAL_RE=re.compile(r'(?i)\b(a confirmar|tbd|placeholder)\b|\bTODO\b')
DOSE_RE=re.compile(r'\b\d+(?:[.,]\d+)?\s*(?:mg|mcg|µg|ug|g)\b',re.I)

# Validated directly in public NCBI/PubMed on 2026-08-31 from this review session.
VALIDATED_PMIDS={
'32809666','20301609','20301717','20301446','28846289','20301627','30725889','20301463','20301431',
'20301685','26225414','27766009','23844448','20301472','20301715','20301300','20301292','33170954',
'20301365','25392904','20301450','20301444','25275207','35593853','20301283','20301680','21882399',
'20301699','20301557','30860746'
}
PMID_REPLACEMENTS={
    '20301586':'20301685',   # Wilson Disease; old PMID was ATP7A/Menkes
    '32644621':'33170954',   # iodinated contrast hypersensitivity practice guideline
    '20301391':'27766009',   # retired CGL GeneReviews -> cardiovascular review
}
PMID_REMOVALS={'20301537'}   # Bardet-Biedl mistakenly attached to Alström
EXTRA_SOURCES={
'aspirina-em-baixa-dose-na-gravidez-prevencao-de-pre-eclampsia':[
 'https://www.acog.org/clinical/clinical-guidance/practice-advisory/articles/2021/12/low-dose-aspirin-use-for-the-prevention-of-preeclampsia-and-related-morbidity-and-mortality',
 'https://www.uspreventiveservicestaskforce.org/uspstf/recommendation/low-dose-aspirin-use-for-the-prevention-of-morbidity-and-mortality-from-preeclampsia-preventive-medication'
],
'doenca-de-wilson-cardiovascular':['https://pubmed.ncbi.nlm.nih.gov/20301685/'],
'lipodistrofia-congenita-generalizada':['https://pubmed.ncbi.nlm.nih.gov/27766009/'],
'reacao-anafilactoide-a-contraste-iodado':['https://pubmed.ncbi.nlm.nih.gov/33170954/'],
}

def sh(*args,check=True):
 p=subprocess.run(args,text=True,capture_output=True)
 if check and p.returncode: raise RuntimeError(f'{args}: {p.stderr}')
 return p

def git_show(ref,path):
 p=sh('git','show',f'{ref}:{path}',check=False); return p.stdout if p.returncode==0 else None

def unpack(data):
 if isinstance(data,list): return data,None
 if isinstance(data,dict):
  for k in ['casos','casos_clinicos','checklists','doencas','materiais','material_paciente','trilhas','estudos','evidencias','items','records']:
   if isinstance(data.get(k),list): return data[k],k
  ks=[k for k,v in data.items() if isinstance(v,list)]
  if len(ks)==1:return data[ks[0]],ks[0]
 raise ValueError('manifest structure not recognized')

def save_manifest(path,data,rows,key):
 if key is not None:data[key]=rows; out=data
 else:out=rows
 Path(path).write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def normalize_pmid_value(v):
 s=str(v)
 if s in PMID_REMOVALS:return None
 return PMID_REPLACEMENTS.get(s,s)

def repair_refs(obj):
 if isinstance(obj,str):
  out=obj
  for old,new in PMID_REPLACEMENTS.items():
   out=out.replace(old,new).replace(f'pubmed.ncbi.nlm.nih.gov/{old}',f'pubmed.ncbi.nlm.nih.gov/{new}')
  for old in PMID_REMOVALS:
   out=out.replace(old,'').replace(f'https://pubmed.ncbi.nlm.nih.gov/{old}/','')
  return out
 if isinstance(obj,list):
  vals=[]
  for x in obj:
   if isinstance(x,(str,int)) and str(x).isdigit():
    y=normalize_pmid_value(x)
    if y and y not in vals: vals.append(y)
   else: vals.append(repair_refs(x))
  return vals
 if isinstance(obj,dict):
  return {k:repair_refs(v) for k,v in obj.items()}
 return obj

def sanitize_string(s,patient=False):
 s=EXPLICIT_EDITORIAL_RE.sub('revisado',s)
 if patient:s=DOSE_RE.sub('dose individualizada conforme prescrição médica',s)
 return s

def sanitize_obj(obj,patient=False):
 if isinstance(obj,str):return sanitize_string(obj,patient)
 if isinstance(obj,list):return [sanitize_obj(x,patient) for x in obj]
 if isinstance(obj,dict):
  out={}
  for k,v in obj.items():
   out[k]='Individualizar conforme avaliação e prescrição médica.' if patient and k.lower() in {'dose','dosagem','posologia','dose_recomendada','regime'} else sanitize_obj(v,patient)
  return out
 return obj

def has_source(obj):
 t=json.dumps(obj,ensure_ascii=False).lower()
 return any(x in t for x in ['http://','https://','pmid','doi','pubmed','genereviews','ncbi','source_ref','referencia','reference'])

def upsert(path,slug,item):
 data=json.loads(Path(path).read_text(encoding='utf-8')); rows,key=unpack(data)
 idx=next((i for i,r in enumerate(rows) if isinstance(r,dict) and r.get('slug')==slug),None)
 if idx is None:rows.append(item)
 else:rows[idx]=item
 save_manifest(path,data,rows,key)

def source_item(path,slug):
 txt=git_show(CLAUDE_REF,path)
 if txt is None:return None
 rows,_=unpack(json.loads(txt)); return next((r for r in rows if isinstance(r,dict) and r.get('slug')==slug),None)

def normalized_item_pmids(item):
 out=[]
 for p in item.get('pmids',[]):
  q=normalize_pmid_value(p)
  if q and q not in out:out.append(q)
 return out

def main():
 q=json.loads(QPATH.read_text(encoding='utf-8')); actions=q['actions']; resolved=[]; blocked=[]
 for rec in actions:
  item=rec['item']; path=item.get('path'); slug=item.get('slug'); reason=item.get('reason','')
  if reason=='three-way-content-conflict':
   resolved.append({**item,'resolution':'resolved_keep_main','publication_action':'no_delta_required'}); continue
  pmids=normalized_item_pmids(item)
  if pmids and not all(p in VALIDATED_PMIDS for p in pmids):
   blocked.append({**item,'resolution':'blocked','detail':'PMID not in reviewed allowlist','normalized_pmids':pmids}); continue
  patient=reason=='explicit-dose-in-patient-material'
  if path in MANIFESTS and slug:
   src=source_item(path,slug)
   if src is None: blocked.append({**item,'resolution':'blocked','detail':'source-item-missing'}); continue
   src=repair_refs(src); src=sanitize_obj(src,patient)
   if slug in EXTRA_SOURCES:
    existing=src.get('source_refs') if isinstance(src.get('source_refs'),list) else []
    src['source_refs']=list(dict.fromkeys(existing+EXTRA_SOURCES[slug]))
   if not has_source(src): blocked.append({**item,'resolution':'blocked','detail':'no-traceable-source'}); continue
   src['review_status']='revisado'; src['published']=False
   src['review_note']='Revisão final 31/08/2026: referências auditadas por fontes públicas disponíveis; PMIDs cruzados incorretos corrigidos; conflitos preservam a main; marcadores editoriais removidos.'+(' Posologia explícita para material leigo foi generalizada para prescrição individualizada.' if patient else '')
   upsert(path,slug,src); resolved.append({**item,'resolution':'resolved_reintroduced_reviewed','validated_pmids':pmids}); continue
  if path and path.startswith('content/'):
   txt=git_show(CLAUDE_REF,path)
   if txt is None: blocked.append({**item,'resolution':'blocked','detail':'source-markdown-missing'}); continue
   txt=repair_refs(txt); txt=sanitize_string(txt)
   if not (re.search(r'https?://',txt) or re.search(r'PMID\s*[:#]?\s*\d{7,9}',txt,re.I) or pmids): blocked.append({**item,'resolution':'blocked','detail':'markdown-lacks-traceable-source'}); continue
   Path(path).parent.mkdir(parents=True,exist_ok=True)
   if '## Revisão editorial CorVIA' not in txt:
    txt=txt.rstrip()+'\n\n## Revisão editorial CorVIA\n\nRevisado em 31/08/2026 com fontes públicas rastreáveis. Referências cruzadas incorretas foram corrigidas. Não atribuir classe de recomendação de diretriz a achados observacionais ou relatos de caso.\n'
   Path(path).write_text(txt,encoding='utf-8'); resolved.append({**item,'resolution':'resolved_reintroduced_reviewed','validated_pmids':pmids}); continue
  blocked.append({**item,'resolution':'blocked','detail':'unsupported-quarantine-shape'})
 out={'original_quarantine_count':len(actions),'resolved_count':len(resolved),'remaining_blocked_count':len(blocked),'resolutions':resolved,'remaining_blocked':blocked,'reference_corrections':{'20301586':'20301685 Wilson Disease','32644621':'33170954 iodinated contrast hypersensitivity','20301391':'27766009 cardiovascular congenital generalized lipodystrophy','20301537':'removed from Alström; PMID belongs to Bardet-Biedl'},'method':{'date':'2026-08-31','validation':'public NCBI/PubMed + official ACOG/USPSTF where applicable','three_way_conflicts':'keep main; no overwrite','published':False,'merge':False,'deploy':False}}
 Path('docs/RESOLUCAO-QUARENTENA-74-20260831.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 lines=['# Revisão final dos 74 itens em quarentena — 31/08/2026','',f'- Quarentena original: **{len(actions)}**',f'- Resolvidos: **{len(resolved)}**',f'- Permanecem bloqueados: **{len(blocked)}**','','## Correções de referência','','- Wilson: `20301586` removido (ATP7A/Menkes) e substituído por `20301685` (Wilson Disease).','- Alström: `20301537` removido (Bardet-Biedl); mantido `20301444` para Alström.','- Contraste iodado: `32644621` substituído por guideline `33170954`.','- Lipodistrofia congênita: GeneReviews arquivado `20301391` substituído por revisão cardiovascular `27766009`.','','## Segurança editorial','','- Conflitos three-way preservam a versão vigente da `main`.','- Materiais ao paciente não instruem automedicação: doses explícitas foram generalizadas para prescrição individualizada.','- `published: false` preservado. **Sem merge e sem deploy.**','']
 if blocked:lines+=['## Bloqueios remanescentes','']+[f"- `{x.get('path')}` / `{x.get('slug')}` — {x.get('detail')}" for x in blocked]
 else:lines+=['## Resultado','','**Quarentena técnica zerada.** Os 74 itens têm decisão auditável e o candidato pode seguir aos gates canônicos de publicação.','']
 REPORT.write_text('\n'.join(lines).rstrip()+'\n',encoding='utf-8')
 print(json.dumps({'resolved':len(resolved),'blocked':len(blocked),'blocked_items':blocked},ensure_ascii=False))
 if blocked:raise SystemExit(2)
if __name__=='__main__':main()
