---
title: "Escore IABP-SHOCK II: Estratificação de Risco de Mortalidade no Choque Cardiogênico Pós-IAM"
slug: escore-iabp-shock-ii-estratificacao-de-risco-de-mortalidade-no-choque-cardiogenico-pos-iam
theme: "Calculadoras"
kind: calculadora
review_status: revisado
source_refs: ["Pöss J, Köster J, Fuernau G, Eitel I, de Waha S, Ouarrak T, Lassus J, Harjola VP, Zeymer U, Thiele H, Desch S. Risk Stratification for Patients in Cardiogenic Shock After Acute Myocardial Infarction. J Am Coll Cardiol. 2017;69(15):1913-1920. DOI: 10.1016/j.jacc.2017.02.027. PMID: 28408020", "Harjola VP, Lassus J, Sionis A, Køber L, Tarvasmäki T, Spinar J, Parissis J, Banaszewski M, Silva-Cardoso J, Carubelli V, Di Somma S, Tolppanen H, Zeymer U, Thiele H, Nieminen MS, Mebazaa A; CardShock Study Investigators, GREAT network. Clinical picture and risk prediction of short-term mortality in cardiogenic shock. Eur J Heart Fail. 2015;17(5):501-509. PMID: 25820680 — coorte de validação externa (n=137) citada no artigo de derivação do escore"]
legacy_source: "Documento novo, escrito nesta sessão. Esta pasta já cobre o ensaio IABP-SHOCK II (eficácia do balão intra-aórtico) em dois documentos próprios de outras pastas (Terapia_intensiva e Doença_coronariana), e cobre o escore SAVE para sobrevida pré-ECMO — mas nenhum documento existente descrevia o escore de risco de mortalidade derivado da própria população do ensaio/registro IABP-SHOCK II (Pöss J et al., JACC 2017), pergunta distinta: não é sobre o benefício do balão, é sobre estratificação prognóstica no choque cardiogênico pós-IAM já estabelecido, com ou sem balão."
---

# Escore IABP-SHOCK II: Estratificação de Risco de Mortalidade no Choque Cardiogênico Pós-IAM

## O que é e o problema que resolve
A mortalidade no choque cardiogênico (CS) pós-infarto agudo do miocárdio permanece alta, e a decisão terapêutica precoce — intensidade de suporte, indicação de suporte circulatório mecânico, comunicação de prognóstico — depende de estratificar o risco o quanto antes. Pöss J et al., *Journal of the American College of Cardiology* 2017;69(15):1913-1920 (PMID 28408020), desenvolveram o **escore IABP-SHOCK II** exatamente para essa lacuna: uma ferramenta prognóstica **fácil de calcular à beira do leito**, derivada da própria população do ensaio/registro IABP-SHOCK II (*Intraaortic Balloon Pump in Cardiogenic Shock II*, NCT00491036), para prever mortalidade em 30 dias.

Este documento descreve **o escore de risco**, não o ensaio terapêutico — o ensaio IABP-SHOCK II (balão intra-aórtico versus tratamento convencional) já está coberto em dois documentos próprios desta base, listados em "Tudo com Tudo" abaixo.

## Como foi derivado
- População: pacientes com choque cardiogênico complicando infarto agudo do miocárdio, da coorte do ensaio/registro IABP-SHOCK II;
- Método: **análise de regressão multivariável stepwise**, buscando um modelo simples e utilizável na prática clínica diária;
- Validação interna na própria população do registro IABP-SHOCK II;
- **Validação externa** na população do estudo **CardShock** (Harjola VP et al., *Eur J Heart Fail* 2015;17(5):501-509, PMID 25820680), com n=137.

