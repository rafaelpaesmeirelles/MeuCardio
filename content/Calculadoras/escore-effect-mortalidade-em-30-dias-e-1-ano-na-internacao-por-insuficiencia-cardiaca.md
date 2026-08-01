---
title: "Escore EFFECT: Mortalidade em 30 Dias e 1 Ano na Internação por Insuficiência Cardíaca"
slug: escore-effect-mortalidade-em-30-dias-e-1-ano-na-internacao-por-insuficiencia-cardiaca
theme: "Calculadoras"
kind: calculadora
review_status: revisado
source_refs: ["Lee DS, Austin PC, Rouleau JL, Liu PP, Naimark D, Tu JV. Predicting mortality among patients hospitalized for heart failure: derivation and validation of a clinical model. JAMA. 2003;290(19):2581-2587. DOI: 10.1001/jama.290.19.2581. PMID: 14625335 — estudo do Enhanced Feedback for Effective Cardiac Treatment (EFFECT), Ontário, Canadá; coorte de derivação de 2.624 pacientes (1999-2001) e de validação de 1.407 pacientes (1997-1999), 4.031 pacientes no total"]
legacy_source: "Documento novo, escrito em 01/08/2026. A pasta já tem o GWTG-HF (mortalidade intra-hospitalar, registro americano de 2010) e o Seattle Heart Failure Model (sobrevida ambulatorial de longo prazo em IC crônica), mas nenhum escore cobria a internação aguda por IC com horizonte de 30 dias E 1 ano ao mesmo tempo, derivado numa coorte diferente (Ontário, Canadá, base comunitária) e décadas antes do GWTG-HF. O EFFECT preenche essa lacuna com fonte primária distinta, sem repetir variável ou coorte de nenhum escore já cadastrado."
---

# Escore EFFECT: Mortalidade em 30 Dias e 1 Ano na Internação por Insuficiência Cardíaca

## Definicao
Modelo clínico de predição de mortalidade para pacientes hospitalizados por insuficiência cardíaca (IC), derivado e validado a partir do estudo **EFFECT (Enhanced Feedback for Effective Cardiac Treatment)**, em Ontário, Canadá — Lee DS et al., JAMA. 2003;290(19):2581-2587 (PMID 14625335). Usa apenas variáveis disponíveis nas primeiras horas da apresentação hospitalar, e estima o risco em **dois horizontes ao mesmo tempo: 30 dias e 1 ano**, o que o distingue do GWTG-HF (só mortalidade intra-hospitalar) e do Seattle Heart Failure Model (só IC crônica ambulatorial), ambos já registrados nesta pasta.

## O estudo de derivacao e validacao
Estudo retrospectivo de base comunitária, com **4.031 pacientes** internados por IC em múltiplos hospitais de Ontário: **2.624 pacientes na coorte de derivação** (1999-2001) e **1.407 pacientes na coorte de validação** (1997-1999), identificados como parte do estudo EFFECT.

**Desfechos avaliados:** mortalidade por todas as causas em 30 dias e em 1 ano.

**Mortalidade observada:**
- **Intra-hospitalar**: 8,9% (derivação) e 8,2% (validação)
- **Em 30 dias**: 10,7% (derivação) e 10,4% (validação)
- **Em 1 ano**: 32,9% (derivação) e 30,5% (validação)

## Preditores identificados
A análise multivariável identificou como preditores independentes de mortalidade em 30 dias E em 1 ano:
- **Idade mais avançada**
- **Pressão arterial sistólica mais baixa**
- **Frequência respiratória mais alta**
- **Nível mais alto de ureia (blood urea nitrogen)**

(todos com p<0,001)
- **Hiponatremia** (p<0,01)

**Comorbidades associadas a maior mortalidade**, com razão de chances (odds ratio, OR) para mortalidade em 30 dias:
- **Doença cerebrovascular**: OR 1,43 (IC95% 1,03-1,98; p=0,03)
- **Doença pulmonar obstrutiva crônica**: OR 1,66 (IC95% 1,22-2,27; p=0,002)
- **Cirrose hepática**: OR 3,22 (IC95% 1,08-9,65; p=0,04)
- **Demência**: OR 2,54 (IC95% 1,77-3,65; p<0,001)
- **Câncer**: OR 1,86 (IC95% 1,28-2,70; p=0,001)

