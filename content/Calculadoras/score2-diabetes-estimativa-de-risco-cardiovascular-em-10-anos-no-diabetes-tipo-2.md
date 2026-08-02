---
title: "SCORE2-Diabetes: Estimativa de Risco Cardiovascular em 10 Anos no Diabetes Tipo 2"
slug: score2-diabetes-estimativa-de-risco-cardiovascular-em-10-anos-no-diabetes-tipo-2
theme: "Calculadoras"
kind: calculadora
review_status: revisado
source_refs: ["Pennells L, Kaptoge S, Østergaard HB, Read SH, Carinci F, Franzosi MG, et al.; SCORE2-Diabetes Working Group and the ESC Cardiovascular Risk Collaboration. SCORE2-Diabetes: 10-year cardiovascular risk estimation in type 2 diabetes in Europe. Eur Heart J. 2023;44(28):2544-2556. DOI: 10.1093/eurheartj/ehad260. PMID: 37247330. Texto integral conferido no PMC (PMC10361012), incluindo a Tabela 2 de hazard ratios de sub-distribuição", "Marx N, Federici M, Schütt K, Müller-Wieland D, Ajjan RA, Antunes MJ, et al. 2023 ESC Guidelines for the management of cardiovascular disease in patients with diabetes. Eur Heart J. 2023;44(39):4043-4140. DOI: 10.1093/eurheartj/ehad192. PMID: 37622663 — categorias de risco clínico citadas via resumo oficial ACC ('Ten Points to Remember'), texto integral do PDF da diretriz não localizado em acesso aberto nesta sessão", "SCORE2 working group and ESC Cardiovascular Risk Collaboration. SCORE2 risk prediction algorithms: new models to estimate 10-year risk of cardiovascular disease in Europe. Eur Heart J. 2021;42(25):2439-2454. DOI: 10.1093/eurheartj/ehab309. PMID: 34120177 — modelo-base do qual o SCORE2-Diabetes deriva"]
legacy_source: "Documento novo, escrito em 02/08/2026. A pasta Calculadoras já tem SCORE2/SCORE2-OP (mecânica geral e aplicabilidade no Brasil) e Pooled Cohort Equations/PREVENT, mas nenhum documento dedicado ao SCORE2-Diabetes como calculadora — só uma menção resumida dentro do protocolo geral 'doenca-cardiovascular-em-pacientes-com-diabetes-estratificacao-de-risco-e-manejo-esc-2023.md' (tema Diabetes e cardiologia), baseada em resumo secundário (ACC Ten Points / ESC Congress News). Este documento vai à fonte primária (Pennells et al. 2023) e traz a tabela de coeficientes, os exemplos numéricos originais e as limitações declaradas pelos próprios autores — não repete o protocolo geral de manejo, que trata de metas de HbA1c, LDL e escolha de fármaco."
---

# SCORE2-Diabetes: Estimativa de Risco Cardiovascular em 10 Anos no Diabetes Tipo 2

## Por que existe um SCORE2 separado para diabetes

A ESC não recomenda o SCORE2 comum (documento `score2-e-score2-op.md`, nesta mesma pasta) para pessoas com diabetes — o próprio artigo do SCORE2-Diabetes registra isso explicitamente: *"embora o SCORE2 tenha sido desenvolvido em todos os indivíduos sem DCV prévia, incluindo aqueles com e sem diabetes, a ESC não recomenda o SCORE2 para uso em pessoas com diabetes"*. O motivo é que diabetes tipo 2 não é um fator de risco homogêneo: o próprio risco varia várias vezes entre um paciente recém-diagnosticado com HbA1c controlada e função renal normal e outro diagnosticado há décadas com HbA1c elevada e TFG reduzida — variação que o SCORE2 comum, ao tratar "diabetes" como uma única variável binária dentro do modelo geral (ou ao excluir diabéticos e classificá-los à parte), não capta.

O **SCORE2-Diabetes** (Pennells L, Kaptoge S, Østergaard HB et al.; SCORE2-Diabetes Working Group and the ESC Cardiovascular Risk Collaboration, *Eur Heart J*. 2023;44(28):2544-2556, **PMID 37247330**, PMC10361012) foi construído estendendo os modelos do SCORE2, usando dados de participantes individuais de **quatro grandes bases** — **229.460 participantes com diabetes tipo 2 e sem DCV prévia (43.706 eventos)** — somando fatores de risco convencionais aos **especificamente relacionados ao diabetes**: idade ao diagnóstico, HbA1c e taxa de filtração glomerular estimada (TFGe) por creatinina.

