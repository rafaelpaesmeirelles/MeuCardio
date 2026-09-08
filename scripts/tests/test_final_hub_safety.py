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

@pytest.mark.parametrize('major,minor,positive', [('1','1',False),('1','2',True),('2','0',True)])
def test_sarcoidosis_jcs_alternative_path(hubs, major, minor, positive):
    result = evaluate(hubs, 'sarcoidose-cardiaca', criterios_maiores_sjc_atendidos=major, criterios_menores_sjc_atendidos=minor)
    assert not result['invalid_fields']
    assert any(x in result['matched_rules'] for x in ['jcs_um_maior_dois_menores','criterios_maiores_suficientes']) == positive

@pytest.mark.parametrize('biopsy,rule_id', [('granuloma_nao_caseoso','biopsia_granuloma_nao_caseoso'),('negativa_inconclusiva','biopsia_negativa_nao_exclui')])
def test_sarcoidosis_biopsy_outcomes_have_guidance(hubs, biopsy, rule_id):
    result = evaluate(hubs, 'sarcoidose-cardiaca', biopsia_realizada_resultado=biopsy)
    assert rule_id in result['matched_rules']
    assert result['supporting'] or result['messages']

def test_qt_polymorphic_vt_has_immediate_flow(hubs):
    result = evaluate(hubs, 'torsades-de-pointes-qt-longo-adquirido', tv_polimorfica_sustentada_em_curso=True)
    assert result['risk'] == 'emergencia'
    assert result['recommended_flow']

def test_negative_qtc_is_invalid(hubs):
    result = evaluate(hubs, 'torsades-de-pointes-qt-longo-adquirido', qtc_medido_ms=-10)
    assert result['invalid_fields'] == ['qtc_medido_ms']

def test_isolated_qtc500_does_not_force_emergency(hubs):
    result = evaluate(hubs, 'torsades-de-pointes-qt-longo-adquirido', qtc_medido_ms=500)
    assert result['risk'] == 'prioritario'
    assert result['recommended_flow']

@pytest.mark.parametrize('score,expected', [('6','baixo'),('7','moderado'),('10','moderado'),('11','alto'),('21','alto')])
def test_tisdale_confirmed_total_boundaries(hubs, score, expected):
    result = evaluate(hubs, 'torsades-de-pointes-qt-longo-adquirido', tisdale_total_conferido=score)
    assert not result['invalid_fields']
    assert 'tisdale_total_'+expected in result['matched_rules']
    assert len([x for x in result['matched_rules'] if x.startswith('tisdale_total_')]) == 1

@pytest.mark.parametrize('size,small', [(9,True),(10,False),(12,False)])
def test_prosthetic_thrombus_size_guidance_is_consistent(hubs, size, small):
    result = evaluate(hubs, 'protese-valvar-mecanica', tipo_de_trombose='nao_obstrutiva', tamanho_trombo_mm=size,
        evento_embolico_associado=False, persistencia_apesar_anticoagulacao_otima=False)
    assert ('trombo_nao_obstrutivo_pequeno_sem_repercussao' in result['matched_rules']) == small
    assert 'trombo_nao_obstrutivo_grande' not in result['matched_rules']

@pytest.mark.parametrize('contra,expected', [(True,False),(False,True)])
def test_fibrinolysis_requires_eligibility(hubs, contra, expected):
    result = evaluate(hubs, 'protese-valvar-mecanica', tipo_de_trombose='obstrutiva',posicao_valvar='tricuspide_pulmonar',
        trombose_confirmada_por_imagem=True, contraindicacao_fibrinolise=contra)
    assert ('protese_direita_favorece_fibrinolise' in result['matched_rules']) == expected

def test_acute_thrombus_gets_anticoagulation_guidance(hubs):
    result = evaluate(hubs, 'protese-valvar-mecanica', momento_clinico='suspeita_trombose_aguda', tempo_em_faixa_terapeutica_inadequado=True)
    assert 'tempo_em_faixa_inadequado_reforcar_educacao' in result['matched_rules']

@pytest.mark.parametrize('low,expected', [(True,True),(False,False)])
def test_as_early_intervention_requires_low_procedural_risk(hubs, low, expected):
    result = evaluate(hubs, 'estenose-aortica', gravidade_ecocardiograma='grave', sintomas_atribuiveis=False,
        fracao_ejecao_ve=60, bnp_muito_elevado=True, baixo_risco_procedimento=low)
    assert ('criterios-intervencao-precoce-assintomatico' in result['matched_rules']) == expected

