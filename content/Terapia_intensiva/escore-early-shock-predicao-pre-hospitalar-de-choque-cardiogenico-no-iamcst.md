---
title: "Escore EARLY SHOCK: Predição Pré-Hospitalar de Choque Cardiogênico no IAMCST"
slug: escore-early-shock-predicao-pre-hospitalar-de-choque-cardiogenico-no-iamcst
theme: "Terapia intensiva"
kind: estudo
review_status: revisado
source_refs: ["Yang C, Lee T, Kochan A, et al. Prehospital Prediction of Cardiogenic Shock Among Patients With ST-Segment-Elevation Myocardial Infarction: The EARLY SHOCK Score. J Am Heart Assoc. 2025;14(19):e040681. DOI: 10.1161/JAHA.124.040681. Epub 2025 Aug 12. PMID: 40792594. PMCID: PMC12684621. Texto integral, incluindo Tabelas 3-5, lido via PMC"]
legacy_source: "Documento novo, escrito em 12/08/2026. A biblioteca já tem a classificação SCAI de estágios do choque cardiogênico (diagnóstico do choque já instalado) e a Classificação SCAI já registrada, mas nenhum documento cobria PREDIÇÃO do choque antes de ele se instalar, no momento pré-hospitalar — que é quando a ativação precoce do time de choque tem mais chance de mudar o desfecho."
---

# Escore EARLY SHOCK: Predição Pré-Hospitalar de Choque Cardiogênico no IAMCST

## Definição
A classificação SCAI de estágios do choque cardiogênico, já registrada nesta biblioteca, descreve a gravidade de um choque **já instalado**. O EARLY SHOCK é uma ferramenta diferente: um escore de risco para prever, **ainda no atendimento pré-hospitalar**, quais pacientes com infarto com supradesnivelamento do segmento ST (IAMCST) vão desenvolver choque cardiogênico **intra-hospitalar**, usando apenas dados que o serviço de atendimento pré-hospitalar (SAMU/EMS) já coleta rotineiramente — sem exame de sangue, sem ecocardiograma. O objetivo declarado é permitir a ativação precoce do time de choque antes mesmo da chegada ao hospital.

## O estudo (Yang et al., JAHA 2025)
Yang C et al. J Am Heart Assoc. 2025;14(19):e040681 (PMID 40792594). Coorte retrospectiva com dados prospectivos de um sistema de saúde *hub-and-spoke* duplo (Vancouver, Canadá), abril de 2012 a dezembro de 2020, com **2.736 pacientes consecutivos** com IAMCST submetidos a angioplastia primária.

- **415 pacientes (15,2%) desenvolveram choque cardiogênico intra-hospitalar**
- Regressão logística multivariável identificou **8 preditores independentes**, com validação interna por reamostragem (*bootstrapping*, 1.000 amostras)
- **Estatística C do modelo completo (Modelo 1): 0,87** (IC95% 0,86-0,90), com corte por otimismo ajustado também em 0,87 — discriminação considerada excelente

### Os 8 preditores e suas razões de chance (análise multivariável, Modelo 1)
O nome **EARLY SHOCK** é o acrônimo dos componentes: sinais vitais do atendimento pré-hospitalar (frequência cardíaca e pressão arterial sistólica), idade, terapia renal substitutiva, localização do infarto, glicemia/diabetes ("*sugar*"), insuficiência cardíaca prévia e parada cardíaca.

| Preditor | OR (IC95%) | 
|---|---|
| Idade ≥ 80 anos (referência: < 55 anos) | 2,48 (1,53-4,00) |
| Diálise em curso | 4,53 (1,47-13,98) |
| Insuficiência cardíaca prévia | 2,56 (1,41-4,64) |
| FC de apresentação ≥ 100 bpm (referência: 70-79 bpm) | 3,25 (2,00-5,29) |
| PAS inicial < 90 mmHg (referência: ≥ 170 mmHg) | 22,41 (12,86-39,05) |
| PAS inicial 90-109 mmHg | 8,65 (5,10-14,68) |
| Parada cardíaca pré-hospitalar | 17,56 (12,53-24,62) |
| Infarto de localização anterior (vs. não anterior) | 1,60 (1,21-2,12) |

Diabetes teve OR 1,34 (IC95% 0,98-1,82, p=0,065) na análise multivariável — associação que perdeu significância estatística formal em relação à univariável (OR 1,39, p=0,006), mas o próprio estudo manteve a variável no modelo por relevância clínica reconhecida na literatura de choque cardiogênico.

### O escore de pontos e o desempenho por faixa de risco
Os coeficientes de regressão foram convertidos em pontos inteiros (dividindo cada coeficiente pelo menor coeficiente do modelo). A pontuação total possível varia de **0 a 105 no Modelo 1** (modelo completo, com os 8 preditores). Desempenho, conforme a Tabela 5 do artigo (probabilidade prevista vs. observada de choque, Modelo 1):

