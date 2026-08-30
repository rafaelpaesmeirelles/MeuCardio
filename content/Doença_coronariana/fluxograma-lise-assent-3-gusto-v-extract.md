---
title: "Fluxograma: adjunto à lise — ASSENT-3 (tríplice), GUSTO-V (morte NS), ExTRACT (morte/reinfarto)"
slug: fluxograma-lise-assent-3-gusto-v-extract
theme: "Doença coronariana"
kind: fluxograma
summary: "ASSENT-3 reduz composto com isquemia refratária; morte isolada ausente no abstract. GUSTO-V morte 30 d P=0,43. ExTRACT: morte/reinfarto sim, morte P=0,11. HERO-2: bivalirudina morte NS."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em ASSENT-3 PMID 11530146, GUSTO-V PMID 11425410, ExTRACT PMID 16537665. Revisão científica concluída em 30/08/2026."
source_refs:
  - "ASSENT-3 Investigators. Lancet. 2001;358(9282):605-613. PMID: 11530146."
  - "Topol EJ. GUSTO V. Lancet. 2001;357(9272):1905-1914. PMID: 11425410."
  - "GUSTO III Investigators. N Engl J Med. 1997;337(16):1118-23. PMID: 9340503."
  - "Antman EM, et al. ExTRACT-TIMI 25. N Engl J Med. 2006;354(14):1477-1488. PMID: 16537665."
  - "ASSENT-4 PCI Investigators. Lancet. 2006;367(9510):569-578. PMID: 16488800."
  - "COBALT Investigators. N Engl J Med. 1997;337(16):1124-30. PMID: 9340504."
  - "INJECT. Lancet. 1995;346(8971):329-36. PMID: 7623530."
  - "Documento da casa fluxograma-lise-gissi-1-isis-2-assent-2."
  - "Documento da casa fluxograma-lise-gissi-2-isis-3-gusto-i."
  - "Documento da casa fluxograma-lise-tardia-late-emeras."
---

# Fluxograma: o que a lise realmente ganhou

```mermaid
flowchart TD
  R0["Quer citar adjunto à fibrinolise"] --> D1{"Qual o desfecho?"}

  D1 -->|"Morte 30 d"| C1(["GUSTO-V reteplase+abciximabe P=0,43 NS<br/>GUSTO-III reteplase vs t-PA P=0,54 NS<br/>HERO-2 bivalirudina P=0,85 NS<br/>ExTRACT morte P=0,11 NS"])

  D1 -->|"Morte ou reinfarto"| C2(["ExTRACT enoxaparina vs HNF: 9,9% vs 12,0%<br/>Morte isolada NS. Sangramento maior sobe"])

  D1 -->|"Tríplice com isquemia refratária"| C3(["ASSENT-3: enox ou abciximabe vs HNF<br/>Não vender como mortalidade"])

  D1 -->|"ICP 'facilitada' com lise plena"| C4(["ASSENT-4 PCI: piora. Morte hospitalar 6% vs 3%<br/>Primário 90 d 19% vs 13%. Ver fluxograma-icp-facilitada-assent-4-finesse"])

  D1 -->|"Dois bolus vs infusão"| C5(["COBALT: t-PA duplo bolus NÃO equivalente<br/>GUSTO-III: reteplase vs t-PA acelerado P=0,54<br/>INJECT: reteplase ≈ SK (margem 1 pp)"])

  D1 -->|"SK, AAS ou TNK vs t-PA?"| C6(["GISSI-1 / ISIS-2 / ASSENT-2<br/>Ver fluxograma-lise-gissi-1-isis-2-assent-2"])

  D1 -->|"Lise depois de 6 h?"| C7(["LATE ITT NS; EMERAS hospitalar NS<br/>Ver fluxograma-lise-tardia-late-emeras"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7 conduta;
```

## Mensagem prática

**Abciximabe na lise não reduz morte (GUSTO-V). Reteplase não supera t-PA acelerado (GUSTO-III). Enoxaparina na lise reduz morte/reinfarto (ExTRACT), não morte isolada.**
