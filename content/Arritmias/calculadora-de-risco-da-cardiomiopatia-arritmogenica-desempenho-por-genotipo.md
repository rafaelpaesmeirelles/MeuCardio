---
title: "Calculadora de Risco da Cardiomiopatia Arritmogênica: Desempenho Genótipo-Dependente e o Limite da RM com Realce Tardio"
slug: calculadora-de-risco-da-cardiomiopatia-arritmogenica-desempenho-por-genotipo
theme: "Arritmias"
kind: calculadora
review_status: revisado
source_refs: ["Cadrin-Tourigny J, Bosman LP, Wang W, Tadros R, Bhonsale A, Bourfiss M, et al. Sudden Cardiac Death Prediction in Arrhythmogenic Right Ventricular Cardiomyopathy: A Multinational Collaboration. Circ Arrhythm Electrophysiol. 2021;14(1):e008509. PMID: 33296238 — abstract lido na íntegra via PubMed nesta sessão", "Gasperetti A, Carrick R, Protonotarios A, Laredo M, van der Schaaf I, Syrris P, et al. Long-Term Arrhythmic Follow-Up and Risk Stratification of Patients With Desmoplakin-Associated Arrhythmogenic Cardiomyopathy. JACC Adv. 2024 Mar. PMID: 38938828 — abstract lido na íntegra via PubMed nesta sessão", "De Marco C, Asatryan B, Te Riele ASJM, Di Marco A, et al. Left Ventricular Late Gadolinium Enhancement for Arrhythmic Risk Prediction in ARVC. Circ Arrhythm Electrophysiol. 2026;19(2):e014265. DOI: 10.1161/CIRCEP.125.014265. PMID: 41608798 — abstract lido na íntegra via PubMed nesta sessão"]
legacy_source: "Documento novo, escrito em 12/08/2026. A pasta já tinha um documento sobre COMO SE DIAGNOSTICA a cardiomiopatia arritmogênica (cardiomiopatia-arritmogenica-criterios-de-padua-2020-e-task-force-revisada-de-2010.md — critérios de Task Force 2010 e Padua 2020). Esse documento responde 'o paciente tem a doença?'; este documento novo responde uma pergunta seguinte e distinta — 'em quem já tem o diagnóstico confirmado, qual o risco de arritmia ventricular fatal, e a ferramenta quantitativa usada para essa decisão (a calculadora de risco de Cadrin-Tourigny) funciona igual em qualquer genótipo?' A resposta, medida em 2024 e testada de novo com imagem em 2026, é não — e essa nuance genótipo-dependente não estava registrada em nenhum documento já publicado nesta pasta."
---

# Calculadora de Risco da Cardiomiopatia Arritmogênica: Desempenho Genótipo-Dependente e o Limite da RM com Realce Tardio

## A pergunta que este documento responde, e a que ele não responde
`cardiomiopatia-arritmogenica-criterios-de-padua-2020-e-task-force-revisada-de-2010.md`, já publicado nesta pasta, cobre os critérios que definem **se** um paciente tem cardiomiopatia arritmogênica. Uma vez confirmado o diagnóstico, surge uma pergunta diferente e igualmente decisiva: **qual é o risco de arritmia ventricular com risco de vida nesse paciente específico, e esse risco justifica um cardiodesfibrilador implantável (CDI)?** A ferramenta quantitativa mais usada para essa segunda pergunta é a calculadora de risco publicada por Cadrin-Tourigny et al. em 2021 — e o achado central deste documento é que **seu desempenho não é uniforme entre os diferentes genes causadores da doença**.

## A calculadora original — derivação multinacional
Cadrin-Tourigny J et al. Circ Arrhythm Electrophysiol. 2021;14(1):e008509 (PMID 33296238). Coorte multinacional de **864 pacientes** com cardiomiopatia arritmogênica de ventrículo direito definida (idade média 40±16 anos, 53% homens), seguimento mediano de **5,75 anos** (IQR 2,77-10,58):

