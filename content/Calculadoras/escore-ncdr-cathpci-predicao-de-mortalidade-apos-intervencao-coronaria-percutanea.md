---
title: 'Escore de Risco NCDR CathPCI (ACC): Predição de Mortalidade Após Intervenção Coronária Percutânea'
slug: escore-ncdr-cathpci-predicao-de-mortalidade-apos-intervencao-coronaria-percutanea
theme: Calculadoras
kind: calculadora
review_status: revisado
source_refs:
- 'Brennan JM, Curtis JP, Dai D, Fitzgerald S, Khandelwal AK, Spertus JA, Rao SV, Singh M, Shaw RE, Ho KK, Krone
  RJ, Weintraub WS, Weaver WD, Peterson ED. Enhanced mortality risk prediction with a focus on high-risk percutaneous
  coronary intervention: results from 1,208,137 procedures in the NCDR (National Cardiovascular Data Registry).
  JACC Cardiovasc Interv. 2013;6(8):790-799. DOI: 10.1016/j.jcin.2013.03.020. PMID: 23968699 — registro nacional
  americano CathPCI (ACC/NCDR), 1.208.137 procedimentos de intervenção coronária percutânea em 1.252 hospitais,
  julho/2009 a junho/2011, com validação em amostra de split-sample'
legacy_source: Documento novo, escrito nesta sessão. A pasta já cobre escores de risco pós-angioplastia primária
  no IAM com supra de ST (CADILLAC), pós-choque cardiogênico já estabelecido (IABP-SHOCK II), risco cirúrgico (EuroSCORE
  II, STS Risk Score) e a decisão anatômica entre PCI e CABG (SYNTAX, SYNTAX II) — mas nenhum documento existente
  cobria o modelo de risco de mortalidade da própria ICP como procedimento, aplicável ao universo geral de pacientes
  submetidos a cateterismo intervencionista (eletivos e de urgência/emergência, com ou sem choque), que é o papel
  equivalente ao STS Risk Score do lado cirúrgico. Esse é o modelo do registro CathPCI do American College of Cardiology/NCDR
  que sustenta a calculadora de risco de ICP de uso corrente à beira do leito nos EUA.
summary: null
tags: []
evidence_level: null
source_tier: A
gaps: []
published: true
---

# Escore de Risco NCDR CathPCI (ACC): Predição de Mortalidade Após Intervenção Coronária Percutânea

## O que é e o problema que resolve
Assim como o STS Risk Score estima mortalidade cirúrgica antes de uma cirurgia cardíaca, o **modelo de risco do registro CathPCI** — mantido pelo National Cardiovascular Data Registry (NCDR) do American College of Cardiology (ACC) — estima **mortalidade intra-hospitalar após intervenção coronária percutânea (ICP)**, no universo geral de pacientes submetidos ao procedimento (eletivo, urgente, emergente ou de resgate, com ou sem choque cardiogênico). Brennan JM et al., *JACC Cardiovascular Interventions* 2013;6(8):790-799 (PMID 23968699), desenvolveram e validaram esse modelo a partir de **1.208.137 procedimentos de ICP realizados em 1.252 hospitais** participantes do registro CathPCI, entre **julho de 2009 e junho de 2011**.

O objetivo declarado foi permitir **consentimento informado individualizado antes do procedimento** e comparação de qualidade ajustada por risco entre hospitais — a mesma lógica de uso do STS Risk Score, aplicada à ICP em vez da cirurgia.

## Como foi derivado
- População: procedimentos de ICP registrados no CathPCI Registry no período do estudo, incluindo diferentes níveis de gravidade clínica (diferente do CADILLAC, restrito a angioplastia primária no IAM com supra de ST, ou do IABP-SHOCK II Risk Score, restrito a choque cardiogênico já estabelecido);
- Desfecho: **mortalidade intra-hospitalar**;
- Método: regressão, com avaliação de **discriminação e calibração em amostra de validação separada (split-sample)**;
- Três modelos foram desenvolvidos e comparados: um **modelo completo**, um **modelo pré-cateterismo** (variáveis disponíveis antes do procedimento) e um **escore simplificado para uso à beira do leito** (*simplified bedside risk score*).

## O que o resumo confirma sobre desempenho
Citado diretamente do resumo indexado:
- **Mortalidade intra-hospitalar geral**: **1,4%** na coorte completa;
- **Variação por apresentação clínica**: de **0,2% nos casos eletivos** a **65,9% nos pacientes com choque e parada cardíaca recente**;
- **C-estatística na amostra de validação**: **0,930** (modelo completo), **0,928** (modelo pré-cateterismo) e **0,925** (escore simplificado à beira do leito) — discriminação elevada e próxima entre os três modelos. Houve leve superestimação no extremo de maior risco;
- **Preditores mais fortes de mortalidade**: **choque cardiogênico** e **urgência do procedimento** (eletivo vs. urgente/emergente/de resgate);
- **Fatores angiográficos significativos**: **oclusão total crônica**, **trombose subaguda de stent** e **localização em tronco de coronária esquerda**.

