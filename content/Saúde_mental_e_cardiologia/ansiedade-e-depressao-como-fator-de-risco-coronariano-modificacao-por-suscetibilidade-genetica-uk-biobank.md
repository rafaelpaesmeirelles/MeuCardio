---
title: "Ansiedade e Depressão como Fator de Risco Coronariano: Suscetibilidade Genética Explica a Associação? (UK Biobank, Nakada 2025)"
slug: ansiedade-e-depressao-como-fator-de-risco-coronariano-modificacao-por-suscetibilidade-genetica-uk-biobank
theme: "Saúde mental e cardiologia"
kind: estudo
review_status: pendente_revisao
source_refs: ["Nakada S, Ward J, Strawbridge RJ, Welsh P, Celis-Morales C, Ho FK, Pell JP. Anxiety disorder, depression and coronary artery disease: associations and modification by genetic susceptibility. BMC Med. 2025;23(1):73. DOI: 10.1186/s12916-025-03915-4. PMID: 39915848. PMCID: PMC11804096 — coorte prospectiva UK Biobank, 288.031 participantes elegíveis, seguimento mediano de 13,4-13,6 anos"]
legacy_source: "Documento novo, escrito em 09/09/2026. A pasta já documenta ansiedade crônica como fator de risco coronariano (metanálise de Roest 2010, busca até 2009, sem qualquer teste de suscetibilidade genética), depressão pós-infarto (Van Melle/ENRICHD) e depressão como fator de risco para insuficiência cardíaca incidente (metanálise de 2,6 milhões), mas nenhum documento perguntava se a associação entre transtornos mentais e doença coronariana é explicada por risco genético compartilhado, nem comparava ansiedade isolada, depressão isolada e a combinação das duas dentro do mesmo desenho. Esta coorte do UK Biobank (Nakada et al., BMC Medicine, fevereiro de 2025) fecha essa lacuna com escore de risco poligênico (PRS_CAD) e teste formal de interação — pergunta distinta, mecanística, ainda ausente na base."
---

# Ansiedade e Depressão como Fator de Risco Coronariano: Suscetibilidade Genética Explica a Associação?

## A pergunta que este documento responde
A pasta já registra que ansiedade crônica (Roest et al., 2010) e depressão pós-infarto (Van Melle, ENRICHD) se associam a risco cardiovascular. Nenhum documento até agora perguntou **por quê**: será que quem tem ansiedade ou depressão simplesmente carrega, por acaso, mais variantes genéticas de risco para doença coronariana — e é isso que explica a associação observada, não um efeito causal do sofrimento psíquico em si? E o que acontece quando ansiedade e depressão coexistem no mesmo paciente? Nakada et al. testaram exatamente isso, com escore de risco poligênico (PRS) para doença arterial coronariana (DAC) e teste formal de interação estatística.

## O estudo
Nakada S et al., BMC Medicine, 2025;23(1):73 (PMID 39915848; PMCID PMC11804096; DOI 10.1186/s12916-025-03915-4). Coorte prospectiva usando dados do **UK Biobank**, recrutamento entre 2007 e 2010 em 22 centros de avaliação na Inglaterra, Escócia e País de Gales.

**Seleção da amostra**: dos mais de 500.000 participantes recrutados no UK Biobank, **288.031 foram elegíveis** após excluir 164.957 por etnia autorreferida diferente de branca, 25.224 por doença cardiovascular prévia à linha de base, 23.290 por diagnóstico de ansiedade ou depressão surgido **após** a linha de base (para reduzir causalidade reversa), e 628 por dados sociodemográficos incompletos. A restrição a participantes de etnia branca foi deliberada, pois o escore de risco poligênico usado (derivado do consórcio CARDIoGRAMplus4C) foi construído predominantemente em populações de ascendência europeia.

- **Exposição**: diagnóstico de transtorno de ansiedade e/ou depressão **antes** da linha de base, identificado por dados de internação hospitalar vinculados (CID-10)
- **Desfecho**: DAC incidente (CID-10 I20–I25), identificada por internação hospitalar ou certidão de óbito após a linha de base
- **PRS_CAD**: escore de risco poligênico para DAC, derivado do CARDIoGRAMplus4C, categorizado em tercis (baixo, intermediário, alto)
- Modelos de Cox ajustados por idade, sexo, escolaridade e índice de privação de área (Townsend); modelos adicionais ajustados por PRS_CAD, array de genotipagem e 10 componentes principais de ancestralidade

