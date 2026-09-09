---
title: "Escore MECKI: Teste Cardiopulmonar de Exercício Combinado a Índices Cardíaco e Renal na Insuficiência Cardíaca"
slug: escore-mecki-teste-cardiopulmonar-de-exercicio-combinado-a-indices-cardiaco-e-renal-na-insuficiencia-cardiaca
theme: "Calculadoras"
kind: calculadora
review_status: revisado
source_refs: ["Agostoni P, Corrà U, Cattadori G, Veglia F, La Gioia R, Scardovi AB, Emdin M, Metra M, Sinagra G, Limongelli G, Raimondo R, Re F, Guazzi M, Belardinelli R, Parati G, Magrì D, Fiorentini C, Mezzani A, Salvioni E, Scrutinio D, Ricci R, Bettari L, Di Lenarda A, Pastormerlo LE, Pacileo G, Vaninetti R, Apostolo A, Iorio A, Paolillo S, Palermo P, Contini M, Confalonieri M, Giannuzzi P, Passantino A, Cas LD, Piepoli MF, Passino C; MECKI Score Research Group. Metabolic exercise test data combined with cardiac and kidney indexes, the MECKI score: a multiparametric approach to heart failure prognosis. Int J Cardiol. 2013;167(6):2710-2718. DOI: 10.1016/j.ijcard.2012.06.113. PMID: 22795401 — coorte de derivação e validação cruzada, 2.716 pacientes, 13 centros italianos"]
legacy_source: "Documento novo. A pasta Calculadoras já tem instrumentos de predição de sobrevida/mortalidade na insuficiência cardíaca a partir de variáveis clínicas, farmacológicas e laboratoriais (Seattle Heart Failure Model, MAGGIC, escore EFFECT, GWTG-HF), mas nenhum que incorpore diretamente parâmetros do TESTE CARDIOPULMONAR DE EXERCÍCIO (CPET) — pico de VO2 e VE/VCO2 slope, variáveis funcionais amplamente usadas na avaliação de IC avançada e triagem para transplante/suporte circulatório mecânico, e que os modelos já registrados não incluem diretamente."
---

# Escore MECKI: Teste Cardiopulmonar de Exercício Combinado a Índices Cardíaco e Renal na Insuficiência Cardíaca

## O que resolve
Nenhum dos instrumentos de predição de sobrevida na insuficiência cardíaca já registrados nesta biblioteca (Seattle Heart Failure Model, MAGGIC, EFFECT, GWTG-HF) incorpora diretamente dados do **teste cardiopulmonar de exercício (TCPE/CPET)** — em particular o **pico de consumo de oxigênio (VO2 pico)** e a **inclinação VE/VCO2 (eficiência ventilatória)**, dois dos parâmetros mais usados isoladamente na avaliação prognóstica de IC avançada e na triagem para transplante cardíaco ou suporte circulatório mecânico. O **escore MECKI** ("Metabolic Exercise test data Combined with cardiac and Kidney Indexes") foi desenvolvido para integrar esses dados de exercício a variáveis clínicas, laboratoriais e ecocardiográficas de fácil obtenção, num único modelo prognóstico multiparamétrico.

## Derivação (Agostoni P et al., Int J Cardiol 2013, PMID 22795401)
Estudo multicêntrico italiano, coorte de derivação com **2.716 pacientes com insuficiência cardíaca sistólica**, seguidos em **13 centros** por mediana de **1.041 dias** (variação de 4 a 5.185 dias). Análise de regressão de risco proporcional de Cox com seleção stepwise de variáveis, seguida de procedimento de validação cruzada. O desfecho do estudo foi um **composto de morte cardiovascular e transplante cardíaco de urgência**.

