---
title: "Fluxograma: CADILLAC vs ADMIRAL — stent no IAM sim; abciximabe de rotina não"
slug: fluxograma-cadillac-admiral-stent-e-abciximabe-no-iam
theme: "Doença coronariana"
kind: fluxograma
summary: "CADILLAC: primário 6 meses cai por TVR do stent; morte/IAM/AVC NS; reestenose independente do abciximabe. ADMIRAL n=300 reduz composto 30 d. GUSTO-IV ACS: abciximabe médico NS."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em CADILLAC PMID 11919304 e ADMIRAL PMID 11419426. Revisão científica concluída em 30/08/2026."
source_refs:
  - "Stone GW, et al. CADILLAC. N Engl J Med. 2002;346(13):957-966. PMID: 11919304."
  - "Montalescot G, et al. ADMIRAL. N Engl J Med. 2001;344(25):1895-1903. PMID: 11419426."
---

# Fluxograma: stent e GPI no IAM antigo

```mermaid
flowchart TD
  R0["Quer citar stent ou abciximabe no IAM"] --> D1{"Qual a pergunta?"}

  D1 -->|"Stent vs balão na ICP primária"| C1(["CADILLAC: primário cai por TVR<br/>Morte/reinfarto/AVC NS"])

  D1 -->|"Abciximabe de rotina no IAM"| C2(["CADILLAC: reestenose independente do GPI<br/>ADMIRAL n=300 não anula o CADILLAC"])

  D1 -->|"GPI sem revasc precoce"| C3(["GUSTO-IV ACS: morte/IAM NS<br/>Outro arquivo"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3 conduta;
```

## Mensagem prática

**Stent no IAM: TVR, não mortalidade. Abciximabe rotineiro: não vender ADMIRAL contra CADILLAC.**
