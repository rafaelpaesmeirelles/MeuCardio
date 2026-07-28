---
title: "TIMI Risk Score"
slug: timi-risk-score
theme: "Calculadoras"
kind: calculadora
review_status: pendente_revisao
source_refs: ["Antman EM, Cohen M, Bernink PJLM, McCabe CH, Horacek T, Papuchis G, Mautner B, Corbalan R, Radley D, Braunwald E. The TIMI risk score for unstable angina/non-ST elevation MI: a method for prognostication and therapeutic decision making. JAMA. 2000;284(7):835-842. DOI: 10.1001/jama.284.7.835. PMID: 10938172", "Morrow DA, Antman EM, Charlesworth A, et al. TIMI risk score for ST-elevation myocardial infarction: a convenient, bedside, clinical score for risk assessment at presentation. Circulation. 2000;102(17):2031-2037. DOI: 10.1161/01.cir.102.17.2031. PMID: 11044416"]
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
- **interpretacao**: o artigo original não define faixas de baixo/intermediário/alto — reporta gradiente contínuo de eventos (morte, IAM ou revascularização urgente em 14 dias) na coorte de derivação do TIMI 11B: 4,7% para escore 0/1; 8,3% para 2; 13,2% para 3; 19,9% para 4; 26,2% para 5; 40,9% para 6/7 (p<0,001 para tendência). A categorização em três faixas é convenção de uso, não do artigo — e a que circulava aqui classificava escore 5 como intermediário, apesar de 26,2% de eventos em 14 dias

## Versao stemi
- **variaveis**: ['Idade 65-74/>75 anos (2/3 pontos)', 'Diabetes, hipertensão ou angina prévia', 'PAS <100 mmHg', 'FC >100 bpm', 'Classe Killip ≥2', 'Peso <67 kg', 'IAM anterior ou BRE', 'Tempo até tratamento >4h']
- **pontuacao**: Soma ponderada (escore de 0 a 14)
- **interpretacao**: mortalidade em 30 dias cresce de forma contínua com o escore. As faixas de baixo/intermediário/alto que circulavam aqui não vieram do artigo de derivação — VERIFICAÇÃO HUMANA NECESSÁRIA para conferir a tabela de mortalidade por escore em Morrow DA et al., Circulation 2000;102:2031-2037

## Aplicacao pratica
Utilizado para orientar decisões sobre estratégia invasiva precoce vs. conservadora em SCA, e mais recentemente para triagem de candidatos à alta precoce em pacientes de baixo risco

## Limitacoes
Desenvolvido antes da era de troponina de alta sensibilidade; GRACE 2.0 geralmente apresenta melhor discriminação prognóstica em coortes contemporâneas

## Fonte
Antman EM et al. JAMA. 2000;284(7):835-842 (AI/NSTEMI) e Morrow DA et al. Circulation. 2000;102(17):2031-2037 (STEMI) — artigos de derivação dos dois escores
