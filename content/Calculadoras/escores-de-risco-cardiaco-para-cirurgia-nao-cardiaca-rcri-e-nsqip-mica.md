---
title: "Escores de Risco Cardíaco para Cirurgia Não Cardíaca: RCRI e NSQIP MICA"
slug: escores-de-risco-cardiaco-para-cirurgia-nao-cardiaca-rcri-e-nsqip-mica
theme: "Calculadoras"
kind: calculadora
review_status: revisado
source_refs: ["Lee TH, Marcantonio ER, Mangione CM, Thomas EJ, Polanczyk CA, et al. Derivation and prospective validation of a simple index for prediction of cardiac risk of major noncardiac surgery. Circulation. 1999;100(10):1043-1049. PMID: 10477528 — 4.315 pacientes com 50 anos ou mais, coorte de derivação (2.893) e de validação (1.422)", "Ford MK, Beattie WS, Wijeysundera DN. Systematic review: prediction of perioperative cardiac complications and mortality by the revised cardiac risk index. Ann Intern Med. 2010;152(1):26-35. PMID: 20048269 — revisão sistemática de 24 estudos e 792.740 pacientes", "Gupta PK, Gupta H, Sundaram A, Kaushik M, Fang X, et al. Development and validation of a risk calculator for prediction of cardiac risk after surgery. Circulation. 2011;124(4):381-387. PMID: 21730309 — escore NSQIP MICA, derivação em 211.410 pacientes (2007) e validação em 257.385 (2008)"]
legacy_source: "Documento novo, escrito em 01/08/2026. A pasta de Calculadoras tinha os escores de SCA, de FA, de TEV e de cirurgia cardíaca (EuroSCORE II, STS), mas nenhum para a pergunta mais comum da interconsulta: qual é o risco cardíaco desta cirurgia NÃO cardíaca. O RCRI é o escore mais usado do mundo para isso, e não estava na base. O tema clínico Perioperatório pertence à outra sessão; este documento é do escore, e fica em Calculadoras, como os demais."
---

# Escores de Risco Cardíaco para Cirurgia Não Cardíaca

## O RCRI — o escore mais usado, e por quê
Lee TH et al., Circulation. 1999;100(10):1043-1049 (PMID 10477528). Coorte prospectiva de **4.315 pacientes com 50 anos ou mais** submetidos a procedimentos eletivos maiores não cardíacos em hospital universitário terciário.

**Complicações cardíacas maiores ocorreram em 56 (2%) dos 2.893 pacientes da coorte de derivação.**

**Os seis preditores independentes do Índice de Risco Cardíaco Revisado:**
1. **Cirurgia de alto risco**
2. **História de doença isquêmica do coração**
3. **História de insuficiência cardíaca congestiva**
4. **História de doença cerebrovascular**
5. **Tratamento pré-operatório com insulina**
6. **Creatinina sérica pré-operatória > 2,0 mg/dL**

**Taxa de complicação cardíaca maior por número de fatores:**

| fatores | coorte de derivação | coorte de validação |
|---|---|---|
| **0** | **0,5%** | **0,4%** |
| **1** | **1,3%** | **0,9%** |
| **2** | **4%** | **7%** |
| **≥ 3** | **9%** | **11%** |

**Conclusão dos autores:** em pacientes **estáveis** submetidos a cirurgia maior não cardíaca **não urgente**, o índice identifica quem está sob risco mais alto — e também **quem é de baixo risco, em quem avaliação adicional dificilmente ajudará**.

**A segunda metade dessa frase é a mais útil na prática, e a mais ignorada:** o escore serve tanto para escalar investigação quanto para **parar de investigar**.

## O que a validação sistemática mostrou — e onde o RCRI falha
Ford MK, Beattie WS, Wijeysundera DN, Ann Intern Med. 2010;152(1):26-35 (PMID 20048269). Revisão sistemática de **24 estudos e 792.740 pacientes**; 18 relataram complicações cardíacas, e apenas **6 desses 18 eram prospectivos com vigilância uniforme e adjudicação cega**.

**Desempenho por cenário:**

| cenário | área sob a curva | sensibilidade | especificidade |
|---|---|---|---|
| **cirurgia não cardíaca mista** | **0,75** (IC95% 0,72-0,79) | 0,65 (0,46-0,81) | 0,76 (0,58-0,88) |
| **cirurgia VASCULAR** | **0,64** (IC95% 0,61-0,66) | 0,70 (0,53-0,82) | 0,55 (0,45-0,66) |
| **predição de MORTE** | mediana **0,62** (variação 0,54-0,78) | — | — |

- Razão de verossimilhança positiva na cirurgia mista: **2,78** (IC95% 1,74-4,45); negativa: **0,45** (0,31-0,67)
- **Não foi possível agrupar a área sob a curva para morte, por heterogeneidade altíssima (I² = 95%)**