- **Desfecho estudado**: arritmia ventricular com risco de vida (LTVA) — morte súbita cardíaca, morte súbita abortada, taquicardia ventricular sustentada, ou TV tratada por CDI a mais de 250 bpm
- **Eventos**: **93 de 864 pacientes (10,8%)** tiveram LTVA no seguimento
- **Modelo final — 4 preditores**: idade jovem, sexo masculino, contagem de extrassístoles ventriculares, e número de derivações do ECG com inversão de onda T
- **Desempenho (C-index, corrigido para otimismo)**: **0,74** (IC95% 0,69-0,80) — calibração praticamente perfeita (slope 0,95, IC95% 0,94-0,98)
- **Achado contraintuitivo dos próprios autores**: TV sustentada prévia e a extensão da doença estrutural (funcional) **não** se associaram de forma independente a LTVA subsequente no modelo final — só os 4 preditores acima entraram

## O limite genótipo-específico — o gene da desmoplaquina (DSP)
Gasperetti A et al. JACC Adv. 2024 (PMID 38938828) testaram especificamente essa calculadora numa coorte de pacientes com cardiomiopatia arritmogênica causada por variante patogênica em **desmoplaquina (DSP)** — um dos genes causadores mais estudados, com fenótipo já reconhecido como distinto do fenótipo clássico ligado a PKP2 (mais envolvimento de ventrículo esquerdo, por exemplo). **252 pacientes DSP-positivos** (idade média 39,6±16,9 anos, 35,3% homens), seguimento mediano de **44,5 meses** (IQR 19,6-78,3):

- **94 pacientes (37,3%)** tiveram arritmia ventricular durante o seguimento
- Entre os **204 pacientes sem arritmia ventricular no início**, a incidência de evento novo foi **32,8%** (**7,37% ao ano**) — taxa anual bem mais alta do que a impressão que a taxa agregada de 10,8% em 5,75 anos da coorte de derivação (majoritariamente outros genes) sugere
- **Preditor mais forte de evento nos primeiros 5 anos**: história de taquicardia ventricular não sustentada (TVNS) prévia, com razão de risco ajustada de **2,097** (p=0,004) — variável que **não faz parte** dos 4 preditores do modelo original
- Envolvimento de ventrículo esquerdo (presente em 194 dos 252 pacientes) associou-se a maior risco (log-rank p=0,0239)
- **Idade e sexo masculino — dois dos 4 preditores do modelo original — não foram preditores significativos nesta coorte DSP**
- **Desempenho da calculadora original nesta população**: C-statistic de **0,604** (IC95% 0,594-0,614) — bem abaixo do 0,74 da derivação. **Em quem tinha envolvimento de ventrículo esquerdo, o desempenho caiu para 0,558** (IC95% 0,556-0,560), **praticamente equivalente ao acaso** (0,5)
- **Conclusão dos autores**: pacientes DSP-positivos enfrentam risco arrítmico substancial, e as ferramentas de estratificação existentes são inadequadas para essa população — é necessário um algoritmo específico por genótipo

## A tentativa de refinamento por imagem — realce tardio de VE não resolveu
De Marco C et al. Circ Arrhythm Electrophysiol. 2026;19(2):e014265 (PMID 41608798) testaram se o realce tardio de gadolínio (RTG) no ventrículo esquerdo à ressonância magnética cardíaca melhora a predição de risco além da calculadora já existente — estudo multicêntrico prospectivo (17 centros), **385 pacientes** com cardiomiopatia arritmogênica definida, sem arritmia ventricular sustentada prévia, com RM cardíaca basal, seguimento de **3,1 anos** (IQR 1,2-5,8):

