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

## Tabela de pontos por variavel (Table 4 do artigo original)
Tabela extraída do texto completo do artigo (Lee DS et al., JAMA. 2003;290(19):2581-2587, Table 4 "Heart Failure Risk Scoring System", p. 2585), conferida diretamente no PDF do periódico — não reconstruída de memória nem de fonte secundária.

| Variável | Pontos — escore de 30 dias | Pontos — escore de 1 ano |
|---|---|---|
| **Idade, anos** | + idade (em anos) | + idade (em anos) |
| **Frequência respiratória, irpm** (mínimo 20; máximo 45)* | + frequência (em irpm) | + frequência (em irpm) |
| **Pressão arterial sistólica, mmHg†** | | |
| ≥180 | −60 | −50 |
| 160-179 | −55 | −45 |
| 140-159 | −50 | −40 |
| 120-139 | −45 | −35 |
| 100-119 | −40 | −30 |
| 90-99 | −35 | −25 |
| <90 | −30 | −20 |
| **Ureia (BUN), mg/dL** (máximo 60 mg/dL)*‡ | + nível (em mg/dL) | + nível (em mg/dL) |
| **Sódio sérico <136 mEq/L** | +10 | +10 |
| **Doença cerebrovascular** | +10 | +10 |
| **Demência** | +20 | +15 |
| **Doença pulmonar obstrutiva crônica** | +10 | +10 |
| **Cirrose hepática** | +25 | +35 |
| **Câncer** | +15 | +15 |
| **Hemoglobina <10,0 g/dL (<100 g/L)** | não se aplica ao escore de 30 dias | +10 |

\* Valores acima do máximo ou abaixo do mínimo listado recebem o valor máximo/mínimo correspondente (ou seja, frequência respiratória é truncada em 20 e 45 irpm antes de somar; ureia é truncada em 60 mg/dL antes de somar).
† Pressão arterial mais alta é protetora nos dois modelos — por isso os pontos são **subtraídos** conforme a faixa, não somados.
‡ O valor máximo de ureia (60 mg/dL) equivale a 21 mmol/L; o escore é calculado usando o valor em mg/dL.

**Como somar:** escore de 30 dias = idade + frequência respiratória + pontos de pressão arterial sistólica + ureia + pontos de sódio + pontos de doença cerebrovascular + pontos de demência + pontos de DPOC + pontos de cirrose hepática + pontos de câncer. O escore de 1 ano usa a mesma soma, acrescida dos pontos de hemoglobina (que não entram no escore de 30 dias).

**Faixas de risco** (o artigo as descreve em relação a um escore intermediário de referência, 91-120 pontos): muito baixo (≤60 pontos), baixo (61-90), intermediário (91-120), alto (121-150) e muito alto (>150) — os dois extremos e suas mortalidades já constavam na seção acima.

O próprio artigo cita, na nota de rodapé da Table 4, que uma versão eletrônica da calculadora estava disponível em `http://www.ccort.ca/CHFriskmodel.asp` (Canadian Cardiovascular Outcomes Research Team) — endereço histórico de 2003, hoje fora do ar, registrado aqui apenas como a atribuição original do próprio artigo, não como link ativo.

## Conclusao do proprio estudo
**"Entre pacientes com insuficiência cardíaca de base comunitária, fatores identificáveis dentro de horas da apresentação hospitalar previram o risco de mortalidade em 30 dias e em 1 ano. O índice preditivo, validado externamente, pode auxiliar os clínicos a estimar o risco de mortalidade por insuficiência cardíaca e a fornecer orientação quantitativa para a tomada de decisão no cuidado da insuficiência cardíaca."**

## Sintese pratica
O EFFECT ocupa um espaço que nem o GWTG-HF nem o Seattle Heart Failure Model cobrem sozinhos: estima risco **na internação aguda**, com dado colhido **nas primeiras horas**, e projeta esse risco tanto para **30 dias** (decisão de intensidade de cuidado e de planejamento de alta) quanto para **1 ano** (conversa sobre prognóstico com o paciente e a família antes da alta). O gradiente entre os extremos de risco é acentuado — de 0,4% a 59,0% de mortalidade em 30 dias entre o escore mais baixo e o mais alto —, o que o torna útil tanto para tranquilizar o paciente de baixo risco quanto para escalonar cuidado no de alto risco. É anterior em quase uma década ao GWTG-HF e foi derivado numa população diferente (coorte canadense de base comunitária, não registro americano de hospitais participantes), o que o torna um ponto de comparação útil, não um substituto.

## Armadilhas clinicas
- **Não confundir com o GWTG-HF**: o GWTG-HF (Peterson PN et al., 2010, já registrado nesta pasta) prevê **só mortalidade intra-hospitalar**, com variáveis parcialmente diferentes (frequência cardíaca e raça entram no GWTG-HF; frequência respiratória e comorbidades específicas — cerebrovascular, DPOC, cirrose, demência, câncer — entram no EFFECT). São escores complementares, não intercambiáveis.
- **Não confundir com o Seattle Heart Failure Model**: aquele estima sobrevida ambulatorial de **1 a 3 anos** em IC **crônica**, calculado com dado de consulta, não de internação aguda.
- **A pressão arterial sistólica pontua ao contrário do que a intuição sugere**: pressão mais alta é protetora, então os pontos são **subtraídos** (de −30 na faixa <90 mmHg até −60 na faixa ≥180 mmHg) — inverter o sinal por engano derruba o escore inteiro.
- **Ureia e frequência respiratória são truncadas antes de somar** (ureia no máximo 60 mg/dL, frequência respiratória entre 20 e 45 irpm) — valor medido fora dessa faixa entra no cálculo pelo limite, não pelo valor bruto.
- **O escore de 30 dias e o de 1 ano usam tabelas de pontos diferentes**, não a mesma soma aplicada a dois cortes: cirrose hepática, por exemplo, vale +25 no escore de 30 dias e +35 no de 1 ano, e a hemoglobina só entra no escore de 1 ano.
- A coorte de derivação e validação é **de base comunitária canadense (Ontário)** — extrapolar para outra população sem considerar diferença de perfil assistencial e de sistema de saúde é uma limitação do próprio desenho do estudo, não exclusiva deste escore.
