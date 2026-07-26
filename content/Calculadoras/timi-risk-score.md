---
title: "TIMI Risk Score"
slug: timi-risk-score
theme: "Calculadoras"
kind: calculadora
review_status: pendente_revisao
source_refs: []
legacy_source: "calculadoras/calculadora-timi-risk-score.md"
---

# TIMI Risk Score

## Nome
TIMI Risk Score

## Aplicacao
Estimativa de risco em síndrome coronariana aguda, com versões distintas para angina instável/NSTEMI e para STEMI

## Versao ua nstemi
- **variaveis**: ['Idade ≥65 anos', '≥3 fatores de risco para DAC', 'Estenose coronariana ≥50% conhecida', 'Uso de AAS nos últimos 7 dias', '≥2 episódios de angina em <24h', 'Desvio de segmento ST ≥0,5mm', 'Marcadores cardíacos elevados']
- **pontuacao**: 1 ponto cada variável presente (escore de 0 a 7)
- **interpretacao**: 0-2 pontos: baixo risco; 3-5 pontos: risco intermediário; ≥6 pontos: alto risco
- **fonte**: PMC  (tabela comparativa de escores de risco em SCA)

## Versao stemi
- **variaveis**: ['Idade 65-74/>75 anos (2/3 pontos)', 'Diabetes, hipertensão ou angina prévia', 'PAS <100 mmHg', 'FC >100 bpm', 'Classe Killip ≥2', 'Peso <67 kg', 'IAM anterior ou BRE', 'Tempo até tratamento >4h']
- **pontuacao**: Soma ponderada (escore de 0 a 14)
- **interpretacao**: 0-4 pontos: baixo risco; 5-8 pontos: risco intermediário; ≥9 pontos: alto risco
- **fonte**: PMC

## Aplicacao pratica
Utilizado para orientar decisões sobre estratégia invasiva precoce vs. conservadora em SCA, e mais recentemente para triagem de candidatos à alta precoce em pacientes de baixo risco

## Limitacoes
Desenvolvido antes da era de troponina de alta sensibilidade; GRACE 2.0 geralmente apresenta melhor discriminação prognóstica em coortes contemporâneas

## Fonte
PMC — Tabela comparativa de escores de risco em SCA
