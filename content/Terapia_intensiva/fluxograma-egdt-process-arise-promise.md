---
title: "Fluxograma: EGDT no choque séptico — ProCESS, ARISE e ProMISe são NS"
slug: fluxograma-egdt-process-arise-promise
theme: "Terapia intensiva"
kind: fluxograma
summary: "Três multicêntricos de EGDT vs usual: ProCESS morte 60 d NS; ARISE 90 d P=0,90; ProMISe 90 d P=0,90 e mais caro. Não vender o ensaio unicêntrico antigo. SOAP-II é vasopressor; CLOVERS é volume — outras perguntas. Não inventar números do Rivers."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em ProCESS PMID 24635773, ARISE 25272316 e ProMISe 25776532. Rivers 2001 não relido. Publicação sujeita à aprovação do responsável técnico. Revisão independente ChatGPT concluída em 29/08/2026: desfechos primários, amostra, comparadores, PMIDs/DOIs e mensagens de segurança conferidos; liberado para publicação pelo responsável técnico."
source_refs:
  - "ProCESS Investigators. N Engl J Med. 2014;370(18):1683-1693. PMID: 24635773."
  - "ARISE Investigators. N Engl J Med. 2014;371(16):1496-1506. PMID: 25272316."
  - "Mouncey PR, et al. ProMISe. N Engl J Med. 2015;372(14):1301-1311. PMID: 25776532."
---

# Fluxograma: EGDT protocolar no choque séptico?

```mermaid
flowchart TD
  R0["Choque séptico no PA, já com antibiótico e volume"] --> D1{"Quer citar EGDT de 6 h com PVC/SvO2/transfusão/inotrópico?"}

  D1 -->|"ProCESS 2014 EUA"| C1(["1.341; morte hospitalar 60 d<br/>protocolar vs usual P=0,83<br/>EGDT vs padrão P=0,31"])

  D1 -->|"ARISE 2014 ANZ"| C2(["1.600; morte 90 d 18,6% vs 18,8%<br/>P=0,90"])

  D1 -->|"ProMISe 2015 Inglaterra"| C3(["1.260; morte 90 d 29,5% vs 29,2%<br/>P=0,90; mais caro"])

  R0 --> D2{"A pergunta é outra?"}

  D2 -->|"Qual vasopressor?"| C4(["SOAP-II: arquivo próprio"])
  D2 -->|"Quanto volume?"| C5(["CLOVERS: arquivo próprio"])
  D2 -->|"Ensaio unicêntrico antigo"| C6(["Não relido aqui. Não anular os três NS"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## Mensagem prática

**Três multicêntricos, primário de morte NS.** Não protocolar CVC/SvO2/transfusão/dobutamina como se isso reduzisse mortalidade contemporânea.
