---
title: "Escore H2FPEF: Probabilidade Diagnóstica de ICFEp em Dispneia Inexplicada"
slug: escore-h2fpef-probabilidade-diagnostica-de-icfep-em-dispneia-inexplicada
theme: "Calculadoras"
kind: calculadora
review_status: revisado
source_refs: ["Reddy YNV, Carter RE, Obokata M, Redfield MM, Borlaug BA. A Simple, Evidence-Based Approach to Help Guide Diagnosis of Heart Failure With Preserved Ejection Fraction. Circulation. 2018;138(9):861-870. DOI: 10.1161/CIRCULATIONAHA.118.034646. PMID: 29792299 — texto completo lido na íntegra (PDF de acesso aberto), derivação em 414 pacientes e validação externa em 100 pacientes, com cateterismo direito e teste de esforço invasivo como padrão de referência"]
legacy_source: "Documento novo, escrito em 02/08/2026. O tema Calculadoras já cobria escores de insuficiência cardíaca voltados a prognóstico (MAGGIC, Seattle Heart Failure Model, GWTG-HF, EFFECT), mas nenhum deles responde à pergunta que precede o tratamento: dado um paciente com dispneia de esforço inexplicada e função sistólica preservada, qual é a probabilidade de que a causa seja ICFEp? O H2FPEF preenche essa lacuna diagnóstica."
---

# Escore H2FPEF: Probabilidade Diagnóstica de ICFEp em Dispneia Inexplicada

## O problema que o escore resolve
O paciente euvolêmico, compensado, com dispneia de esforço e fração de ejeção preservada é um dos desafios diagnósticos mais comuns e mais mal resolvidos da cardiologia clínica. Quando há congestão franca ao exame físico ou à radiografia, o diagnóstico de insuficiência cardíaca com fração de ejeção preservada (ICFEp) é óbvio. Fora dessa situação — que é a maioria dos encaminhamentos ambulatoriais —, não havia, até 2018, nenhum critério com base em evidência para estimar a probabilidade de ICFEp antes de indicar (ou dispensar) o teste invasivo de esforço, que é o padrão-ouro mas é caro, tecnicamente complexo e impraticável para todo paciente dispneico.

Reddy et al. (Mayo Clinic, Circulation 2018) desenvolveram o **H2FPEF** exatamente para essa lacuna: um escore não invasivo, baseado só em características clínicas e ecocardiográficas de rotina, que estima a probabilidade de ICFEp e orienta se o paciente pode ser tratado como tal com confiança razoável, dispensado do diagnóstico, ou se precisa de teste adicional (tipicamente o teste de estresse diastólico ou o próprio cateterismo com esforço).

## Como o estudo foi feito
- **Coorte de derivação**: 414 pacientes consecutivos encaminhados para cateterismo direito com teste de esforço invasivo por dispneia inexplicada na Mayo Clinic (2006-2016) — 267 com ICFEp confirmada (casos) e 147 com dispneia não cardíaca (controles), prevalência de ICFEp de 64%.
- **Padrão de referência**: ICFEp definida por pressão de capilar pulmonar (PCP) elevada em repouso (≥15 mmHg) **ou** durante exercício (≥25 mmHg), medida diretamente por cateter. Dispneia não cardíaca exigiu hemodinâmica de repouso e de esforço normais.
- **Coorte de validação (teste)**: 100 pacientes consecutivos independentes, 61 com ICFEp (prevalência 61%).
- Fração de ejeção <50% (atual ou prévia), valvopatia relevante, hipertensão arterial pulmonar, pericardite constritiva, cardiomiopatia primária e transplante cardíaco foram critérios de exclusão.

## As seis variáveis e a pontuação exata
Da regressão logística multivariável (Tabela 3 do artigo), a pontuação foi atribuída pela **força de associação com ICFEp** — por isso os pesos não são iguais:

| Variável | Definição operacional | Pontos |
|---|---|---|
| **H**eavy (obesidade) | Índice de massa corporal **> 30 kg/m²** | **2** |
| **H**ipertensão tratada | Uso de **2 ou mais** anti-hipertensivos | **1** |
| **F**ibrilação atrial | Paroxística ou permanente, por história clínica/ECG | **3** |
| **P**ressão pulmonar elevada | Pressão sistólica de artéria pulmonar estimada ao eco **> 35 mmHg** | **1** |
| **E**lder (idade) | Idade **> 60 anos** | **1** |
| **F**illing pressure (pressão de enchimento) | Relação **E/e' > 9** ao Doppler tecidual | **1** |

