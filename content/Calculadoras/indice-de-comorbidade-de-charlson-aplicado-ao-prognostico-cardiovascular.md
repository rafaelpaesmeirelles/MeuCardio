---
title: "Índice de Comorbidade de Charlson Aplicado ao Prognóstico Cardiovascular"
slug: indice-de-comorbidade-de-charlson-aplicado-ao-prognostico-cardiovascular
theme: "Calculadoras"
kind: calculadora
review_status: revisado
source_refs: ["Charlson ME, Pompei P, Ales KL, MacKenzie CR. A new method of classifying prognostic comorbidity in longitudinal studies: development and validation. J Chronic Dis. 1987;40(5):373-383. DOI: 10.1016/0021-9681(87)90171-8. PMID: 3558716 — ARTIGO ORIGINAL do índice. O resumo confirma as faixas de mortalidade por escore e a comparação com o sistema de Kaplan-Feinstein; a tabela completa de doenças e pesos foi confirmada por via secundária qualificada (ver referência de 2022, abaixo), não pelo texto completo deste artigo, que não foi acessado nesta sessão", "Charlson M, Szatrowski TP, Peterson J, Gold J. Validation of a combined comorbidity index. J Clin Epidemiol. 1994;47(11):1245-1251. DOI: 10.1016/0895-4356(94)90129-5. PMID: 7722560 — versão AJUSTADA POR IDADE do índice, lida no PubMed; traz os riscos relativos por unidade de comorbidade e por década de idade", "Sachdev M, Sun JL, Tsiatis AA, Nelson CL, Mark DB, Jollis JG. The prognostic importance of comorbidity for mortality in patients with stable coronary artery disease. J Am Coll Cardiol. 2004;43(4):576-582. DOI: 10.1016/j.jacc.2003.10.031. PMID: 14975466 — validação do índice de Charlson especificamente em doença coronariana estável, Duke Databank for Cardiovascular Diseases, 1.471 pacientes", "Charlson ME, Carrozzino D, Guidi J, Patierno C. Charlson Comorbidity Index: A Critical Review of Clinimetric Properties. Psychother Psychosom. 2022;91(1):8-35. DOI: 10.1159/000521288. PMID: 34991091 — revisão crítica com a própria Mary Charlson como primeira autora; Tabela 1 ('The CCI: the 19 item-version') reproduz literalmente as 19 condições e pesos do índice original, citando o artigo de 1987 como fonte. Texto completo obtido em PDF e lido com pdftotext -layout — é a fonte da tabela completa acrescentada nesta revisão", "Quan H, Sundararajan V, Halfon P, Fong A, Burnand B, Luthi JC, Saunders LD, Beck CA, Feasby TE, Ghali WA. Coding algorithms for defining comorbidities in ICD-9-CM and ICD-10 administrative data. Med Care. 2005;43(11):1130-1139. DOI: 10.1097/01.mrl.0000182534.19832.83. PMID: 16224307 — Tabela 1 do artigo (códigos CID-9-CM de Deyo e CID-10), lida em PDF, confirma a versão administrativa de 17 categorias que funde tumor sólido/leucemia/linfoma numa só", "Glasheen WP, Cordier T, Gumpina R, Haugh G, Davis J, Renda A. Charlson Comorbidity Index: ICD-9 Update and ICD-10 Translation. Am Health Drug Benefits. 2019;12(4):188-197. PMID: 31428236 — confirma que o instrumento original de 1987 tinha 19 categorias com pesos 1/2/3/6, e descreve a estrutura hierárquica (só a condição mais grave de cada par conta) e a fusão de Deyo das três categorias de câncer não metastático em 1992"]
legacy_source: "Documento novo, escrito em 01/08/2026. A pasta Calculadoras tinha escores de sangramento (HAS-BLED, CRUSADE, VTE-BLEED), de risco isquêmico (CHA2DS2-VASc, TIMI, GRACE, SYNTAX) e de insuficiência cardíaca (MAGGIC, Seattle Heart Failure Model, GWTG-HF), mas nenhum instrumento de COMORBIDADE GERAL — a pergunta de quanto a doença associada, e não só a doença cardíaca em si, pesa no prognóstico do paciente. É lacuna real: conferido por grep, nenhum documento da pasta nem do restante de content/ menciona Charlson."
---

# Índice de Comorbidade de Charlson Aplicado ao Prognóstico Cardiovascular

