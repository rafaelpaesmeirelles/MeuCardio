---
title: "GRACE 2.0 (Global Registry of Acute Coronary Events)"
slug: grace-20-global-registry-of-acute-coronary-events
theme: "Calculadoras"
kind: calculadora
review_status: pendente_revisao
source_refs: []
legacy_source: "calculadoras/calculadora-grace-2-0-completa.md"
---

# GRACE 2.0 (Global Registry of Acute Coronary Events)

## Nome
GRACE 2.0 (Global Registry of Acute Coronary Events)

## Aplicacao
Estimativa de mortalidade intra-hospitalar e em 6 meses em pacientes com síndrome coronariana aguda (STEMI e AI/NSTEMI)

## Variaveis pontuacao
- **parametro**: Idade; **faixas**: [{'faixa': '<30', 'pontos': 0}, {'faixa': '30-39', 'pontos': 8}, {'faixa': '40-49', 'pontos': 25}, {'faixa': '50-59', 'pontos': 41}, {'faixa': '60-69', 'pontos': 58}, {'faixa': '70-79', 'pontos': 75}, {'faixa': '80-89', 'pontos': 91}, {'faixa': '>90', 'pontos': 100}]
- **parametro**: Frequência cardíaca (bpm); **faixas**: [{'faixa': '<50', 'pontos': 0}, {'faixa': '50-69', 'pontos': 3}, {'faixa': '70-89', 'pontos': 9}, {'faixa': '90-109', 'pontos': 15}, {'faixa': '110-149', 'pontos': 24}, {'faixa': '150-199', 'pontos': 38}, {'faixa': '>200', 'pontos': 46}]
- **parametro**: PA sistólica (mmHg); **faixas**: [{'faixa': '<80', 'pontos': 58}, {'faixa': '80-99', 'pontos': 53}, {'faixa': '100-119', 'pontos': 43}, {'faixa': '120-139', 'pontos': 34}, {'faixa': '140-159', 'pontos': 24}, {'faixa': '160-199', 'pontos': 10}, {'faixa': '>200', 'pontos': 0}]
- **parametro**: Creatinina (µmol/L); **faixas**: [{'faixa': '<35,36', 'pontos': 1}, {'faixa': '35,36-70,71', 'pontos': 4}, {'faixa': '70,72-106,07', 'pontos': 7}, {'faixa': '106,08-141,43', 'pontos': 10}, {'faixa': '141,43-176,7', 'pontos': 13}, {'faixa': '176,8-353', 'pontos': 21}, {'faixa': '≥354', 'pontos': 28}]
- **parametro**: Classe Killip; **faixas**: [{'faixa': 'I - sem sinais de IC', 'pontos': 0}, {'faixa': 'II - estertores e/ou turgência jugular', 'pontos': 20}, {'faixa': 'III - edema pulmonar agudo', 'pontos': 39}, {'faixa': 'IV - choque cardiogênico', 'pontos': 59}]
- **parametro**: Parada cardíaca na admissão; **faixas**: [{'faixa': 'Sim', 'pontos': 39}, {'faixa': 'Não', 'pontos': 0}]
- **parametro**: Desvio de segmento ST no ECG; **faixas**: [{'faixa': 'Sim', 'pontos': 28}, {'faixa': 'Não', 'pontos': 0}]
- **parametro**: Enzimas cardíacas anormais; **faixas**: [{'faixa': 'Sim', 'pontos': 14}, {'faixa': 'Não', 'pontos': 0}]

## Formula
Soma direta de todos os pontos das 8 variáveis clínicas

## Interpretacao mortalidade 6 meses
- **pontuacao**: 0-87; **risco**: 0-2%
- **pontuacao**: 88-128; **risco**: 3-10%
- **pontuacao**: 129-149; **risco**: 10-20%
- **pontuacao**: 150-173; **risco**: 20-30%
- **pontuacao**: 174-182; **risco**: 40%
- **pontuacao**: 183-190; **risco**: 50%
- **pontuacao**: 191-199; **risco**: 60%
- **pontuacao**: 200-207; **risco**: 70%
- **pontuacao**: 208-218; **risco**: 80%
- **pontuacao**: 219-284; **risco**: 90%
- **pontuacao**: ≥285; **risco**: 99%

## Modelo alternativo nao linear
- **descricao**: Versão GRACE 2.0 (2014) usa modelo de regressão logística não linear em vez de soma de pontos por faixa, com equação: xb = -7,7035 + (0,0531×idade) + (0,0087×FC) - (0,0168×PAS) + (0,1823×Killip) + (0,6931×parada cardíaca) + (1,4586×desvio ST) + (0,4700×enzimas) + (0,8755×creatinina)
- **probabilidade**: p = exp(xb) / (1 + exp(xb)), representando probabilidade de óbito da admissão até 6 meses
- **fonte**: RDocumentation

## Aplicacao pratica
Amplamente recomendado sobre TIMI para estratificação de risco em SCA devido à melhor discriminação prognóstica; orienta decisão sobre timing de estratégia invasiva (urgente vs. precoce vs. eletiva)

## Limitacoes
Requer 8 variáveis para cálculo completo, mais complexo de aplicar à beira do leito sem calculadora eletrônica em comparação a escores mais simples como TIMI

## Fonte
ClinCaseQuest ; MedCentral ; GRACE Score oficial
