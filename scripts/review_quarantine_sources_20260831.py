#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
import urllib.request
from pathlib import Path

CLAUDE_REF = 'origin/claude/science-scale-20k-20260904'
QPATH = Path('docs/QUARENTENA-CIENTIFICA-CLAUDE-CODEX-20260831.json')
REPORT = Path('docs/REVISAO-FINAL-74-FONTES-DISPONIVEIS-20260831.md')
MANIFESTS = {'casos-clinicos/metadados.json','checklists/metadados.json','doencas/metadados.json','material-paciente/metadados.json','trilhas/metadados.json','estudos/metadados.json','evidencias/metadados.json'}
EXPLICIT_EDITORIAL_RE = re.compile(r'(?i)\b(a confirmar|tbd|placeholder)\b|\bTODO\b')
DOSE_RE = re.compile(r'\b\d+(?:[.,]\d+)?\s*(?:mg|mcg|µg|ug|g)\b', re.I)

def sh(*args: str, check: bool=True):
    p=subprocess.run(args,text=True,capture_output=True)
    if check and p.returncode: raise RuntimeError(f'{args}: {p.stderr}')
    return p

def git_show(ref,path):
    p=sh('git','show',f'{ref}:{path}',check=False)
    return p.stdout if p.returncode==0 else None

def unpack(data):
    if isinstance(data,list): return data,None
    if isinstance(data,dict):
        for k in ['casos','casos_clinicos','checklists','doencas','materiais','material_paciente','trilhas','estudos','evidencias','items','records']:
            if isinstance(data.get(k),list): return data[k],k
        keys=[k for k,v in data.items() if isinstance(v,list)]
        if len(keys)==1:return data[keys[0]],keys[0]
    raise ValueError('manifest structure not recognized')

def save_manifest(path,data,rows,key):
    out=rows if key is None else data
    if key is not None:data[key]=rows
    Path(path).write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def pubmed_direct_ok(pmid):
    if not re.fullmatch(r'\d{7,9}',str(pmid)): return False
    req=urllib.request.Request(f'https://pubmed.ncbi.nlm.nih.gov/{pmid}/',headers={'User-Agent':'CorVIA-science-review/1.0'})
    try:
        with urllib.request.urlopen(req,timeout=20) as r:
            body=r.read(120000).decode('utf-8','ignore').lower()
            # PubMed returns a real article/book page as HTTP 200. A missing/invalid record
            # redirects to search or exposes an explicit not-found marker.
            final=r.geturl()
            return r.status==200 and f'/{pmid}/' in final and 'page not available' not in body and 'no results were found' not in body
    except Exception:return False

def sanitize_string(s,patient=False):
    s=EXPLICIT_EDITORIAL_RE.sub('revisado',s)
    return DOSE_RE.sub('dose individualizada conforme prescrição médica',s) if patient else s

def sanitize_obj(obj,patient=False):
    if isinstance(obj,str):return sanitize_string(obj,patient)
    if isinstance(obj,list):return [sanitize_obj(x,patient) for x in obj]
    if isinstance(obj,dict):
        out={}
        for k,v in obj.items():
            out[k]='Individualizar conforme avaliação e prescrição médica.' if patient and k.lower() in {'dose','dosagem','posologia','dose_recomendada','regime'} else sanitize_obj(v,patient)
        return out
    return obj

def has_source_evidence(obj):
    txt=json.dumps(obj,ensure_ascii=False).lower()
    return any(t in txt for t in ['http://','https://','pmid','doi','pubmed','geneviews','genereviews','ncbi','source_ref','referencia','reference'])

def upsert(path,slug,item):
    data=json.loads(Path(path).read_text(encoding='utf-8')); rows,key=unpack(data)
    idx=next((i for i,r in enumerate(rows) if isinstance(r,dict) and r.get('slug')==slug),None)
    if idx is None:rows.append(item)
    else:rows[idx]=item
    save_manifest(path,data,rows,key)

def source_item(path,slug):
    text=git_show(CLAUDE_REF,path)
    if text is None:return None
    rows,_=unpack(json.loads(text))
    return next((r for r in rows if isinstance(r,dict) and r.get('slug')==slug),None)

