---
title: "Fluxograma: lise pré-hospitalar e ICP sem cirurgia — CAPTIM (NS), WEST (n=304), C-PORT (composto), STAT (TVR)"
slug: fluxograma-lise-pre-hospitalar-captim-west-cport-stat
theme: "Doença coronariana"
kind: fluxograma
summary: "CAPTIM: ICP não superior à lise na rua. WEST: viabilidade, composto 3 braços semelhante. C-PORT: composto sim, morte NS, sem cirurgia no local. STAT: n=123, composto puxado por TVR, morte P=1,00."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em CAPTIM PMID 12243916, WEST PMID 16757491, C-PORT PMID 11960536, STAT PMID 11263625. Revisão científica concluída em 30/08/2026."
source_refs:
  - "Bonnefoy E, et al. CAPTIM. Lancet. 2002;360(9336):825-829. PMID: 12243916."
  - "Armstrong PW. WEST. Eur Heart J. 2006;27(13):1530-1538. PMID: 16757491."
  - "Aversano T, et al. C-PORT. JAMA. 2002;287(15):1943-1951. PMID: 11960536."
  - "Le May MR, et al. STAT. J Am Coll Cardiol. 2001;37(4):985-991. PMID: 11263625."
  - "Documento da casa stream-estrategia-farmacoinvasiva-quando-icp-atrasa."
  - "Documento da casa fluxograma-icp-primaria-versus-lise-pami-prague-air."
---

# Fluxograma: lise na rua e sala no hospital comunitário

```mermaid
flowchart TD
  R0["Lise fora do terciário?"] --> D1{"Qual o ensaio?"}

  D1 -->|"Lise na ambulância vs ICP"| C1(["CAPTIM: composto 8,2% vs 6,2%<br/>IC cruza 0. Morte P=0,61"])

  D1 -->|"TNK ± invasão vs ICP, n=304"| C2(["WEST: composto 25/24/23%<br/>Morte+IAM não é o primário"])

  D1 -->|"Sala nova, sem cirurgia no prédio"| C3(["C-PORT: composto 6 meses P=0,03<br/>Morte P=0,72"])

  D1 -->|"Stent vs t-PA, n=123"| C4(["STAT: composto puxado por TVR<br/>Morte 4,8% vs 3,3% P=1,00"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4 conduta;
```

## Mensagem prática

**CAPTIM não mostra superioridade da ICP sobre a lise pré-hospitalar.** STAT e WEST não são ensaios de mortalidade.
