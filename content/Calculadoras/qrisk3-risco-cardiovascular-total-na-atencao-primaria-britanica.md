---
title: "QRISK3: Risco Cardiovascular Total na Atenção Primária Britânica"
slug: qrisk3-risco-cardiovascular-total-na-atencao-primaria-britanica
theme: "Calculadoras"
kind: calculadora
review_status: revisado
published: false
source_refs: ["Hippisley-Cox J, Coupland C, Brindle P. Development and validation of QRISK3 risk prediction algorithms to estimate future risk of cardiovascular disease: prospective cohort study. BMJ. 2017;357:j2099. DOI: 10.1136/bmj.j2099. PMID: 28536104. PMCID: PMC5441081 — texto integral conferido via PMC (variáveis do modelo final, estatísticas de desempenho por sexo e subgrupo, categorias étnicas, período e tamanho das coortes)", "Mortensen MB, Tybjærg-Hansen A, Nordestgaard BG. Statin Eligibility for Primary Prevention of Cardiovascular Disease According to 2021 European Prevention Guidelines Compared With Other International Guidelines. JAMA Cardiol. 2022;7(8):836-843. DOI: 10.1001/jamacardio.2022.1876. PMID: 35793078 — validação externa/comparação do QRISK3 (junto com SCORE2 e PCE) na coorte dinamarquesa Copenhagen General Population Study (66.909 participantes)", "Pate A, Emsley R, van Staa T. Impact of lowering the risk threshold for statin treatment on statin prescribing: a descriptive study in English primary care. Br J Gen Pract. 2020;70(700):e765-e771. DOI: 10.3399/bjgp20X713057. PMID: 33020170 — confirma que o NICE (Clinical Guideline 181) baixou o limiar de indicação de estatina de 20% para 10% de risco em 10 anos, em 2014", "Masson W, Rossi E, Mora-Crespo LM, Cornejo-Peña G, Pessio C, Gago M, Alvarado RN, Scolnik M. Cardiovascular risk stratification and appropriate use of statins in patients with systemic lupus erythematosus according to different strategies. Clin Rheumatol. 2020;39(2):455-462. DOI: 10.1007/s10067-019-04856-z. PMID: 31802350 — aplicação do QRISK3 num subgrupo com lúpus eritematoso sistêmico (LES), conforme recomendação do NICE"]
legacy_source: "Documento novo, escrito em 08/09/2026. A pasta Calculadoras já cobria Framingham (FRS), SCORE2/SCORE2-OP (com documento dedicado de aplicabilidade no paciente brasileiro), SCORE2-Diabetes e a família americana Pooled Cohort Equations/PREVENT, mas nenhum documento tratava do escore de risco cardiovascular total mais usado na atenção primária do Reino Unido — o QRISK3, referência oficial do NICE (Clinical Guideline 181) para indicação de estatina em prevenção primária. O QRISK3 difere estruturalmente das demais famílias por ser derivado diretamente de registros eletrônicos de atenção primária em escala nacional (base QResearch), e por incluir preditores ausentes nas outras ferramentas cobertas nesta pasta — fibrilação atrial, artrite reumatoide, lúpus eritematoso sistêmico, doença renal crônica em estágio 3, enxaqueca, uso de corticoide, uso de antipsicótico atípico, doença mental grave, disfunção erétil e variabilidade da pressão arterial sistólica."
---

# QRISK3: Risco Cardiovascular Total na Atenção Primária Britânica

## O que o QRISK3 tenta resolver
As famílias de escore já cobertas nesta pasta — Framingham, SCORE2/SCORE2-OP e Pooled Cohort Equations/PREVENT — foram derivadas de coortes de pesquisa dedicadas, com um conjunto relativamente enxuto de variáveis clássicas (idade, sexo, pressão arterial, colesterol, tabagismo, diabetes). O QRISK3 nasce de uma lógica diferente: foi derivado diretamente dos **registros eletrônicos de rotina da atenção primária inglesa** (base QResearch), o que permitiu incorporar dezenas de milhões de pacientes-ano de seguimento e testar, um a um, fatores de risco que nenhuma das outras ferramentas considera — fibrilação atrial, doenças autoimunes, doença renal crônica em estágio inicial, uso crônico de certas classes de medicamento e condições psiquiátricas.

Hippisley-Cox J, Coupland C, Brindle P. *Development and validation of QRISK3 risk prediction algorithms to estimate future risk of cardiovascular disease: prospective cohort study*. **BMJ. 2017;357:j2099** (**PMID 28536104**, DOI 10.1136/bmj.j2099, PMCID PMC5441081, texto integral em acesso aberto). É a atualização do QRISK2 (2008), incorporando novos fatores de risco candidatos que ainda não haviam sido testados formalmente no modelo anterior.

