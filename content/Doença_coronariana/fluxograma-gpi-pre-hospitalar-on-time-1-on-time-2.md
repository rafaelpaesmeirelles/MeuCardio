---
title: 'Fluxograma: tirofibana pré-hospitalar — On-TIME 1 (TIMI 3 NS) vs On-TIME 2 (desvio de ST)'
slug: fluxograma-gpi-pre-hospitalar-on-time-1-on-time-2
theme: Doença coronariana
kind: fluxograma
summary: 'On-TIME 1: primário TIMI 3 19% vs 15% P=0,22; morte/IAM 1 a 7% vs 7%. On-TIME 2: primário ST 3,6 vs 4,8 mm; análise
  combinada posterior avaliou MACE, sem redução significativa de mortalidade isolada.'
review_status: revisado
fonte_producao: grok
review_note: 'Conferidos PMID 15140531/18707985/20510211: On-TIME 1 compara início precoce/tardio; On-TIME 2 inclui primário
  eletrocardiográfico e análise combinada pré-especificada de 1.398. Mantidos MACE positivo e mortalidade não significativa;
  removido ramo não referenciado de outra molécula.'
source_refs:
- 'van ''t Hof AW, et al. On-TIME. Eur Heart J. 2004;25(10):837-846. PMID: 15140531.'
- 'Van''t Hof AW, et al. On-TIME 2. Lancet. 2008;372(9638):537-546. PMID: 18707985.'
- 'ten Berg JM et al. Effect of early, pre-hospital initiation of high bolus dose tirofiban in patients with ST-segment elevation
  myocardial infarction on short- and long-term clinical outcome. J Am Coll Cardiol. 2010;55:2446-2455. DOI: 10.1016/j.jacc.2009.11.091.
  PMID: 20510211.'
tags: []
source_tier: A
gaps: []
published: true
---

# Fluxograma: GPI no caminho da ICP primária

```mermaid
flowchart TD
  R0["Tirofibana antes da sala?"] --> D1{"Qual o ensaio?"}

  D1 -->|"On-TIME 1, n=507"| C1(["Primário TIMI 3: 19% vs 15% P=0,22<br/>Morte/IAM 1 a: 7% vs 7%"])

  D1 -->|"On-TIME 2, n=984"| C2(["Primário: desvio residual de ST<br/>Primário de reperfusão; ver análise clínica combinada abaixo"])


  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2 conduta;
```

## Mensagem prática

O primário do On-TIME 1 foi neutro. A fase duplo-cega do On-TIME 2 avaliou reperfusão, mas não esgota o programa: a análise combinada pré-especificada de 1.398 participantes das fases aberta e duplo-cega (PMID 20510211) encontrou MACE em 30 dias de 5,8% versus 8,6% (p=0,043). A mortalidade isolada não teve redução estatisticamente significativa em 30 dias (p=0,051) ou um ano (p=0,08). Isso não demonstra benefício de mortalidade nem autoriza tirofibana pré-hospitalar rotineira no cuidado contemporâneo.

No On-TIME 1, o comparador foi tirofibana iniciada no laboratório de cateterismo; no On-TIME 2, foi ausência de tirofibana/placebo, conforme a fase. Não confundir antecipação da mesma terapia com adição de terapia.

## Tudo com Tudo

- [On-TIME 2: tirofibana pré-hospitalar e reperfusão na ICP primária](/biblioteca/on-time-2-tirofibana-pre-hospitalar-no-iamcsst-com-icp) — Liga o fluxograma ao On-TIME 2, preservando desvio de ST como primário e distinguindo TIMI 3 do On-TIME 1.
