---
title: "CADILLAC Risk Score: Predição de Mortalidade Após Angioplastia Primária no Infarto Agudo do Miocárdio"
slug: cadillac-risk-score-predicao-de-mortalidade-apos-angioplastia-primaria-no-iam
theme: "Calculadoras"
kind: calculadora
review_status: revisado
published: false
review_note: "Revisão clínica individual em 2026-09-08: derivação/validação original (PMID 15862409) e validação externa contemporânea (PMID 34772341/PMCID PMC8588705) conferidas; cortes operacionais, limites de generalização e uso estritamente prognóstico explicitados."
source_refs: ["Halkin A, Singh M, Nikolsky E, Grines CL, Tcheng JE, Garcia E, Cox DA, Turco M, Stuckey TD, Na Y, Lansky AJ, Gersh BJ, O'Neill WW, Mehran R, Stone GW. Prediction of mortality after primary percutaneous coronary intervention for acute myocardial infarction: the CADILLAC risk score. J Am Coll Cardiol. 2005;45(9):1397-1405. DOI: 10.1016/j.jacc.2005.01.041. PMID: 15862409.", "Wilson RS, Malamas P, Dembo B, Lall SK, Zaman N, Peterson BR. The CADILLAC risk score accurately identifies patients at low risk for in-hospital mortality and adverse cardiovascular events following ST elevation myocardial infarction. BMC Cardiovasc Disord. 2021;21(1):533. DOI: 10.1186/s12872-021-02348-0. PMID: 34772341. PMCID: PMC8588705 — validação contemporânea retrospectiva em 341 pacientes com STEMI tratados por PCI primária."]
legacy_source: "Documento novo, escrito em 09/09/2026. A pasta Calculadoras já cobria escores de risco cirúrgico (EuroSCORE II, STS Risk Score), o escore anatômico de complexidade coronariana (SYNTAX e SYNTAX Score II, para decisão entre PCI e CABG) e os escores de síndrome coronariana aguda aplicados na apresentação/triagem (TIMI, GRACE 2.0, HEART) — mas nenhum documento cobria um escore que prediz mortalidade especificamente DEPOIS de realizada a angioplastia primária no IAM, incorporando o resultado angiográfico pós-procedimento (fluxo TIMI) e a função ventricular basal. Essa é uma pergunta distinta: não é 'qual a probabilidade de complicação antes de decidir a estratégia' (GRACE/TIMI/HEART) nem 'CABG ou PCI é melhor para esta anatomia' (SYNTAX), é 'este paciente, já submetido à angioplastia primária, tem que prognóstico de curto e longo prazo'. Checagem de colisão feita em content/**/*.md, não só nos JSONs: a pasta Doença_coronariana já tem documentos sobre o ENSAIO CADILLAC (Stone GW, NEJM 2002, PMID 11919304 — stent vs. PTCA ± abciximabe) e sobre ADMIRAL/EPILOG (outros ensaios de abciximab na ICP) — nenhum deles trata do escore de risco derivado posteriormente a partir da coorte CADILLAC, que é o objeto deste documento; são complementares, não duplicados, e o ensaio original foi linkado na seção Tudo com Tudo. Verificado via PubMed E-utilities nesta sessão (esearch + efetch de texto puro do abstract, PMID confirmado diretamente)."
---

# CADILLAC Risk Score: Predição de Mortalidade Após Angioplastia Primária no Infarto Agudo do Miocárdio

## O que é e a lacuna que preenche

O **CADILLAC risk score** foi desenvolvido para responder a uma pergunta que os escores de risco de síndrome coronariana aguda já cobertos nesta pasta (TIMI, GRACE 2.0, HEART) não respondem: qual o prognóstico de um paciente **depois** de submetido à **angioplastia primária (PCI primária)** para infarto agudo do miocárdio (IAM) — quando já se sabe, inclusive, o resultado angiográfico do próprio procedimento.

Halkin A et al., *J Am Coll Cardiol*. 2005;45(9):1397-1405 (PMID 15862409), descrevem explicitamente, no objetivo do artigo, que escores de risco anteriores após terapia de reperfusão incorporavam variáveis clínicas e/ou angiográficas, mas **não consideravam a função ventricular esquerda basal**, e que estudos prévios **não haviam sido validados contra bases de dados ou estudos independentes**. O CADILLAC risk score nasceu para corrigir as duas lacunas ao mesmo tempo.

## Desenho: derivação e validação

