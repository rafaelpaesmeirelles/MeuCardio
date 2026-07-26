---
title: "CRUSADE Bleeding Score"
slug: crusade-bleeding-score
theme: "Calculadoras"
kind: calculadora
review_status: pendente_revisao
source_refs: []
legacy_source: "calculadoras/calculadora-crusade-risco-de-sangramento.md"
---

# CRUSADE Bleeding Score

## Nome
CRUSADE Bleeding Score

## Aplicacao
Estimativa de risco de sangramento maior intra-hospitalar em pacientes com SCA sem supra de ST (NSTEMI/angina instável) em uso de terapia antitrombótica

## Variaveis
- **nome**: Hematócrito basal (%); **faixas**: [{'faixa': '<31', 'pontos': 9}, {'faixa': '31-33,9', 'pontos': 7}, {'faixa': '34-36,9', 'pontos': 3}, {'faixa': '37-39,9', 'pontos': 2}, {'faixa': '≥40', 'pontos': 0}]
- **nome**: Clearance de creatinina (mL/min); **faixas**: [{'faixa': '≤15', 'pontos': 39}, {'faixa': '15,1-30', 'pontos': 35}, {'faixa': '30,1-60', 'pontos': 28}, {'faixa': '60,1-90', 'pontos': 17}, {'faixa': '90,1-120', 'pontos': 7}, {'faixa': '>120', 'pontos': 0}]
- **nome**: Frequência cardíaca (bpm); **faixas**: [{'faixa': '≤70', 'pontos': 0}, {'faixa': '71-80', 'pontos': 1}, {'faixa': '81-90', 'pontos': 3}, {'faixa': '91-100', 'pontos': 6}, {'faixa': '101-110', 'pontos': 8}, {'faixa': '111-120', 'pontos': 10}, {'faixa': '≥121', 'pontos': 11}]
- **nome**: Sexo feminino; **pontos**: 8
- **nome**: Sinais de insuficiência cardíaca na admissão; **pontos**: 7
- **nome**: Doença vascular prévia (DAP ou AVC); **pontos**: 6
- **nome**: Diabetes mellitus; **pontos**: 6
- **nome**: Pressão arterial sistólica (mmHg); **faixas**: [{'faixa': '≤90', 'pontos': 10}, {'faixa': '91-100', 'pontos': 8}, {'faixa': '101-120', 'pontos': 5}, {'faixa': '121-180', 'pontos': 1}, {'faixa': '181-200', 'pontos': 3}, {'faixa': '≥201', 'pontos': 5}]

## Formula
Soma direta dos pontos de todas as 8 variáveis (escore de 1 a 100 pontos)

## Interpretacao por quintil
- **categoria**: Risco muito baixo; **escore**: ≤20; **sangramento maior**: 3,1%
- **categoria**: Risco baixo; **escore**: 21-30; **sangramento maior**: ~5,5%
- **categoria**: Risco moderado; **escore**: 31-40; **sangramento maior**: ~8-9%
- **categoria**: Risco alto; **escore**: 41-50; **sangramento maior**: ~12%
- **categoria**: Risco muito alto; **escore**: ≥50; **sangramento maior**: 19,5%

## Validacao
C-statistic de 0,80-0,82 em coortes contemporâneas espanholas, com boa calibração (Hosmer-Lemeshow p>0,3); menor capacidade discriminativa em subgrupo específico tratado com ≥2 antitrombóticos sem cateterismo (C=0,56)

## Aplicacao pratica
Usado em conjunto com escores isquêmicos (GRACE, TIMI) para balancear risco trombótico vs. hemorrágico na escolha de estratégia antitrombótica e via de acesso (radial preferencial em alto risco de sangramento)

## Limitacoes
Desenvolvido especificamente para NSTEMI; validação em STEMI é mais limitada, embora estudos de validação existam para essa extensão

## Fonte
AHA Journals ; MDCalc ; Duke CICU
