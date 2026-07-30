---
title: "PESI e sPESI — Escore de Gravidade do Tromboembolismo Pulmonar"
slug: pesi-e-spesi-escore-de-gravidade-do-tromboembolismo-pulmonar
theme: "Calculadoras"
kind: calculadora
review_status: revisado
source_refs: ["Aujesky D, Obrosky DS, Stone RA, et al. Derivation and validation of a prognostic model for pulmonary embolism (PESI). Am J Respir Crit Care Med. 2005;172(8):1041-1046. DOI: 10.1164/rccm.200506-862OC. PMID: 16020800", "Jiménez D, Aujesky D, Moores L, et al; RIETE Investigators. Simplification of the pulmonary embolism severity index for prognostication in patients with acute symptomatic pulmonary embolism (sPESI). Arch Intern Med. 2010;170(15):1383-1389. DOI: 10.1001/archinternmed.2010.199. PMID: 20696966", "Bonsu KO, et al. Optimizing sPESI with heart rate threshold adjustments for risk stratification in acute pulmonary embolism: a retrospective cohort study. Vasc Med. 2026. PMCID: PMC13254130 (texto completo em acesso aberto) — reproduz e cita a construção original do sPESI (Jiménez D et al. 2010): 1 ponto por variável, seis variáveis, corte de 110 bpm herdado do PESI"]
legacy_source: "Documento novo — o PESI/sPESI já era citado por nome em content/Tromboembolismo/tromboembolismo-pulmonar-agudo-diagnostico-e-manejo-escers-2019.md, mas sem as variáveis nem os pontos do escore."
---

# PESI e sPESI — Escore de Gravidade do Tromboembolismo Pulmonar

## Definicao
O Pulmonary Embolism Severity Index (PESI) é a regra de predição clínica usada para estimar mortalidade em 30 dias em paciente com TEP agudo e decidir intensidade inicial de tratamento — inclusive elegibilidade para alta precoce/tratamento ambulatorial. É citado por nome nos documentos de TEP desta biblioteca, mas sem as variáveis nem os pontos. Este documento fecha essa lacuna.

## Derivacao do pesi original
Derivado e validado a partir de 15.531 internações por TEP em 186 hospitais da Pensilvânia (67% derivação, 33% validação interna), com validação externa em 221 pacientes da Suíça e França. Regra baseada em **11 características clínicas** obtidas na apresentação, sem necessidade de exame laboratorial.

## Variaveis e pontuacao do pesi
- **idade**: pontuação igual à idade em anos (ex.: 70 anos = 70 pontos)
- **sexo masculino**: +10
- **câncer**: +30
- **insuficiência cardíaca**: +10
- **doença pulmonar crônica**: +10
- **pulso ≥110/min**: +20
- **pressão arterial sistólica <100 mmHg**: +30
- **frequência respiratória ≥30/min**: +20
- **temperatura <36°C**: +20
- **estado mental alterado** (desorientação, letargia, estupor ou coma): +60
- **saturação arterial de oxigênio <90%** (com ou sem oxigênio suplementar): +20

## Classes de risco e mortalidade em 30 dias
A soma da idade em anos com os pontos de cada característica presente classifica o paciente em 5 classes, com mortalidade em 30 dias medida nas amostras de derivação e validação:
- **classe I (≤65 pontos), risco muito baixo**: mortalidade 0-1,6%
- **classe II (66-85 pontos), risco baixo**: mortalidade 1,7-3,5%
- **classe III (86-105 pontos), risco intermediário**: mortalidade 3,2-7,1%
- **classe IV (106-125 pontos), risco alto**: mortalidade 4,0-11,4%
- **classe V (>125 pontos), risco muito alto**: mortalidade 10,0-24,5%

Óbito hospitalar e complicações não fatais ficaram em ≤1,1% na classe I e ≤1,9% na classe II — é essa margem de segurança que sustenta considerar classes I e II para tratamento ambulatorial.