## O que preenche
Os escores desta pasta estimam risco a partir de variáveis da **doença cardíaca aguda** (GRACE,
TIMI), da **anatomia coronariana** (SYNTAX) ou da **insuficiência cardíaca em si** (MAGGIC, Seattle
Heart Failure Model). Nenhum deles responde a uma pergunta distinta e frequente: **o quanto a carga
de doenças associadas — não a cardiopatia índice — determina o prognóstico deste paciente
específico.** O Índice de Comorbidade de Charlson (**CCI**, *Charlson Comorbidity Index*) foi
desenhado exatamente para isso, e uma validação específica em doença arterial coronariana mostra
que ele compete de igual para igual com a fração de ejeção como preditor de sobrevida de longo
prazo.

## Origem do índice e o que o resumo confirma
Charlson ME et al., J Chronic Dis. 1987;40(5):373-383 (PMID 3558716). Um índice ponderado — que leva
em conta o **número e a gravidade** das doenças coexistentes — foi desenvolvido numa coorte de
**559 pacientes clínicos** e testado numa segunda coorte de **685 pacientes** com seguimento de
**10 anos**.

**Mortalidade em 1 ano por faixa de escore, na coorte de desenvolvimento:**

| Escore de Charlson | Mortalidade em 1 ano | N |
|---|---|---|
| **0** | **12%** | 181 |
| **1-2** | **26%** | 225 |
| **3-4** | **52%** | 71 |
| **≥ 5** | **85%** | 82 |

**Na coorte de validação (10 anos de seguimento), percentual de pacientes que morreram por doença
comórbida, por escore:**

| Escore | Óbito por doença comórbida | N |
|---|---|---|
| **0** | **8%** | 588 |
| **1** | **25%** | 54 |
| **2** | **48%** | 25 |
| **≥ 3** | **59%** | 18 |

Cada nível a mais do índice associou-se a aumento **em degrau** da mortalidade cumulativa atribuível
à comorbidade (log-rank χ² = 165; p < 0,0001). Na coorte de seguimento mais longo, a **idade também
foi preditor independente** de mortalidade (p < 0,001). Os próprios autores relatam que o novo
índice teve desempenho **semelhante** a um sistema anterior de Kaplan e Feinstein.

## Tabela completa: as 19 condições e seus pesos
O resumo do PubMed do artigo de 1987 confirma as faixas de escore e a mortalidade correspondente
(tabelas acima), mas não lista as 19 condições nem o peso individual de cada uma — isso está só no
texto completo do artigo de 1987, que é anterior ao PMC e não foi acessado nesta sessão. A tabela
abaixo fecha essa lacuna por uma via diferente e verificável: é a reprodução literal da **Tabela 1
("The CCI: the 19 item-version")** de um artigo de revisão crítica que tem a própria **Mary Charlson
como primeira autora** — Charlson ME, Carrozzino D, Guidi J, Patierno C. *Charlson Comorbidity Index:
A Critical Review of Clinimetric Properties.* Psychother Psychosom. 2022;91(1):8-35. DOI:
10.1159/000521288. PMID: 34991091 — que cita o artigo de 1987 (PMID 3558716) como referência [14]
exatamente para essa tabela. O texto completo em PDF foi obtido e a tabela lida diretamente
(`pdftotext -layout`), não de memória nem de fonte secundária não verificável.

| Condição | Peso |
|---|---|
| Infarto do miocárdio (MI) | **1** |
| Insuficiência cardíaca congestiva (CHF) | **1** |
| Doença arterial periférica | **1** |
| Doença cerebrovascular | **1** |
| Demência | **1** |
| Doença pulmonar crônica | **1** |
| Doença do tecido conjuntivo | **1** |
| Úlcera péptica | **1** |
| Doença hepática leve | **1** |
| Diabetes (sem lesão de órgão-alvo) | **1** |
| Hemiplegia | **2** |
| Doença renal moderada ou grave | **2** |
| Diabetes com lesão de órgão-alvo | **2** |
| Tumor sólido sem metástase | **2** |
| Leucemia | **2** |
| Linfoma | **2** |
| Doença hepática moderada ou grave | **3** |
| Tumor sólido metastático | **6** |
| AIDS | **6** |