## As seis variáveis do escore
Seis variáveis emergiram como preditores independentes de mortalidade em 30 dias, citadas literalmente do resumo:
- **Idade > 73 anos**;
- **AVC prévio**;
- **Glicemia na admissão > 10,6 mmol/L (191 mg/dL)**;
- **Creatinina na admissão > 132,6 μmol/L (1,5 mg/dL)** — para o cálculo de função renal ajustada por peso e idade, ver [Clearance de Creatinina por Cockcroft-Gault](/biblioteca/clearance-de-creatinina-cockcroft-gault-ajuste-de-dose-em-cardiologia), já coberto nesta pasta;
- **Fluxo TIMI < 3 após a angioplastia coronariana percutânea** (ou seja, reperfusão angiográfica subótima do vaso culpado);
- **Lactato arterial na admissão > 5 mmol/L**.

**VERIFICAÇÃO HUMANA NECESSÁRIA**: o resumo indexado afirma que **"1 ou 2 pontos foram atribuídos a cada variável"**, mas **não especifica no texto do abstract qual peso exato (1 ou 2) foi atribuído a cada uma das seis variáveis individualmente**. Essa tabela variável-a-variável não está confirmada nesta pesquisa a partir do resumo; para aplicação em paciente real, use a calculadora oficial ou consulte o texto completo do artigo (Pöss J et al., JACC 2017;69(15):1913-1920) antes de reconstruir os pesos por fonte secundária não conferida — mesmo cuidado já registrado no documento do Escore SAVE desta pasta.

## Estratificação de risco e desempenho
Três categorias de risco, resultantes da soma dos pontos (máximo de 9), citadas literalmente do resumo:

| Categoria de risco | Pontuação | Mortalidade em 30 dias (derivação/registro IABP-SHOCK II) | Mortalidade (validação externa, CardShock, n=137) |
|---|---|---|---|
| Baixo risco | 0 a 2 | 23,8% | 28,0% |
| Risco intermediário | 3 ou 4 | 49,2% | 42,9% |
| Alto risco | 5 a 9 | 76,6% | 77,3% |

- Diferença entre categorias: **p < 0,0001** na coorte de derivação/registro; **p < 0,001** na validação externa;
- **Discriminação (AUROC/c-estatística)**: **0,79** na população do registro IABP-SHOCK II (validação interna) e **0,73** na validação externa (CardShock) — discriminação boa a moderada nas duas coortes;
- **Análise de Kaplan-Meier**: aumento escalonado (*stepwise*) de mortalidade entre as categorias de risco, com diferença estatisticamente significativa entre baixo e intermediário risco (p = 0,04) e entre baixo e alto risco (p = 0,008).

## O que este documento NÃO reproduz
**A atribuição exata de 1 ou 2 pontos a cada uma das seis variáveis** não está disponível no resumo indexado consultado nesta sessão (ver VERIFICAÇÃO HUMANA NECESSÁRIA acima). Este documento confirma diretamente do resumo: as seis variáveis, os cortes numéricos de cada uma, as três categorias de risco (faixas de pontuação), as taxas de mortalidade observadas em cada categoria (derivação e validação externa) e os dois valores de AUROC — mas não a tabela de pontos individual por variável.

