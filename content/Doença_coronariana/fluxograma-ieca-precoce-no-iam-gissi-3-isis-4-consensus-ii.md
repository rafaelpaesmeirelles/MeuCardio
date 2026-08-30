---
title: "Fluxograma: IECA no IAM — oral precoce (GISSI-3/ISIS-4) não é EV (CONSENSUS II) nem SAVE/AIRE/TRACE"
slug: fluxograma-ieca-precoce-no-iam-gissi-3-isis-4-consensus-ii
theme: "Doença coronariana"
kind: fluxograma
summary: "IAM não selecionado: GISSI-3 lisinopril e ISIS-4 captopril reduzem morte com ganho absoluto pequeno. CONSENSUS II (enalaprilato EV) primário NS, mais hipotensão. SAVE/AIRE/TRACE são IC/FE baixa. Nitrato de rotina NS. Magnésio do ISIS-4 não está no abstract relido."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em GISSI-3 PMID 7910229, ISIS-4 PMID 7661937 (abstract truncado), CONSENSUS II PMID 1495520. Revisão independente ChatGPT concluída em 29/08/2026: desfechos primários, amostra, comparadores, PMIDs/DOIs e mensagens de segurança conferidos; liberado para publicação pelo responsável técnico."
source_refs:
  - "GISSI-3. Lancet. 1994;343(8906):1115-1122. PMID: 7910229."
  - "ISIS-4. Lancet. 1995;345(8951):669-685. PMID: 7661937."
  - "Swedberg K, et al. CONSENSUS II. N Engl J Med. 1992;327(10):678-684. PMID: 1495520."
---

# Fluxograma: qual IECA no IAM?

```mermaid
flowchart TD
  R0["Quer citar IECA no IAM"] --> D1{"Qual a população e a via?"}

  D1 -->|"IAM não selecionado, oral <24 h"| C1(["GISSI-3 lisinopril: morte OR 0,88<br/>ISIS-4 captopril: 7,19% vs 7,69%; 2p=0,02<br/>Ganho absoluto pequeno; hipotensão sobe"])

  D1 -->|"EV nas primeiras 24 h"| C2(["CONSENSUS II: morte 6 meses P=0,26 NS<br/>Hipotensão 12% vs 3%. Não fazer"])

  D1 -->|"IC clínica ou FE baixa, depois da fase aguda"| C3(["SAVE / AIRE / TRACE — outro arquivo<br/>Não misturar com GISSI-3"])

  D1 -->|"Nitrato ou magnésio de rotina"| C4(["GISSI-3 GTN NS. ISIS-4 mononitrato NS.<br/>Magnésio: abstract truncado — não inventar"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4 conduta;
```

## Mensagem prática

**Oral precoce no IAM amplo: ganho pequeno. EV imediato: não. IC/FE baixa: SAVE/AIRE/TRACE.**
