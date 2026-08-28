"""Contrato do lote de APROFUNDAMENTO Tudo com Tudo de 28/08/2026 — ficha
já existente dor-toracica-pediatrica (área cardiopediatria) em
doencas/metadados.json.

Sexto lote de aprofundamento do dia. O lote não cria documento novo: conecta a
ficha a conteúdo já publicado e revisado, mantendo o contrato Tudo com Tudo.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from app.services.clinical_rule_engine import validate_question_definitions, validate_rule_definitions

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DOENCAS_PATH = REPOSITORY_ROOT / "doencas/metadados.json"
SLUG = "dor-toracica-pediatrica"
MIN_LIST_ITEMS = {"presentation":6,"differentials":6,"tests":5,"red_flags":5,"ambulatory_flow":5,"emergency_flow":3,"monitoring":5,"special_populations":4}
MIN_TEXT_CHARS = {"epidemiology":600,"treatment_summary":1500}
MIN_DIAGNOSTIC_APPROACH_CHARS = 800
PASTAS_NAO_DOCUMENTO = ("Farmacologia", "Calculadoras", "Exames")
DOSE_PATTERNS = (r"\d+[\.,]?\d*\s*mg\b",r"\d+[\.,]?\d*\s*mg/kg",r"\d+[\.,]?\d*\s*mcg")
ALLOWED_ADD_KEYS = {"risk","red_flags","supporting","opposing","missing_information","suggested_tests","differentials","ambulatory_flow","emergency_flow","messages"}
DOCUMENTOS_COMPARTILHADOS_COM_OUTRAS_FICHAS = {
    "dor-toracica-pediatrica-avaliacao-de-sinais-de-alarme-cardiaco-vs-causa-nao-cardiaca",
    "sindrome-de-turner-na-crianca-e-adolescente-espectro-cardiovascular-indice-de-tamanho-aortico-e-rastreio-antes-do-estrogenio",
    "isquemia-coronaria-aguda-apos-switch-arterial",
    "descompensacao-aguda-da-circulacao-de-fontan",
    "cardiomiopatia-restritiva-na-crianca-e-no-adolescente-etiologia-genetica-diagnostico-diferencial-e-transplante-precoce",
    "miocardite-pos-vacina-de-mrna-em-adolescentes-incidencia-comparacao-com-covid-19-e-vigilancia-atual",
    "cardiomiopatia-induzida-por-taquicardia-na-crianca-diagnostico-diferencial-e-recuperacao-apos-ablacao",
    "miocardite-aguda-pediatrica-diagnostico-suporte-hemodinamico-e-ecmo",
    "trombose-coronaria-e-infarto-em-aneurisma-de-kawasaki",
    "miocardite-fulminante-pediatrica-e-choque-cardiogenico",
}

def _load_doencas() -> dict[str, dict]:
    items=json.loads(DOENCAS_PATH.read_text(encoding="utf-8")); return {item["slug"]:item for item in items}

def _all_document_paths() -> dict[str, Path]:
    result={}
    for path in (REPOSITORY_ROOT/"content").rglob("*.md"):
        text=path.read_text(encoding="utf-8",errors="replace"); slug=None
        if text.startswith("---"):
            frontmatter=text.split("---",2)[1]; match=re.search(r'^slug:\s*["\']?([^"\'\n]+)',frontmatter,re.MULTILINE)
            if match: slug=match.group(1).strip()
        result[slug or path.stem]=path
    return result

def test_ficha_continua_existindo_com_mesmo_slug(): assert SLUG in _load_doencas()
def test_marcacao_editorial_correta():
    item=_load_doencas()[SLUG]; assert item.get("fonte_producao")=="claude"; assert item.get("review_status")=="revisado"; assert item.get("completeness")=="completo"; assert item.get("area")=="cardiopediatria"; assert item.get("review_note"); assert item.get("source_refs") and len(item["source_refs"])>=5; assert item.get("version")==2
def test_catalogacao_original_preservada():
    item=_load_doencas()[SLUG]; assert item.get("name")=="Dor torácica pediátrica"; assert "dor no peito na criança" in (item.get("aliases") or []); assert item.get("category")=="sintoma_e_exame"; assert item.get("subtype")=="dor_toracica"; assert item.get("prevalence_rank")==29
def test_profundidade_minima_e_nao_e_resumo():
    item=_load_doencas()[SLUG]
    for field,minimum in MIN_LIST_ITEMS.items(): value=item.get(field) or []; assert isinstance(value,list); assert len(value)>=minimum
    for field,minimum in MIN_TEXT_CHARS.items(): value=item.get(field) or ""; assert isinstance(value,str); assert len(value)>=minimum
    diagnostic=item.get("diagnostic_approach"); assert diagnostic; assert isinstance(diagnostic,(str,dict)); assert (len(diagnostic) if isinstance(diagnostic,str) else len(json.dumps(diagnostic,ensure_ascii=False)))>=MIN_DIAGNOSTIC_APPROACH_CHARS
def test_assistente_deterministico_seguro():
    item=_load_doencas()[SLUG]; questions=item.get("assistant_questions") or []; rules=item.get("assistant_rules") or []; assert len(questions)>=3; assert len(rules)>=3; q_errors,q_ids=validate_question_definitions(SLUG,questions); r_errors=validate_rule_definitions(SLUG,rules,q_ids); assert q_errors==[]; assert r_errors==[]; assert any(rule.get("priority",0)>=70 for rule in rules)
    for rule in rules: assert not (set(rule.get("add",{}).keys())-ALLOWED_ADD_KEYS)
    serialized=json.dumps(rules,ensure_ascii=False).casefold(); assert "mwho" not in serialized; assert "hfa-icos" not in serialized
def test_nenhuma_dose_de_farmaco_em_nenhum_campo():
    serialized=json.dumps(_load_doencas()[SLUG],ensure_ascii=False)
    for pattern in DOSE_PATTERNS: assert re.findall(pattern,serialized)==[]
def test_vinculos_tudo_com_tudo_resolvem_e_sao_documentos_narrativos():
    item=_load_doencas()[SLUG]; documentos=_all_document_paths(); related=item.get("related_document_slugs") or []; assert len(related)>=10; assert [slug for slug in related if slug not in documentos]==[]; assert [slug for slug in related if any(pasta in str(documentos[slug]) for pasta in PASTAS_NAO_DOCUMENTO)]==[]; assert len(related)==len(set(related))
def test_related_document_slugs_sao_todos_sobre_dor_toracica():
    item=_load_doencas()[SLUG]; documentos=_all_document_paths()
    for slug in item.get("related_document_slugs") or []:
        texto=documentos[slug].read_text(encoding="utf-8",errors="replace").casefold(); assert "dor torácica" in texto or "dor toracica" in texto
def test_documentos_compartilhados_sao_os_esperados_e_documentados():
    item=_load_doencas()[SLUG]; doencas=_load_doencas(); related=set(item.get("related_document_slugs") or []); encontrados=set()
    for outro_slug,outro_item in doencas.items():
        if outro_slug!=SLUG: encontrados|=(related&set(outro_item.get("related_document_slugs") or []))
    inesperados=encontrados-DOCUMENTOS_COMPARTILHADOS_COM_OUTRAS_FICHAS; assert inesperados==set(),f"sobreposição não documentada com outra ficha: {inesperados}"
def test_patient_material_slug_resolve():
    item=_load_doencas()[SLUG]; material=item.get("patient_material_slug"); assert material=="dor-toracica-pediatrica"; materiais={x["slug"] for x in json.loads((REPOSITORY_ROOT/"material-paciente/metadados.json").read_text(encoding="utf-8"))}; assert material in materiais