---
title: 'Fluxograma: HAS na gestante — não é PREVENT'
slug: fluxograma-has-na-gestante-nao-e-prevent
theme: Hipertensão
kind: fluxograma
review_status: revisado
source_refs:
- De Backer J, et al. 2025 ESC Guidelines for the management of cardiovascular disease and pregnancy. Eur Heart J. 2025. PMID
  40878294.
review_note: Fluxo confrontado com ESC2025; corrigido ramo que ignorava HAS crônica já controlada e reforçada avaliação obstétrica
  da pré-eclâmpsia, além do alvo pressórico. Conexões temáticas selecionadas e links por slugs da fila conferidos.
summary: 'ESC 2025 gravidez: visar < 140/90 (I B). HAS = ≥ 140 e/ou ≥ 90. AHA 2025 <130/80 e PREVENT 7,5% não reescrevem o
  pré-natal.'
tags: []
source_tier: A
gaps: []
published: true
---

# Fluxograma: HAS na gestante — não é PREVENT

ESC 2025 gravidez: visar **< 140/90** (I B). HAS = ≥ 140 e/ou ≥ 90. AHA 2025 <130/80 e PREVENT 7,5% **não** reescrevem o pré-natal.

## Árvore de decisão

```mermaid
flowchart TD
  X0["Mulher com PA elevada"]
  D0{"Está grávida — porta ESC 2025 DCV e gravidez?"}
  C0(["Não gestante: meta AHA 2025 menor 130/80 e PREVENT 7,5% — outra ficha"])
  D1{"PA ≥ 140 e/ou ≥ 90 em medidas repetidas?"}
  C1(["PA abaixo de 140/90: seguir pré-natal e revisar história/medicamentos. PA controlada não apaga HAS prévia"])
  D2{"PA ≥ 160 e/ou ≥ 110 — hipertensão grave da ESC 2025?"}
  C2(["Grave: labetalol IV, urapidil, nicardipina ou nifedipina oral curta / metildopa — I C. Hidralazina IV segunda linha. Internar"])
  D3{"Há proteinúria, disfunção materna ou uteroplacentária — pré-eclâmpsia?"}
  C3(["Suspeita de pré-eclâmpsia: avaliação obstétrica imediata, gravidade e indicação de parto. Visar PA menor 140/90"])
  C4(["HAS leve 140/90 a 159/109: iniciar em 140/90. Labetalol, nifedipina ou metildopa. PAD menor 80 não é alvo"])

  X0 --> D0
  D0 -->|"Não"| C0
  D0 -->|"Sim"| D1
  D1 -->|"Não"| C1
  D1 -->|"Sim"| D2
  D2 -->|"Sim — grave"| C2
  D2 -->|"Não — leve/moderada"| D3
  D3 -->|"Sim"| C3
  D3 -->|"Não"| C4

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f
  class C0,C1,C2,C3,C4 conduta
```

## Tudo com Tudo

- [Alvo 140/90 na gestante — não é a meta 130/80](/biblioteca/alvo-140-90-na-gestante-nao-e-a-meta-130-80)
- [Alvo pressórico na gestação: ESC 2025 (<140/90) e o recorte da AHA/ACC 2025](/biblioteca/alvo-pressorio-na-gestacao-esc-2025-e-aha-2025)
- [ESC 2025: doença cardiovascular e gravidez — Pregnancy Heart Team e mWHO 2.0](/biblioteca/esc-2025-doenca-cardiovascular-e-gravidez-equipe-e-mwho-20)
- [ESC 2025: insuficiência cardíaca aguda e choque na gestação](/biblioteca/esc-2025-ic-aguda-e-choque-na-gestacao)
