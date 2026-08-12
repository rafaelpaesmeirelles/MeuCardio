---
title: "Escores APPLE e APCEL: Predição de Recorrência Após Ablação por Cateter de Fibrilação Atrial"
slug: escore-apple-e-apcel-predicao-de-recorrencia-apos-ablacao-de-fibrilacao-atrial
theme: "Calculadoras"
kind: calculadora
review_status: revisado
source_refs: ["Kornej J, Hindricks G, Shoemaker MB, Husser D, Arya A, Sommer P, et al. The APPLE score: a novel and simple score for the prediction of rhythm outcomes after catheter ablation of atrial fibrillation. Clin Res Cardiol. 2015;104(10):871-876. DOI: 10.1007/s00392-015-0856-x. PMID: 25876528. PMCID: PMC4726453 — texto completo aberto lido na íntegra, derivação em 1.145 pacientes (Leipzig) e validação externa em 261 pacientes (Vanderbilt)", "Ulus T, Ahmadi AŞ, Çolak E. A new scoring system to predict the risk of late recurrence in extended follow-up after atrial fibrillation catheter ablation: APCEL score. J Arrhythm. 2025;41(2):e70048. DOI: 10.1002/joa3.70048. PMID: 40130217. PMCID: PMC11931582 — texto completo aberto lido na íntegra, coorte única de 206 pacientes, seguimento mediano de 40 meses, sem validação externa publicada", "Cui W, Bin X, Ning L, Xie J. Construction and validation of a regularized logistic regression model for predicting late recurrence after ablation in persistent atrial fibrillation: a clinical parameter approach. Front Cardiovasc Med. 2025;12:1713560. DOI: 10.3389/fcvm.2025.1713560. PMID: 41458987. PMCID: PMC12741151 — texto completo aberto, usado aqui só para o dado comparativo de desempenho do APPLE score numa coorte contemporânea de FA persistente"]
legacy_source: "Documento novo, escrito em 12/08/2026. O tema Calculadoras cobre escores de risco de AVC/sangramento na FA (CHA₂DS₂-VA, HAS-BLED, ABC, ATRIA, ORBIT, HEMORR2HAGES, SAMe-TT2R2) e de risco pós-stent/pós-TEV, mas não tinha nenhum escore dedicado à pergunta que antecede a decisão de indicar ablação por cateter: qual é a probabilidade de recorrência da arritmia depois do procedimento? Esta lacuna nunca tinha sido preenchida nesta biblioteca."
---

# Escores APPLE e APCEL: Predição de Recorrência Após Ablação por Cateter de Fibrilação Atrial

## O problema que estes escores tentam resolver
A ablação por cateter de fibrilação atrial (FA) reduz sintomas e pode reduzir internação por IC, mas a **recorrência é comum** — ocorre em até 50% dos pacientes no primeiro ano, segundo os próprios autores do APPLE score. Nenhum dos escores clássicos de FA (CHA₂DS₂-VA, HAS-BLED) foi desenhado para essa pergunta: eles estimam risco de AVC e de sangramento sob anticoagulação, **não** a probabilidade de a arritmia voltar depois do procedimento. Um escore de recorrência ajuda a calibrar a expectativa do paciente antes do procedimento e a decidir a intensidade do seguimento (monitorização prolongada, antiarrítmico de manutenção, indicação de um segundo procedimento).

## O APPLE score — a referência mais estabelecida
Kornej J et al., Clin Res Cardiol. 2015;104(10):871-876 (PMID 25876528), do Heart Center de Leipzig, com validação externa em Vanderbilt:
- **Desenho**: derivação em **1.145 pacientes** (60±10 anos, 65% homens, 62% FA paroxística), desfecho = recorrência de FA entre 3 e 12 meses após a ablação; **validação externa em 261 pacientes** de outro centro, com seguimento comparável
- **Componentes, 1 ponto cada** (o nome é o próprio mnemônico): **A**ge (idade) > 65 anos; **P**ersistent AF (FA persistente, não paroxística); i**P**aired eGFR (TFG estimada < 60 mL/min/1,73m²); **L**A diameter (diâmetro do átrio esquerdo) ≥ 43 mm; **E**F (fração de ejeção) < 50%
- **Faixa**: 0 a 5 pontos

**Desempenho**: o APPLE superou o CHADS₂ e o CHA₂DS₂-VASc na predição de recorrência — **AUC 0,634** (IC95% 0,600-0,668) contra **0,538** (CHADS₂) e **0,542** (CHA₂DS₂-VASc), p<0,001. Na coorte de validação externa, desempenho semelhante: **AUC 0,624** (IC95% 0,562-0,687). Comparado a um APPLE de 0, o odds ratio para recorrência foi **1,73** (score 1), **2,79** (score 2) e **4,70** (score ≥3), todos com p<0,05.

