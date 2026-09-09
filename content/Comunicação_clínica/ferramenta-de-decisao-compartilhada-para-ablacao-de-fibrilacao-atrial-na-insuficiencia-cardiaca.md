---
kind: estudo
published: true
review_note: 'Resumo Peng conferido; mantidos n, taxas, HR e interação. Corrigida extrapolação causal/individual dos clusters;
  conteúdo restrito a resumo crítico sem implementação ou classificação clínica não verificada. Conferência editorial final:
  título alinhado ao corpo revisado, campos de classificação e resumo conferidos, referências bibliográficas organizadas e
  espaçamento corrigido quando necessário. Vínculos internos preservados.'
review_status: revisado
slug: ferramenta-de-decisao-compartilhada-para-ablacao-de-fibrilacao-atrial-na-insuficiencia-cardiaca
source_refs:
- 'Peng X, He L, Wang J, Li N, Cui J, Xia S, Zuo S, Jiang C, Hu J, Hong K, Li Z, Zhang P, Zhou N, Sang C, Long D, Du X, Dong
  J, Ma C. Development and validation of risk stratification and shared decision-making tool for catheter ablation for atrial
  fibrillation in patients with heart failure: a multicentre cohort study. EClinicalMedicine. 2025;83:103219. DOI: 10.1016/j.eclinm.2025.103219.
  PMID: 40641819. PMCID: PMC12242850. Coorte de derivação China-AF (registro chinês, 31 hospitais, 2011-2022) com validação
  externa no ensaio CABANA.'
theme: Comunicação clínica
title: Ferramenta de Estratificação de Risco e Decisão Compartilhada para Ablação de FA na Insuficiência Cardíaca
summary: 'Peng X et al. (EClinicalMedicine, 2025) construíram uma ferramenta para essa pergunta específica:

  uma proposta de estratificação prognóstica e exploração de heterogeneidade de tratamento, que não determina individualmente
  benefício causal nem elegibilidade.'
tags: []
source_tier: A
gaps: []
---

# Ferramenta de Estratificação de Risco e Decisão Compartilhada para Ablação de FA na Insuficiência Cardíaca

## O problema que este documento resolve
Fibrilação atrial (FA) e insuficiência cardíaca (IC) coexistem com frequência e se retroalimentam:
a FA piora a função ventricular pela perda da contração atrial e pela frequência irregular, e a IC
favorece o substrato para a FA. O CASTLE-AF já mostrou que a ablação por cateter reduz mortalidade
e internação por IC nesse grupo em relação ao tratamento farmacológico isolado — mas **CASTLE-AF
selecionou uma população específica** (FE reduzida, portadores de dispositivo), e a decisão do dia a
dia é outra: diante de um paciente real, com FA e IC de fenótipo variado, **quem realmente se
beneficia da ablação a ponto de justificar o risco e o desconforto do procedimento, e quem não**?

Peng X et al. (EClinicalMedicine, 2025) construíram uma ferramenta para essa pergunta específica:
uma proposta de estratificação prognóstica e exploração de heterogeneidade de tratamento, que não determina individualmente benefício causal nem elegibilidade.

## Desenho do estudo
Estudo de coorte multicêntrico, em duas etapas:
- **Coorte de derivação**: registro China-AF, **31 hospitais chineses**, pacientes recrutados entre
  **1º de agosto de 2011 e 31 de dezembro de 2022** — **3.122 pacientes** com FA e IC (excluídos os
  assintomáticos), sendo **1.476 mulheres (47,3%)** e **1.646 homens (52,7%)**.
- **Coorte de validação externa**: subconjunto do ensaio **CABANA** (internacional, multicêntrico,
  randomizado, aberto) — **778 pacientes**, **345 mulheres (44,3%)** e **433 homens (55,7%)**,
  populações etnicamente diversas, diferente da coorte de derivação (majoritariamente chinesa).

A ferramenta foi construída aplicando **clustering não supervisionado seguido de modelos de
aprendizado supervisionado** sobre **25 características clínicas de fácil obtenção** (descritas pelos autores como acessíveis; não se presume ausência de necessidade de exames) — decisão de desenho que teve o propósito
explícito de tornar a ferramenta aplicável na prática, não só em ambiente de pesquisa.