Direto do abstract (PMID 15862409):
- **Coorte de derivação**: ensaio **CADILLAC** (*Controlled Abciximab and Device Investigation to Lower Late Angioplasty Complications*) — **2.082 pacientes**
- **Coorte de validação**: ensaio **Stent-PAMI** (*Stent-Primary Angioplasty in Myocardial Infarction*) — **900 pacientes**
- **Método**: regressão logística e o procedimento *jackknife* para selecionar correlatos independentes de **mortalidade em 1 ano**, que foram então ponderados e integrados num sistema de pontuação inteira (escore de pontos)
- Ambas as coortes vieram de **ensaios clínicos randomizados multicêntricos de PCI primária no IAM**. O escore, porém, resulta de uma análise prognóstica pós-hoc dessas bases; sua derivação e validação não constituem um ensaio randomizado do uso do escore

## As sete variáveis e a pontuação

O modelo de Halkin et al. (PMID 15862409) selecionou sete variáveis do modelo multivariado inicial e as ponderou conforme sua associação com mortalidade em 1 ano. Os cortes operacionais são reproduzidos conforme a literatura primária de derivação/validação:

| Variável | Pontos |
|---|---|
| Idade > 65 anos | 2 |
| Classe de Killip 2/3 | 3 |
| Fração de ejeção do ventrículo esquerdo basal < 40% | 4 |
| Anemia: hematócrito <39% em homens ou <36% em mulheres | 2 |
| Insuficiência renal: clearance de creatinina estimado <60 mL/min | 3 |
| Doença trivascular | 2 |
| Fluxo TIMI final 0–2 | 2 |

**Escore total**: soma direta dos pontos (máximo aritmético de 18, calculado a partir da soma dos sete itens acima — o abstract não enuncia esse total explicitamente, é resultado direto da soma).

**Achado destacado pelos próprios autores**: entre as sete variáveis, a **fração de ejeção do ventrículo esquerdo basal é o preditor isolado mais forte de sobrevida** — é também a variável com maior peso (4 pontos) e a que os autores citam nominalmente na conclusão como devendo ser incorporada a modelos de risco após reperfusão.

Os cortes operacionais acima constam da literatura primária de derivação/validação. O cálculo exige os dados originais do paciente; valores ausentes, unidades incompatíveis ou outra definição laboratorial não devem ser completados por aproximação. Para o cálculo do clearance, consulte também [Clearance de Creatinina (Cockcroft-Gault)](/biblioteca/clearance-de-creatinina-cockcroft-gault-ajuste-de-dose-em-cardiologia), lembrando que o documento de apoio não substitui a definição do próprio escore.

## Estratificação de risco e desempenho (c-estatística)

Três estratos de risco, citados literalmente do abstract:
- **Baixo risco**: 0 a 2 pontos
- **Risco intermediário**: 3 a 5 pontos
- **Alto risco**: ≥ 6 pontos

Discriminação (c-estatística), reportada separadamente para a coorte de derivação (CADILLAC) e de validação (Stent-PAMI):

| Desfecho | Derivação (CADILLAC, n=2.082) | Validação (Stent-PAMI, n=900) |
|---|---|---|
| Mortalidade em 30 dias | 0,83 | 0,81 |
| Mortalidade em 1 ano | 0,79 | 0,78 |

Os autores classificam essa performance como "excelente acurácia prognóstica para sobrevida" nos dois conjuntos.

**O que este documento NÃO confirma**: o abstract não traz as taxas de mortalidade absoluta (percentual) observadas em cada um dos três estratos de risco (baixo/intermediário/alto), nem em 30 dias nem em 1 ano — só a discriminação (c-estatística) do modelo como um todo. Reproduzir essas taxas a partir de uma calculadora online ou de uma tabela de terceiros não conferida contra o texto completo repetiria o erro que este projeto já identificou e corrigiu antes no documento de GRACE 2.0 desta pasta. Quem precisar da mortalidade absoluta por estrato deve confirmar contra o texto completo do artigo original (PMID 15862409), não contra este resumo.

## Validação externa posterior

Há estudos posteriores que aplicaram o CADILLAC em outras coortes. Em uma análise retrospectiva contemporânea de **341 pacientes com STEMI tratados por PCI primária** em um único centro entre 2014 e 2018 (Wilson et al., 2021; PMID 34772341), o escore foi comparado a TIMI, GRACE e classe de Killip. A coorte excluiu pacientes com parada cardíaca, choque cardiogênico ou necessidade de suporte mecânico, e avaliou desfechos diferentes dos da derivação; portanto, não reproduz integralmente a população nem as estimativas originais. Ela confirma que o CADILLAC já foi avaliado externamente, mas não elimina a necessidade de calibração local nem autoriza transportar as c-estatísticas de 2005 para qualquer serviço atual.