## Coorte de derivação e de validação
Estudo de coorte aberta e prospectiva, usando dados da base **QResearch**, com pacientes de **25 a 84 anos**, livres de doença cardiovascular e sem prescrição de estatina no início do seguimento:
- **Coorte de derivação**: **981 clínicas de atenção primária** na Inglaterra, resultando em **7.895.503 pacientes** segundo o resumo indexado no PubMed (o texto completo, conferido via PMC, registra a coorte final de derivação em cerca de 7,89 milhões de pacientes, com 363.565 casos incidentes de doença cardiovascular ao longo de 50,8 milhões de pessoas-ano de seguimento)
- **Coorte de validação**: um conjunto **separado de 328 clínicas** (sem sobreposição com as de derivação), com **2.671.298 pacientes**
- Desfecho: doença cardiovascular incidente, registrada em qualquer uma de três fontes de dados vinculadas — registro de atenção primária, óbito ou internação hospitalar
- Modelos derivados por regressão de Cox, separadamente para homens e mulheres, com avaliação do risco em **10 anos**

## Variáveis do modelo
O QRISK3 mantém as variáveis já presentes no QRISK2 — idade, etnia (nove categorias, com "branco ou não registrado" como referência), índice de privação social (escore de Townsend), pressão arterial sistólica, índice de massa corporal, razão colesterol total/HDL, tabagismo, história familiar de doença coronariana em parente de primeiro grau com menos de 60 anos, diabetes tipo 1, diabetes tipo 2, hipertensão tratada, artrite reumatoide, fibrilação atrial e doença renal crônica (originalmente só estágios 4-5) — e testa formalmente um conjunto de **novos candidatos**, dos quais entraram no modelo final:
- Doença renal crônica **estágio 3** (ampliando a definição prévia, que só considerava estágio 4-5)
- Variabilidade da pressão arterial sistólica (desvio-padrão de medidas repetidas)
- Enxaqueca
- Uso de corticoide
- Lúpus eritematoso sistêmico (LES)
- Uso de antipsicótico atípico
- Doença mental grave
- Disfunção erétil (apenas no modelo masculino)

**HIV/AIDS foi testado e não entrou no modelo final** — a fonte registra explicitamente que essa variável não atingiu significância estatística no critério pré-especificado de inclusão. Isso não significa que HIV seja irrelevante para risco cardiovascular por outras vias; significa apenas que, nesta coorte e neste modelo específico, ele não agregou poder preditivo suficiente para ser incluído.

## Desempenho
Estatísticas de discriminação e calibração na coorte de validação, relatadas separadamente por sexo (valores do resumo oficial indexado no PubMed):
- **Mulheres**: estatística C de Harrell **0,88**; estatística D **2,48**; variação explicada (R²) **59,6%**
- **Homens**: estatística C de Harrell **0,86**; estatística D **2,26**; variação explicada (R²) **54,8%**

O próprio artigo descreve o desempenho geral do QRISK3 atualizado como **semelhante** ao do QRISK2 — ou seja, os novos preditores aumentam a granularidade clínica sem necessariamente elevar de forma expressiva a discriminação agregada. O desempenho variou entre estratos, mas este texto não usa estimativas de subgrupo como limiares clínicos nem reproduz valores que não tenham sido confirmados na fonte primária.

## O que muda na prática
- O QRISK3 (ou seu antecessor QRISK2, conforme a versão vigente da diretriz local) é a **ferramenta oficialmente recomendada pelo NICE** (National Institute for Health and Care Excellence, Reino Unido) para estimar risco cardiovascular e orientar a indicação de estatina em prevenção primária
- Em 2014, o NICE (Clinical Guideline 181) **baixou o limiar de indicação de estatina de 20% para 10%** de risco estimado em 10 anos — achado confirmado em Pate A, Emsley R, van Staa T. *Br J Gen Pract*. 2020;70(700):e765-e771 (**PMID 33020170**), que descreve esse limiar de 10% como o novo ponto de corte oficial e mede o impacto real da mudança sobre a prescrição de estatina na atenção primária inglesa
- Diferente das outras famílias cobertas nesta pasta, o QRISK3 incorpora diretamente **fibrilação atrial, artrite reumatoide e LES** como variáveis de entrada — Masson W et al., *Clin Rheumatol*. 2020;39(2):455-462 (**PMID 31802350**), aplicou o QRISK3 (ao lado do Framingham ajustado) numa coorte de pacientes com LES, seguindo explicitamente a recomendação do NICE de usar essa ferramenta nesse contexto clínico
- Para o médico que já usa Framingham, SCORE2 ou PCE/PREVENT com um paciente que também tem fibrilação atrial, doença renal crônica leve, enxaqueca com aura, LES ou uso crônico de corticoide, o QRISK3 é a única das ferramentas desta pasta que capta esses fatores **diretamente na estimativa de risco cardiovascular total** — nas outras famílias, esses fatores no máximo entram como "reforçadores" qualitativos de decisão, sem entrar no cálculo numérico

## Armadilhas clínicas