**Pontuação total: 0 a 9.** O nome do escore é o próprio mnemônico das seis variáveis: **H**(eavy) + **H**(ipertenso, 2 fármacos) + **F**(ibrilação atrial) + **P**(ressão pulmonar) + **E**(lder) + **F**(illing pressure) = H2FPEF.

**Por que os pesos diferem:** na regressão multivariável do escore em pontos, obesidade teve odds ratio ajustado de 3,10 (IC95% 1,85-5,18) e fibrilação atrial de 5,78 (IC95% 2,28-14,62) — as duas variáveis mais fortes, refletindo o papel central de ambas na fisiopatologia da ICFEp já estabelecido na literatura prévia. As quatro variáveis restantes (idade, anti-hipertensivos, E/e', PASP) tiveram odds ratio ajustado entre 1,99 e 2,83, e por isso valem 1 ponto cada.

## Desempenho discriminativo
- **Coorte de derivação**: área sob a curva ROC (AUC) de **0,841** (IC95% 0,802-0,881; P<0,0001). Cada aumento de 1 ponto no escore dobrou a chance de ICFEp — odds ratio **1,98** (IC95% 1,74-2,30 no resumo; 1,73-2,30 no corpo do artigo, pequena divergência tipográfica entre as duas seções do próprio texto, ambas citadas aqui por transparência).
- **Coorte de validação externa (teste)**: AUC **0,886** (P<0,0001) — desempenho mantido, sem perda relevante ao aplicar o escore fixado a pacientes novos.
- **Validação interna por bootstrap** (1.000 réplicas): AUC corrigida por otimismo de **0,838** para o modelo categórico (o escore em pontos) e **0,857** para a versão contínua do modelo.
- **Calibração**: teste de Hosmer-Lemeshow sem evidência de má calibração nas três amostras — derivação (P=0,14), validação (P=0,53) e amostra conjunta (P=0,18) — ou seja, a probabilidade prevista pelo modelo correspondeu à prevalência observada em cada faixa de escore.
- **Superioridade sobre os algoritmos de consenso então vigentes**: o H2FPEF discriminou melhor do que os critérios do consenso de especialistas endossados pelas diretrizes da Sociedade Europeia de Cardiologia — aumento de AUC de **0,169** (IC95% 0,120-0,217) frente ao algoritmo de 2016, e de **0,173** (IC95% 0,132-0,215) frente ao de 2007 (ambos P<0,0001). **Nota de escopo**: essa comparação é com os algoritmos de consenso pré-existentes, não com o algoritmo HFA-PEFF da ESC (publicado só em 2019, portanto posterior a este artigo e fora do desenho deste estudo).

## Como interpretar a pontuação — as três faixas
Os próprios autores propõem, em texto (não como corte estatisticamente re-otimizado, mas como uso pretendido do escore), três faixas de decisão clínica:

| Faixa de pontuação | Uso pretendido |
|---|---|
| **0 ou 1** | Probabilidade baixa — permite **afastar** ICFEp com confiança razoável na maioria dos casos |
| **2 a 5** | Probabilidade **intermediária** — zona em que teste adicional (tipicamente teste de estresse diastólico ao eco, ou cateterismo com esforço) é necessário para decidir |
| **6 a 9** | Probabilidade alta — permite **estabelecer** o diagnóstico com confiança razoável |

**VERIFICAÇÃO HUMANA NECESSÁRIA**: o artigo apresenta a probabilidade estimada de ICFEp associada a cada valor individual de pontuação (0 a 9) na **Figura 1** (painel inferior), mas esse dado está depositado como **gráfico de barras (imagem)**, não como tabela em texto — a extração do PDF (texto completo lido, `pdftotext -layout`) confirma que a legenda descreve o gráfico ("a probabilidade de ICFEp aumentou com o aumento do escore H2FPEF") sem reproduzir os valores numéricos em nenhum trecho textual do artigo, incluindo o material suplementar referenciado (que não foi possível abrir nesta sessão). As três faixas categóricas acima **são citação literal do texto do artigo** (seção de Discussão) e podem ser usadas com segurança; a probabilidade percentual exata associada a cada ponto individual (por exemplo, "escore 4 = X% de probabilidade") não deve ser citada sem alguém abrir a Figura 1 do PDF original e ler os valores diretamente da imagem, ou consultar a calculadora online oficial dos autores (referenciada no artigo como "HFpEF calculator", disponível como material suplementar on-line).

## Exemplo numérico de aplicação
Paciente de 68 anos (idade >60: **+1**), obesa com IMC 33 kg/m² (**+2**), em uso de 3 anti-hipertensivos (**+1**), com fibrilação atrial paroxística documentada (**+3**). Ecocardiograma mostra E/e' de 11 (**+1**) e pressão sistólica de artéria pulmonar estimada em 40 mmHg (**+1**).

**Soma: 1 + 2 + 1 + 3 + 1 + 1 = 9 pontos** — extremo superior da faixa de alta probabilidade (6-9), compatível com estabelecer o diagnóstico de ICFEp com confiança razoável sem necessariamente exigir o teste invasivo de esforço como próximo passo.

Contraste: paciente de 54 anos (idade >60: **0**), IMC 32 kg/m² (**+2**), sem fibrilação atrial (**0**), em uso de 1 anti-hipertensivo (**0**), E/e' de 7 (**0**), PASP estimada em 28 mmHg (**0**). **Soma: 2 pontos** — já entra na faixa intermediária (2-5) só pela obesidade, ilustrando como uma única variável de peso alto empurra o paciente para fora da faixa de exclusão confiante.

## Como usar na prática
- O escore foi desenhado para o cenário específico de **dispneia de esforço inexplicada com função sistólica preservada e sem congestão evidente** — não para o paciente já claramente descompensado, em quem o diagnóstico de insuficiência cardíaca é clínico e não depende de escore.
- As seis variáveis usam dado **de rotina**: história clínica, número de anti-hipertensivos em uso, ECG/história para fibrilação atrial, e duas medidas do ecocardiograma transtorácico padrão (E/e' e pressão sistólica de artéria pulmonar estimada) — nenhum exame adicional é necessário para calcular.
- O uso pretendido é **bayesiano, não binário**: o escore não substitui o julgamento clínico nem dispensa investigação em toda faixa intermediária — ele organiza quem precisa de teste adicional e quem provavelmente não precisa.
- **NT-proBNP não entrou no modelo final**: os autores testaram e não encontrou-se ganho discriminativo incremental ao acrescentá-lo às variáveis clínicas e ecocardiográficas já presentes — ausência do biomarcador no escore não deve ser lida como falta de associação com ICFEp, e sim como falta de valor **incremental** neste modelo específico.

## Armadilhas clínicas
- **Aplicar o escore a paciente com fração de ejeção reduzida ou congestão franca** — fora do desenho do estudo, que excluiu especificamente esses cenários.
- **Tratar a faixa intermediária (2-5) como "ICFEp descartada" ou "ICFEp confirmada"** — o próprio artigo é explícito que essa faixa exige teste adicional, não uma leitura binária.
- **Somar pontos de forma incompleta por falta de eco recente** — duas das seis variáveis (E/e' e pressão sistólica de artéria pulmonar) dependem de ecocardiograma; sem ele, o escore fica incompleto e a interpretação das faixas não é válida.
- **Extrapolar as probabilidades percentuais por ponto de fontes secundárias não verificadas** — como registrado acima, o valor numérico exato por ponto individual está em imagem no artigo original e não foi transcrito neste documento; calculadoras de terceiros que apresentam essa tabela devem ser conferidas contra o gráfico original antes de uso clínico.
- **Ignorar o viés de encaminhamento da coorte de derivação**: todos os pacientes do estudo foram referenciados para teste invasivo, o que pode ter inflado a prevalência de ICFEp na amostra (64% na derivação) em relação à população geral de dispneia inexplicada em atenção primária — os próprios autores discutem essa limitação.
- **Confundir com escores prognósticos de ICFEp/IC em geral** (MAGGIC, Seattle Heart Failure Model, EFFECT, GWTG-HF, já cobertos nesta biblioteca) — aqueles estimam mortalidade em quem **já tem** o diagnóstico; o H2FPEF resolve a pergunta anterior, se o diagnóstico existe.
