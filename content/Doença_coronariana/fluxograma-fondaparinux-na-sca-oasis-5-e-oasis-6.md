---
title: "Fluxograma: fondaparinux na SCA — OASIS-5 (NSTE) e OASIS-6 (IAMCSST)"
slug: fluxograma-fondaparinux-na-sca-oasis-5-e-oasis-6
theme: "Doença coronariana"
kind: fluxograma
summary: "NSTE conservador: fondaparinux 2,5 mg empata isquemia e corta sangramento maior (OASIS-5). IAMCSST com lise ou sem reperfusão: reduz morte/reinfarto (OASIS-6). ICP primária: OASIS-6 sem benefício — não usar este ensaio para autorizar. Trombose de cateter não está nos abstracts — seguir a monografia na sala."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada nos abstracts de OASIS-5 (PMID 16537663) e OASIS-6 (PMID 16537725). Trombose de cateter NÃO relida nos abstracts — a árvore não inventa cifra; aponta a monografia. Revisão científica concluída em 30/08/2026."
source_refs:
  - "Fifth Organization to Assess Strategies in Acute Ischemic Syndromes Investigators; Yusuf S, et al. OASIS-5. N Engl J Med. 2006;354(14):1464-1476. PMID: 16537663."
  - "Yusuf S, et al. OASIS-6. JAMA. 2006;295(13):1519-1530. PMID: 16537725."
  - "Documentos da casa oasis-5-fondaparinux-versus-enoxaparina-na-sca, oasis-6-fondaparinux-no-iamcsst e fondaparinux-sodico."
---

# Fluxograma: fondaparinux na SCA

```mermaid
flowchart TD
  R0["SCA e alguém propôs fondaparinux 2,5 mg"] --> D1{"Qual o quadro?"}

  D1 -->|"NSTE, estratégia conservadora<br/>ou sem ICP imediata"| C1(["Fondaparinux 2,5 mg/d.<br/>OASIS-5: isquemia 9 d 5,8% vs 5,7%.<br/>Sangramento maior 2,2% vs 4,1%"])

  D1 -->|"IAMCSST com lise<br/>ou sem reperfusão"| C2(["Fondaparinux 2,5 mg até 8 d.<br/>OASIS-6: morte/reinfarto 30 d 9,7% vs 11,2%.<br/>Tamponade 28 vs 48"])

  D1 -->|"ICP primária"| C3(["Não. OASIS-6: sem benefício neste estrato.<br/>Heparina da árvore HEAT/VALIDATE"])

  D1 -->|"Já na mesa de ICP<br/>tendo recebido fondaparinux"| C4(["Não inventar trombose de cateter aqui.<br/>Seguir a monografia/árvore de dose da casa"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4 conduta;
```

## Mensagem prática

**Fondaparinux ganha onde não há ICP primária.** OASIS-5 (NSTE) e OASIS-6 (lise/sem reperfusão) são populações distintas; nenhum dos dois autoriza o uso na ICP primária.
