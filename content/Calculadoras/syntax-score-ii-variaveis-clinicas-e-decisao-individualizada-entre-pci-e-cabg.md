---
title: "SYNTAX Score II: Variáveis Clínicas e Decisão Individualizada entre PCI e CABG"
slug: syntax-score-ii-variaveis-clinicas-e-decisao-individualizada-entre-pci-e-cabg
theme: "Calculadoras"
kind: calculadora
review_status: revisado
source_refs: ["Farooq V, van Klaveren D, Steyerberg EW, et al. Anatomical and clinical characteristics to guide decision making between coronary artery bypass surgery and percutaneous coronary intervention for individual patients: development and validation of SYNTAX score II. Lancet. 2013;381(9867):639-650. DOI: 10.1016/S0140-6736(13)60108-7. PMID: 23439103", "Sotomi Y, Cavalcante R, van Klaveren D, et al. Individual Long-Term Mortality Prediction Following Either Coronary Stenting or Bypass Surgery in Patients With Multivessel and/or Unprotected Left Main Disease: An External Validation of the SYNTAX Score II Model in the 1,480 Patients of the BEST and PRECOMBAT Randomized Controlled Trials. JACC Cardiovasc Interv. 2016;9(15):1564-1572. DOI: 10.1016/j.jcin.2016.04.023. PMID: 27491605", "Takahashi K, Serruys PW, Fuster V, et al. Redevelopment and validation of the SYNTAX score II to individualise decision making between percutaneous and surgical revascularisation in patients with complex coronary artery disease: secondary analysis of the multicentre randomised controlled SYNTAXES trial with external cohort validation. Lancet. 2020;396(10260):1399-1412. PMID: 33038944 — citado apenas para registrar a existência da versão atualizada de 2020, não detalhado neste documento; variáveis exatas do modelo 2020 não confirmadas em profundidade nesta sessão, VERIFICAÇÃO HUMANA NECESSÁRIA para quem for adotar essa versão"]
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

## Limitações reconhecidas

- **Não tem fórmula fechada simples.** A regressão de Cox com oito variáveis e seus termos de interação não se reduz a uma soma de pontos como o SYNTAX anatômico original — o cálculo depende de nomograma ou calculadora eletrônica dedicada (`syntaxscore.org`), o que dificulta o uso rápido à beira do leito sem acesso à ferramenta.
- **Superestimação de risco no extremo mais grave**, observada na validação externa de Sotomi Y et al. — a calibração é menos confiável exatamente na faixa de maior risco, que costuma ser a mais decisiva para a escolha da estratégia.
- **A população de derivação e das validações citadas neste documento é de doença trivascular e/ou de tronco de coronária esquerda**, o mesmo recorte do ensaio SYNTAX original — extrapolar para doença coronariana menos complexa (uni ou biarterial) não é diretamente sustentado pelas fontes aqui citadas.
- **Existe uma versão redesenhada e mais recente, o SYNTAX Score II 2020** (Takahashi K et al., Lancet 2020;396(10260):1399-1412, PMID 33038944), derivada também a partir de FREEDOM, BEST e PRECOMBAT além do SYNTAX trial, que passa a prever mortalidade em 10 anos e um composto de eventos cardiovasculares maiores em 5 anos, e não apenas mortalidade em 4 anos. Este documento não detalha o modelo 2020 — as variáveis exatas dele e sua relação de substituição (ou não) do modelo 2013 não foram confirmadas em profundidade nesta sessão de pesquisa. `VERIFICAÇÃO HUMANA NECESSÁRIA` para quem for adotar especificamente a versão 2020 na prática.

## Armadilhas clínicas

- Confundir o SYNTAX Score II com o SYNTAX score anatômico original e aplicar os tercis (≤22/23-32/≥33) como se valessem para o Score II — os dois têm lógica de uso diferente: um é corte por faixa, o outro é comparação de mortalidade prevista entre estratégias.
- Tentar calcular o SYNTAX Score II "de cabeça" ou por aproximação — o modelo não tem fórmula de soma simples; usar a calculadora/nomograma oficial é necessário para o resultado ser confiável.
- Tratar diabetes como fator que pesa na escolha entre CABG e PCI dentro deste modelo especificamente — o próprio artigo de derivação mostra que diabetes não teve interação significativa com a escolha de estratégia (p=0,67), ao contrário do que a intuição clínica geral sobre diabetes e doença coronariana poderia sugerir.
- Usar a mortalidade prevista pelo modelo como valor absoluto e definitivo para aquele paciente, sem considerar a limitação de calibração conhecida (superestimação em risco mais alto) e sem envolver a decisão compartilhada da Heart Team — o escore é ferramenta de apoio à decisão, não substituto dela.
- Aplicar o SYNTAX Score II fora da população em que foi derivado e validado (doença trivascular e/ou de tronco de coronária esquerda) como se o desempenho estivesse comprovado igualmente para doença coronariana menos extensa.