**Seis variáveis, entre as diversas avaliadas, mostraram associação independente com o prognóstico** e compõem o escore MECKI:
- **Hemoglobina**
- **Sódio (Na⁺)**
- **Função renal**, estimada pela fórmula **MDRD**
- **Fração de ejeção do ventrículo esquerdo** (por ecocardiografia)
- **Pico de consumo de oxigênio (% do predito)** — parâmetro do teste cardiopulmonar de exercício
- **Inclinação VE/VCO2 (VE/VCO2 slope)** — parâmetro do teste cardiopulmonar de exercício

**A fórmula exata de combinação dos coeficientes de cada variável (os pesos da equação de Cox) não está detalhada no resumo indexado verificado nesta sessão** — para reprodução exata do cálculo do escore, `VERIFICAÇÃO HUMANA NECESSÁRIA` contra o texto completo do artigo (Int J Cardiol. 2013;167(6):2710-2718) e/ou a calculadora oficial mantida pelo grupo de pesquisa.

## Desempenho preditivo (área sob a curva ROC)
O escore MECKI identificou o risco do desfecho composto (morte cardiovascular + transplante de urgência) com desempenho discriminativo alto e consistente ao longo do seguimento:

| Horizonte de seguimento | AUC (IC95%) |
|---|---|
| 1 ano | **0,804 (0,754-0,852)** |
| 2 anos | **0,789 (0,750-0,828)** |
| 3 anos | **0,762 (0,726-0,799)** |
| 4 anos | **0,760 (0,724-0,796)** |

A discriminação se manteve na faixa de "alta" (AUC acima de 0,75) em todos os quatro horizontes de tempo avaliados, com discreta e esperada redução ao longo do seguimento mais prolongado.

## Conclusão do próprio estudo
**"Este é o primeiro estudo multicêntrico de grande escala em que um escore prognóstico — o escore MECKI — foi construído para pacientes com IC sistólica considerando dados de teste cardiopulmonar de exercício combinados a medidas clínicas, laboratoriais e ecocardiográficas."** Os autores concluem que, na população estudada, o escore MECKI foi validado com sucesso, apresentando AUC muito alta.

## Síntese prática
O valor diferencial do escore MECKI nesta biblioteca está em ser o único instrumento de predição de sobrevida na IC que incorpora diretamente parâmetros funcionais do teste cardiopulmonar de exercício — pico de VO2 e VE/VCO2 slope — ao lado de variáveis clínicas (hemoglobina, sódio), renal (MDRD) e ecocardiográfica (fração de ejeção), sem exigir dados de dispositivo ou de esquema farmacológico completo como o Seattle Heart Failure Model. Isso o torna particularmente aplicável no cenário em que o TCPE já foi realizado como parte da investigação de IC avançada (triagem para transplante ou suporte circulatório mecânico), permitindo aproveitar diretamente esse dado, já coletado, numa estimativa prognóstica multiparamétrica validada em coorte de grande porte (2.716 pacientes, mediana de seguimento superior a 2,8 anos).

## Armadilhas clínicas
- Aplicar o escore MECKI a paciente que não realizou teste cardiopulmonar de exercício — duas das seis variáveis (pico de VO2 e VE/VCO2 slope) só existem a partir desse exame; não há substituto informal para essas medidas dentro do escore.
- Usar o escore MECKI isoladamente como critério de elegibilidade para transplante cardíaco ou suporte circulatório mecânico — é instrumento de estimativa prognóstica multiparamétrica, não um critério de listagem por si só; decisões de transplante seguem os critérios específicos já registrados em outros documentos desta biblioteca (ISHLT).
- Assumir que a fórmula de combinação dos coeficientes está totalmente descrita neste documento — o resumo verificado nesta sessão identifica as seis variáveis independentes e o desempenho (AUC) do modelo final, mas não detalha os pesos exatos da equação de Cox; a reprodução manual do cálculo exige o texto completo ou a calculadora oficial do grupo.
- Tratar a coorte de derivação (pacientes com IC **sistólica**, ou seja, fração de ejeção reduzida) como equivalente a IC com fração de ejeção preservada — a fonte primária verificada nesta sessão descreve especificamente população com IC sistólica; extrapolação para ICFEp não está sustentada por este estudo.