## Um dado recente que pede cautela: o desempenho não se sustenta em toda coorte
Cui W et al., Front Cardiovasc Med. 2025;12:1713560 (PMID 41458987), dezembro de 2025, testou o APPLE score numa coorte contemporânea de **300 pacientes com FA persistente** submetidos a ablação por radiofrequência entre 2023 e 2024: o desempenho caiu para **AUC 0,506** — **praticamente equivalente ao acaso**. O escore comparador MB-LATER teve desempenho melhor nessa mesma coorte (AUC 0,663), mas nenhum dos escores clássicos testados alcançou boa discriminação nesse cenário específico.

**Isso não invalida o APPLE score** — a coorte de 2025 era só de FA persistente (população mais homogênea e de risco mais alto de recorrência, que reduz a capacidade de qualquer escore discriminar), enquanto a derivação original incluía 62% de FA paroxística. **O ensinamento prático é outro**: nenhum escore de recorrência pós-ablação tem desempenho robusto e estável em toda população de FA, e a discriminação moderada (AUC na faixa de 0,6-0,65) é o teto realista da maioria deles — não uma limitação de amostra pequena, é limitação genuína da ferramenta.

## APCEL — escore novo (2025), ainda preliminar
Ulus T et al., J Arrhythm. 2025;41(2):e70048 (PMID 40130217), Turquia:
- **Desenho**: **206 pacientes** com ablação índice de FA paroxística ou persistente, seguimento mediano de **40 meses** (21-57) — o mais longo entre os escores de recorrência tardia até a publicação, segundo os próprios autores
- **Componentes**: recorrência precoce (dentro do período de blanking) = **3 pontos**; duração da FA pré-ablação > 19 meses = **2 pontos**; FA persistente, DPOC e índice de volume atrial esquerdo > 31 mL/m² = **1 ponto cada**
- **Desempenho**: AUC **0,940** aos 6 meses, **0,865** aos 12 meses, **0,814** aos 24 meses e **0,798** aos 36 meses — números bem mais altos que os do APPLE, mas de uma coorte muito menor e sem validação externa

**⚠️ VERIFICAÇÃO HUMANA NECESSÁRIA — inconsistência encontrada na própria fonte, não resolvida por esta revisão**: o artigo define os grupos de risco de duas formas diferentes em partes distintas do texto. Na seção de Métodos, os autores descrevem "grupo 1 (score <2), grupo 2 (score 2-3) e grupo 3 (score >3)"; na seção de Resultados e na legenda da Figura 3, os mesmos três grupos aparecem como "grupo 1 (score <3), grupo 2 (score 3-5) e grupo 3 (score >5)". As duas versões não são a mesma partição, e o texto completo (PMC11931582) não esclarece qual prevalece. **Não escolhemos uma das duas para não fabricar a versão correta** — quem for usar os pontos de corte do APCEL deve conferir a versão publicada mais atualizada ou o material suplementar antes de aplicar clinicamente.

**Por que este documento inclui um escore com essa ressalva**: é a única publicação de 2024-2026 encontrada com um escore de recorrência tardia genuinamente novo (a maioria da literatura recente do período são modelos de aprendizado de máquina ou validações de escores antigos, não escores de pontos novos). Optamos por descrevê-lo com a limitação declarada, em vez de omiti-lo ou de escolher arbitrariamente uma das duas versões dos pontos de corte.

## Limitações comuns aos escores de recorrência pós-ablação
- **Nenhum deles orienta a técnica de ablação** (radiofrequência vs. crioballão vs. campo pulsado) nem substitui a decisão compartilhada sobre indicar ou não o procedimento
- **AUC na faixa de 0,5 a 0,65 é discriminação fraca a moderada** — mesmo o APPLE, na validação original, está longe de ser um preditor forte isolado
- **O APCEL não tem validação externa publicada** até esta revisão (agosto de 2026) — só a coorte de derivação, de um único centro
- **Definição de "recorrência tardia" varia entre os estudos** (após período de blanking, após 12 meses, seguimento estendido de até 40 meses no APCEL) — comparar AUC entre escores com desfechos definidos de forma diferente exige cautela

## Armadilhas clínicas
- **Usar o APPLE (ou o APCEL) para decidir se indica ou não a ablação** — os dois escores foram derivados em pacientes **já submetidos** ao procedimento, e servem para estimar prognóstico pós-ablação, não para selecionar quem deve ser ablacionado
- **Tratar o APCEL como equivalente em robustez ao APPLE** — o APPLE tem validação externa publicada há mais de uma década em população maior; o APCEL é preliminar, com a inconsistência de corte já registrada acima
- **Ignorar a queda de desempenho do APPLE em FA persistente** (AUC 0,506 na coorte de 2025) e aplicar o escore com a mesma confiança em qualquer subtipo de FA
- **Confundir APPLE com CHA₂DS₂-VASc** — os componentes se sobrepõem parcialmente (idade, mas não os mesmos limiares), e servem a perguntas clínicas completamente diferentes: um estima recorrência de arritmia, o outro estima risco de AVC sob FA já estabelecida