def test_as_ef52_low_risk_not_missed(hubs):
    result = evaluate(hubs, 'estenose-aortica', gravidade_ecocardiograma='grave', sintomas_atribuiveis=False,
        fracao_ejecao_ve=52, feve_reduzida_atribuivel_ea=True, baixo_risco_procedimento=True)
    assert 'ea_feve50a55_baixo_risco' in result['matched_rules']

def test_moderate_as_concomitant_surgery_is_considered(hubs):
    result = evaluate(hubs, 'estenose-aortica', gravidade_ecocardiograma='moderada', outra_cirurgia_cardiaca_indicada=True,
        risco_cirurgico_aceitavel_concomitante=True)
    assert 'ea_moderada_cirurgia_concomitante' in result['matched_rules']

@pytest.mark.parametrize('age,expected', [(55,'ea_modalidade_savr_menor70'),(75,'ea_modalidade_tavi70')])
def test_as_modality_uses_age_after_indication(hubs, age, expected):
    result = evaluate(hubs, 'estenose-aortica', gravidade_ecocardiograma='grave', intervencao_valvar_indicada_heart_team=True,
        idade_anos=age,morfologia_valvar='tricuspide', anatomia_adequada_tavi=True,risco_cirurgico_estimado='baixo')
    assert expected in result['matched_rules']

def test_adult_respiratory_arrest_with_pulse_does_not_start_compressions(hubs):
    result = evaluate(hubs, 'parada-cardiorrespiratoria-e-morte-subita-abortada', unresponsive=True,
        abnormal_breathing=True,pulse_status='definite',ems_and_aed=False)
    assert result['risk'] == 'emergencia'
    assert 'pulso-presente-ventilacao' in result['matched_rules']
    assert not {'presumir-parada','pulso-ausente-ou-incerto','cadeia-ainda-incompleta'} & set(result['matched_rules'])

@pytest.mark.parametrize('pulse',['lay_or_not_checked','absent_or_uncertain'])
def test_collapse_without_definite_pulse_starts_cpr(hubs,pulse):
    result = evaluate(hubs,'parada-cardiorrespiratoria-e-morte-subita-abortada',unresponsive=True,
        abnormal_breathing=True,pulse_status=pulse)
    assert 'presumir-parada' in result['matched_rules']

def test_unconscious_normal_breathing_has_emergency_route(hubs):
    result = evaluate(hubs,'parada-cardiorrespiratoria-e-morte-subita-abortada',unresponsive=True,
        abnormal_breathing=False,pulse_status='definite')
    assert result['risk']=='emergencia'
    assert 'inconsciente-respiracao-normal' in result['matched_rules']
    assert 'presumir-parada' not in result['matched_rules']

def test_rosc_does_not_continue_initial_compression_instruction(hubs):
    result = evaluate(hubs,'parada-cardiorrespiratoria-e-morte-subita-abortada',unresponsive=True,
        abnormal_breathing=True,pulse_status='absent_or_uncertain',rosc=True,ems_and_aed=False)
    assert result['risk']=='emergencia'
    assert 'pos-retorno-circulacao' in result['matched_rules']
    assert not {'presumir-parada','pulso-ausente-ou-incerto','cadeia-ainda-incompleta'} & set(result['matched_rules'])

@pytest.fixture(scope='module')
def collapse_triage():
    from app.services.triage_manifest import load_triage_records
    return next(x for x in load_triage_records(ROOT/'triagem-sintomas/metadados.json')
        if x['slug']=='colapso-subito-inconsciencia-e-respiracao-anormal')

def assess_collapse(x,**answers):
    return evaluate_rules(questions=x['questions'],rules=x['rules'],answers=answers,
        base_emergency_flow=x['emergency_flow'],base_ambulatory_flow=x['ambulatory_flow'])

@pytest.mark.parametrize('adult',[True,False])
def test_triage_definite_pulse_excludes_cpr_rules(collapse_triage,adult):
    result=assess_collapse(collapse_triage,scene_safe=True,adult_patient=adult,responsive=False,
        breathing_normally=False,definite_pulse_professional='definite_pulse',aed_requested=False)
    assert 'pulso-com-apneia-profissional' in result['matched_rules']
    assert not {'respiracao-anormal-nao-e-respiracao-normal','dea-ainda-nao-solicitado',
        'possivel-parada-leigo','possivel-parada-profissional','pediatrico-sem-resposta-respiracao-anormal'} & set(result['matched_rules'])