## O que muda na prática

- O CADILLAC risk score responde a uma pergunta pós-procedimento: dado que a PCI primária já foi feita e o resultado angiográfico já é conhecido (fluxo TIMI final), qual o risco de morte em 30 dias e em 1 ano deste paciente específico.
- Isso o distingue de TIMI, GRACE 2.0 e HEART — escores de risco aplicados na apresentação, sem incorporar o resultado do próprio procedimento — e do SYNTAX/SYNTAX Score II, que respondem a uma pergunta de **escolha de estratégia de revascularização** (PCI vs. CABG), não de prognóstico pós-PCI primária no IAM.
- Classe de Killip 2/3 e fração de ejeção <40% aumentam a pontuação, mas o total é um marcador prognóstico. Ele **não indica, isoladamente, UTI, suporte mecânico, nova revascularização ou alta**, nem prediz especificamente choque refratário.
- O escore usa a **classificação de Killip** como uma de suas sete variáveis de entrada — ver o documento dedicado, [Classificação de Killip](/biblioteca/classificacao-de-killip-classe-funcional-na-fase-aguda-do-infarto), para a definição completa das quatro classes.

## Armadilhas clínicas

- **Confundir com GRACE 2.0 ou TIMI** — estes avaliam risco na apresentação da síndrome coronariana aguda; o CADILLAC risk score pressupõe que a PCI primária **já foi realizada**, incluindo o fluxo TIMI pós-procedimento como variável de entrada. Não são intercambiáveis nem medem o mesmo momento da doença.
- **Confundir com SYNTAX/SYNTAX Score II** — aqueles orientam a escolha entre PCI e CABG por complexidade anatômica (mais aplicável a doença estável ou multiarterial fora do contexto de PCI primária de emergência); o CADILLAC risk score não participa dessa decisão, é estritamente prognóstico após a PCI primária já ter sido feita.
- **Tratar o escore total (máximo aritmético 18) como validado enquanto tal pelo artigo** — o valor máximo é resultado de soma simples dos pontos listados no abstract, não um número que os autores enunciam explicitamente; os estratos de risco (0-2/3-5/≥6) sim são citados literalmente.
- **Buscar as taxas de mortalidade absolutas por estrato de risco em calculadora de terceiros e tratá-las como confirmadas** — este documento não confirma essas taxas (ver seção acima); só a discriminação (c-estatística) foi confirmada diretamente do abstract.
- **Aplicar definições locais diferentes às variáveis** — anemia usa hematócrito <39% em homens ou <36% em mulheres, e insuficiência renal usa clearance estimado <60 mL/min; substituir esses critérios por outros altera o escore validado.

## Tudo com Tudo

- [CADILLAC: stent no IAM; o composto não é morte](/biblioteca/cadillac-stent-versus-angioplastia-com-ou-sem-abciximabe-no-iam) — o ensaio original (Stone GW, NEJM 2002, PMID 11919304) cuja coorte de 2.082 pacientes é a mesma usada para derivar este escore
- [Classificação de Killip: Classe Funcional na Fase Aguda do Infarto](/biblioteca/classificacao-de-killip-classe-funcional-na-fase-aguda-do-infarto)
- [GRACE 2.0 (Global Registry of Acute Coronary Events)](/biblioteca/grace-20-global-registry-of-acute-coronary-events)
- [TIMI Risk Score](/biblioteca/timi-risk-score)
- [Clearance de Creatinina (Cockcroft-Gault): Ajuste de Dose em Cardiologia](/biblioteca/clearance-de-creatinina-cockcroft-gault-ajuste-de-dose-em-cardiologia)
- [SYNTAX Score II: Variáveis Clínicas e Decisão Individualizada entre PCI e CABG](/biblioteca/syntax-score-ii-variaveis-clinicas-e-decisao-individualizada-entre-pci-e-cabg)
- [Escore SAVE: Sobrevida Após ECMO Venoarterial no Choque Cardiogênico Refratário](/biblioteca/escore-save-sobrevida-apos-ecmo-venoarterial-no-choque-cardiogenico-refratario)
