"""Clinical decision regressions from unresolved PRs 717, 723 and 700."""
from pathlib import Path
import sys
import pytest
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'backend'))
from app.services.disease_manifest import load_disease_records
from app.services.clinical_rule_engine import evaluate_rules

@pytest.fixture(scope='module')
def hubs():
    return {x['slug']: x for x in load_disease_records(ROOT / 'doencas/metadados.json')}

def evaluate(hubs, slug, **answers):
    x = hubs[slug]
    return evaluate_rules(questions=x['assistant_questions'], rules=x['assistant_rules'], answers=answers)

@pytest.mark.parametrize('severity', ['leve', 'moderada'])
@pytest.mark.parametrize('symptomatic', [True, False])
def test_nonsevere_ar_does_not_recommend_valve_intervention(hubs, severity, symptomatic):
    result = evaluate(hubs, 'insuficiencia-aortica', apresentacao_temporal='cronica', gravidade_eco=severity,
        sintomas_atribuiveis_ia=symptomatic, feve_repouso_percent=40, dsfve_mm=60,
        risco_cirurgico='baixo', indicacao_outra_cirurgia_cardiaca_concomitante=True)
    assert not result['invalid_fields']
    assert not any(x.startswith('cronica_') or x == 'cirurgia_cardiaca_concomitante' for x in result['matched_rules'])

def test_severe_symptomatic_ar_triggers_assessment(hubs):
    result = evaluate(hubs, 'insuficiencia-aortica', apresentacao_temporal='cronica', gravidade_eco='grave',
        sintomas_atribuiveis_ia=True, risco_cirurgico='intermediario_alto')
    assert 'cronica_sintomatica_cirurgia' in result['matched_rules']

def test_inoperable_ar_does_not_trigger_surgical_recommendation(hubs):
    result = evaluate(hubs, 'insuficiencia-aortica', apresentacao_temporal='cronica', gravidade_eco='grave',
        sintomas_atribuiveis_ia=True, risco_cirurgico='proibitivo', anatomia_adequada_tavi_dedicado=True)
    assert 'cronica_sintomatica_cirurgia' not in result['matched_rules']
    assert 'cronica_sintomatica_risco_proibitivo_tavi' in result['matched_rules']

@pytest.mark.parametrize('ef,expected', [(50,'cronica_assintomatica_disfuncao_ve_classe_i'), (54,'cronica_assintomatica_zona_iib_baixo_risco')])
def test_ar_class_i_and_iib_are_not_concurrent(hubs, ef, expected):
    result = evaluate(hubs, 'insuficiencia-aortica', apresentacao_temporal='cronica', gravidade_eco='grave',
        sintomas_atribuiveis_ia=False, risco_cirurgico='baixo', feve_repouso_percent=ef)
    assert expected in result['matched_rules']
    assert sum(x.startswith('cronica_assintomatica_') for x in result['matched_rules']) == 1

@pytest.mark.parametrize('risk,expected', [(False,False),(True,True)])
def test_marfan_45mm_requires_additional_risk(hubs, risk, expected):
    result = evaluate(hubs, 'insuficiencia-aortica', etiologia_aortopatia='marfan',
        diametro_raiz_aorta_ascendente_mm=45, marfan_fator_risco_adicional=risk)
    assert ('aorta_dilatada_tecido_conjuntivo' in result['matched_rules']) == expected

@pytest.mark.parametrize('context,variant,expected', [('achado_incidental','nao_testado',False),('achado_incidental','negativo_ou_indeterminado',False),('diagnostico_ja_confirmado','nao_testado',True),('rastreio_familiar','positivo_dsp',True)])
def test_acm_sport_counseling_requires_disease_or_causal_variant(hubs, context, variant, expected):
    result = evaluate(hubs, 'cardiomiopatia-arritmogenica', contexto_avaliacao=context,
        variante_genetica_identificada=variant, pratica_esporte_competitivo_endurance=True)
    assert not result['invalid_fields']
    assert ('restricao_esporte_endurance' in result['matched_rules']) == expected

@pytest.mark.parametrize('stage', ['nao_estadiado','mayo_i_iv','al_iss_i_iiib','al_iss_iiic'])
def test_confirmed_al_requires_treatment_at_every_stage(hubs, stage):
    result = evaluate(hubs, 'amiloidose-cardiaca-cadeia-leve', age_years=65, acute_instability=False,
        amyloid_typing='cadeia_leve_al', cardiac_biomarker_stage=stage)
    assert 'al-confirmada-tratamento-todos-estagios' in result['matched_rules']
    assert ('tipagem-confirma-al-estagio-ultra-alto' in result['matched_rules']) == (stage == 'al_iss_iiic')

def test_unperformed_al_workup_cannot_reassure(hubs):
    result = evaluate(hubs, 'amiloidose-cardiaca-cadeia-leve', age_years=65, acute_instability=False,
        extracardiac_al_signs=False, monoclonal_workup='nao_solicitado')
    assert 'sem-sinais-de-alerta' not in result['matched_rules']
    assert 'investigacao-clonal-nao-realizada' in result['matched_rules']

def test_indeterminate_typing_with_clone_is_not_a_dead_end(hubs):
    result = evaluate(hubs, 'amiloidose-cardiaca-cadeia-leve', age_years=65, acute_instability=False,
        amyloid_typing='indeterminada', monoclonal_workup='alterado')
    assert 'clonalidade-alterada-sem-tipagem' in result['matched_rules']

def test_acute_al_instability_overrides_stable_routing(hubs):
    result = evaluate(hubs, 'amiloidose-cardiaca-cadeia-leve', age_years=65, acute_instability=True,
        amyloid_typing='cadeia_leve_al', cardiac_biomarker_stage='mayo_i_iv')
    assert result['risk'] == 'emergencia'
    assert result['recommended_flow']