- **132 pacientes (34,3%)** tinham RTG de VE; **98 (25,5%)** tinham padrão de alto risco (epicárdico, transmural, ou combinação de septo com parede livre)
- **67 pacientes (17,4%)** tiveram arritmia ventricular sustentada no seguimento
- **Análise univariável**: RTG de VE associado a maior risco (HR 1,82, p=0,014); padrão de alto risco também associado (HR 1,85, p=0,017)
- **Depois de ajustar pelo risco já estimado pela calculadora de Cadrin-Tourigny**: **nem o RTG de VE (p=0,85) nem o padrão de alto risco (p=0,87) predisseram o desfecho de forma independente**
- **Conclusão dos autores**: apesar de associado ao risco arrítmico isoladamente, o RTG de VE **não agregou valor prognóstico incremental** à calculadora de risco já existente

## Síntese prática
A calculadora de Cadrin-Tourigny tem desempenho bom (C-index 0,74) na coorte multinacional em que foi derivada — mas essa coorte é predominantemente composta por genes diferentes de DSP. **Quando testada especificamente em pacientes com cardiomiopatia arritmogênica por desmoplaquina, seu desempenho cai para quase o equivalente ao acaso (C-statistic 0,558) exatamente no subgrupo com envolvimento de ventrículo esquerdo** — que é também o subgrupo fenotípico mais característico de DSP. É o mesmo padrão de fracasso de generalização já registrado nesta pasta para o escore de Sieira na síndrome de Brugada (ver `escore-de-sieira-na-sindrome-de-brugada-e-o-fracasso-na-validacao-externa.md`): ferramenta de risco derivada numa população pode não se transferir para um subgrupo genético ou fenotípico distinto, mesmo quando a derivação original teve boa calibração. A tentativa mais óbvia de refinamento — acrescentar RM com realce tardio — não resolveu o problema quando testada formalmente: o achado é positivo isoladamente, mas desaparece após ajuste pelo risco já estimado pela calculadora.

## Como este documento se relaciona com os outros da pasta
Complementa, sem se sobrepor, `cardiomiopatia-arritmogenica-criterios-de-padua-2020-e-task-force-revisada-de-2010.md` (diagnóstico, não risco) e `restricao-de-exercicio-na-cardiomiopatia-arritmogenica-de-ventriculo-direito-dose-resposta-e-mecanismo.md` (restrição de exercício como intervenção modificadora de risco, não estratificação por calculadora). O padrão de "escore com bom desempenho na derivação e desempenho ruim em subgrupo específico" ecoa diretamente `escore-de-sieira-na-sindrome-de-brugada-e-o-fracasso-na-validacao-externa.md`, ainda que sejam doenças e ferramentas diferentes.

## Armadilhas clínicas
- Aplicar a calculadora de Cadrin-Tourigny com a mesma confiança em qualquer paciente com cardiomiopatia arritmogênica, sem considerar o genótipo — em portador de variante em desmoplaquina, especialmente com envolvimento de ventrículo esquerdo, o desempenho da ferramenta é próximo do acaso
- Usar idade jovem e sexo masculino como tranquilizadores de baixo risco em paciente DSP-positivo — na coorte específica de DSP, essas duas variáveis (que são 2 dos 4 preditores do modelo geral) **não** foram preditores significativos
- Assumir que agregar RM com realce tardio de VE resolve a limitação da calculadora em qualquer cenário — testado formalmente com ajuste estatístico adequado, o RTG de VE não acrescentou valor preditivo independente
- Ignorar a taquicardia ventricular não sustentada prévia como sinal de alerta em paciente DSP-positivo por não constar entre os 4 preditores do modelo geral — nesta população específica, foi o preditor mais forte de evento nos primeiros 5 anos (aHR 2,097)
- Extrapolar os achados deste documento (específicos de DSP) para outros genes causadores de cardiomiopatia arritmogênica (PKP2, DSG2, DSC2, entre outros) sem fonte própria — a limitação de desempenho documentada aqui foi medida especificamente na população DSP-positiva
