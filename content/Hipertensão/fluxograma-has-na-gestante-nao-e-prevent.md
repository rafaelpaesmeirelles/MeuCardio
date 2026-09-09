---
kind: fluxograma
published: true
review_note: Revisão integral do recorte ESC 2025, tabelas visuais 12/13/20, Figura
  22 e AHA 2025/CHAP. Confirmado AAS prevenção I A e dose distinta de SCA. Fluxos
  sem convergência e sem estádio intermediário; choque inclui pré-viabilidade e suporte
  em paralelo. SCAD estável não implica ICP, BP alvo não aplicado ao choque, gestante
  138/88 sem HAS não inicia fármaco automaticamente.
review_status: revisado
slug: fluxograma-has-na-gestante-nao-e-prevent
source_refs:
- De Backer J, et al. 2025 ESC Guidelines for the management of cardiovascular disease
  and pregnancy. Eur Heart J. 2025. PMID 40878294.
- ESC gravidez 2025, tabelas 12, 13 e 20 e Figuras 11/22 conferidas. https://academic.oup.com/eurheartj/article/46/43/4462/8234487
theme: Hipertensão
title: 'Fluxograma: HAS na gestante — não é PREVENT'
---

# Fluxograma: HAS na gestante — não é PREVENT

ESC 2025 gravidez: visar **< 140/90** (I B). HAS = ≥ 140 e/ou ≥ 90. AHA 2025 <130/80 e PREVENT 7,5% **não** reescrevem o pré-natal. Nós finais duplicados.

## Árvore de decisão

```mermaid
flowchart TD
  X0["Mulher com PA elevada; avaliar sintomas de alarme e estabilidade"]
  D0{"Está grávida — porta ESC 2025 DCV e gravidez?"}
  C0(["Não gestante: meta AHA 2025 menor 130/80 e PREVENT 7,5% — outra ficha"])
  D1{"PA ≥ 140 e/ou ≥ 90 em medidas repetidas?"}
  C1(["PA atual abaixo de 140/90: não diagnosticar nova HAS por esta medida; se já tratada, não suspender automaticamente"])
  D2{"PA ≥ 160 e/ou ≥ 110 — hipertensão grave da ESC 2025?"}
  C2(["Grave: labetalol IV, urapidil, nicardipina ou nifedipina oral curta / metildopa — I C. Hidralazina IV segunda linha. Internar"])
  D3{"Há proteinúria, disfunção materna ou uteroplacentária — pré-eclâmpsia?"}
  C3(["Suspeita de pré-eclâmpsia: avaliação obstétrica urgente, gravidade materno-fetal e plano terapêutico; alvo não substitui manejo da síndrome"])
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

- Hipertensão
- Gravidez
- Comunicação clínica
- Terapia intensiva
- Cardiologia geriátrica
Sintomas neurológicos, dor epigástrica, dispneia, convulsão ou deterioração materno-fetal exigem avaliação imediata, mesmo sem PA grave documentada. Hipertensão prévia controlada continua sendo diagnóstico; proteinúria não é obrigatória para pré-eclâmpsia com disfunção de órgão-alvo.
