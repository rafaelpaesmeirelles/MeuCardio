---
title: "Escore de Mehran (ACUITY/HORIZONS-AMI): Risco de Sangramento Maior na Síndrome Coronariana Aguda"
slug: escore-de-mehran-acuity-horizons-risco-de-sangramento-na-sindrome-coronariana-aguda
theme: "Calculadoras"
kind: calculadora
review_status: revisado
source_refs: ["Mehran R, Pocock SJ, Nikolsky E, Clayton T, Dangas GD, Kirtane AJ, Parise H, Fahy M, Manoukian SV, Feit F, Ohman ME, Witzenbichler B, Guagliumi G, Lansky AJ, Stone GW. A risk score to predict bleeding in patients with acute coronary syndromes. J Am Coll Cardiol. 2010;55(23):2556-2566. DOI: 10.1016/j.jacc.2009.09.076. PMID: 20513595 — artigo de derivação, coorte, preditores, c-estatístico e associação com mortalidade conferidos nesta sessão via PubMed E-utilities (esearch por autor 'Mehran R' + termos 'bleeding percutaneous coronary intervention risk score', depois efetch em XML/texto puro do registro, PMID confirmado diretamente).", "Taha S, D'Ascenzo F, Moretti C, Omedè P, Montefusco A, Bach RG, Alexander KP, Mehran R, Ariza-Solé A, Zoccai GB, Gaita F. Accuracy of bleeding scores for patients presenting with myocardial infarction: a meta-analysis of 9 studies and 13,759 patients. Postepy Kardiol Interwencyjnej. 2015;11(3):182-190. DOI: 10.5114/pwki.2015.54011. PMID: 26677357. PMCID: PMC4631731 — usado apenas como validação externa agregada (AUC do escore ACUITY/Mehran fora da coorte de derivação), abstract conferido nesta sessão via PubMed E-utilities."]
legacy_source: "Documento novo, escrito em 09/09/2026. Checagem de colisão feita em content/**/*.md (não só nos JSONs) e na pasta Calculadoras especificamente: já existem CRUSADE (crusade-bleeding-score), HAS-BLED (has-bled), ORBIT (escore-orbit-risco-de-sangramento-em-fibrilacao-atrial-anticoagulada), ATRIA (escores-atria-risco-de-avc-e-de-sangramento-na-fibrilacao-atrial), HEMORR2HAGES, PARIS (escore-paris-risco-de-trombose-e-de-sangramento-apos-stent), DAPT/PRECISE-DAPT, IMPROVE e VTE-BLEED — mas nenhum documento cobre o escore de sangramento derivado por Mehran R et al. a partir das coortes ACUITY e HORIZONS-AMI (JACC 2010, PMID 20513595), que é o escore de sangramento mais amplamente usado e testado especificamente na síndrome coronariana aguda tratada com estratégia invasiva/ICP (diferente do CRUSADE, derivado só em NSTEMI, e do PARIS, que mede sangramento e trombose de stent a 2 anos pós-alta). Também confirmado que os documentos já existentes sobre os ensaios ACUITY e REPLACE-2/HORIZONS-AMI (pasta Doença_coronariana, ex.: acuity-bivalirudina-na-sca-invasiva.md) tratam do desfecho de eficácia/segurança dos próprios ensaios, não do escore de sangramento derivado posteriormente dessas coortes combinadas — são complementares, não duplicados. Verificado via PubMed E-utilities nesta sessão (esearch + efetch de abstract/XML, PMIDs 20513595 e 26677357 confirmados diretamente no registro)."
---

# Escore de Mehran (ACUITY/HORIZONS-AMI): Risco de Sangramento Maior na Síndrome Coronariana Aguda

## O que é e por que falta nesta pasta

O **escore de Mehran** — também citado na literatura como **escore de sangramento ACUITY/HORIZONS-AMI** — foi derivado por **Mehran R et al.** e publicado no ***Journal of the American College of Cardiology*** em 2010 (*J Am Coll Cardiol. 2010;55(23):2556-2566*, DOI 10.1016/j.jacc.2009.09.076, **PMID: 20513595**), sob o título literal *"A risk score to predict bleeding in patients with acute coronary syndromes"*.

A pasta Calculadoras já cobre vários escores de sangramento — CRUSADE (derivado só em NSTEMI), HAS-BLED/ORBIT/ATRIA/HEMORR2HAGES (fibrilação atrial anticoagulada), PARIS (sangramento e trombose de stent no seguimento de 2 anos pós-alta) e DAPT/PRECISE-DAPT (duração da dupla antiagregação) — mas nenhum documento tratava do escore que foi derivado numa coorte combinada de **síndrome coronariana aguda de espectro completo** (NSTEMI, STEMI e ACS biomarcador-negativa) tratada com estratégia invasiva, e que incorpora explicitamente a **escolha do regime antitrombótico periprocedimento** (heparina + inibidor da glicoproteína IIb/IIIa vs. bivalirudina isolada) como uma das variáveis do modelo — uma pergunta distinta da do CRUSADE (risco basal em NSTEMI, sem variável de tratamento) e da do PARIS (janela de seguimento pós-alta, não intra-hospitalar/30 dias).

