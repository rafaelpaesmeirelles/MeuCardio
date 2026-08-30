---
title: "Fluxograma: ultrafiltração na IC aguda — UNLOAD (peso sim, dispneia NS) vs CARRESS-HF (UF inferior no rim)"
slug: fluxograma-ultrafiltracao-unload-carress
theme: "Insuficiência cardíaca"
kind: fluxograma
summary: "UNLOAD n=200: peso 48 h sim, dispneia coprimário NS, reinternação secundária. CARRESS-HF n=188: UF inferior no bivariado creatinina+peso; mais SAE. Não fundir."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em UNLOAD PMID 17291932 e CARRESS-HF PMID 23131078. Revisão científica concluída em 30/08/2026."
source_refs:
  - "Costanzo MR, et al. UNLOAD. J Am Coll Cardiol. 2007;49(6):675-683. PMID: 17291932."
  - "Bart BA, et al. CARRESS-HF. N Engl J Med. 2012;367(24):2296-2304. PMID: 23131078."
  - "Documento da casa dose-furosemida-bolus-versus-infusao-alta-versus-baixa-na-ic-aguda."
---

# Fluxograma: máquina versus diurético

```mermaid
flowchart TD
  R0["Congestão na IC aguda"] --> D1{"Qual o ensaio?"}

  D1 -->|"Hipervolemia sem exigir LRA"| C1(["UNLOAD: peso sim, dispneia NS<br/>Reinternação 90 d é secundário, n=200"])

  D1 -->|"Piora renal + congestão persistente"| C2(["CARRESS-HF: UF inferior no primário<br/>Creatinina sobe. Peso igual. Mais SAE"])

  D1 -->|"Só via/intensidade da furosemida?"| C3(["DOSE — coprimários NS"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3 conduta;
```

## Mensagem prática

**UNLOAD tira peso; CARRESS mostra custo renal.** Não usar um para apagar o outro.