**Aplicabilidade fora da coorte de derivação**
- O QRISK3 foi derivado e validado **inteiramente em população inglesa de atenção primária (base QResearch)**, usando um sistema de registro eletrônico específico (EMIS); o próprio artigo original reconhece essa limitação e pede validação independente em outro sistema de dados
- Mortensen MB et al., *JAMA Cardiol*. 2022;7(8):836-843 (**PMID 35793078**), validou externamente o QRISK3 (ao lado de SCORE2 e da Pooled Cohort Equations) numa coorte dinamarquesa contemporânea (Copenhagen General Population Study, 66.909 participantes, seguimento médio de 9,2 anos): o QRISK3 apresentou razão predito/observado de **1,3** — ou seja, **superestimou o risco real observado** nessa população nórdica, no mesmo patamar de superestimação da Pooled Cohort Equations americana (também 1,3), enquanto o SCORE2 europeu teve calibração ligeiramente melhor (razão 0,8)
- Essa mesma validação mostrou que, usando os critérios do NICE (que se apoiam no QRISK3), **26% dos 66.909 participantes** seriam elegíveis para estatina — proporção bem mais alta que a do critério europeu ESC 2021 (4%) e intermediária entre os critérios americano ACC/AHA (34%) e ESC/EAS 2019 (20%). Isso ilustra que o limiar de 10% do NICE, combinado à calibração do QRISK3, tende a classificar uma fração maior da população como elegível a estatina do que os critérios europeus mais recentes — divergência de estratégia de saúde pública, não necessariamente "erro" de um modelo em relação ao outro
- As **nove categorias étnicas** usadas no QRISK3 refletem a composição populacional do Reino Unido e sua codificação de censo — aplicar o modelo a pacientes de etnia não representada de forma equivalente nessas categorias (por exemplo, a maioria da população brasileira, majoritariamente miscigenada e não categorizada por essa classificação britânica) é uma extrapolação sem validação direta nesta fonte

**Sobreposição e substituição de escore anterior**
- O QRISK3 **não substitui formalmente** o Framingham, o SCORE2/SCORE2-OP ou a Pooled Cohort Equations/PREVENT fora do sistema de saúde britânico — é a ferramenta de referência **dentro do NICE**, não um consenso internacional; cada uma dessas famílias segue sendo a referência oficial em sua respectiva diretriz de origem (ESC para SCORE2, ACC/AHA para PCE/PREVENT)
- **Não comparar diretamente o percentual do QRISK3 com o do SCORE2, do PCE ou do PREVENT** para o mesmo paciente como se fossem a mesma escala — desfechos, horizontes de calibração e composição das coortes de origem diferem entre as famílias (ver documento `pooled-cohort-equations-e-equacoes-prevent-risco-cardiovascular-em-prevencao-primaria.md`, nesta mesma pasta, sobre o mesmo cuidado entre PCE e SCORE2)
- **Não se aplica a quem já tem doença cardiovascular estabelecida** — a coorte de derivação e de validação excluiu explicitamente pacientes com doença cardiovascular prévia e pacientes já em uso de estatina; nesses casos a conduta é de prevenção secundária, não de estimativa de risco de primeiro evento
- **Tratar o "modelo completo" como algo calculável de cabeça** — o QRISK3 combina dezenas de variáveis (incluindo variabilidade de pressão arterial, que exige mais de uma medida registrada) em uma equação não linear; não existe uma tabela simples de pontos somáveis como em escores mais simples desta pasta (ex.: CHA₂DS₂-VASc, HAS-BLED) — o cálculo depende da calculadora oficial ou de sua implementação validada
- Fora do Reino Unido, a saída deve ser tratada como extrapolação: as fontes citadas aqui não estabelecem recalibração ou validação brasileira do QRISK3. Este registro, portanto, não sustenta interpretar o percentual como calibrado para a população brasileira nem adotá-lo como ferramenta padrão local.

## Escopo deste registro

Este é o registro **prático**: descreve população elegível, variáveis de entrada, interpretação e limites de uso na atenção primária britânica. A derivação estatística e a validação do modelo são tratadas separadamente em [QRISK3 — derivação e validação na coorte QResearch](/biblioteca/qrisk3-risco-cardiovascular-em-10-anos-derivacao-e-validacao-na-coorte-qresearch). Os dois registros não representam calculadoras concorrentes, e nenhum deles implementa ou reproduz a equação.

## Conteúdo CorVIA conectado
- [Pooled Cohort Equations (ASCVD Risk Estimator) e as Equações PREVENT: Risco Cardiovascular em Prevenção Primária](/biblioteca/pooled-cohort-equations-e-equacoes-prevent-risco-cardiovascular-em-prevencao-primaria)
- [SCORE2 e SCORE2-OP](/biblioteca/score2-e-score2-op)
- [SCORE2 e SCORE2-OP — aplicabilidade e limites no paciente brasileiro](/biblioteca/score2-score2-op-aplicabilidade-e-limites-no-paciente-brasileiro)
- [Framingham Risk Score (FRS)](/biblioteca/framingham-risk-score-frs)
- [SCORE2-Diabetes: Estimativa de Risco Cardiovascular em 10 Anos no Diabetes Tipo 2](/biblioteca/score2-diabetes-estimativa-de-risco-cardiovascular-em-10-anos-no-diabetes-tipo-2)
- [Escores ATRIA: Risco de AVC e de Sangramento na Fibrilação Atrial](/biblioteca/escores-atria-risco-de-avc-e-de-sangramento-na-fibrilacao-atrial)