| Faixa de escore | Probabilidade prevista | Probabilidade observada (IC95%) |
|---|---|---|
| 0-11 | < 5% | 2,2% (1,5-3,2%) |
| 12-16 | 5-9% | 6,8% (5,0-8,9%) |
| 17-20 | 10-19% | 16,7% (12,0-22,2%) |
| 21-23 | 20-29% | 30,9% (22,9-39,9%) |
| 24-26 | 30-39% | 40,6% (31,1-50,5%) |
| 27-28 | 40-49% | 41,1% (31,1-51,6%) |
| ≥ 29-30 | > 50% | ≥ 53,2% |
| ≥ 42 | ≥ 90% | 92,7% |

Pelo índice de Youden, o ponto de corte ótimo do Modelo 1 foi **escore ≥ 18**, com **sensibilidade de 0,79 e especificidade de 0,83** para identificar quem vai desenvolver choque cardiogênico intra-hospitalar.

### Dois modelos alternativos, mais simples
O estudo também derivou versões reduzidas do escore, para cenários em que nem todo dado está disponível de imediato:
- **Modelo 2** (exclui parada cardíaca pré-hospitalar como preditor): estatística C **0,80**; pontuação total até 61; corte ótimo **≥ 10**, sensibilidade 0,72 e especificidade 0,75
- **Modelo 3** (só variáveis numéricas — idade, FC e PAS de apresentação, sem os componentes categóricos de diálise/IC prévia/localização/parada): estatística C **0,79**; pontuação total até 60; corte ótimo **> 12**, sensibilidade 0,67 e especificidade 0,79

## Conclusão do próprio estudo
**"Identificamos 8 variáveis clínicas que predizem fortemente choque cardiogênico entre pacientes com IAMCST submetidos a angioplastia primária. Isso foi desenvolvido no escore EARLY SHOCK, que pode ser aplicado facilmente no ambiente pré-hospitalar para identificar rapidamente choque cardiogênico e permitir a ativação do time de choque. A validação externa do sistema de escore está pendente para aplicação mais ampla."**

## Síntese prática
O EARLY SHOCK usa só o que o socorrista já mede na ambulância — frequência cardíaca, pressão arterial sistólica, idade, e informação de história clínica rapidamente obtida (diálise, insuficiência cardíaca prévia) e do próprio ECG pré-hospitalar (localização do infarto, parada cardíaca) — para estratificar, ainda antes da chegada ao hospital, quem tem risco real de evoluir para choque. A discriminação é boa (C-estatística 0,87), e a faixa de escore ≥ 42 identifica um subgrupo com probabilidade observada de choque acima de 90%, útil para acionar o time de choque cardiogênico e preparar recurso (leito de UTI, disponibilidade de suporte circulatório mecânico) antes mesmo da porta do hospital. É complementar, não substituto, à classificação SCAI: o EARLY SHOCK prediz **quem vai chocar**; o SCAI classifica **a gravidade de quem já está em choque**.

## Armadilhas clínicas
- **Aplicar o escore como se já estivesse validado externamente** — o próprio estudo é claro que a validação externa está pendente; a coorte é de um único sistema de saúde (Vancouver, Canadá), com um protocolo regional específico, e o desempenho pode não se replicar em outra população ou sistema de atendimento
- **Usar a tabela de pontos exata por categoria sem consultar a figura original do artigo** — a conversão precisa de cada categoria (por exemplo, quantos pontos exatos idade 70-79 vs. ≥80 anos recebe) está publicada como figura (Figura 3 do artigo), não como tabela de texto — `VERIFICAÇÃO HUMANA NECESSÁRIA` para quem for implementar o cálculo exato ponto a ponto: confirme contra a Figura 3 do PMC12684621 antes de programar uma calculadora
- **Confundir os três modelos** — o Modelo 1 (0-105 pontos, corte ≥18) inclui parada cardíaca pré-hospitalar como preditor e tem o melhor desempenho; os Modelos 2 e 3 são versões reduzidas com desempenho discriminativo menor (C-estatística 0,80 e 0,79) e pontuação em escala diferente — não misturar o corte de um modelo com a pontuação de outro
- **Tratar diabetes como preditor forte e independente** — na análise multivariável do próprio estudo, diabetes não atingiu significância estatística (p=0,065), diferente do que a análise univariável isolada sugeria
- **Esquecer que o desfecho é choque cardiogênico intra-hospitalar em pacientes já triados para angioplastia primária** — a coorte não inclui pacientes que não chegaram a receber reperfusão, o que pode limitar a generalização para sistemas de saúde com tempo porta-balão mais longo ou acesso mais restrito a hemodinâmica