## Variáveis de entrada

Citadas literalmente da fonte, em dois grupos:

**Variáveis "SCORE2" (herdadas do modelo geral):**
- Idade
- Sexo
- Tabagismo atual
- Pressão arterial sistólica (mmHg)
- Colesterol total (mmol/L)
- Colesterol HDL (mmol/L)
- História de diabetes mellitus (tipo 2)

**Variáveis específicas do diabetes, acrescentadas neste modelo:**
- Idade ao diagnóstico do diabetes (anos)
- HbA1c (mmol/mol, unidade IFCC — não a unidade percentual do NGSP usada nos EUA e no Brasil; a conversão é necessária antes de aplicar o modelo)
- TFGe (mL/min/1,73 m², calculada pela equação CKD-EPI 2009 na derivação do modelo; os autores testaram e confirmaram equivalência de resultado usando a equação CKD-EPI 2021)

## Como o número é calculado — coeficientes da fonte primária

O modelo é um **regressão de risco competitivo específica por sexo** (modelos de Fine e Gray, que tratam a morte por causa não cardiovascular como risco competitivo, evitando superestimar o risco de DCV em quem tem maior chance de morrer de outra causa antes). Os coeficientes de SCORE2 (idade, tabagismo, PAS, colesterol total, HDL, história de diabetes) foram **fixados nos mesmos valores do SCORE2 original** e usados como *offset*; sobre eles foram estimados coeficientes adicionais que modificam o efeito de cada variável **especificamente em quem tem diabetes**, mais os coeficientes das três variáveis novas. Todas as variáveis contínuas têm **termo de interação com idade** (o efeito de cada fator de risco declina com o avanço da idade, achado já conhecido de estudos anteriores) e o TFGe entra com um **termo quadrático**, para captar a relação não linear entre função renal e risco.

A Tabela 2 do artigo mostra os **hazard ratios de sub-distribuição (SHR)** já combinando o efeito original do SCORE2 com o ajuste específico do diabetes — valores prontos para uso, não coeficientes brutos de regressão:

| Variável | Efeito principal — Homens | Termo de interação com idade — Homens | Efeito principal — Mulheres | Termo de interação com idade — Mulheres |
|---|---|---|---|---|
| Idade (por 5 anos) | 1,71 (1,66–1,76) | — | 1,94 (1,88–2,00) | — |
| Tabagismo atual | 1,61 (1,53–1,70) | 0,94 (0,91–0,96) | 1,85 (1,73–1,98) | 0,89 (0,87–0,92) |
| PA sistólica (por 20 mmHg) | 1,14 (1,11–1,17) | 0,97 (0,96–0,99) | 1,15 (1,12–1,19) | 0,98 (0,97–1,00) |
| Colesterol total (por 1 mmol/L) | 1,12 (1,10–1,14) | 0,98 (0,97–0,99) | 1,12 (1,09–1,15) | 0,98 (0,97–0,99) |
| Colesterol HDL (por 0,5 mmol/L) | 0,90 (0,86–0,93) | 1,01 (0,99–1,03) | 0,85 (0,82–0,89) | 1,02 (1,00–1,04) |
| História de diabetes | 1,91 (1,81–2,01) | 0,91 (0,88–0,93) | 2,25 (2,11–2,40) | 0,88 (0,85–0,91) |
| Idade ao diagnóstico (por 5 anos) | 0,90 (0,89–0,91) | — | 0,89 (0,88–0,90) | — |
| HbA1c (por 1 DP) | 1,10 (1,09–1,11) | 0,99 (0,98–0,99) | 1,12 (1,11–1,14) | 0,98 (0,98–0,98) |
| ln(TFGe) (por 1 DP) | 0,94 (0,93–0,96) | 1,01 (1,01–1,01) | 0,94 (0,92–0,95) | 1,02 (1,01–1,02) |
| ln(TFGe)² (termo quadrático) | 1,01 (1,00–1,01) | — | 1,01 (1,00–1,01) | — |