## Desenho e coorte de derivação

Direto do abstract do registro (PMID 20513595):
- **Objetivo declarado**: desenvolver um escore de risco prático para prever o risco e as implicações do sangramento maior na síndrome coronariana aguda (SCA)
- **Coortes de origem**: **ACUITY** (*Acute Catheterization and Urgent Intervention Triage strategY*) e **HORIZONS-AMI** (*Harmonizing Outcomes with RevasculariZatiON and Stents in Acute Myocardial Infarction*)
- **Tamanho da coorte combinada**: **17.421 pacientes** com SCA, incluindo infarto sem supra de ST (NSTEMI), infarto com supra de ST (STEMI) e SCA biomarcador-negativa
- **Método**: escore de risco em números inteiros, derivado de um modelo de regressão logística multivariável, para prever **sangramento maior não relacionado a CABG dentro de 30 dias**

## Preditores do modelo

Citação literal do abstract, traduzida: o modelo identificou **6 preditores basais independentes** — **sexo feminino, idade avançada, creatinina sérica elevada, contagem de leucócitos elevada, anemia** e **apresentação como NSTEMI ou STEMI** (em contraste com SCA biomarcador-negativa) — **mais 1 variável relacionada ao tratamento**: uso de **heparina associada a inibidor da glicoproteína IIb/IIIa**, em vez de **bivalirudina isolada**.

**Sobre os valores numéricos de cada preditor**: o abstract do registro (PMID 20513595) nomeia as 6 variáveis basais e a variável de tratamento e reporta o desempenho agregado do modelo, mas **não publica, no próprio texto do abstract, a tabela de pontos inteiros atribuídos a cada variável ou faixa de variável** (por exemplo, quantos pontos por década de idade, ou por faixa de creatinina). Essa tabela existe no corpo/figuras do artigo original (texto completo pago, não indexado em PMC — sem PMCID neste registro) e em calculadoras de terceiros que a reproduzem. Conforme a diretriz desta base, uma tabela de coeficientes que só é confirmável em fonte secundária (calculadora online, revisão, tabela reproduzida sem acesso ao artigo primário) **não conta como confirmada**. Os valores exatos de pontuação por variável são, portanto: **VERIFICAÇÃO HUMANA NECESSÁRIA** (checar diretamente o texto completo de Mehran R et al., JACC 2010;55(23):2556-2566, Tabela de derivação do escore).

## Desempenho reportado na derivação

Direto do abstract do registro (PMID 20513595):
- **Incidência do desfecho**: sangramento maior não relacionado a CABG dentro de 30 dias ocorreu em **744 pacientes (7,3%)** da coorte de 17.421
- **Discriminação do modelo**: **c-estatístico = 0,74**
- **Gradiente de risco**: o escore inteiro diferenciou pacientes com taxa de sangramento maior não-CABG em 30 dias variando de **1% a mais de 40%**
- **Associação com mortalidade**: em modelo de Cox com covariável tempo-dependente ajustada, o sangramento maior foi preditor independente de aumento de **3,2 vezes** na mortalidade; o vínculo com risco de morte foi mais forte para sangramento maior definido pelo critério TIMI (não relacionado a CABG), seguido por sangramento maior não-TIMI (com ou sem transfusão); hematomas isolados de grande extensão e sangramento relacionado a CABG **não** se associaram de forma significativa a mortalidade subsequente

## Validação externa

Taha S, D'Ascenzo F, Moretti C, et al. *Postepy Kardiol Interwencyjnej*. 2015;11(3):182-190 (**PMID: 26677357**, PMCID PMC4631731) — meta-análise de **9 estudos e 13.759 pacientes** de validação externa de escores de sangramento na síndrome coronariana aguda. Achados diretos do abstract:
- Escores avaliados: **CRUSADE, ACUITY (o escore de Mehran aqui descrito), ACTION e GRACE**
- Taxa agregada de sangramento maior intra-hospitalar nas coortes de validação: **7,80%** (IC 5,5-9,2)
- **Desempenho do escore ACUITY em toda a população de SCA**: **AUC 0,71** (IC 0,63-0,77) — semelhante ao CRUSADE (AUC 0,71; IC 0,64-0,80) e inferior ao ACTION (AUC 0,75; IC 0,72-0,79); todos superiores ao GRACE (AUC 0,66; IC 0,64-0,67) para esse desfecho
- Em **STEMI**, os escores tiveram desempenho semelhante entre si; o **CRUSADE foi o único validado externamente também em NSTEMI** nesta meta-análise
- Para **ACTION e ACUITY**, a acurácia aumentou em pacientes com **acesso radial**; para o CRUSADE, não houve diferença por via de acesso

Desempenho em população brasileira especificamente: **não localizado nesta pesquisa — VERIFICAÇÃO HUMANA NECESSÁRIA**.

