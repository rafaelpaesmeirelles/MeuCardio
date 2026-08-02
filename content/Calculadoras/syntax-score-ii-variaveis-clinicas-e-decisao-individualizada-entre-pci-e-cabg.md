---
title: "SYNTAX Score II: Variáveis Clínicas e Decisão Individualizada entre PCI e CABG"
slug: syntax-score-ii-variaveis-clinicas-e-decisao-individualizada-entre-pci-e-cabg
theme: "Calculadoras"
kind: calculadora
review_status: revisado
source_refs: ["Farooq V, van Klaveren D, Steyerberg EW, et al. Anatomical and clinical characteristics to guide decision making between coronary artery bypass surgery and percutaneous coronary intervention for individual patients: development and validation of SYNTAX score II. Lancet. 2013;381(9867):639-650. DOI: 10.1016/S0140-6736(13)60108-7. PMID: 23439103", "Sotomi Y, Cavalcante R, van Klaveren D, et al. Individual Long-Term Mortality Prediction Following Either Coronary Stenting or Bypass Surgery in Patients With Multivessel and/or Unprotected Left Main Disease: An External Validation of the SYNTAX Score II Model in the 1,480 Patients of the BEST and PRECOMBAT Randomized Controlled Trials. JACC Cardiovasc Interv. 2016;9(15):1564-1572. DOI: 10.1016/j.jcin.2016.04.023. PMID: 27491605", "Takahashi K, Serruys PW, Fuster V, Farkouh ME, Spertus JA, Cohen DJ, et al. Redevelopment and validation of the SYNTAX score II to individualise decision making between percutaneous and surgical revascularisation in patients with complex coronary artery disease: secondary analysis of the multicentre randomised controlled SYNTAXES trial with external cohort validation. Lancet. 2020;396(10260):1399-1412. DOI: 10.1016/S0140-6736(20)32114-0. PMID: 33038944 — resumo consultado via PubMed/Europe PMC nesta sessão: confirma metodologia (índice prognóstico clínico por regressão de Cox combinado, em segundo estágio, com o tratamento designado e dois modificadores de efeito pré-especificados — tipo de doença e escore SYNTAX anatômico), coortes de validação cruzada (ensaio SYNTAX, n=1800) e externa (FREEDOM+BEST+PRECOMBAT, n=3380), desfechos (mortalidade em 5 e 10 anos, MACE composto em 5 anos) e c-index de cada validação. O resumo NÃO enumera nominalmente as sete variáveis clínicas do modelo — texto completo pago na Lancet, não acessado nesta sessão", "Ninomiya K, Serruys PW, Garg S, et al. The Utility of the SYNTAX Score II and SYNTAX Score 2020 for Identifying Patients with Three-Vessel Disease Eligible for Percutaneous Coronary Intervention in the Multivessel TALENT Trial: A Prospective Pilot Experience. Rev Cardiovasc Med. 2022;23(4):133. DOI: 10.31083/j.rcm2304133. PMID: 39076220. PMCID: PMC11273643 (acesso aberto) — fonte SECUNDÁRIA, usada especificamente para a lista nominal das sete variáveis clínicas do SYNTAX Score II 2020, citando explicitamente Takahashi et al. 2020 (referência [6] do próprio artigo) como origem dessa lista. Texto verbatim conferido no HTML integral do PMC, não só em resumo de IA"]
legacy_source: "Documento novo, complementar ao já existente sobre o SYNTAX score anatômico original (syntax-score-complexidade-anatomica-e-escolha-entre-pci-e-cabg.md) — este documento cobre especificamente o SYNTAX Score II, versão que incorpora variáveis clínicas ao escore anatômico."
---

# SYNTAX Score II: Variáveis Clínicas e Decisão Individualizada entre PCI e CABG

## Diferença em relação ao SYNTAX score original

O [SYNTAX score original](./syntax-score-complexidade-anatomica-e-escolha-entre-pci-e-cabg.md) é **puramente anatômico**: mede só a complexidade da doença coronariana pela angiografia (número de lesões, localização, bifurcação, oclusão total crônica, calcificação, trombo), sem nenhuma variável clínica do paciente. Dois pacientes com a mesma anatomia recebem o mesmo escore, mesmo que um tenha 45 anos e função ventricular normal e o outro 80 anos, doença renal crônica e disfunção ventricular grave.

