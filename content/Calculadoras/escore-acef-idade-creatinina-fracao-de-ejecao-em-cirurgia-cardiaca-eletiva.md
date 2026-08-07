---
title: "Escore ACEF: Idade, Creatinina e Fração de Ejeção em Cirurgia Cardíaca Eletiva"
slug: escore-acef-idade-creatinina-fracao-de-ejecao-em-cirurgia-cardiaca-eletiva
theme: "Calculadoras"
kind: calculadora
review_status: revisado
source_refs: ["Ranucci M, Castelvecchio S, Menicanti L, Frigiola A, Pelissero G. Risk of assessing mortality risk in elective cardiac operations: age, creatinine, ejection fraction, and the law of parsimony. Circulation. 2009;119(24):3053-3061. DOI: 10.1161/CIRCULATIONAHA.108.842393. PMID: 19506110 — série de desenvolvimento (n=4.557) e série de validação (n=4.091), um único centro (IRCCS Policlinico S. Donato, Milão)"]
legacy_source: "Documento novo, escrito nesta sessão. A pasta já cobre EuroSCORE II e STS Risk Score para risco cirúrgico cardíaco, ambos modelos com dezenas de variáveis. Faltava o contraponto deliberadamente minimalista: um escore de 3 variáveis, desenhado para superar o overfitting dos modelos complexos em cirurgia eletiva de baixa mortalidade."
---

# Escore ACEF: Idade, Creatinina e Fração de Ejeção em Cirurgia Cardíaca Eletiva

## A lógica: "a lei da parcimônia"
Modelos de risco cirúrgico cardíaco costumam somar dezenas de variáveis (o EuroSCORE II e o STS Risk Score, já documentados nesta pasta, são exemplos). Ranucci M et al. (Circulation. 2009;119(24):3053-3061, PMID 19506110) partiram de uma observação estatística simples: em **cirurgia eletiva**, a mortalidade operatória é baixa, o número de eventos registrados por ano é limitado, e um modelo com muitas variáveis corre risco real de **sobreajuste** (overfitting) aos dados de derivação. Os autores testaram se um modelo **radicalmente mais simples**, com apenas 3 fatores, teria acurácia comparável.

## A fórmula
O escore ACEF (**A**ge, **C**reatinine, **E**jection **F**raction) é calculado como:

**ACEF = idade (anos) ÷ fração de ejeção (%) + 1 (se creatinina sérica > 2 mg/dL)**

Sem tabela de pontos, sem coeficientes múltiplos — uma razão simples entre idade e fração de ejeção, com um acréscimo binário para disfunção renal significativa.

## Desenvolvimento e validação
- **Série de desenvolvimento:** 4.557 pacientes adultos submetidos a cirurgia cardíaca eletiva no mesmo centro, 2001-2003.
- **Série de validação:** 4.091 pacientes subsequentes, mesmo centro.
- O ACEF foi comparado a **5 outros escores de risco** na série de validação, com acurácia discriminativa (estatística C, análise de curva ROC).

## Desempenho
- O **escore da Cleveland Clinic** teve a melhor acurácia geral (0,812), com o **ACEF logo abaixo (0,808)** — praticamente equivalente, apesar de usar 1/10 das variáveis dos modelos mais complexos.
- Em **cirurgia coronariana**, os dois escores tiveram desempenho equivalente (0,815 vs. 0,813).
- Em **cirurgia coronariana isolada**, o **ACEF teve a MELHOR acurácia entre todos os modelos testados (0,826)**, superando inclusive o escore da Cleveland Clinic (0,806).

**Conclusão dos autores, no texto:** um modelo de risco limitado a 3 preditores independentes tem acurácia e calibração **similares ou superiores** a escores mais complexos quando aplicado a operações cardíacas eletivas.

## Uso prático
O ACEF é útil como estimativa rápida à beira do leito ou em discussão de Heart Team, especialmente quando os dados completos exigidos por EuroSCORE II ou STS (que pedem dezenas de variáveis) ainda não estão disponíveis ou quando se quer uma segunda estimativa independente e simples para cruzar com o modelo mais complexo. Não substitui os escores validados em populações mais amplas e heterogêneas (incluindo cirurgia de urgência/emergência, fora do escopo do desenho original do ACEF).

## Limitações, declaradas com honestidade
Desenvolvido e validado em **um único centro italiano**, com desempenho não replicado nesta consulta em coortes externas multicêntricas. O desenho original cobre **exclusivamente cirurgia eletiva** — a fórmula não foi validada para cirurgia de urgência/emergência, nas quais outros fatores (choque cardiogênico, tempo até a intervenção) pesam mais e não entram no cálculo. A variável "creatinina > 2 mg/dL" é um corte binário grosseiro comparado a escalas contínuas de função renal (como a taxa de filtração glomerular estimada) usadas em escores mais recentes.