## Leitura clínica e armadilhas
- **Não confundir o escore de risco com o ensaio IABP-SHOCK II**: o ensaio testou se o balão intra-aórtico reduz mortalidade no choque cardiogênico pós-IAM (resultado neutro, já coberto nos documentos [Balão Intra-Aórtico no Choque Cardiogênico: o Ensaio IABP-SHOCK II](/biblioteca/balao-intra-aortico-no-choque-cardiogenico-o-ensaio-iabp-shock-ii) e [Choque Cardiogênico na Síndrome Coronariana Aguda: CULPRIT-SHOCK e IABP-SHOCK II](/biblioteca/choque-cardiogenico-na-sindrome-coronariana-aguda-culprit-shock-e-iabp-shock-ii)); o escore de risco aqui descrito é uma ferramenta **prognóstica**, derivada da mesma população de estudo, mas que responde a uma pergunta diferente — "qual o risco deste paciente", não "o balão ajuda".
- **Distinção do Escore SAVE**: o SAVE prediz sobrevida **pré-canulação de ECMO-VA**, num subgrupo já definido como candidato a suporte mecânico avançado; o IABP-SHOCK II Risk Score se aplica de forma mais geral a qualquer paciente em choque cardiogênico pós-IAM, sem pressupor indicação prévia de um suporte específico.
- **Distinção da Classificação de Killip e do CADILLAC risk score**: Killip classifica gravidade clínica na fase aguda do infarto (uma de suas quatro classes já denota choque cardiogênico, sem quantificar risco numérico dentro do choque); o CADILLAC risk score é estritamente pós-angioplastia primária, com estratos 0-2/3-5/≥6 e c-estatística 0,79-0,83 para mortalidade em 30 dias/1 ano numa população geral pós-IAM com supra de ST (não restrita a choque). O IABP-SHOCK II Risk Score, em contraste, foi derivado e validado **especificamente dentro da população já em choque cardiogênico**.
- **Não aplicar os pontos por intuição** — sem a tabela de pesos por variável confirmada (ver seção acima), o cálculo manual do escore total não deve ser reconstruído a partir de fontes terciárias não conferidas nesta sessão.

## Síntese

| Item | Valor |
|---|---|
| Variáveis do modelo | 6 (idade > 73 anos, AVC prévio, glicemia admissão > 191 mg/dL, creatinina admissão > 1,5 mg/dL, fluxo TIMI < 3 pós-ICP, lactato arterial > 5 mmol/L) |
| Pontuação por variável | 1 ou 2 pontos cada (distribuição exata não confirmada no resumo — VERIFICAÇÃO HUMANA NECESSÁRIA) |
| Faixa de pontuação total | 0 a 9 |
| Categorias de risco | Baixo (0-2), intermediário (3-4), alto (5-9) |
| Mortalidade em 30 dias por categoria (derivação) | 23,8% / 49,2% / 76,6% |
| Mortalidade por categoria (validação externa, CardShock) | 28,0% / 42,9% / 77,3% |
| AUROC (derivação/registro) | 0,79 |
| AUROC (validação externa) | 0,73 |
| População de derivação | Choque cardiogênico pós-IAM, coorte do ensaio/registro IABP-SHOCK II |

## Tudo com Tudo

- [Balão Intra-Aórtico no Choque Cardiogênico: o Ensaio IABP-SHOCK II](/biblioteca/balao-intra-aortico-no-choque-cardiogenico-o-ensaio-iabp-shock-ii) — o ensaio cuja população deu origem a este escore de risco
- [Choque Cardiogênico na Síndrome Coronariana Aguda: CULPRIT-SHOCK e IABP-SHOCK II](/biblioteca/choque-cardiogenico-na-sindrome-coronariana-aguda-culprit-shock-e-iabp-shock-ii)
- [Classificação SCAI de Estágios do Choque Cardiogênico](/biblioteca/classificacao-scai-de-estagios-do-choque-cardiogenico)
- [Escore SAVE: Sobrevida Após ECMO Venoarterial no Choque Cardiogênico Refratário](/biblioteca/escore-save-sobrevida-apos-ecmo-venoarterial-no-choque-cardiogenico-refratario)
- [CADILLAC Risk Score: Predição de Mortalidade Após Angioplastia Primária no IAM](/biblioteca/cadillac-risk-score-predicao-de-mortalidade-apos-angioplastia-primaria-no-iam)
- [Classificação de Killip: Classe Funcional na Fase Aguda do Infarto](/biblioteca/classificacao-de-killip-classe-funcional-na-fase-aguda-do-infarto)
- [Clearance de Creatinina por Cockcroft-Gault: Ajuste de Dose de Cardioativos e DOAC](/biblioteca/clearance-de-creatinina-cockcroft-gault-ajuste-de-dose-em-cardiologia)