O **SYNTAX Score II**, derivado e validado por Farooq V et al., Lancet 2013;381(9867):639-650 (PMID 23439103), nasceu exatamente para corrigir essa limitação: combina o escore anatômico original com **variáveis clínicas** que também pesam na mortalidade e no risco comparativo de cada estratégia de revascularização. O objetivo declarado dos autores é permitir uma **decisão individualizada** entre cirurgia de revascularização miocárdica (CABG) e intervenção coronária percutânea (PCI) — não mais só "quão complexa é a anatomia", mas "qual estratégia tem menor mortalidade prevista para este paciente específico".

## As oito variáveis do modelo

O modelo final do SYNTAX Score II, obtido por regressão de Cox aplicada à coorte do próprio ensaio SYNTAX (1.800 pacientes com doença trivascular e/ou de tronco de coronária esquerda, randomizados para CABG ou PCI), inclui **oito preditores**:

1. **Escore SYNTAX anatômico** (o escore original, como variável contínua)
2. **Idade**
3. **Clearance de creatinina** (função renal)
4. **Fração de ejeção do ventrículo esquerdo (FEVE)**
5. **Presença de doença de tronco de coronária esquerda desprotegido**
6. **Sexo feminino**
7. **DPOC** (doença pulmonar obstrutiva crônica)
8. **Doença arterial periférica**

**Achado notável do próprio artigo**: diabetes foi testado como candidato e **não entrou no modelo final** — a interação entre diabetes e a escolha de estratégia (CABG vs. PCI) não foi estatisticamente significativa (p de interação = 0,67). Ou seja, diabetes não ajudou a diferenciar qual das duas estratégias é preferível para o paciente, mesmo sendo fator de risco cardiovascular reconhecido em outros contextos.

## Como o escore é usado na prática — estimativa comparativa, não um corte único

Ao contrário do SYNTAX score original, que usa **tercis fixos** (≤22, 23-32, ≥33) para orientar a decisão, o SYNTAX Score II **não funciona por um valor de corte único**. Ele gera, para cada paciente, **duas estimativas separadas de mortalidade em 4 anos** — uma assumindo que o paciente seria tratado com CABG, outra assumindo PCI — e a estratégia com a **menor mortalidade prevista** é a indicada como preferível para aquele paciente específico.

Essa comparação depende de como as variáveis clínicas se combinam com a anatomia: o próprio artigo descreve que, para obter mortalidade equivalente entre CABG e PCI, pacientes mais jovens, mulheres e pacientes com FEVE reduzida precisam de um escore anatômico **mais baixo** (ou seja, toleram menos complexidade anatômica antes de a balança pender para CABG), enquanto pacientes mais idosos, com doença de tronco desprotegido ou com DPOC toleram um escore anatômico **mais alto** antes de a cirurgia se tornar claramente preferível.

Na prática, essa comparação **não é calculada à mão**: o modelo é implementado como um **nomograma** e como calculadora on-line (disponível em `syntaxscore.org`, mantida pelo grupo que desenvolveu o escore), porque a combinação das oito variáveis num escore de Cox não tem fórmula fechada simples de se reproduzir manualmente à beira do leito.

## Desempenho preditivo — ganho de discriminação sobre o escore anatômico puro

O artigo de derivação (Farooq V et al., 2013) reporta o **índice de concordância (c-index)** como medida de quão bem o modelo discrimina risco de mortalidade, comparando o SYNTAX Score II ao SYNTAX anatômico original:

| Validação | SYNTAX anatômico (original) | SYNTAX Score II |
|---|---|---|
| Interna (coorte do ensaio SYNTAX) | c-index 0,567 | c-index **0,725** |
| Externa (registro DELTA) | c-index 0,612 | c-index **0,716** |

O ganho de discriminação é substancial nas duas validações — o escore anatômico puro tem desempenho discriminativo apenas discretamente acima do acaso (0,567/0,612), enquanto o SYNTAX Score II se aproxima da faixa considerada de boa discriminação (~0,72-0,73).

## Validação externa independente

