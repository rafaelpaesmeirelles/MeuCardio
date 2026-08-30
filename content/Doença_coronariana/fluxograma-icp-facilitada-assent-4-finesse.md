---
title: "Fluxograma: ICP facilitada — ASSENT-4 (lise plena piora) e FINESSE (primário NS)"
slug: fluxograma-icp-facilitada-assent-4-finesse
theme: "Doença coronariana"
kind: fluxograma
summary: "ASSENT-4: TNK plena antes da ICP, morte hospitalar 6% vs 3%, primário 90 d 19% vs 13% (RR 1,39). FINESSE: reteplase meia-dose+abciximabe ou abciximabe pré-ICP vs abciximabe no laboratório; primário 90 d 9,8% / 10,5% / 10,7% (P=0,55). Resolução de ST não é desfecho clínico. ASSENT-3 é adjunto à lise, não esta pergunta."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em ASSENT-4 PCI PMID 16488800 e FINESSE PMID 18499565 (NCBI efetch nesta revisão editorial). Revisão científica concluída em 30/08/2026."
source_refs:
  - "ASSENT-4 PCI Investigators. Lancet. 2006;367(9510):569-578. PMID: 16488800."
  - "Ellis SG, et al. FINESSE. N Engl J Med. 2008;358(21):2205-2217. PMID: 18499565."
  - "Documento da casa assent-3-tenecteplase-com-enoxaparina-ou-abciximabe — outra pergunta."
---

# Fluxograma: não facilitar a ICP primária com lise

```mermaid
flowchart TD
  R0["Quer 'facilitar' a ICP do IAMCSST?"] --> D1{"Com o quê?"}

  D1 -->|"Tenecteplase plena 1–3 h antes<br/>(ASSENT-4 PCI)"| C1(["Não. Parou por morte hospitalar 6% vs 3%<br/>Primário 90 d 19% vs 13% RR 1,39<br/>AVC 1,8% vs 0"])

  D1 -->|"Meia reteplase + abciximabe<br/>ou abciximabe pré-ICP (FINESSE)"| C2(["Não. Primário 9,8% / 10,5% / 10,7% P=0,55<br/>Morte 90 d P=0,49. Resolução de ST não conta"])

  D1 -->|"Adjunto à lise, sem ICP de rotina<br/>(ASSENT-3 / GUSTO-V / ExTRACT)"| C3(["Outra pergunta. Ver fluxograma-lise-assent-3-gusto-v-extract"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3 conduta;
```

## Mensagem prática

**ICP primária não se facilita com lise plena (faz mal) nem com GPI/meia-lise (não ganha).** Resolução de ST no FINESSE não substitui o primário nulo.