Valores entre parênteses são intervalo de confiança de 95%. Variáveis contínuas foram centradas na idade de 60 anos, PAS 120 mmHg, colesterol total 6 mmol/L, HDL 1,3 mmol/L, idade ao diagnóstico 50 anos, HbA1c 31 mmol/mol e TFGe 90 mL/min/1,73m² (ln-TFGe de 4,5). Um desvio-padrão de HbA1c equivale a 9,34 mmol/mol; um desvio-padrão de ln(TFGe) equivale a 0,15. A sobrevida basal mediana em 10 anos nas coortes de derivação foi **0,9625 para homens e 0,9795 para mulheres** — os valores a partir dos quais o risco absoluto é calculado depois de combinar os hazard ratios.

Os modelos foram então **recalibrados por região de risco cardiovascular europeia** (mesma metodologia e mesmas quatro regiões do SCORE2/SCORE2-OP, ver `score2-e-score2-op.md`), usando fatores de recalibração idênticos aos já derivados para o SCORE2.

## Exemplo numérico da própria fonte, usado aqui como verificação

O artigo fornece dois conjuntos de exemplos ilustrativos, um no resumo (arredondado) e outro no corpo do texto (com uma casa decimal) — os dois batem entre si, o que serve como conferência cruzada antes de aceitar os números:

**Na região de risco moderado**, homem de 60 anos, não fumante, com fatores de risco convencionais médios (PAS 140 mmHg, colesterol total 5,5 mmol/L, HDL 1,3 mmol/L):
- HbA1c 50 mmol/mol, TFGe 90 mL/min/1,73m², diagnóstico de diabetes aos 60 anos → **risco de DCV em 10 anos de 11,0%**
- HbA1c 70 mmol/mol, TFGe 60 mL/min/1,73m², diagnóstico de diabetes aos 50 anos → **risco de 17,2%**, mesma idade atual e mesmos fatores convencionais — só as três variáveis específicas do diabetes mudaram, e o risco quase se distribui em 6 pontos percentuais.

Para uma mulher com as mesmas características: **7,9%** e **12,7%**, respectivamente.

**Comparando regiões de risco** (mesmo homem/mulher com o perfil desfavorável de HbA1c 70, TFGe 60, diagnóstico aos 50 anos): **12,9% (homem) e 9,8% (mulher) na região de baixo risco, contra 31,2% (homem) e 34,0% (mulher) na região de risco muito alto** — citado literalmente da fonte. Vale notar, como achado curioso e não um erro de transcrição: na região de risco muito alto o risco estimado da mulher **ultrapassa** o do homem (34,0% vs. 31,2%), invertendo a relação observada na região moderada — consequência da recalibração regional combinada com os termos de interação por sexo e idade do próprio modelo, não uma inconsistência do documento.

## Desempenho medido — discriminação e comparação com o SCORE2 comum

- **C-index nas bases de derivação**: 0,704 (IC95% 0,701–0,706) na SCID (Escócia), 0,733 (0,727–0,739) na CPRD (Inglaterra) e 0,666 (0,653–0,678) na ERFC/UK Biobank.
- **Validação externa** (217.036 indivíduos adicionais, 38.602 eventos): C-index de 0,670 (0,667–0,673) na SNDR (registro sueco de diabetes, 168.585 indivíduos) e 0,658 (0,648–0,669) na SIDIAP (coorte catalã, 21.698 indivíduos); 0,661 (0,622–0,699) em Malta e 0,688 (0,672–0,705) na Croácia (bases EUBIROD).
- **Ganho sobre o SCORE2 comum aplicado ao mesmo paciente diabético**: aumento de C-index de **0,009 a 0,031** conforme a base, com melhora estatisticamente significativa em todas — a maior melhora nas bases de derivação (SCID, CPRD, ERFC/UK Biobank: 0,021 a 0,026) e menor nas de validação externa (SNDR, SIDIAP: 0,009).
- **Reclassificação de risco**: NRI contínuo de 25,2 (22,4–28,0) na CPRD e 28,7 (27,7–29,8) na SNDR ao trocar SCORE2 por SCORE2-Diabetes; NRI categórico (usando as faixas <5%, 5–10%, 10–15%, 15–20% e >25%) de 24,6 (22,5–26,8) na CPRD e 13,7 (12,9–14,5) na SNDR, com **44,8% e 31,9%** dos casos reclassificados de forma apropriada, respectivamente.
- O ganho de discriminação trazido pelas três variáveis específicas do diabetes foi **maior** do que o ganho trazido por colesterol total e HDL no mesmo modelo — achado que a fonte usa para justificar a inclusão dessas variáveis, não uma comparação decorativa.
- Comparado ao **escore ADVANCE** (outro modelo específico para diabetes, recomendado pela diretriz ESC 2021 de prevenção cardiovascular), o SCORE2-Diabetes mostrou discriminação **discretamente superior**, nos dados disponíveis para essa comparação.

