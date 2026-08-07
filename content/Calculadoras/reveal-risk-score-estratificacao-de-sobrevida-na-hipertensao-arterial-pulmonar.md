---
title: "REVEAL Risk Score: Estratificação de Sobrevida na Hipertensão Arterial Pulmonar"
slug: reveal-risk-score-estratificacao-de-sobrevida-na-hipertensao-arterial-pulmonar
theme: "Calculadoras"
kind: calculadora
review_status: revisado
source_refs: ["Benza RL, Miller DP, Gomberg-Maitland M, Frantz RP, Foreman AJ, Coffey CS, Frost A, Barst RJ, Badesch DB, Elliott CG, Liou TG, McGoon MD. Predicting survival in pulmonary arterial hypertension: insights from the Registry to Evaluate Early and Long-Term Pulmonary Arterial Hypertension Disease Management (REVEAL). Circulation. 2010;122(2):164-172. DOI: 10.1161/CIRCULATIONAHA.109.898122. PMID: 20585012 — artigo original, derivação em 2.716 pacientes do registro americano REVEAL", "Benza RL, Gomberg-Maitland M, Elliott CG, Farber HW, Foreman AJ, Frost AE, McGoon MD, Pasta DJ, Selej M, Burger CD, Frantz RP. Predicting Survival in Patients With Pulmonary Arterial Hypertension: The REVEAL Risk Score Calculator 2.0 and Comparison With ESC/ERS-Based Risk Assessment Strategies. Chest. 2019;156(2):323-337. DOI: 10.1016/j.chest.2019.02.004. PMID: 30772387 — atualização REVEAL 2.0, comparação de discriminação contra as estratégias de risco COMPERA e FPHR baseadas nas diretrizes ESC/ERS"]
legacy_source: "Documento novo, escrito nesta sessão. A pasta Calculadoras já tinha os escores de gravidade do TEP (PESI/sPESI, Genebra, Wells) e nenhum escore prognóstico dedicado à hipertensão arterial pulmonar (HAP), apesar de o tema Hipertensão pulmonar já ter documentos clínicos que citam estratificação de risco (baixo/intermediário/alto) sem detalhar o instrumento que a origina. Segue o mesmo padrão já usado no documento de GRACE 2.0 desta pasta: quando a tabela de pontos exata não está disponível no resumo indexado nem em fonte primária aberta, o documento traz os preditores, a direção do efeito e o desempenho estatístico verificados, e remete ao cálculo pela ferramenta oficial em vez de reconstruir a equação por fonte secundária não conferida."
---

# REVEAL Risk Score: Estratificação de Sobrevida na Hipertensão Arterial Pulmonar

## O que é
O REVEAL Risk Score nasceu do registro americano **REVEAL** (Registry to Evaluate Early and Long-Term PAH Disease Management), criado para dar à hipertensão arterial pulmonar (HAP) uma **ferramenta quantitativa de predição de sobrevida** — Benza RL et al., *Circulation* 2010;122(2):164-172 (PMID 20585012), descrevem explicitamente que, até aquele momento, **não havia instrumento de predição de sobrevida estabelecido para uso em pesquisa ou na prática clínica** na HAP.

## Derivação original (2010)
Analisando **2.716 pacientes com HAP** consecutivamente inscritos no registro REVEAL, os autores identificaram os preditores independentes de mortalidade em 1 ano (sobrevida global em 1 ano na coorte: **91,0%**, IC95% 89,9-92,1) por regressão de Cox multivariada:

| Variável associada a MAIOR mortalidade | Razão de risco (IC95%) |
|---|---|
| Resistência vascular pulmonar > 32 unidades Wood | 4,1 (2,0-8,3) |
| HAP associada a hipertensão portal | 3,6 (2,4-5,4) |
| Classe funcional IV (NYHA/OMS modificada) | 3,1 (2,2-4,4) |
| Homens com mais de 60 anos | 2,2 (1,6-3,0) |
| História familiar de HAP | 2,2 (1,2-4,0) |

Também entraram no modelo, com contribuição prognóstica confirmada mas sem razão de risco isolada citada no resumo: insuficiência renal, HAP associada a doença do tecido conjuntivo, classe funcional III, pressão de átrio direito, pressão arterial sistólica e frequência cardíaca de repouso, distância no teste de caminhada de 6 minutos, peptídeo natriurético tipo B, capacidade de difusão de monóxido de carbono percentual predita, e derrame pericárdico ao ecocardiograma.

A partir dessas variáveis os autores derivaram uma **equação prognóstica ponderada**, validada por técnica de bootstrapping.

## Atualização REVEAL 2.0 (2019)
Benza RL et al., *Chest* 2019;156(2):323-337 (PMID 30772387), reavaliaram pontos de corte e pesos das variáveis e testaram variáveis novas, numa subpopulação do registro que sobreviveu ao menos 1 ano após a inclusão (usada como linha de base desta análise). Principais achados, citados diretamente do resumo:

- O **REVEAL 2.0 manteve discriminação semelhante** à do escore original nessa subpopulação (estatística c = 0,76 vs. 0,74) e **separou bem os pacientes em três categorias de risco** (baixo/intermediário/alto), prevendo tanto piora clínica quanto mortalidade no seguimento de ao menos 1 ano;
- Comparado às estratégias de risco derivadas das diretrizes ESC/ERS — os registros **COMPERA** e **FPHR (French Pulmonary Hypertension Registry)** — o REVEAL 2.0 de três categorias teve **discriminação maior** (estatística c = 0,73) que a COMPERA (c = 0,62) ou a FPHR (c = 0,64);
- **Tanto a COMPERA quanto a FPHR subestimaram e superestimaram risco** em comparação ao REVEAL 2.0 — ou seja, a diferença não foi só de magnitude da discriminação, foi também de calibração.

## O que este documento NÃO reproduz, e por quê
**A tabela de pontos variável a variável do REVEAL 2.0** (os cortes exatos e o peso numérico de cada item, como os que os documentos de GRACE e TIMI desta pasta trazem para seus respectivos escores) **não está disponível no resumo indexado de nenhum dos dois artigos**, e o texto completo não foi acessado nesta sessão. Reconstruir esses pesos a partir de calculadora de terceiros não conferida contra o artigo original repetiria o erro que este projeto já identificou e corrigiu antes (ver o documento de GRACE 2.0 nesta mesma pasta, onde a equação foi removida por não ter sido possível confirmá-la contra a fonte). **Para o cálculo do escore em um paciente real, use a calculadora eletrônica oficial do REVEAL** — o padrão já adotado neste projeto para o GRACE 2.0, pela mesma razão.

## O que este documento sustenta com segurança
- A HAP tem, desde 2010, uma ferramenta quantitativa validada de predição de sobrevida baseada em variáveis clínicas, hemodinâmicas, funcionais e laboratoriais de rotina — não depende de teste especializado além do que já compõe a avaliação padrão do paciente com HAP;
- A versão atualizada (REVEAL 2.0) discrimina risco **melhor** que as estratégias derivadas das diretrizes europeias de HAP (COMPERA, FPHR) na comparação direta feita pelos próprios autores do REVEAL — achado relevante para quem decide qual ferramenta usar na reavaliação periódica de risco recomendada pelas diretrizes de tratamento.