## Escopo desta síntese
Este documento analisa o estudo de 2013 e não implementa uma calculadora. Não fornece pesos para cálculo manual nem deve ser usado para gerar risco individual. A versão histórica aqui estudada não deve ser confundida com atualizações posteriores do registro.

## O que este documento NÃO reproduz
Este documento confirma diretamente do resumo: a coorte de derivação (tamanho, número de hospitais, período), o desfecho, a estrutura de três modelos, as três c-estatísticas de validação, a mortalidade geral e por apresentação clínica extrema, e os preditores mais fortes citados nominalmente. **Não reproduz** a tabela de pontos por variável do escore simplificado, nem os intervalos de confiança das c-estatísticas, nem estatística de calibração (ex.: Hosmer-Lemeshow) — ausentes do resumo indexado.

## Leitura clínica e armadilhas
- **Não confundir com o CADILLAC risk score**: o CADILLAC é restrito a angioplastia primária no IAM com supra de ST; o modelo CathPCI/NCDR aqui descrito cobre **todo o espectro de ICP**, eletiva e de urgência/emergência, em qualquer indicação.
- **Não confundir com o escore IABP-SHOCK II**: aquele é derivado e validado **dentro** da população já em choque cardiogênico pós-IAM; o modelo CathPCI/NCDR inclui o choque cardiogênico como uma de suas variáveis preditoras mais fortes, mas dentro de uma coorte geral de ICP que vai do eletivo ao mais grave.
- **Papel equivalente, do lado percutâneo, ao STS Risk Score do lado cirúrgico**: nas discussões de heart team entre ICP e CABG (apoiadas também pelo SYNTAX Score II para a escolha anatômica), o modelo CathPCI/NCDR e o STS Risk Score são as ferramentas comparáveis de estimativa de risco de mortalidade específicas de cada estratégia, cada uma derivada e validada dentro do respectivo procedimento — não devem ser somadas ou comparadas número a número entre si sem essa ressalva.
- **É um modelo de mortalidade intra-hospitalar**, não de desfecho combinado, não de sangramento (para isso, ver CRUSADE e Mehran/ACUITY-HORIZONS nesta pasta) e não de longo prazo.

## Síntese

| Item | Valor |
|---|---|
| Coorte de derivação | 1.208.137 procedimentos de ICP, 1.252 hospitais, registro CathPCI (ACC/NCDR), jul/2009-jun/2011 |
| Desfecho | Mortalidade intra-hospitalar |
| Mortalidade geral | 1,4% (variação de 0,2% no eletivo a 65,9% no choque com PCR recente) |
| Modelos desenvolvidos | Completo, pré-cateterismo, simplificado à beira do leito |
| C-estatística (validação) | 0,930 / 0,928 / 0,925, respectivamente |
| Preditores mais fortes | Choque cardiogênico, urgência do procedimento |
| Fatores angiográficos significativos | Oclusão total crônica, trombose subaguda de stent, tronco de coronária esquerda |
| Cálculo individual | Não implementado neste documento |

## Tudo com Tudo

- [CADILLAC Risk Score: Predição de Mortalidade Após Angioplastia Primária no Infarto Agudo do Miocárdio](/biblioteca/cadillac-risk-score-predicao-de-mortalidade-apos-angioplastia-primaria-no-iam) — mesmo tipo de modelo, restrito à angioplastia primária no IAM com supra de ST
- [Escore IABP-SHOCK II: Estratificação de Risco de Mortalidade no Choque Cardiogênico Pós-IAM](/biblioteca/escore-iabp-shock-ii-estratificacao-de-risco-de-mortalidade-no-choque-cardiogenico-pos-iam) — choque cardiogênico é o preditor mais forte também no modelo CathPCI/NCDR
- [SYNTAX Score II: Variáveis Clínicas e Decisão Individualizada entre PCI e CABG](/biblioteca/syntax-score-ii-variaveis-clinicas-e-decisao-individualizada-entre-pci-e-cabg) — mesma decisão de heart team, eixo anatômico
- [STS Risk Score: Modelos de Risco da Society of Thoracic Surgeons](/biblioteca/sts-risk-score-modelos-de-risco-da-society-of-thoracic-surgeons) — ferramenta equivalente do lado cirúrgico da mesma decisão de heart team
- [Classificação de Killip: Classe Funcional na Fase Aguda do Infarto](/biblioteca/classificacao-de-killip-classe-funcional-na-fase-aguda-do-infarto) — outra estratificação de gravidade clínica na fase aguda do infarto
- [Escore de Mehran (ACUITY/HORIZONS-AMI): Risco de Sangramento Maior na Síndrome Coronariana Aguda](/biblioteca/escore-de-mehran-acuity-horizons-risco-de-sangramento-na-sindrome-coronariana-aguda) — eixo complementar de sangramento na mesma decisão periprocedimento de ICP
- [Classificação SCAI de Estágios do Choque Cardiogênico](/biblioteca/classificacao-scai-de-estagios-do-choque-cardiogenico) — estratifica a gravidade do choque cardiogênico, variável preditora central deste modelo