Além da validação no registro DELTA já incluída no artigo original, o modelo foi testado de forma **independente**, por outro grupo, em uma coorte fora da derivação: Sotomi Y et al., JACC Cardiovasc Interv. 2016;9(15):1564-1572 (PMID 27491605), validação externa do SYNTAX Score II em **1.480 pacientes** dos ensaios **BEST** e **PRECOMBAT** (600 com doença de tronco de coronária esquerda desprotegido, 880 com doença multiarterial):

- Mortalidade global por todas as causas: **6,1%** em seguimento mediano de 4,9 anos
- c-index na população total: **0,685**
- c-index por subgrupo: doença de tronco desprotegido — PCI 0,718 vs. CABG 0,662; doença multiarterial — PCI 0,700 vs. CABG 0,661
- Calibração: satisfatória de forma geral, com tendência a **superestimar** a mortalidade nos estratos de risco mais alto
- Relevância clínica direta: mortalidade foi **maior** quando o tratamento efetivamente realizado **divergiu** da recomendação do modelo, e **semelhante** quando a conduta coincidiu com a recomendação — achado que sustenta a utilidade prática do escore na decisão, e não só o desempenho estatístico isolado.

## A versão redesenhada: SYNTAX Score II 2020

Existe uma versão redesenhada e mais recente do modelo, o **SYNTAX Score II 2020** (Takahashi K et al., Lancet 2020;396(10260):1399-1412, PMID 33038944). Ela foi derivada não da coorte original do ensaio SYNTAX, mas do **seguimento de 10 anos** desse mesmo ensaio — o estudo de extensão **SYNTAXES** —, e validada externamente na população combinada de três outros ensaios randomizados, **FREEDOM, BEST e PRECOMBAT** (n=3.380).

**O que está confirmado diretamente no resumo do artigo original** (consultado nesta sessão via PubMed/Europe PMC):

- **Desfechos diferentes e mais longos que o modelo de 2013**: em vez de mortalidade em 4 anos, o SYNTAX Score II 2020 prevê **mortalidade por todas as causas em 10 anos** e um **composto de eventos cardiovasculares maiores em 5 anos** (morte por qualquer causa, AVC não fatal ou infarto do miocárdio não fatal).
- **Estrutura em dois estágios**: um índice prognóstico clínico obtido por regressão de Cox para prever óbito em 10 anos é combinado, num segundo estágio, com o tratamento designado (PCI ou CABG) e com **dois modificadores de efeito pré-especificados** — o tipo de doença (trivascular vs. tronco de coronária esquerda) e o escore SYNTAX anatômico.
- **Desempenho (c-index)**:

| Validação | Desfecho | PCI | CABG |
|---|---|---|---|
| Cruzada, coorte do ensaio SYNTAX (n=1.800) | Mortalidade em 10 anos | 0,73 (IC95% 0,69-0,76) | 0,73 (IC95% 0,69-0,76) |
| Cruzada, coorte do ensaio SYNTAX (n=1.800) | MACE em 5 anos | 0,65 (IC95% 0,61-0,69) | 0,71 (IC95% 0,67-0,75) |
| Externa, FREEDOM + BEST + PRECOMBAT (n=3.380) | MACE em 5 anos | 0,67 (IC95% 0,63-0,70) | 0,62 (IC95% 0,58-0,66) |

A calibração na validação externa foi descrita como boa para o desfecho de MACE em 5 anos, e o benefício estimado de CABG sobre PCI variou substancialmente entre os pacientes da população estudada.

**O que está confirmado por fonte secundária, não pelo resumo do artigo original** (o texto completo é pago na Lancet e não foi acessado nesta sessão): a lista nominal das variáveis clínicas. Segundo Ninomiya K, Serruys PW, Garg S, et al., Rev Cardiovasc Med. 2022;23(4):133 (PMID 39076220, PMCID PMC11273643, acesso aberto, texto conferido verbatim) — artigo que cita Takahashi et al. 2020 explicitamente como fonte dessa lista —, o SYNTAX Score II 2020 usa **sete fatores prognósticos clínicos**: idade, diabetes mellitus tratado clinicamente (com ou sem insulina), DPOC, doença arterial periférica, tabagismo atual, clearance de creatinina e FEVE.

