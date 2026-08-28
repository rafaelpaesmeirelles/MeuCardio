"""Contrato do aprofundamento Tudo com Tudo de hipertensão arterial pediátrica — 28/08/2026."""
from __future__ import annotations
import json,re
from pathlib import Path
from app.services.clinical_rule_engine import validate_question_definitions,validate_rule_definitions
REPOSITORY_ROOT=Path(__file__).resolve().parents[2]; DOENCAS_PATH=REPOSITORY_ROOT/"doencas/metadados.json"; SLUG="hipertensao-arterial-pediatrica"
MIN_LIST_ITEMS={"presentation":8,"differentials":3,"tests":3,"red_flags":3,"ambulatory_flow":3,"emergency_flow":2,"monitoring":3,"special_populations":5}; MIN_TEXT_CHARS={"epidemiology":700,"treatment_summary":1800}; MIN_DIAGNOSTIC_APPROACH_CHARS=800
PASTAS_NAO_DOCUMENTO=("Farmacologia","Calculadoras","Exames"); DOSE_PATTERNS=(r"\d+[\.,]?\d*\s*mg\b",r"\d+[\.,]?\d*\s*mg/kg",r"\d+[\.,]?\d*\s*mcg"); ALLOWED_ADD_KEYS={"risk","red_flags","supporting","opposing","missing_information","suggested_tests","differentials","ambulatory_flow","emergency_flow","messages"}
DOCUMENTOS_COMPARTILHADOS_COM_OUTRAS_FICHAS={
 "hipertensao-arterial-sistemica-na-crianca-e-no-adolescente-diagnostico-por-percentil-causas-secundarias-e-tratamento-aap-2017",
 "coarctacao-de-aorta-na-crianca-diagnostico-criterios-de-intervencao-e-hipertensao-residual",
 "sindrome-de-turner-na-crianca-e-adolescente-espectro-cardiovascular-indice-de-tamanho-aortico-e-rastreio-antes-do-estrogenio",
 "obesidade-infantil-e-risco-cardiovascular-hipertensao-dislipidemia-aterogenica-e-dano-subclinico-em-orgao-alvo",
}
def _load_doencas():
 items=json.loads(DOENCAS_PATH.read_text(encoding="utf-8")); return {x["slug"]:x for x in items}
def _all_document_paths():
 result={}
 for p in (REPOSITORY_ROOT/"content").rglob("*.md"):
  t=p.read_text(encoding="utf-8",errors="replace"); s=None
  if t.startswith("---"):
   m=re.search(r'^slug:\s*["\']?([^"\'\n]+)',t.split("---",2)[1],re.MULTILINE); s=m.group(1).strip() if m else None
  result[s or p.stem]=p
 return result
def test_ficha_continua_existindo_com_mesmo_slug(): assert SLUG in _load_doencas()
def test_marcacao_editorial_correta():
 i=_load_doencas()[SLUG]; assert i.get("fonte_producao")=="claude"; assert i.get("review_status")=="pendente_revisao"; assert i.get("completeness")=="completo"; assert i.get("area")=="cardiopediatria"; assert i.get("review_note"); assert i.get("source_refs") and len(i["source_refs"])>=5; assert i.get("version")==2
def test_catalogacao_e_conteudo_previo_preservados():
 i=_load_doencas()[SLUG]; assert i.get("name")=="Hipertensão arterial pediátrica"; assert "HAS pediátrica" in (i.get("aliases") or []); assert i.get("category")=="doenca_prevalente"; assert i.get("subtype")=="pressao_arterial"; assert i.get("prevalence_rank")==1; assert len(i.get("assistant_questions") or [])>=5; assert len(i.get("assistant_rules") or [])>=5
def test_profundidade_minima_dos_campos_preenchidos_e_dos_novos():
 i=_load_doencas()[SLUG]
 for f,n in MIN_LIST_ITEMS.items(): assert isinstance(i.get(f) or [],list) and len(i.get(f) or [])>=n
 for f,n in MIN_TEXT_CHARS.items(): assert isinstance(i.get(f) or "",str) and len(i.get(f) or "")>=n
 d=i.get("diagnostic_approach"); assert d and isinstance(d,(str,dict)); assert (len(d) if isinstance(d,str) else len(json.dumps(d,ensure_ascii=False)))>=MIN_DIAGNOSTIC_APPROACH_CHARS
def test_assistente_deterministico_seguro():
 i=_load_doencas()[SLUG]; q=i.get("assistant_questions") or []; r=i.get("assistant_rules") or []; qe,ids=validate_question_definitions(SLUG,q); re_=validate_rule_definitions(SLUG,r,ids); assert qe==[] and re_==[]; assert any(x.get("priority",0)>=70 for x in r)
 for x in r: assert not(set(x.get("add",{}))-ALLOWED_ADD_KEYS)
 s=json.dumps(r,ensure_ascii=False).casefold(); assert "mwho" not in s and "hfa-icos" not in s
def test_nenhuma_dose_de_farmaco_em_nenhum_campo():
 s=json.dumps(_load_doencas()[SLUG],ensure_ascii=False)
 for p in DOSE_PATTERNS: assert re.findall(p,s)==[]
def test_vinculos_tudo_com_tudo_resolvem_e_sao_documentos_narrativos():
 i=_load_doencas()[SLUG]; docs=_all_document_paths(); rel=i.get("related_document_slugs") or []; assert len(rel)>=4; assert [x for x in rel if x not in docs]==[]; assert [x for x in rel if any(a in str(docs[x]) for a in PASTAS_NAO_DOCUMENTO)]==[]; assert len(rel)==len(set(rel))
def test_related_document_slugs_sao_todos_sobre_hipertensao():
 i=_load_doencas()[SLUG]; docs=_all_document_paths()
 for x in i.get("related_document_slugs") or []: assert "hipertens" in docs[x].read_text(encoding="utf-8",errors="replace").casefold()
def test_documentos_compartilhados_sao_os_esperados_e_documentados():
 i=_load_doencas()[SLUG]; ds=_load_doencas(); rel=set(i.get("related_document_slugs") or []); found=set()
 for slug,o in ds.items():
  if slug!=SLUG: found|=rel&set(o.get("related_document_slugs") or [])
 unexpected=found-DOCUMENTOS_COMPARTILHADOS_COM_OUTRAS_FICHAS; assert unexpected==set(),f"sobreposição não documentada com outra ficha: {unexpected}"
def test_patient_material_slug_resolve_quando_presente():
 i=_load_doencas()[SLUG]; m=i.get("patient_material_slug")
 if not m: return
 assert m in {x["slug"] for x in json.loads((REPOSITORY_ROOT/"material-paciente/metadados.json").read_text(encoding="utf-8"))}