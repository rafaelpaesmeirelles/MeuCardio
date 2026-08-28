"""Contrato do aprofundamento pontual Tudo com Tudo de hipotensão ortostática — 28/08/2026."""
from __future__ import annotations
import json,re
from pathlib import Path
from app.services.clinical_rule_engine import validate_question_definitions,validate_rule_definitions
REPOSITORY_ROOT=Path(__file__).resolve().parents[2]; DOENCAS_PATH=REPOSITORY_ROOT/"doencas/metadados.json"; SLUG="hipotensao-ortostatica-no-idoso"
MIN_LIST_ITEMS={"presentation":3,"differentials":4,"tests":3,"red_flags":3,"ambulatory_flow":3,"emergency_flow":2,"monitoring":5,"special_populations":5}; MIN_TEXT_CHARS={"epidemiology":600,"treatment_summary":1500}
PASTAS_NAO_DOCUMENTO=("Farmacologia","Calculadoras","Exames"); DOSE_PATTERNS=(r"\d+[\.,]?\d*\s*mg\b",r"\d+[\.,]?\d*\s*mg/kg",r"\d+[\.,]?\d*\s*mcg"); ALLOWED_ADD_KEYS={"risk","red_flags","supporting","opposing","missing_information","suggested_tests","differentials","ambulatory_flow","emergency_flow","messages"}
DOCUMENTOS_ORIGINAIS={"hipotensao-ortostatica-e-sindrome-de-taquicardia-postural-pots-diagnostico-diferencial","hipotensao-pos-prandial-no-idoso-cardiopata-mecanismo-prevalencia-e-manejo","hipotensao-ortostatica-nao-e-motivo-para-desescalonar-o-anti-hipertensivo"}
DOCUMENTOS_COMPARTILHADOS_COM_OUTRAS_FICHAS={
 "hipotensao-ortostatica-e-sindrome-de-taquicardia-postural-pots-diagnostico-diferencial",
 "hipotensao-pos-prandial-no-idoso-cardiopata-mecanismo-prevalencia-e-manejo",
 "fluxograma-hipotensao-ortostatica-diagnostico-causa-e-manejo-escalonado",
 "fluxograma-sincope-reflexa-versus-cardiaca-diagnostico-diferencial",
 "fluxograma-sincope-idoso-investigacao-diferenciada",
 "sincope-classificacao-etiologica-em-tres-grandes-grupos",
 "sincope-diagnostico-e-manejo-esc-2018",
 "sincope-e-risco-de-fratura-por-queda-o-que-os-estudos-de-coorte-mostram",
 "fluxograma-hipertensao-no-idoso-e-no-fragil-quando-iniciar-alvo-e-desintensificacao-esc-2024",
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
def test_marcacao_editorial_correta_apos_aprofundamento():
 i=_load_doencas()[SLUG]; assert i.get("fonte_producao")=="claude"; assert i.get("review_status")=="pendente_revisao"; assert i.get("completeness")=="completo"; assert i.get("area")=="cardiogeriatria"; assert i.get("review_note"); assert i.get("source_refs") and len(i["source_refs"])>=5; assert i.get("version")==2
def test_catalogacao_e_conteudo_previo_preservados():
 i=_load_doencas()[SLUG]; assert i.get("name")=="Hipotensão ortostática no idoso"; assert "queda de pressão ao levantar" in (i.get("aliases") or []); assert i.get("category")=="sindrome_geriatrica"; assert i.get("subtype")=="quedas_e_sincope"; assert i.get("prevalence_rank")==2; assert len(i.get("assistant_questions") or [])>=5; assert len(i.get("assistant_rules") or [])>=5
def test_profundidade_minima_dos_campos_preenchidos_e_dos_novos():
 i=_load_doencas()[SLUG]
 for f,n in MIN_LIST_ITEMS.items(): assert isinstance(i.get(f) or [],list) and len(i.get(f) or [])>=n
 for f,n in MIN_TEXT_CHARS.items(): assert isinstance(i.get(f) or "",str) and len(i.get(f) or "")>=n
def test_assistente_deterministico_seguro():
 i=_load_doencas()[SLUG]; q=i.get("assistant_questions") or []; r=i.get("assistant_rules") or []; qe,ids=validate_question_definitions(SLUG,q); re_=validate_rule_definitions(SLUG,r,ids); assert qe==[] and re_==[]; assert any(x.get("priority",0)>=70 for x in r)
 for x in r: assert not(set(x.get("add",{}))-ALLOWED_ADD_KEYS)
 s=json.dumps(r,ensure_ascii=False).casefold(); assert "mwho" not in s and "hfa-icos" not in s
def test_nenhuma_dose_de_farmaco_em_nenhum_campo():
 s=json.dumps(_load_doencas()[SLUG],ensure_ascii=False)
 for p in DOSE_PATTERNS: assert re.findall(p,s)==[]
def test_vinculos_tudo_com_tudo_resolvem_e_sao_documentos_narrativos():
 i=_load_doencas()[SLUG]; docs=_all_document_paths(); rel=i.get("related_document_slugs") or []; assert len(rel)>=12; assert DOCUMENTOS_ORIGINAIS.issubset(set(rel)); assert [x for x in rel if x not in docs]==[]; assert [x for x in rel if any(a in str(docs[x]) for a in PASTAS_NAO_DOCUMENTO)]==[]; assert len(rel)==len(set(rel))
def test_related_document_slugs_sao_todos_sobre_hipotensao_ortostatica():
 i=_load_doencas()[SLUG]; docs=_all_document_paths(); terms=("hipotensão ortostática","hipotensao ortostatica","hipotensão postural")
 for x in i.get("related_document_slugs") or []: assert any(t in docs[x].read_text(encoding="utf-8",errors="replace").casefold() for t in terms)
def test_documentos_compartilhados_sao_os_esperados_e_documentados():
 i=_load_doencas()[SLUG]; ds=_load_doencas(); rel=set(i.get("related_document_slugs") or []); found=set()
 for slug,o in ds.items():
  if slug!=SLUG: found|=rel&set(o.get("related_document_slugs") or [])
 unexpected=found-DOCUMENTOS_COMPARTILHADOS_COM_OUTRAS_FICHAS; assert unexpected==set(),f"sobreposição não documentada com outra ficha: {unexpected}"
def test_patient_material_slug_resolve():
 i=_load_doencas()[SLUG]; m=i.get("patient_material_slug"); assert m=="tontura-ao-levantar-hipotensao-ortostatica-e-pots"; assert m in {x["slug"] for x in json.loads((REPOSITORY_ROOT/"material-paciente/metadados.json").read_text(encoding="utf-8"))}