## Estratificacao de risco pelo indice
O modelo gera um **índice de risco** (soma ponderada das variáveis acima) que estratifica claramente pacientes de baixo e de alto risco:
- **Escore muito baixo (≤60)**: mortalidade de **0,4% em 30 dias** e **7,8% em 1 ano**
- **Escore muito alto (>150)**: mortalidade de **59,0% em 30 dias** e **78,8% em 1 ano**
- Pacientes com escores de risco em 1 ano mais altos tiveram sobrevida reduzida em todos os pontos de tempo até 1 ano (log-rank, p<0,001)

**Discriminação, na coorte de derivação:** área sob a curva ROC de **0,80 para mortalidade em 30 dias** e **0,77 para mortalidade em 1 ano**. Na coorte de validação externa, as taxas de mortalidade previstas corresponderam de perto às observadas em todo o espectro de risco.

`VERIFICAÇÃO HUMANA NECESSÁRIA`: o resumo estruturado do PubMed confirma os preditores, as razões de chance das comorbidades e os pontos de corte de risco (≤60 e >150) com os desfechos correspondentes, mas **não traz a tabela detalhada de pontos por variável** (quantos pontos cada faixa de idade, de pressão arterial, de frequência respiratória, de ureia e de sódio contribui para a soma). Essa tabela existe no texto completo do artigo (JAMA 2003;290(19):2581-2587) e não deve ser reconstruída de memória — consultar o artigo original ou o nomograma publicado antes de aplicar o escore ponto a ponto na prática.

## Conclusao do proprio estudo
**"Entre pacientes com insuficiência cardíaca de base comunitária, fatores identificáveis dentro de horas da apresentação hospitalar previram o risco de mortalidade em 30 dias e em 1 ano. O índice preditivo, validado externamente, pode auxiliar os clínicos a estimar o risco de mortalidade por insuficiência cardíaca e a fornecer orientação quantitativa para a tomada de decisão no cuidado da insuficiência cardíaca."**

## Sintese pratica
O EFFECT ocupa um espaço que nem o GWTG-HF nem o Seattle Heart Failure Model cobrem sozinhos: estima risco **na internação aguda**, com dado colhido **nas primeiras horas**, e projeta esse risco tanto para **30 dias** (decisão de intensidade de cuidado e de planejamento de alta) quanto para **1 ano** (conversa sobre prognóstico com o paciente e a família antes da alta). O gradiente entre os extremos de risco é acentuado — de 0,4% a 59,0% de mortalidade em 30 dias entre o escore mais baixo e o mais alto —, o que o torna útil tanto para tranquilizar o paciente de baixo risco quanto para escalonar cuidado no de alto risco. É anterior em quase uma década ao GWTG-HF e foi derivado numa população diferente (coorte canadense de base comunitária, não registro americano de hospitais participantes), o que o torna um ponto de comparação útil, não um substituto.

## Armadilhas clinicas
- **Não confundir com o GWTG-HF**: o GWTG-HF (Peterson PN et al., 2010, já registrado nesta pasta) prevê **só mortalidade intra-hospitalar**, com variáveis parcialmente diferentes (frequência cardíaca e raça entram no GWTG-HF; frequência respiratória e comorbidades específicas — cerebrovascular, DPOC, cirrose, demência, câncer — entram no EFFECT). São escores complementares, não intercambiáveis.
- **Não confundir com o Seattle Heart Failure Model**: aquele estima sobrevida ambulatorial de **1 a 3 anos** em IC **crônica**, calculado com dado de consulta, não de internação aguda.
- **Não aplicar o corte de risco (≤60 ou >150) sem a tabela de pontos completa** — os dois cortes citados aqui vieram do resumo estruturado do artigo, mas o cálculo do escore de cada paciente depende da tabela detalhada de pontos por variável, que está marcada como pendente de verificação no texto completo.
- A coorte de derivação e validação é **de base comunitária canadense (Ontário)** — extrapolar para outra população sem considerar diferença de perfil assistencial e de sistema de saúde é uma limitação do próprio desenho do estudo, não exclusiva deste escore.