## Quem tinha o quê, e o que aconteceu com eles
- **779 participantes (0,3%) com transtorno de ansiedade**; **1.788 (0,6%) com depressão**; **557 (0,2%) com ansiedade isolada**; **1.566 (0,5%) com depressão isolada** — a diferença aritmética indica cerca de 222 participantes com as duas condições concomitantes
- Entre quem tinha ansiedade: **112 (14,5%) desenvolveram DAC**, contra **21.212 (7,4%)** entre quem não tinha — seguimento mediano de **13,4 anos** (com ansiedade) e **13,6 anos** (sem)
- Entre quem tinha depressão: **238 (13,4%) desenvolveram DAC**, contra **21.086 (7,4%)** entre quem não tinha

## Achados principais
- **Transtorno de ansiedade**: **HR 2,31 (IC95% 1,92-2,78)** para DAC incidente, ajustado por confundidores sociodemográficos
- **Depressão**: **HR 2,15 (IC95% 1,90-2,24)** para DAC incidente, no mesmo ajuste — intervalo de confiança relatado exatamente assim no artigo original, chamativamente estreito; não há explicação adicional no resumo consultado, e o valor não deve ser arredondado nem "corrigido" sem checagem do artigo completo (`VERIFICAÇÃO HUMANA NECESSÁRIA` para quem for citar esse IC especificamente)
- **Interação aditiva entre depressão e PRS_CAD**: **RERI 0,97 (IC95% 0,12-1,81)** — a associação entre depressão e DAC foi **mais forte entre quem tinha PRS_CAD alto**. **Não houve evidência equivalente de interação para transtorno de ansiedade**
- Mesmo entre participantes com **PRS_CAD baixo** (ou seja, baixo risco genético de base), a associação com DAC incidente persistiu:
  - **Ansiedade isolada**: HR 1,68 (IC95% 1,16-2,44)
  - **Depressão isolada**: HR 2,13 (IC95% 1,72-2,64)
  - **Ansiedade e depressão concomitantes**: **HR 3,85 (IC95% 2,48-5,98)** — a maior magnitude de risco entre todas as categorias testadas
- Ajuste adicional por potenciais mediadores (tabagismo, IMC, minutos-MET de atividade física, qualidade da dieta, hipertensão, LDL-colesterol, hiperglicemia e proteína C-reativa) **atenuou** todas essas associações em todas as categorias de PRS_CAD, mas **elas permaneceram significativas** — padrão consistente com mediação parcial, não com confusão total
- Análise de sensibilidade excluindo participantes com condição de saúde mental grave prevalente **manteve resultados consistentes**
- Os autores citam que a única interação semelhante testada antes (depressão x PRS_CAD, coorte finlandesa de 19.999 participantes) **não encontrou evidência de interação** — atribuída pelos próprios autores, no artigo aqui resumido, a possível falta de poder estatístico pelo tamanho amostral menor

## Conclusão literal dos autores
**"A suscetibilidade genética à DAC pode contribuir parcialmente para o agrupamento entre depressão e DAC, mas não fornece uma explicação completa, nem explica a associação entre transtorno de ansiedade e DAC. Portanto, outros mecanismos devem ser explorados."**

## Síntese prática
Este estudo responde de forma direta a uma pergunta que o paciente ansioso ou deprimido às vezes faz nos próprios termos: "isso é genético, ou é o sofrimento que está me fazendo mal?" A resposta, pelos dados desta coorte, é **as duas coisas, em proporções diferentes**. Para depressão, existe uma interação real com risco genético — quem já carrega risco poligênico alto para DAC parece ser adicionalmente penalizado pela depressão. Para ansiedade, esse mecanismo genético-específico **não aparece**: o risco associado à ansiedade é praticamente igual em qualquer estrato de PRS_CAD, sugerindo que a via causal (se houver) não passa pela mesma arquitetura genética compartilhada testada aqui. O achado clinicamente mais robusto é o das duas condições concomitantes: mesmo em quem tem risco genético baixo, ansiedade e depressão juntas associam-se ao maior risco relativo do estudo inteiro (HR 3,85) — reforço para que o rastreamento de saúde mental em cardiologia (já coberto pelo fluxograma ESC 2025 desta pasta) não trate ansiedade e depressão como intercambiáveis nem avalie apenas uma das duas isoladamente.