def test_child_collapse_no_longer_falls_through(collapse_triage):
    result=assess_collapse(collapse_triage,scene_safe=True,adult_patient=False,responsive=False,
        breathing_normally=False,definite_pulse_professional='not_assessed_lay')
    assert result['risk']=='emergencia'
    assert 'pediatrico-sem-resposta-respiracao-anormal' in result['matched_rules']
    assert 'possivel-parada-leigo' not in result['matched_rules']

def test_pregnancy_alone_is_not_collapse_emergency(collapse_triage):
    result=assess_collapse(collapse_triage,scene_safe=True,adult_patient=True,responsive=True,
        breathing_normally=True,special_cause=True)
    assert not result['matched_rules']
    assert result['risk'] not in {'urgente','emergencia'}

def test_unsafe_scene_does_not_instruct_approach(collapse_triage):
    result=assess_collapse(collapse_triage,scene_safe=False,adult_patient=True,responsive=False,
        breathing_normally=False,definite_pulse_professional='definite_pulse',special_cause=True)
    assert result['matched_rules']==['cena-insegura']

def test_triage_normal_breathing_unconscious_not_reassured(collapse_triage):
    result=assess_collapse(collapse_triage,scene_safe=True,responsive=False,breathing_normally=True)
    assert 'inconsciente-com-respiracao-normal' in result['matched_rules']
    assert result['risk']=='emergencia'

@pytest.mark.parametrize('degree',['segundo_grau_mobitz_2','alto_grau','terceiro_grau_completo'])
def test_advanced_avb_permanent_pacing_does_not_require_symptoms(hubs,degree):
    result=evaluate(hubs,'bloqueio-atrioventricular',grau_bav=degree,sintomatico=False,
        instabilidade_hemodinamica_aguda=False,causa_reversivel_identificada=False,
        investigacao_reversibilidade_concluida=True)
    assert 'bav-avancado-indicacao-permanente' in result['matched_rules']
    assert result['risk']=='urgente'
    assert result['recommended_flow']
    assert not any('ambulatorial prolongada' in str(x) for x in result['suggested_tests'])

def test_reversible_avb_has_support_without_automatic_permanent_implant(hubs):
    result=evaluate(hubs,'bloqueio-atrioventricular',grau_bav='terceiro_grau_completo',sintomatico=False,
        causa_reversivel_identificada=True,investigacao_reversibilidade_concluida=True)
    assert 'bav-avancado-causa-reversivel' in result['matched_rules']
    assert 'bav-avancado-indicacao-permanente' not in result['matched_rules']

def test_incidental_first_degree_avb_does_not_trigger_pacing_for_other_shock(hubs):
    result=evaluate(hubs,'bloqueio-atrioventricular',grau_bav='primeiro_grau',sintomatico=False,
        instabilidade_hemodinamica_aguda=True,instabilidade_atribuivel_bradicardia=False)
    assert result['risk']=='emergencia'
    assert 'instabilidade-investigar-causa' in result['matched_rules']
    assert 'bav_alto_grau_instavel_emergencia' not in result['matched_rules']
    assert 'primeiro_grau_ou_mobitz1_assintomatico_rotina' not in result['matched_rules']

def test_lyme_serology_alone_does_not_prescribe_antibiotic(hubs):
    result=evaluate(hubs,'bloqueio-atrioventricular',sorologia_lyme_realizada='sim_positiva',
        cardite_lyme_clinicamente_compativel=False)
    assert 'lyme_confirmada_tratamento' not in result['matched_rules']
    assert 'lyme-sorologia-isolada' in result['matched_rules']

def test_suspected_lyme_carditis_does_not_wait_for_serology(hubs):
    result=evaluate(hubs,'bloqueio-atrioventricular',sorologia_lyme_realizada='nao_realizada',
        cardite_lyme_clinicamente_compativel=True)
    assert 'lyme-suspeita-clinica-nao-esperar-sorologia' in result['matched_rules']

def test_two_to_one_avb_not_equated_with_mobitz2(hubs):
    result=evaluate(hubs,'bloqueio-atrioventricular',grau_bav='bav_2_1_indeterminado',
        causa_reversivel_identificada=False,investigacao_reversibilidade_concluida=True)
    assert not result['invalid_fields']
    assert 'bav-2-1-definir-nivel' in result['matched_rules']
    assert 'bav-avancado-indicacao-permanente' not in result['matched_rules']
