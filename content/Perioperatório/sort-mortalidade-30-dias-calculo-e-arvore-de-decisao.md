---
title: "SORT: risco percentual de mortalidade em 30 dias"
slug: sort-mortalidade-30-dias-calculo-e-arvore-de-decisao
theme: "Perioperatório"
kind: documento
fonte_producao: chatgpt
review_status: pendente_revisao
summary: "Regressão logística pré-operatória de seis variáveis para mortalidade global em 30 dias."
source_refs:
  - "Protopapa KL, Simpson JC, Smith NCE, Moonesinghe SR. Br J Surg. 2014;101(13):1774-1783. PMID: 25388883. PMCID: PMC4240514. DOI: 10.1002/bjs.9638."
---

# SORT — Surgical Outcome Risk Tool

Endpoint: **mortalidade por todas as causas em 30 dias**. O modelo final teve **AUROC 0,91** na validação.

Constante **−7,366**. Coeficientes: ASA III +1,411; IV +2,388; V +4,081; urgência expedited +1,236; urgente +1,657; imediata +2,452; especialidade GI/torácica/vascular +0,712; cirurgia extra-major/complexa +0,381; câncer +0,667; idade 65–79 +0,777; ≥80 +1,591. Probabilidade = `exp(x)/[1+exp(x)]`.

```mermaid
flowchart TD
 A["Cirurgia não cardíaca"] --> B["ASA"]
 B --> C["Urgência: eletiva / expedited / urgente / imediata"]
 C --> D{"GI, torácica ou vascular?"}
 D --> E["Severidade extra-major/complexa"]
 E --> F["Câncer"]
 F --> G["Idade <65 / 65–79 / ≥80"]
 G --> H["Constante −7,366 + coeficientes"]
 H --> I["Função logística"]
 I --> J["Mortalidade percentual em 30 dias"]
```

```mermaid
flowchart TD
 A["SORT calculado"] --> B["Comunicar risco absoluto de mortalidade"]
 B --> C{"Risco altera decisão/planejamento?"}
 C -->|"Não"| D["Consentimento e planejamento habitual"]
 C -->|"Sim"| E["Decisão compartilhada + alternativas + nível de cuidado pós-op"]
 D --> F["Risco cardíaco é calculado separadamente"]
 E --> F
 F --> G["Não somar/promediar SORT com RCRI/MICA/GSCRI"]
```

Limitações: “extra-major/complexa” deve seguir a taxonomia original; expedited, urgente e imediata são categorias distintas. SORT não substitui avaliação cardiológica específica.