**Pontuação:** soma simples dos pesos das condições presentes no paciente — sem a idade, o teto
teórico é 33 pontos, com as 19 condições simultaneamente presentes. A hierarquia é implícita ao
desenho do instrumento: entre duas formas de gravidade da mesma condição, só a mais grave conta —
por exemplo, doença hepática leve (1) e moderada/grave (3) não se somam, vale só a mais grave
presente; o mesmo vale para diabetes sem/com lesão de órgão-alvo (Glasheen WP, Cordier T, Gumpina R,
et al. *Charlson Comorbidity Index: ICD-9 Update and ICD-10 Translation.* Am Health Drug Benefits.
2019;12(4):188-197. PMID: 31428236 — descreve essa estrutura hierárquica citando o artigo de 1987).

> ⚠️ **Duas versões em circulação — não confundir ao contar condições.** A versão **original de 1987**
> (acima, 19 itens) trata "tumor sólido sem metástase", "leucemia" e "linfoma" como três categorias
> separadas, cada uma com peso 2. A adaptação para bases administrativas por código CID — Deyo RA et
> al. 1992 (ICD-9-CM), depois traduzida para CID-10 por Quan H et al., *Coding algorithms for defining
> comorbidities in ICD-9-CM and ICD-10 administrative data.* Med Care. 2005;43(11):1130-1139. DOI:
> 10.1097/01.mrl.0000182534.19832.83. PMID: 16224307 (Tabela 1 do artigo, conferida diretamente em
> PDF) — **funde essas três categorias em uma só** ("qualquer malignidade, incluindo linfoma e
> leucemia", peso 2), reduzindo a lista operacional a **17 categorias**, mesmo peso total possível.
> É a versão usada por quem calcula o índice a partir de banco de dados administrativo/CID em vez de
> avaliação clínica direta — as duas contam o mesmo peso quando o paciente tem só uma daquelas três
> condições, e diferem apenas no caso raro de mais de uma estar presente ao mesmo tempo.

## Versão ajustada por idade
Charlson M et al., J Clin Epidemiol. 1994;47(11):1245-1251 (PMID 7722560). Estudo em **226
pacientes** com hipertensão ou diabetes submetidos a cirurgia eletiva entre 1982 e 1985 (218
sobreviveram até a alta), seguidos por **pelo menos 5 anos** de pós-operatório.

**Resultado central:**
- **Risco relativo de óbito estimado por ponto do índice de comorbidade: 1,4**
- **Risco relativo de óbito estimado por década de idade: 1,4**
- **Quando idade e comorbidade foram modeladas como escore combinado (idade + comorbidade), o
  risco relativo estimado por unidade do escore combinado: 1,45**

Ou seja, **um ponto a mais no índice de comorbidade equivale, em risco relativo, a uma década a mais
de idade** — é essa equivalência que justifica somar idade ao escore de Charlson na versão
"idade-ajustada" (frequentemente citada como CCI + pontos de idade em faixas de 10 anos a partir dos
50), e é o motivo de calculadoras de terceiros oferecerem as duas versões, com e sem idade.

> ⚠️ Mesma ressalva: o resumo confirma os **coeficientes de risco relativo** acima, mas não detalha a
> tabela de pontos por década de idade que costuma acompanhar a versão combinada. **Conferir o texto
> completo antes de aplicar a versão idade-ajustada com pontos específicos por faixa etária.**

## Validação específica em doença arterial coronariana estável
Sachdev M et al., J Am Coll Cardiol. 2004;43(4):576-582 (PMID 14975466), Duke Clinical Research
Institute. Coorte de **1.471 pacientes com DAC** que fizeram cateterismo cardíaco entre 1985 e 1989,
acompanhados até 2000 no **Duke Databank for Cardiovascular Diseases**.

**O que o estudo fez e encontrou, conforme o resumo:**
- Pesos foram atribuídos a doenças individuais conforme sua significância prognóstica em modelos de
  Cox, criando um **índice específico para DAC**, comparado depois ao índice de Charlson já
  estabelecido
- **O índice de Charlson e o índice específico de DAC estiveram fortemente associados à sobrevida de
  longo prazo, e o desempenho foi quase equivalente ao da fração de ejeção do ventrículo esquerdo**
  — é a comparação que dá peso clínico ao uso do Charlson em cardiologia, não só em medicina geral
- Entre os componentes do índice de Charlson, **diabetes, insuficiência renal, DPOC e doença
  arterial periférica tiveram maior significância prognóstica** nesta população com DAC, enquanto
  **úlcera péptica, doença do tecido conjuntivo e linfoma tiveram significância menor**
- **Hemiplegia, leucemia, linfoma, doença hepática grave e AIDS foram raramente identificados** entre
  pacientes submetidos a cateterismo coronariano — ou seja, condições que pesam muito no índice
  original contribuem pouco na prática, simplesmente por serem incomuns nesse tipo de paciente

**Conclusão dos autores:** a doença comórbida está fortemente associada à sobrevida de longo prazo em
pacientes com DAC, e deveria ser medida e considerada em ensaios clínicos, registros de doença,
comparações de qualidade assistencial e no aconselhamento de pacientes individuais.

## Como ler os três estudos juntos
| Estudo | O que estabelece |
|---|---|
| **Charlson 1987** (PMID 3558716) | O índice original e a relação escore → mortalidade em população clínica geral |
| **Charlson 1994** (PMID 7722560) | Que 1 ponto de comorbidade ≈ 1 década de idade em risco relativo — base da versão idade-ajustada |
| **Sachdev 2004** (PMID 14975466) | Que, especificamente em DAC, o índice tem poder prognóstico próximo ao da fração de ejeção — e quais componentes realmente pesam nessa população |

O uso em cardiologia não é extrapolação sem lastro: é um índice **desenvolvido em medicina geral e
depois validado especificamente** em uma grande coorte de doença coronariana, com comparação direta
contra um marcador cardiológico consagrado (FEVE).

## Onde entra na prática
- **Seleção de estratégia em doença coronariana estável** — quando a expectativa de vida limitada
  por comorbidade pesa mais na decisão do que a anatomia coronariana isolada, o mesmo raciocínio que
  fundamenta o uso do RCRI/NSQIP-MICA antes de cirurgia não cardíaca (ver
  `escores-de-risco-cardiaco-para-cirurgia-nao-cardiaca-rcri-e-nsqip-mica.md`, nesta pasta) — aqui o
  recorte é a carga de doença crônica, não o risco perioperatório de um procedimento específico
- **Estratificação de registros e ensaios clínicos** — é o próprio argumento dos autores de 2004:
  comparar desfechos entre serviços ou braços de estudo sem ajustar por comorbidade produz
  comparação enviesada
- **Conversa de expectativa com o paciente**, junto de — nunca no lugar de — dados específicos da
  cardiopatia (FEVE, escore anatômico, biomarcador)

## Armadilhas clínicas
- **Tratar o índice de Charlson como substituto de escore cardíaco específico** — os estudos mostram
  desempenho **comparável** à FEVE em DAC estável, não superioridade nem substituição em outros
  cenários (síndrome coronariana aguda, insuficiência cardíaca aguda têm escores próprios nesta
  pasta)
- **Confundir a versão original de 19 condições com a versão administrativa de 17** — ver a tabela e
  a ressalva acima; a diferença está inteiramente em como "tumor sólido sem metástase", "leucemia" e
  "linfoma" são contadas (três categorias de peso 2 na versão de 1987, ou uma só na versão CID de
  Deyo/Quan), e só importa na prática quando o paciente tem mais de uma dessas três ao mesmo tempo
- **Somar peso de duas gravidades da mesma condição** — a estrutura é hierárquica: entre doença
  hepática leve e moderada/grave, ou entre diabetes com e sem lesão de órgão-alvo, conta-se **só a
  mais grave presente**, nunca as duas somadas
- **Somar idade ao escore sem usar a versão validada** — o RR de 1,4 por década de idade e 1,4 por
  ponto de comorbidade (Charlson 1994) só foi demonstrado no desenho de escore combinado do próprio
  estudo; somar arbitrariamente pontos de idade de outra fonte não tem o mesmo lastro
- **Presumir que todo componente pesa igual em qualquer população** — em pacientes com DAC
  cateterizados, diabetes/insuficiência renal/DPOC/doença arterial periférica dominam o prognóstico
  mais do que úlcera péptica ou doença do tecido conjuntivo, segundo a validação de Sachdev; a
  composição por doença do paciente à frente importa, não só o número final
- **Ignorar que condições raras na prática cardiológica** (hemiplegia, leucemia, linfoma, doença
  hepática grave, AIDS) **têm peso alto no índice original mas baixa prevalência** na população que
  chega ao cateterismo — o escore pode ficar dominado por poucas condições muito comuns (diabetes,
  DRC) mais do que pelas de maior peso nominal
