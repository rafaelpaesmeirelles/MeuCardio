---
title: "AUB-HAS2: score cardiovascular perioperatório e árvore de decisão"
slug: aub-has2-score-metodologia-e-arvore-de-decisao
theme: "Perioperatório"
kind: documento
fonte_producao: chatgpt
review_status: pendente_revisao
summary: "Score simples de 6 itens para risco de morte, IAM ou AVC em 30 dias após cirurgia não cardíaca, com árvore de uso clínico."
source_refs:
  - "Dakik HA, Sbaity E, Msheik A, et al. AUB-HAS2 Cardiovascular Risk Index: Performance in Surgical Subpopulations and Comparison to the Revised Cardiac Risk Index. J Am Heart Assoc. 2020;9(10):e016228. DOI: 10.1161/JAHA.119.016228."
  - "Dakik HA, Eldirani M, Kaspar C, et al. Prospective validation of the AUB-HAS2 cardiovascular risk index. Eur Heart J Qual Care Clin Outcomes. 2022;8(1):96-97. PMID: 33017006. DOI: 10.1093/ehjqcco/qcaa077."
  - "Halvorsen S, Mehilli J, Cassese S, et al. Eur Heart J. 2022;43(39):3826-3924. PMID: 36017553. DOI: 10.1093/eurheartj/ehac270."
  - "Thompson A, Fleischmann KE, Smilowitz NR, et al. 2024 AHA/ACC perioperative guideline. DOI: 10.1161/CIR.0000000000001285."
---

# AUB-HAS2 Cardiovascular Risk Index

## Endpoint

Prediz o risco de **morte, infarto do miocárdio ou AVC em 30 dias** após cirurgia não cardíaca.

## Componentes — 1 ponto cada

- **H**istory of heart disease: história de doença cardíaca;
- **A**ngina/dyspnea: angina ou dispneia;
- **A**ge: idade ≥75 anos;
- **A**nemia: hemoglobina <12 g/dL;
- **S**urgery vascular: cirurgia vascular;
- **S**urgery emergency: cirurgia de emergência.

Pontuação total: **0 a 6**.

## Classificação utilizada pela ESC 2022

- **0–1:** baixo risco;
- **2–3:** risco intermediário;
- **>3:** alto risco.

A ESC 2022 relata taxa pós-operatória **>10%** para escores >3.

Em análise ampla do ACS-NSQIP publicada por Dakik et al., houve aumento progressivo do composto morte/IAM/AVC conforme a pontuação; na subpopulação de cirurgia geral, o desfecho variou de aproximadamente 0,3% com score 0 para 29% com score >3. Esses números **não devem ser extrapolados como taxa universal** para todas as especialidades, pois a taxa absoluta varia conforme o procedimento.

## Árvore de cálculo

```mermaid
flowchart TD
  A["Paciente em avaliação pré-operatória"] --> B["Doença cardíaca prévia? +1"]
  B --> C["Angina ou dispneia? +1"]
  C --> D["Idade ≥75 anos? +1"]
  D --> E["Hemoglobina <12 g/dL? +1"]
  E --> F["Cirurgia vascular? +1"]
  F --> G["Cirurgia de emergência? +1"]
  G --> H["Somar 0-6 pontos"]
  H --> I{"Score 0-1?"}
  I -->|"Sim"| J["Baixo risco"]
  I -->|"Não"| K{"Score 2-3?"}
  K -->|"Sim"| L["Risco intermediário"]
  K -->|"Não: >3"| M["Alto risco"]
```

## Árvore de uso clínico

```mermaid
flowchart TD
  A["AUB-HAS2 calculado"] --> B{"Score 0-1?"}
  B -->|"Sim"| C["Baixo risco pelo AUB-HAS2"]
  C --> D["Se assintomático, estável e cirurgia não elevada: geralmente prosseguir"]
  B -->|"Não"| E{"Score 2-3 ou >3?"}
  E -->|"2-3"| F["Risco intermediário: integrar DASI, procedimento, ECG e biomarcadores conforme indicação"]
  E -->|">3"| G["Alto risco: revisão cardiovascular estruturada + planejamento multidisciplinar"]
  F --> H{"Capacidade funcional pobre/desconhecida + resultado de teste mudará manejo?"}
  G --> H
  H -->|"Não"| I["Otimizar e planejar monitorização; não testar automaticamente"]
  H -->|"Sim"| J["Considerar investigação adicional apropriada"]
```

## Por que é útil

- Apenas seis variáveis, todas disponíveis na avaliação clínica/laboratorial inicial.
- Incorpora **anemia**, **sintomas** e **urgência**, ausentes do RCRI clássico.
- É listado entre os scores de risco perioperatório nas diretrizes ESC 2022 e AHA/ACC 2024.

## Limitações

- O risco absoluto varia de acordo com a especialidade cirúrgica.
- O item “história de doença cardíaca” precisa de definição consistente no formulário institucional.
- O escore estratifica risco; não prescreve isoladamente teste de estresse, CCTA, coronariografia ou cancelamento cirúrgico.
