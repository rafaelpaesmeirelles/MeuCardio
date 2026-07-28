---
title: "SCORE2 e SCORE2-OP"
slug: score2-e-score2-op
theme: "Calculadoras"
kind: calculadora
review_status: revisado
source_refs: ["SCORE2 working group and ESC Cardiovascular Risk Collaboration. SCORE2 risk prediction algorithms: new models to estimate 10-year risk of cardiovascular disease in Europe. Eur Heart J. 2021;42(25):2439-2454. DOI: 10.1093/eurheartj/ehab309. PMID: 34120177", "SCORE2-OP working group and ESC Cardiovascular Risk Collaboration. SCORE2-OP risk prediction algorithms: estimating incident cardiovascular event risk in older persons in four geographical risk regions. Eur Heart J. 2021;42(25):2455-2467. DOI: 10.1093/eurheartj/ehab312. PMID: 34120185"]
legacy_source: "calculadoras/calculadora-score2-score2-op.md"
---

# SCORE2 e SCORE2-OP

## Nome
SCORE2 e SCORE2-OP

## Aplicacao
Estimativa de risco de eventos cardiovasculares fatais e não fatais (infarto, AVC) em 10 anos, em adultos de 40-89 anos sem doença cardiovascular ou diabetes conhecidos; recomendado pela ESC para orientar decisões de prevenção primária

## Populacao alvo
- **score2**: Adultos de 40-69 anos
- **score2 op**: Idosos de 70-89 anos (Older Persons), com calibração específica
- **exclusao**: Pacientes com IAM, AVC, angioplastia ou diabetes prévios são automaticamente classificados como alto risco — a calculadora não se aplica a eles

## Variaveis
- Idade
- Sexo
- Tabagismo atual
- Pressão arterial sistólica
- Colesterol não-HDL (colesterol total menos HDL)

## Formula
Modelo de risco competitivo derivado de regressão, recalibrado por região de risco cardiovascular (baixo, moderado, alto, muito alto), combinando as variáveis acima em estimativa percentual de risco a 10 anos

## Interpretacao por faixa etaria
- **menor 50 anos**: Baixo risco: <2,5%; Alto risco: 2,5-7,5%; Muito alto risco: ≥7,5%
- **50 a 69 anos**: Baixo risco: <5%; Alto risco: 5-10%; Muito alto risco: ≥10%
- **70 anos ou mais**: Baixo risco: <7,5%; Alto risco: 7,5-15%; Muito alto risco: ≥15%
- **fonte**: ESC 2021

## Calibracao regional
Resultado ajustado conforme região de risco cardiovascular do país (ex.: risco moderado, alto ou muito alto), refletindo variação epidemiológica entre populações europeias

## Aplicacao pratica
Resultado percentual orienta discussão sobre intervenções de estilo de vida, indicação de estatina ou tratamento anti-hipertensivo

## Limitacoes
Não aplicável a pacientes com doença cardiovascular estabelecida, diabetes ou LDL/colesterol total extremamente elevado (indicação familiar de hipercolesterolemia requer avaliação separada)

## Fonte
SCORE2 working group. Eur Heart J. 2021;42(25):2439-2454 e SCORE2-OP working group. Eur Heart J. 2021;42(25):2455-2467