Duas diferenças notáveis em relação às oito variáveis do modelo de 2013 (seção acima), ambas conforme a mesma fonte secundária:
- **Diabetes passa a entrar no modelo.** No SYNTAX Score II original (Farooq et al. 2013), diabetes foi testado e explicitamente **não** entrou por falta de interação significativa com a escolha de estratégia (p=0,67, já citado acima). Na versão de 2020, diabetes tratado clinicamente aparece como um dos sete fatores clínicos.
- **Sexo feminino não aparece** na lista de fatores clínicos do modelo de 2020 na fonte consultada, ao contrário do modelo de 2013, que o inclui.

**O que este documento não encontrou fonte para afirmar**: se o SYNTAX Score II 2020 formalmente substitui o modelo de 2013 nas diretrizes de revascularização vigentes, ou se os dois convivem como ferramentas com horizontes de previsão diferentes. A calculadora historicamente mais citada (`syntaxscore.org`) e a maior parte da literatura de validação anterior a 2020 referem-se ao modelo original. Quem for adotar clinicamente a versão 2020 deve confirmar qual delas a calculadora ou o nomograma em uso efetivamente implementa, e — nos pontos específicos assinalados acima como fonte secundária — considerar conferir a lista de variáveis contra o texto completo do artigo original antes de uso crítico.

## Limitações reconhecidas

- **Não tem fórmula fechada simples.** A regressão de Cox com oito variáveis e seus termos de interação não se reduz a uma soma de pontos como o SYNTAX anatômico original — o cálculo depende de nomograma ou calculadora eletrônica dedicada (`syntaxscore.org`), o que dificulta o uso rápido à beira do leito sem acesso à ferramenta.
- **Superestimação de risco no extremo mais grave**, observada na validação externa de Sotomi Y et al. — a calibração é menos confiável exatamente na faixa de maior risco, que costuma ser a mais decisiva para a escolha da estratégia.
- **A população de derivação e das validações citadas neste documento é de doença trivascular e/ou de tronco de coronária esquerda**, o mesmo recorte do ensaio SYNTAX original — extrapolar para doença coronariana menos complexa (uni ou biarterial) não é diretamente sustentado pelas fontes aqui citadas.
- **Existe uma versão redesenhada e mais recente, o SYNTAX Score II 2020** (Takahashi K et al., Lancet 2020;396(10260):1399-1412, PMID 33038944) — ver a seção "A versão redesenhada: SYNTAX Score II 2020" acima, com desfechos, coortes, c-index e variáveis clínicas detalhados e suas fontes. A relação de substituição (ou não) do modelo 2013 pelo de 2020 nas diretrizes vigentes não foi confirmada nesta sessão — quem for adotar a versão 2020 na prática deve conferir qual modelo a ferramenta/calculadora em uso efetivamente implementa.

## Armadilhas clínicas

- Confundir o SYNTAX Score II com o SYNTAX score anatômico original e aplicar os tercis (≤22/23-32/≥33) como se valessem para o Score II — os dois têm lógica de uso diferente: um é corte por faixa, o outro é comparação de mortalidade prevista entre estratégias.
- Tentar calcular o SYNTAX Score II "de cabeça" ou por aproximação — o modelo não tem fórmula de soma simples; usar a calculadora/nomograma oficial é necessário para o resultado ser confiável.
- Tratar diabetes como fator que pesa na escolha entre CABG e PCI dentro deste modelo especificamente — o próprio artigo de derivação mostra que diabetes não teve interação significativa com a escolha de estratégia (p=0,67), ao contrário do que a intuição clínica geral sobre diabetes e doença coronariana poderia sugerir.
- Usar a mortalidade prevista pelo modelo como valor absoluto e definitivo para aquele paciente, sem considerar a limitação de calibração conhecida (superestimação em risco mais alto) e sem envolver a decisão compartilhada da Heart Team — o escore é ferramenta de apoio à decisão, não substituto dela.
- Aplicar o SYNTAX Score II fora da população em que foi derivado e validado (doença trivascular e/ou de tronco de coronária esquerda) como se o desempenho estivesse comprovado igualmente para doença coronariana menos extensa.