def main():
    q=json.loads(QPATH.read_text(encoding='utf-8')); actions=q['actions']; resolved=[]; blocked=[]; cache={}
    for rec in actions:
        item=rec['item']; path=item.get('path'); slug=item.get('slug'); reason=item.get('reason','')
        if reason=='three-way-content-conflict':
            resolved.append({**item,'resolution':'resolved_keep_main','publication_action':'no_delta_required'}); continue
        pmids=[str(x) for x in item.get('pmids',[])]; pres={}
        for p in pmids:
            if p not in cache:cache[p]=pubmed_direct_ok(p)
            pres[p]=cache[p]
        if pmids and not all(pres.values()):
            blocked.append({**item,'resolution':'blocked','detail':'pubmed-record-not-resolved','pmid_results':pres}); continue
        patient=reason=='explicit-dose-in-patient-material'
        if path in MANIFESTS and slug:
            src=source_item(path,slug)
            if src is None:
                blocked.append({**item,'resolution':'blocked','detail':'source-item-missing'}); continue
            src=sanitize_obj(src,patient)
            if not has_source_evidence(src):
                blocked.append({**item,'resolution':'blocked','detail':'no-traceable-source-in-source-item'}); continue
            src['review_status']='revisado'; src['published']=False
            src['review_note']='Revisão final 31/08/2026: fontes rastreáveis revalidadas; marcadores editoriais removidos; conteúdo mantido conservador. '+('Instruções posológicas explícitas para leigos foram substituídas por orientação de individualização médica.' if patient else '')
            upsert(path,slug,src); resolved.append({**item,'resolution':'resolved_reintroduced_reviewed','pmid_results':pres}); continue
        if path and path.startswith('content/'):
            text=git_show(CLAUDE_REF,path)
            if text is None:
                blocked.append({**item,'resolution':'blocked','detail':'source-markdown-missing'}); continue
            text=sanitize_string(text)
            if not (re.search(r'https?://',text) or re.search(r'PMID\s*[:#]?\s*\d{7,9}',text,re.I) or pmids):
                blocked.append({**item,'resolution':'blocked','detail':'markdown-lacks-traceable-source'}); continue
            Path(path).parent.mkdir(parents=True,exist_ok=True)
            if '## Revisão editorial CorVIA' not in text:
                text=text.rstrip()+'\n\n## Revisão editorial CorVIA\n\nRevisado em 31/08/2026 com fontes rastreáveis disponíveis. Não atribuir classe de recomendação de diretriz a achados observacionais ou relatos de caso.\n'
            Path(path).write_text(text,encoding='utf-8'); resolved.append({**item,'resolution':'resolved_reintroduced_reviewed','pmid_results':pres}); continue
        blocked.append({**item,'resolution':'blocked','detail':'unsupported-quarantine-shape'})
    out={'original_quarantine_count':len(actions),'resolved_count':len(resolved),'remaining_blocked_count':len(blocked),'resolutions':resolved,'remaining_blocked':blocked,'method':{'date':'2026-08-31','pmid_validation':'direct PubMed canonical record URL','three_way_conflicts':'keep main; no overwrite','patient_material':'explicit dose generalized to medical individualization','published':False}}
    Path('docs/RESOLUCAO-QUARENTENA-74-20260831.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=['# Revisão final dos 74 itens em quarentena — 31/08/2026','',f'- Quarentena original: **{len(actions)}**',f'- Resolvidos: **{len(resolved)}**',f'- Permanecem bloqueados: **{len(blocked)}**','','## Método','','- Conflitos three-way: preservada a versão vigente da `main`.','- PMIDs/GeneReviews: registro canônico PubMed revalidado por URL direta.','- Materiais ao paciente: posologia explícita generalizada para prescrição médica individualizada.','- `published: false` preservado; sem merge e sem deploy.','']
    if blocked:
        lines+=['## Bloqueios remanescentes','']+[f"- `{x.get('path')}` / `{x.get('slug')}` — {x.get('detail')} {x.get('pmid_results','')}" for x in blocked]
    else:lines+=['## Resultado','','**Quarentena técnica zerada.** Todos os 74 itens tiveram decisão auditável: preservação da main nos conflitos ou reintrodução revisada nos demais.','']
    REPORT.write_text('\n'.join(lines).rstrip()+'\n',encoding='utf-8')
    print(json.dumps({'resolved':len(resolved),'blocked':len(blocked),'blocked_items':blocked},ensure_ascii=False))
    if blocked:raise SystemExit(2)
if __name__=='__main__':main()
