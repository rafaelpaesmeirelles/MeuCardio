"""Contrato do fechamento de lacuna Tudo com Tudo da miocardite pediátrica — 28/08/2026."""
from __future__ import annotations
import json,re
from pathlib import Path
REPOSITORY_ROOT=Path(__file__).resolve().parents[2]; DOENCAS_PATH=REPOSITORY_ROOT/"doencas/metadados.json"; SLUG="miocardite-pediatrica"; PASTAS_NAO_DOCUMENTO=("Farmacologia","Calculadoras","Exames"); TERMOS_TEMA=("miocardite",)
DOCUMENTOS_COMPARTILHADOS_COM_OUTRAS_FICHAS={
 "miocardite-fulminante-pediatrica-e-choque-cardiogenico",
 "miocardite-pos-vacina-de-mrna-em-adolescentes-incidencia-comparacao-com-covid-19-e-vigilancia-atual",
 "miocardite-aguda-pediatrica-diagnostico-suporte-hemodinamico-e-ecmo",
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
 i=_load_doencas()[SLUG]; assert i.get("fonte_producao")=="claude"; assert i.get("review_status")=="pendente_revisao"; assert i.get("completeness")=="completo"; assert i.get("area")=="cardiopediatria"; assert i.get("review_note"); assert i.get("version")==2
def test_catalogacao_e_conteudo_clinico_preexistente_preservados():
 i=_load_doencas()[SLUG]; assert i.get("name")=="Miocardite pediátrica"; assert "miocardite na criança" in (i.get("aliases") or []); assert i.get("category")=="doenca_miocardica"; assert i.get("prevalence_rank")==3; assert i.get("treatment_summary"); assert len(i.get("assistant_rules") or [])>=4
def test_vinculos_tudo_com_tudo_resolvem_e_sao_documentos_narrativos():
 i=_load_doencas()[SLUG]; docs=_all_document_paths(); rel=i.get("related_document_slugs") or []; assert 3<=len(rel)<=7; assert [x for x in rel if x not in docs]==[]; assert [x for x in rel if any(a in str(docs[x]) for a in PASTAS_NAO_DOCUMENTO)]==[]; assert len(rel)==len(set(rel))
def test_related_document_slugs_mencionam_miocardite():
 i=_load_doencas()[SLUG]; docs=_all_document_paths()
 for x in i.get("related_document_slugs") or []: assert any(t in docs[x].read_text(encoding="utf-8",errors="replace").casefold() for t in TERMOS_TEMA)
def test_documentos_compartilhados_sao_os_esperados_e_documentados():
 i=_load_doencas()[SLUG]; ds=_load_doencas(); rel=set(i.get("related_document_slugs") or []); found=set()
 for slug,o in ds.items():
  if slug!=SLUG: found|=rel&set(o.get("related_document_slugs") or [])
 unexpected=found-DOCUMENTOS_COMPARTILHADOS_COM_OUTRAS_FICHAS; assert unexpected==set(),f"sobreposição não documentada com outra ficha: {unexpected}"
def test_patient_material_slug_resolve():
 i=_load_doencas()[SLUG]; m=i.get("patient_material_slug"); assert m=="miocardite-inflamacao-do-musculo-do-coracao-e-recuperacao"; assert m in {x["slug"] for x in json.loads((REPOSITORY_ROOT/"material-paciente/metadados.json").read_text(encoding="utf-8"))}