## Calibração por região de risco

O SCORE2-Diabetes usa as mesmas **quatro regiões de risco cardiovascular europeias** do SCORE2/SCORE2-OP (baixo, moderado, alto e muito alto — definidas por taxa de mortalidade cardiovascular ajustada por idade da OMS; a lista de países por região está no documento `score2-e-score2-op.md`, não repetida aqui). Ao simular a distribuição de risco em populações de 40-79 anos de cada região, a proporção de indivíduos com risco estimado acima de 10% variou de **61% na região de baixo risco a 96% na de risco muito alto**, em homens (51% a 94% em mulheres) — a fonte usa esse achado para argumentar que ignorar a recalibração regional distorceria de forma relevante a distribuição de risco numa população de diabéticos.

## Categorias de risco para decisão clínica

O artigo de derivação do SCORE2-Diabetes **não define, ele mesmo, faixas de decisão clínica** — as faixas usadas na validação estatística (NRI categórico) são um recorte metodológico (<5%, 5–10%, 10–15%, 15–20%, >25%), não uma recomendação de conduta. As categorias que orientam a decisão terapêutica vêm da diretriz de manejo — **2023 ESC Guidelines for the management of cardiovascular disease in patients with diabetes** (Marx N et al., *Eur Heart J*. 2023;44(39):4043-4140, **PMID 37622663**) — cujo texto integral não foi localizado em acesso aberto nesta sessão; as categorias abaixo estão conferidas pelo resumo oficial da diretriz publicado pelo American College of Cardiology ("Ten Points to Remember"), já usado como fonte no documento `doenca-cardiovascular-em-pacientes-com-diabetes-estratificacao-de-risco-e-manejo-esc-2023.md` (tema Diabetes e cardiologia), com o qual este registro é consistente:

- **Baixo risco: <5%**
- **Risco moderado: 5% a <10%**
- **Risco alto: 10% a <20%**
- **Risco muito alto: ≥20%**, ou doença cardiovascular aterosclerótica já estabelecida, ou lesão grave de órgão-alvo (definida pela diretriz por TFGe reduzida, albuminúria ou doença microvascular em três ou mais sítios)

**Atenção**: essas faixas são **percentuais fixos, independentes da idade** — diferente do SCORE2/SCORE2-OP comum, cujas faixas de baixo/alto/muito alto risco mudam conforme a faixa etária (<50, 50–69, ≥70 anos, ver `score2-e-score2-op.md`). Aplicar as faixas etárias do SCORE2 comum ao resultado do SCORE2-Diabetes classificaria o paciente de forma incorreta.

## População-alvo e quando não usar

- **Alvo**: adultos com **diabetes tipo 2**, sem doença cardiovascular estabelecida — a mesma população de uso do SCORE2 comum (prevenção primária), mas com diabetes.
- **Excluídos por desenho**: pacientes com infarto, AVC, angioplastia ou outra DCV aterosclerótica prévios — classificados automaticamente como risco muito alto pela diretriz de manejo, sem necessidade de calcular o escore.
- **Não validado para diabetes tipo 1**: o modelo foi derivado exclusivamente em participantes com diabetes tipo 2; a fonte não testa nem estende a ferramenta para diabetes tipo 1.
- **Faixa etária da derivação**: participantes com mais de 40 anos nas bases de derivação; a fonte não relata desempenho específico em diabéticos mais jovens.

## Limitações declaradas pelos autores

