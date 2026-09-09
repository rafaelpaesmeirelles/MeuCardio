---
title: 'Fluxograma: anticoagulação pelo CHA₂DS₂-VA — ESC 2024'
slug: fluxograma-anticoagulacao-cha2ds2-va-esc-2024
theme: Fibrilação atrial
kind: fluxograma
review_status: revisado
source_refs:
- Van Gelder IC, Rienstra M, Bunting KV, et al.; ESC Scientific Document Group. 2024 ESC Guidelines for the management of
  atrial fibrillation developed in collaboration with the European Association for Cardio-Thoracic Surgery (EACTS). Eur Heart
  J. 2024;45(36):3314-3414. DOI 10.1093/eurheartj/ehae176. PMID 39210723.
- Damman K, Herrington WG, et al. 2026 ESC Guidelines for the management of cardiovascular disease and chronic kidney disease,
  in collaboration with the European Renal Association (ERA). Eur Heart J. 2026. DOI 10.1093/eurheartj/ehag098. PMID 42661426.
review_note: Árvore revisada para evitar anticoagulação apenas por TFGe e omissão de exceções valvares/cardiomiopatias. Corrigida
  exclusão absoluta de FA de dispositivo; dose individual e decisões de escore separadas. Conexões temáticas selecionadas
  e links por slugs da fila conferidos.
summary: Aplicável à avaliação de prevenção tromboembólica de longo prazo na FA clínica. Gestação, cardioversão, prótese mecânica,
  estenose mitral moderada/grave e FA subclínica detectada por dispositivo exigem avaliação específica. Um alerta de pulso
  irregular sem confirmação elétrica não basta para diagnosticar FA.
tags: []
source_tier: A
gaps: []
published: true
---

# Fluxograma: anticoagulação pelo CHA₂DS₂-VA — ESC 2024

Aplicável à avaliação de prevenção tromboembólica de longo prazo na FA clínica. Gestação, cardioversão, prótese mecânica, estenose mitral moderada/grave e FA subclínica detectada por dispositivo exigem avaliação específica. Um alerta de pulso irregular sem confirmação elétrica não basta para diagnosticar FA.

```mermaid
flowchart TD
  R["FA clínica confirmada por registro elétrico"] --> E{"Prótese mecânica ou estenose<br/>mitral moderada/grave?"}
  E -->|Sim| V(["Estratégia com AVK conforme<br/>doença valvar e protocolo específico"])
  E -->|Não| H{"Cardiomiopatia hipertrófica<br/>ou amiloidose cardíaca?"}
  H -->|Sim| A(["Avaliar anticoagulação indicada<br/>independentemente do escore"])
  H -->|Não| S{"CHA₂DS₂-VA"}
  S -->|0| B(["Geralmente sem anticoagulação crônica<br/>pelo escore; reavaliar risco"])
  S -->|1| C(["Considerar anticoagulação<br/>em decisão individual"])
  S -->|≥2| D(["Anticoagulação recomendada"])
  A --> F["Verificar contraindicações, sangramento,<br/>função renal, interações e preferência"]
  C --> F
  D --> F
  F --> G(["Se indicada e elegível: preferir DOAC.<br/>Dose específica; individualizar na DRC avançada"])
```

A idade ≥75 e o antecedente de AVC/AIT/tromboembolismo arterial valem dois pontos cada. IC, hipertensão, diabetes, doença vascular e idade 65–74 valem um cada; sexo não pontua e faixas etárias não se somam. Mulher de 66 anos com hipertensão tem escore 2.

A avaliação hemorrágica identifica fatores corrigíveis; não deve ser usada isoladamente para negar anticoagulação indicada. Não reduzir dose de DOAC sem critérios próprios da molécula. A função renal deve ser calculada pelo método exigido pela bula. Na DRC avançada/diálise, o escore tem limitações e a decisão precisa considerar benefício, risco e equipe especializada.

AF-CARE permanece em todos os ramos: comorbidades, prevenção de AVC, sintomas e reavaliação. Fonte: [ESC FA 2024](https://doi.org/10.1093/eurheartj/ehae176).

## Tudo com Tudo

- [CHA₂DS₂-VA: o sexo saiu do escore — ESC 2024 de FA](/biblioteca/cha2ds2-va-esc-2024-sexo-saiu-do-escore)
- [ESC 2026: IC e FA — o que muda na ficha conjunta](/biblioteca/esc-2026-ic-e-fa-o-que-muda-na-ficha-conjunta)
- [Estabilizador vs silenciador na ATTR-CM](/biblioteca/estabilizador-vs-silenciador-na-attr-cm)