## Limitações, declaradas com honestidade
- **Prevalência muito baixa na amostra** (0,3% ansiedade, 0,6% depressão) frente à prevalência esperada na população geral — os próprios autores atribuem isso à ascertainment por dados de internação hospitalar, que capta preferencialmente os casos mais graves e deixa de fora quadros leves a moderados manejados em atenção primária
- **Restrição a participantes de etnia branca** — necessária pela validade do PRS_CAD nessa ancestralidade, mas limita a generalização direta para outras populações, incluindo a população brasileira miscigenada
- **Viés do "voluntário saudável" do UK Biobank** — participantes tendem a ser mais saudáveis que a população geral, o que pode subestimar as associações reais
- **Desenho observacional**: não é possível estabelecer causalidade a partir de dados de coorte, mesmo com ajuste extenso e teste de mediadores
- **Confusão residual** por variáveis não medidas permanece possível, como em qualquer estudo observacional
- **Não foi avaliada remissão de ansiedade ou depressão ao longo do seguimento** — o estudo classifica pela presença de diagnóstico antes da linha de base, sem capturar se o quadro persistiu, piorou ou remitiu depois

## Armadilhas clínicas
- Tratar o HR de depressão (2,15) como comparável em precisão estatística ao de ansiedade (2,31) sem notar que o intervalo de confiança relatado para depressão é incomumente estreito no resumo consultado — checar o artigo completo antes de citar esse número especificamente em material voltado a outro médico
- Concluir que "ansiedade não tem componente genético compartilhado com DAC" — o estudo mostra apenas que a interação com **este PRS_CAD específico** não foi demonstrada; não exclui outros mecanismos genéticos não testados aqui
- Extrapolar os achados por PRS para pacientes de ascendência não europeia — a amostra foi deliberadamente restrita a participantes brancos, e o próprio PRS_CAD tem validade reduzida fora dessa ancestralidade
- Ler o HR 3,85 (ansiedade e depressão concomitantes, PRS baixo) como se fosse o risco "typical" do estudo — é o extremo superior, dentro de um subgrupo mais raro (concomitância das duas condições, ~222 participantes)
- Confundir este documento com o de Roest 2010 já existente na pasta — ali é metanálise de estudos até 2009 sem qualquer avaliação genética; aqui é uma única coorte de 2025 cujo valor agregado está exatamente no teste de suscetibilidade genética e na comparação direta com depressão isolada e concomitante

## Conteúdo CorVIA conectado
- [Ansiedade Crônica como Fator de Risco Coronariano Independente: a Metanálise de Roest](/biblioteca/ansiedade-cronica-como-fator-de-risco-coronariano-metanalise-de-roest)
- [Depressão Pós-Infarto como Fator de Risco Cardiovascular: Van Melle e ENRICHD](/biblioteca/depressao-pos-infarto-como-fator-de-risco-cardiovascular-van-melle-e-enrichd)
- [Depressão como Fator de Risco para Insuficiência Cardíaca Incidente: Metanálise de 2,6 Milhões](/biblioteca/depressao-como-fator-de-risco-para-insuficiencia-cardiaca-incidente-metanalise-de-2-6-milhoes)
- [Ansiedade e Risco de Fibrilação Atrial: Framingham e Metanálise de Wu](/biblioteca/ansiedade-e-risco-de-fibrilacao-atrial-framingham-e-metanalise-de-wu)
- [Fator Psicossocial como Risco de Infarto: o Estudo INTERHEART](/biblioteca/fator-psicossocial-como-risco-de-infarto-o-estudo-interheart)
- [Fluxograma: Rastreamento de Saúde Mental, Cuidado Escalonado (ESC 2025)](/biblioteca/fluxograma-rastreamento-saude-mental-cuidado-escalonado-esc-2025)
- [Saúde Mental e Doença Cardiovascular: Consenso Clínico ESC 2025](/biblioteca/saude-mental-e-doenca-cardiovascular-consenso-clinico-esc-2025)