- O desfecho do modelo **não inclui insuficiência cardíaca nem doença arterial periférica não fatal** — informação não registrada de forma uniforme nas bases usadas. Os próprios autores alertam que, por isso, a estimativa de risco pode ser **conservadora** e subestimar o benefício potencial de tratamentos que também reduzem risco de IC (como iSGLT2 e agonistas de GLP-1).
- O modelo **não incorpora** história familiar de DCV, status socioeconômico, etnia nem albuminúria — variáveis que a diretriz de manejo pede que sejam consideradas separadamente, por julgamento clínico, especialmente em quem tem história familiar de DCV prematura, grupos étnicos/socioeconômicos de maior risco, ou idade acima de 70 anos (onde multimorbidade e expectativa de vida pesam mais na decisão).
- **A recalibração para regiões de alto e muito alto risco foi extrapolada** a partir de dados de populações de risco baixo e moderado — os autores reconhecem explicitamente essa limitação, por ausência de coortes prospectivas de longo prazo com diabéticos nessas regiões.
- **Nenhuma coorte de derivação ou validação é extra-europeia.** O modelo foi construído e testado inteiramente em populações do Reino Unido, Escócia, Suécia, Espanha (Catalunha), Malta e Croácia.
- Uso concomitante de medicação que já modifica risco cardiovascular (estatina, anti-hipertensivo) **não é uma limitação declarada como tal** — pelo contrário, a fonte observa que a maioria dos participantes das coortes de derivação já usava esse tipo de medicação, então o modelo reflete risco sob tratamento habitual, não risco "não tratado".

## Aplicabilidade no Brasil

**Este ponto não foi testado diretamente na fonte, e por isso fica sinalizado como extrapolação, não como dado confirmado.** O documento `score2-score2-op-aplicabilidade-e-limites-no-paciente-brasileiro.md`, nesta mesma pasta, mostra que o SCORE2 comum foi testado numa coorte brasileira real (ELSA-Brasil) e superestimou o risco observado em 59% (razão previsto/observado de 1,59). Não foi localizada, nesta sessão, nenhuma publicação que teste especificamente o **SCORE2-Diabetes** — com suas variáveis adicionais e recalibração própria — numa coorte brasileira ou latino-americana. Como o SCORE2-Diabetes herda a mesma estrutura de recalibração por região europeia do SCORE2 comum (nenhuma das quatro regiões inclui o Brasil ou a América Latina), é plausível que o mesmo padrão de superestimação se repita, mas isso é inferência por semelhança estrutural, não um achado medido — **VERIFICAÇÃO HUMANA NECESSÁRIA** para quem precisar de uma resposta baseada em dado direto. A diretriz brasileira vigente de dislipidemia/prevenção (SBC 2025, já citada no documento irmão) recomenda o **PREVENT** da AHA como ferramenta preferencial de estratificação em adultos sem DCV estabelecida; não foi localizada, nesta sessão, uma diretriz brasileira que trate especificamente da estratificação de risco em diabetes tipo 2 com ferramenta equivalente ao SCORE2-Diabetes.

## Armadilhas clínicas

- **Aplicar o SCORE2 comum em vez do SCORE2-Diabetes num paciente diabético** — a própria ESC não recomenda essa substituição; o ganho de discriminação (C-index +0,009 a +0,031) e a reclassificação de risco em até 44,8% dos casos mostram que a diferença tem consequência prática, não é ajuste marginal.
- **Confundir a unidade de HbA1c** — o modelo usa **mmol/mol (IFCC)**, não o percentual (NGSP) mais comum na prática clínica brasileira e americana; entrar com o valor percentual sem converter produz um resultado sem sentido.
- **Aplicar as faixas etárias de risco do SCORE2 comum ao resultado do SCORE2-Diabetes** — as faixas de decisão clínica do SCORE2-Diabetes (ESC 2023, diretriz de diabetes) são percentuais fixos que não variam por idade, ao contrário do SCORE2/SCORE2-OP.
- **Usar em diabetes tipo 1** — o modelo não foi derivado nem validado para essa população.
- **Usar em paciente já com DCV aterosclerótica estabelecida** — automaticamente risco muito alto pela diretriz de manejo; o cálculo do escore não se aplica e não deve ser usado para "rebaixar" esse paciente a uma categoria menor.
- **Tratar o resultado como calibrado para o Brasil** — nenhuma validação brasileira ou latino-americana foi localizada para o SCORE2-Diabetes especificamente; o achado de superestimação do SCORE2 comum na coorte ELSA-Brasil é o melhor indício disponível, mas é indireto.
- **Confundir com o escore ADVANCE** — outro modelo específico para diabetes, citado na fonte apenas como comparador de desempenho (SCORE2-Diabetes teve discriminação discretamente superior), não é o mesmo instrumento nem tem a mesma origem.
