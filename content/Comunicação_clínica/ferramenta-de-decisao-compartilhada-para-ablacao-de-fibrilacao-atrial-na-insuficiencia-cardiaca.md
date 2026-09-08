---
title: "Ferramenta de Estratificação de Risco e Decisão Compartilhada para Ablação de FA na Insuficiência Cardíaca"
slug: ferramenta-de-decisao-compartilhada-para-ablacao-de-fibrilacao-atrial-na-insuficiencia-cardiaca
theme: "Comunicação clínica"
kind: estudo
review_status: revisado
source_refs: ["Peng X, He L, Wang J, Li N, Cui J, Xia S, Zuo S, Jiang C, Hu J, Hong K, Li Z, Zhang P, Zhou N, Sang C, Long D, Du X, Dong J, Ma C. Development and validation of risk stratification and shared decision-making tool for catheter ablation for atrial fibrillation in patients with heart failure: a multicentre cohort study. EClinicalMedicine. 2025;83:103219. DOI: 10.1016/j.eclinm.2025.103219. PMID: 40641819. PMCID: PMC12242850. Coorte de derivação China-AF (registro chinês, 31 hospitais, 2011-2022) com validação externa no ensaio CABANA."]
legacy_source: "Documento novo, escrito em 08/09/2026. A pasta já cobre decisão compartilhada para controle de ritmo na FA em geral (auxílio digital de implementação 2026) e para fechamento de apêndice atrial esquerdo, mas nenhum documento tratava especificamente da decisão sobre ABLAÇÃO em paciente que tem FA E insuficiência cardíaca ao mesmo tempo — cenário em que o risco de base já é mais alto e a decisão de submeter o paciente a um procedimento invasivo pesa mais. PMID conferido via PubMed E-utilities nesta sessão."
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
não "a ablação funciona na FA com IC" — isso já estava respondido — mas **"qual paciente, dentro do
espectro de FA com IC, se beneficia o suficiente para que a conversa sobre ablação faça sentido"**.

## Desenho do estudo
Estudo de coorte multicêntrico, em duas etapas:
- **Coorte de derivação**: registro China-AF, **31 hospitais chineses**, pacientes recrutados entre
  **1º de agosto de 2011 e 31 de dezembro de 2022** — **3.122 pacientes** com FA e IC (excluídos os
  assintomáticos), sendo **1.476 mulheres (47,3%)** e **1.646 homens (52,7%)**.
- **Coorte de validação externa**: subconjunto do ensaio **CABANA** (internacional, multicêntrico,
  randomizado, aberto) — **778 pacientes**, **345 mulheres (44,3%)** e **433 homens (55,7%)**,
  populações etnicamente diversas, diferente da coorte de derivação (majoritariamente chinesa).

A ferramenta foi construída aplicando **clustering não supervisionado seguido de modelos de
aprendizado supervisionado** sobre **25 características clínicas de fácil obtenção** (dado
disponível na consulta comum, sem exame adicional) — decisão de desenho que teve o propósito
explícito de tornar a ferramenta aplicável na prática, não só em ambiente de pesquisa.

## Os três grupos de risco identificados
O modelo agrupou os pacientes em **três clusters** distintos, com incidência de eventos compostos
(morte cardiovascular e AVC) claramente separada entre eles, medida em eventos por 100
pessoas-ano:

| Cluster | Incidência do desfecho composto (por 100 pessoas-ano) | IC95% |
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
  associou-se a **redução expressiva do desfecho composto**: **HR ajustado 0,16** (IC95% 0,07–0,36),
  com **p de interação = 0,0039** — ou seja, o efeito da ablação **difere significativamente** entre
  os clusters, não é um efeito uniforme aplicado a toda a população.
- **A mesma direção de efeito se confirmou na coorte de validação externa (CABANA)**: **HR ajustado
  0,19** (IC95% 0,05–0,73, p=0,015) no cluster equivalente de maior risco.

**Leitura clínica direta:** é justamente o paciente de **maior risco basal** — o que mais frequentemente
seria visto como "candidato ruim" por comorbidade e gravidade — quem mostrou o maior benefício
relativo da ablação nesta análise. Isso inverte uma intuição comum na conversa de decisão
compartilhada, em que o risco basal alto tende a ser lido como razão para não arriscar um
procedimento invasivo. Os autores não relatam, nos clusters de menor risco, benefício de magnitude
comparável — a ferramenta serve, portanto, tanto para identificar quem mais se beneficia quanto
para não superestimar o benefício em quem já está em risco baixo.

## Limite metodológico que precisa entrar na conversa com o paciente
Os próprios autores são explícitos sobre isto na conclusão do estudo, e o documento reproduz o
limite sem suavizar: **a ferramenta foi derivada de dados observacionais**, não de um ensaio
randomizado que testasse a ablação estratificada por cluster. A associação entre cluster de maior
risco e maior benefício da ablação é, portanto, **hipótese gerada por dados**, ainda que reforçada
pela validação externa independente no CABANA — e os próprios autores dizem que **a eficácia da
ferramenta ainda precisa de confirmação em ensaios de intervenção e na prática clínica real**.

**VERIFICAÇÃO HUMANA NECESSÁRIA**: o artigo não publica, no resumo, a lista completa e o peso de
cada uma das 25 variáveis clínicas usadas no modelo de clustering, nem os pontos de corte que
definem a fronteira entre os três clusters — essa informação está no texto completo/material
suplementar (PMCID PMC12242850) e não deve ser aplicada à beira do leito sem consultá-la
diretamente na fonte primária.

## Onde isso se encaixa na conversa de decisão compartilhada
Este documento não substitui a evidência de eficácia do CASTLE-AF nem a indicação já estabelecida
de ablação na FA com IC — ele acrescenta uma camada de **individualização do risco basal** que pode
ser usada como ponto de partida da conversa: mostrar ao paciente em qual faixa de risco ele se
encontra, e que, segundo esta análise, é justamente o paciente de maior risco quem mais tende a se
beneficiar — sempre com a ressalva, dita ao paciente, de que a ferramenta ainda não foi validada em
ensaio randomizado prospectivo.

## Fonte
Peng X et al. *Development and validation of risk stratification and shared decision-making tool
for catheter ablation for atrial fibrillation in patients with heart failure: a multicentre cohort
study.* EClinicalMedicine. 2025;83:103219. PMID 40641819, PMCID PMC12242850, DOI
10.1016/j.eclinm.2025.103219 — dados conferidos por leitura direta do resumo estruturado via
PubMed E-utilities nesta sessão (08/09/2026).
