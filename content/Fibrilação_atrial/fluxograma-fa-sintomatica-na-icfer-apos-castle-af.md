---
title: 'Fluxograma: FA sintomática na ICFEr após CASTLE-AF'
slug: fluxograma-fa-sintomatica-na-icfer-apos-castle-af
theme: Fibrilação atrial
kind: fluxograma
review_status: revisado
source_refs:
- Marrouche NF, et al. Catheter Ablation for Atrial Fibrillation with Heart Failure. N Engl J Med. 2018;378:417-427. PMID
  29385358.
- Køber L et al. ESC 2026 heart failure. DOI 10.1093/eurheartj/ehag100. PMID 42661420.
review_note: 'CASTLE-AF e ESC 2026 conferidos: corrigido ramo que chamava toda FEVE >35% de preservada, distinção de CDI prévio
  e otimização em paralelo sem impedir avaliação de ablação. Conexões temáticas selecionadas e links por slugs da fila conferidos.'
summary: 'CASTLE-AF: FEVE ≤35%, CDI, FA sintomática. Composto morte/hosp. IC 28,5% vs 44,6%; HR 0,62. Não é ICFEp. ESC 2026:
  ablação por cateter IIa C em selecionados com FA sintomática e HFrEF; o ensaio tinha recorte mais estreito.'
tags: []
source_tier: A
gaps: []
published: true
---

# Fluxograma: FA sintomática na ICFEr após CASTLE-AF

CASTLE-AF: FEVE ≤35%, CDI, FA sintomática. Composto morte/hosp. IC 28,5% vs 44,6%; HR 0,62. Não é ICFEp. ESC 2026: ablação por cateter IIa C em selecionados com FA sintomática e HFrEF; o ensaio tinha recorte mais estreito.

## Árvore de decisão

```mermaid
flowchart TD
  X0["Paciente com FA e IC"]
  D0{"FEVE ≤ 35% — recorte CASTLE-AF?"}
  C0(["FEVE >35% está fora deste recorte do ensaio; não equivale necessariamente a ICFEp. Avaliar diretriz e fenótipo individual"])
  D1{"CDI já implantado — como no ensaio?"}
  C1(["Fora do recorte de dispositivo do ensaio. Avaliar indicação de CDI e ablação individualmente; não implantar CDI só para reproduzir CASTLE-AF"])
  D2{"FA sintomática — não resposta, intolerância ou recusa de antiarrítmico?"}
  C2(["FA oligossintomática: CASTLE-AF não é ensaio de ablação profilática. Otimizar quádrupla e frequência"])
  D3{"Quádrupla da ICFEr em curso?"}
  C3(["Otimizar terapias toleradas de IC em paralelo à avaliação de ritmo; ablação não substitui a base"])
  C4(["Discutir ablação de FA: composto 51/179 vs 82/184; HR 0,62. Morte 13,4% vs 25,0%. Centro de FA+IC"])
  C5(["Manter estratégia médica de ritmo/frequência se ablação inviável ou recusada. Recalcular CHA2DS2-VA"])

  X0 --> D0
  D0 -->|"Não — FEVE >35%"| C0
  D0 -->|"Sim"| D1
  D1 -->|"Não discutido"| C1
  D1 -->|"Sim"| D2
  D2 -->|"Não"| C2
  D2 -->|"Sim"| D3
  D3 -->|"Base incompleta"| C3
  D3 -->|"Base feita — paciente concorda com ablação"| C4
  D3 -->|"Ablação inviável ou recusada"| C5

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f
  class C0,C1,C2,C3,C4,C5 conduta
```

## Tudo com Tudo

- [CASTLE-AF: ablação de FA na IC com FE reduzida](/biblioteca/castle-af-ablacao-de-fa-na-ic-com-fe-reduzida)
- [ESC 2026: IC e FA — o que muda na ficha conjunta](/biblioteca/esc-2026-ic-e-fa-o-que-muda-na-ficha-conjunta)
- [Quando ablação de FA na IC: o que CASTLE-AF e a ESC 2026 separam](/biblioteca/quando-ablacao-de-fa-na-ic-o-que-castle-af-e-a-esc-2026-separam)