## Aplicação prática — quando usar em vez de CRUSADE, HAS-BLED, ORBIT/ATRIA ou PARIS

- O escore de Mehran é aplicável a **todo o espectro de SCA** (NSTEMI, STEMI e biomarcador-negativa) tratada por estratégia invasiva, e é o único, entre os já cobertos nesta pasta, a incorporar explicitamente o **regime antitrombótico periprocedimento** (heparina + IIb/IIIa vs. bivalirudina isolada) como variável de risco — ou seja, ele estima risco de sangramento condicionado, em parte, a uma escolha terapêutica que o próprio médico está fazendo no momento da ICP.
- **CRUSADE** (crusade-bleeding-score) foi derivado especificamente em **NSTEMI**, sem variável de tratamento, e mede sangramento maior intra-hospitalar; segundo a meta-análise de validação (PMID 26677357), é o único dos quatro escores comparados com validação externa dedicada também em NSTEMI.
- **HAS-BLED, ORBIT e ATRIA** (has-bled; escore-orbit-risco-de-sangramento-em-fibrilacao-atrial-anticoagulada; escores-atria-risco-de-avc-e-de-sangramento-na-fibrilacao-atrial) respondem a uma pergunta clínica diferente: risco de sangramento sob **anticoagulação oral crônica em fibrilação atrial**, não risco periprocedimento de ICP na SCA.
- **PARIS** (escore-paris-risco-de-trombose-e-de-sangramento-apos-stent) mede sangramento (e trombose de stent) no **seguimento ambulatorial de até 2 anos pós-alta** sob dupla antiagregação, enquanto o escore de Mehran mede sangramento maior **intra-hospitalar/até 30 dias**, no contexto agudo da SCA e da própria ICP.
- Na prática, o escore de Mehran é usado, como o CRUSADE, em conjunto com escores isquêmicos (GRACE, TIMI) para balancear risco trombótico vs. hemorrágico na escolha entre estratégias antitrombóticas (bivalirudina isolada vs. heparina + IIb/IIIa) e na via de acesso — a própria fonte de validação externa mostra ganho de acurácia com acesso radial para este escore.

## Armadilhas clínicas

- **Confundir o "escore de Mehran/ACUITY" com o próprio ensaio ACUITY** (Stone GW et al.) ou com o ensaio HORIZONS-AMI — os ensaios testaram estratégias antitrombóticas (bivalirudina vs. heparina+IIb/IIIa); o escore aqui descrito foi derivado posteriormente, usando as coortes combinadas desses dois ensaios como base de dados observacional para modelar risco de sangramento.
- **Buscar a tabela de pontos por variável em calculadora online e tratá-la como fonte primária confirmada** — o abstract do artigo de derivação (PMID 20513595) nomeia as variáveis e o c-estatístico, mas não publica os pesos numéricos por variável no texto do resumo; esse detalhe depende do texto completo, não acessado nesta pesquisa (sem PMCID neste registro).
- **Aplicar o escore fora do contexto de SCA tratada por estratégia invasiva** — a coorte de derivação é toda oriunda de ensaios com cateterismo/ICP; extrapolação para SCA manejada de forma exclusivamente conservadora não foi confirmada nesta pesquisa.
- **Tratar o desempenho do escore (AUC ~0,71-0,74) como superior aos demais escores de sangramento em SCA** — a meta-análise de validação externa (PMID 26677357) mostra desempenho **semelhante** entre ACUITY e CRUSADE, e **inferior** ao ACTION nessa amostra agregada; diferenças pontuais de AUC entre estudos não devem ser lidas como superioridade robusta de um escore sobre o outro.
- **Ignorar a variável de tratamento** — ao contrário do CRUSADE, este escore muda de valor conforme a escolha antitrombótica feita durante a própria ICP; comparar o resultado do escore entre pacientes com regimes diferentes sem considerar essa variável é um erro de leitura do modelo.

## Tudo com Tudo

- [CRUSADE Bleeding Score](/biblioteca/crusade-bleeding-score)
- [HAS-BLED](/biblioteca/has-bled)
- [Escore ORBIT: Risco de Sangramento em Fibrilação Atrial Anticoagulada](/biblioteca/escore-orbit-risco-de-sangramento-em-fibrilacao-atrial-anticoagulada)
- [Escores ATRIA: Risco de AVC e de Sangramento na Fibrilação Atrial](/biblioteca/escores-atria-risco-de-avc-e-de-sangramento-na-fibrilacao-atrial)
- [Escore PARIS: Risco de Trombose e de Sangramento Após Stent](/biblioteca/escore-paris-risco-de-trombose-e-de-sangramento-apos-stent)
- [DAPT Score e PRECISE-DAPT: Duração da Dupla Antiagregação Após Stent](/biblioteca/dapt-score-e-precise-dapt-duracao-da-dupla-antiagregacao-apos-stent)
- [ACUITY: Bivalirudina na SCA Invasiva](/biblioteca/acuity-bivalirudina-na-sca-invasiva)
