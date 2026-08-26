---
title: "Fluxograma: CPVT na gestação e puerpério"
slug: fluxograma-taquicardia-ventricular-polimorfica-catecolaminergica-na-gestacao-e-puerperio
theme: "Gravidez"
kind: fluxograma
summary: "Árvore para síncope/TV em mulher com CPVT, mantendo beta-bloqueador e adicionando flecainida quando há eventos apesar da terapia."
review_status: revisado
review_note: "Conduta conferida diretamente na seção 6.2.3 da ESC 2025 (PMID 40878294): nadolol e propranolol são os betabloqueadores de escolha e devem ser mantidos durante gestação e lactação; flecainida é aditiva quando necessário. Como a própria seção remete à ressalva de lactação da seção 6.2.1, o fluxo agora explicita maior excreção do nadolol no leite, monitorização do lactente em uso de dose alta e evita troca abrupta no pós-parto."
source_refs: ["De Backer J, Haugaa KH, Hasselberg NE, et al. 2025 ESC Guidelines for the management of cardiovascular disease and pregnancy. DOI: 10.1093/eurheartj/ehaf193. PMID: 40878294."]
---

# CPVT na gestação/puerpério

```mermaid
flowchart TD
  R0["Gestante/puérpera com CPVT<br/>+ síncope, TV ou choque do ICD"]
  D1{"TV/FV instável ou PCR?"}
  C1(["Sim: cardioversão/desfibrilação<br/>e ressuscitação imediatas"])
  P1["Estável: ECG/telemetria + eletrólitos<br/>+ revisar adesão e gatilhos adrenérgicos"]
  D2{"Está em nadolol/propranolol<br/>em terapia adequada?"}
  P2["Não: restabelecer/otimizar<br/>betabloqueador especializado"]
  D3{"Síncope/TV/PCR ocorreu<br/>apesar de betabloqueador?"}
  P3["Sim: adicionar/continuar flecainida<br/>conforme eletrofisiologia"]
  D4{"Eventos recorrentes/choques ICD<br/>apesar de terapia ótima?"}
  P4["Eletrofisiologia especializada;<br/>avaliar LCSD/estratégia de dispositivo"]
  C2(["Manter terapia durante gestação,<br/>parto e pós-parto; planejar analgesia/monitorização;<br/>se nadolol em lactação, ponderar exposição<br/>do lactente sem troca abrupta pós-parto"])

  R0 --> D1
  D1 -->|"Sim"| C1
  D1 -->|"Não"| P1
  C1 --> P1
  P1 --> D2
  D2 -->|"Não"| P2
  D2 -->|"Sim"| D3
  P2 --> D3
  D3 -->|"Sim"| P3
  D3 -->|"Não"| C2
  P3 --> D4
  D4 -->|"Sim"| P4
  D4 -->|"Não"| C2
  P4 --> C2

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2 conduta;
```

## Regra prática

Na CPVT, **síncope durante estresse não é “só síncope”**. É um marcador de falha de proteção antiarrítmica até prova em contrário.

Nadolol e propranolol são escolhas da ESC para CPVT e devem ser continuados na
gestação e na lactação. A diferença prática é que o nadolol passa mais para o
leite; em dose alta, o lactente pode precisar de vigilância para bradicardia.
Isso deve ser planejado antes do parto sempre que possível — trocar o
betabloqueador abruptamente no pós-parto pode retirar proteção justamente numa
fase vulnerável.