## Spesi versao simplificada
Versão simplificada derivada retrospectivamente numa coorte espanhola de pacientes ambulatoriais e validada externamente na coorte multinacional RIETE. A regressão logística univariada eliminou as variáveis do PESI original que não mantiveram significância estatística, restando **6 variáveis: idade, câncer, doença cardiopulmonar crônica, frequência cardíaca, pressão arterial sistólica e saturação de oxi-hemoglobina**. A acurácia prognóstica do sPESI não diferiu do PESI original (área sob a curva 0,75; IC95% 0,69-0,80).

**Desempenho**: na coorte de derivação, 30,7% dos pacientes classificados como baixo risco pelo sPESI tiveram mortalidade em 30 dias de 1,0% (IC95% 0,0-2,1%), contra 10,9% (IC95% 8,5-13,2%) no grupo de alto risco. Na validação externa (coorte RIETE), 36,2% classificados como baixo risco tiveram mortalidade de 1,1% (IC95% 0,7-1,5%), contra 8,9% (IC95% 8,1-9,8%) no alto risco.

**Resolvido em 30/07/2026** — os cortes exatos e a estrutura de pontuação, que o resumo indexado do artigo original não detalhava, foram confirmados por um estudo de coorte de 2026 que aplica e cita explicitamente a construção do sPESI (Bonsu et al., Vasc Med, PMCID PMC13254130, texto completo em acesso aberto): **1 ponto para cada uma das seis variáveis presentes**, sem ponderação diferenciada entre elas —

- **idade >80 anos**: 1 ponto
- **câncer** (história): 1 ponto
- **doença cardiopulmonar crônica** (insuficiência cardíaca — definida por hospitalização prévia por IC, sintomas NYHA ≥2, ou FEVE <40% — ou doença pulmonar crônica: asma, DPOC ou doença pulmonar restritiva): 1 ponto
- **frequência cardíaca ≥110 bpm**: 1 ponto — o mesmo corte do PESI original, de onde foi herdado
- **pressão arterial sistólica <100 mmHg**: 1 ponto
- **saturação arterial de oxigênio <90%**: 1 ponto

**Interpretação**: escore **0 = baixo risco**; escore **≥1 = alto risco**. Nenhum óbito em 30 ou 90 dias ocorreu entre pacientes com sPESI=0 na coorte de 696 pacientes ambulatoriais desse estudo — consistente com a margem de segurança já documentada nas coortes de derivação e validação original do sPESI.

## Aplicacao pratica
- **classe I-II do PESI, ou sPESI de baixo risco**: candidatos a considerar tratamento ambulatorial ou alta precoce, desde que sem outros fatores de risco (ver documento de estratégia diagnóstica e manejo do TEP nesta biblioteca — imagem de VD e biomarcadores continuam recomendados mesmo com PESI baixo)
- **classes III-V do PESI, ou sPESI de alto risco**: internação, com estratificação adicional por disfunção de ventrículo direito e biomarcadores para definir risco intermediário-baixo vs. intermediário-alto vs. alto risco hemodinâmico

## Armadilhas clinicas
- Usar o PESI/sPESI para decidir trombólise — os dois escores estratificam mortalidade geral e ajudam a decidir alta/internação; a decisão de reperfusão em TEP de alto risco hemodinâmico é clínica (instabilidade), não pelo escore
- Dispensar imagem de ventrículo direito e biomarcadores só porque o PESI é baixo — a diretriz de TEP mantém essa recomendação mesmo com PESI/sPESI favorável
- Confundir PESI (pontuação ponderada, 11 variáveis, 5 classes, soma inclui a idade em anos) com sPESI (1 ponto por variável, 6 variáveis, só 2 categorias) — os pontos de corte e a forma de pontuar são diferentes entre os dois
- Usar frequência cardíaca abaixo de 110 bpm como corte do sPESI — o valor correto, herdado do PESI original, é ≥110 bpm