## Os três grupos de risco identificados
O modelo agrupou os pacientes em **três clusters** distintos, com incidência de eventos compostos
(morte cardiovascular e AVC) claramente separada entre eles, medida em eventos por 100
pessoas-ano:

| Cluster | Incidência do desfecho composto (por 100 pessoas-ano) | IC 95% |
|---|---|---|
| Cluster 1 (maior risco) | **7,7** | 6,9–8,6 |
| Cluster 2 (risco intermediário) | **6,8** | 6,1–7,7 |
| Cluster 3 (menor risco) | **3,8** | 3,4–4,4 |

Diferença entre os três grupos: **log-rank p < 0,0001**. O mesmo padrão de separação se repetiu
para mortalidade por todas as causas e mortalidade cardiovascular isoladamente, e **se manteve
consistente no subgrupo de IC com fração de ejeção preservada (ICFEp)** — ponto relevante, porque
grande parte da evidência de ablação em IC (incluindo o próprio CASTLE-AF) foi gerada em FE
reduzida, e aqui a estratificação por risco se sustentou também na ICFEp.

## O achado que orienta a decisão compartilhada
O ponto central do estudo, para a conversa com o paciente, não é a estratificação em si — é **como
o benefício da ablação varia conforme o cluster**:

- **No Cluster 1 (maior risco)**, comparada à terapia farmacológica isolada, a ablação por cateter
  associou-se a **redução expressiva do desfecho composto**: **HR ajustado 0,16** (IC 95% 0,07–0,36),
  com **p de interação = 0,0039** — ou seja, o efeito da ablação **difere significativamente** entre
  os clusters, não é um efeito uniforme aplicado a toda a população.
- **A mesma direção de efeito se confirmou na coorte de validação externa (CABANA)**: **HR ajustado
  0,19** (IC 95% 0,05–0,73, p=0,015) no cluster equivalente de maior risco.

A associação mais forte no cluster 1 não significa que qualquer paciente de maior risco deva receber ablação ou que pacientes dos demais clusters não se beneficiem. Os agrupamentos resultam de múltiplas características e não podem ser substituídos por uma impressão clínica de gravidade. Confusão por indicação e seleção podem influenciar a magnitude do efeito observacional.

## Limite metodológico que precisa entrar na conversa com o paciente
Os próprios autores são explícitos sobre isto na conclusão do estudo, e o documento reproduz o
limite sem suavizar: **a ferramenta foi derivada de dados observacionais**, não de um ensaio
randomizado que testasse a ablação estratificada por cluster. A associação entre cluster de maior
risco e maior benefício da ablação é, portanto, **hipótese gerada por dados**, ainda que reforçada
pela validação externa independente no CABANA — e os próprios autores dizem que **a eficácia da
ferramenta ainda precisa de confirmação em ensaios de intervenção e na prática clínica real**.

## Uso deste documento
Este é um resumo crítico do estudo, sem implementação do modelo, classificação de pacientes ou calculadora. Os pesos, variáveis completas e regras de atribuição não foram verificados no material suplementar e não são reconstruídos aqui. A validação externa de uma associação não equivale a demonstrar que usar a ferramenta melhora decisões ou desfechos.

Na decisão compartilhada, apresentar evidências estabelecidas, riscos e alternativas para o fenótipo do paciente. Não informar um cluster ou benefício individual estimado com base apenas nas taxas resumidas neste documento.

## Fonte
Peng X et al. *Development and validation of risk stratification and shared decision-making tool
for catheter ablation for atrial fibrillation in patients with heart failure: a multicentre cohort
study.* EClinicalMedicine. 2025;83:103219. PMID 40641819, PMCID PMC12242850, DOI
10.1016/j.eclinm.2025.103219 — dados conferidos por leitura direta do resumo estruturado via
PubMed E-utilities nesta sessão (08/09/2026).

## Conteúdo clínico relacionado

- [Três ensaios de ablação de FA na IC: CASTLE-AF, RAFT-AF e CASTLE-HTx](/biblioteca/tres-ensaios-de-ablacao-de-fa-na-ic-castle-raft-htx)
- [ESC 2024: diretriz de fibrilação atrial e o modelo AF-CARE](/biblioteca/esc-2024-diretriz-fibrilacao-atrial-af-care)