**Conclusão literal:** o RCRI discrimina **moderadamente bem** na cirurgia não cardíaca mista, **mas NÃO teve bom desempenho na cirurgia vascular nem na predição de morte**.

**Duas consequências diretas:**
1. **Na cirurgia vascular, o RCRI perde boa parte do valor** — área sob a curva de 0,64, pouco acima do acaso
2. **Ele não é um escore de mortalidade** — usá-lo para estimar risco de morte é uso fora da validação

## NSQIP MICA (2011) — o escore que discrimina melhor, com outro custo
Gupta PK et al., Circulation. 2011;124(4):381-387 (PMID 21730309). Derivado do banco prospectivo multicêntrico do **National Surgical Quality Improvement Program** do American College of Surgeons (**mais de 250 hospitais**):
- **211.410 pacientes** na derivação (2007); **1.371 (0,65%)** desenvolveram **infarto ou parada cardíaca perioperatórios**
- **Validação em 257.385 pacientes** (2008)

**Cinco preditores:**
1. **Tipo de cirurgia**
2. **Estado funcional dependente**
3. **Creatinina anormal**
4. **Classe ASA**
5. **Idade crescente**

**Desempenho:**
- **Estatística c de 0,884 (2007) e 0,874 (2008)**
- **O RCRI aplicado ao mesmo banco de 2008 rendeu estatística c de 0,747**

**Conclusão literal:** o desempenho preditivo do calculador **supera o do RCRI**, e a ferramenta foi desenvolvida como **calculadora interativa** para simplificar o processo de consentimento informado.

## Como escolher entre os dois
| | RCRI | NSQIP MICA |
|---|---|---|
| variáveis | **6, todas dicotômicas** | **5, com escalas e tipo de cirurgia detalhado** |
| cálculo | **de cabeça, à beira do leito** | **exige calculadora** |
| desfecho | complicação cardíaca maior | **infarto ou parada cardíaca** |
| discriminação | **c 0,75** (mista) / **0,64** (vascular) | **c 0,874-0,884** |
| desempenho para morte | **ruim** (mediana 0,62) | não é o desfecho |

- **O RCRI é mais simples e mais transportável**, e sua força está em **identificar o baixo risco** — 0,4% a 0,5% de complicação com zero fatores
- **O NSQIP MICA discrimina melhor**, mas exige calculadora e foi derivado de população cirúrgica norte-americana com codificação própria
- **Nenhum dos dois é escore de mortalidade**
- **Na cirurgia vascular, o RCRI perde desempenho** e o julgamento clínico e a avaliação funcional pesam mais

A capacidade funcional pré-operatória e os biomarcadores são a outra metade da avaliação, e o tema
clínico Perioperatório tem documentos próprios na biblioteca. Os escores de cirurgia **cardíaca**
estão nesta mesma pasta: `euroscore-ii-risco-de-mortalidade-em-cirurgia-cardiaca.md` e
`sts-risk-score-modelos-de-risco-da-society-of-thoracic-surgeons.md`.

## Limites
- **O RCRI é de 1999**, de um único hospital terciário, e antecede a troponina de alta sensibilidade e a revascularização contemporânea
- **A revisão sistemática de 2010 registra que os estudos eram, em geral, de baixa qualidade metodológica**, com definições variadas de evento cardíaco e **heterogeneidade estatística e clínica alta**
- **O NSQIP MICA foi derivado e validado em bancos administrativos** norte-americanos, com definições de desfecho próprias
- **Nenhum dos dois é brasileiro**, e a distribuição de tipo de cirurgia e de comorbidade difere
- **Nenhum foi desenhado para cirurgia de urgência** — o RCRI exige procedimento **não urgente** e paciente **estável**
- **Os dois preveem risco basal; não medem o efeito de intervenções** feitas depois da estratificação

## Armadilhas clínicas
- **Usar o RCRI para estimar risco de morte** — a mediana da área sob a curva para óbito foi 0,62, com I² de 95%
- **Aplicar o RCRI à cirurgia vascular como se o desempenho fosse o mesmo** — cai para 0,64
- **Aplicar a paciente instável ou a cirurgia de urgência** — o índice foi derivado em cirurgia eletiva com paciente estável
- **Usar o escore para justificar mais exames em quem tem zero fatores** — os próprios autores dizem que a avaliação adicional dificilmente ajuda aí
- **Tratar os dois escores como intercambiáveis** — desfechos, variáveis e populações de derivação são diferentes
- **Esquecer que estratificar não é tratar** — nenhum dos dois demonstra que agir sobre o resultado melhora desfecho
- **Citar a creatinina de corte do RCRI em outra unidade sem converter** — o critério original é **> 2,0 mg/dL**
