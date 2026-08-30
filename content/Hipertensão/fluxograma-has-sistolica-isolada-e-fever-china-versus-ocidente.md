---
title: "Fluxograma: HAS sistólica isolada e FEVER — China (Syst-China, FEVER) vs Ocidente (SHEP, Syst-Eur, HYVET)"
slug: fluxograma-has-sistolica-isolada-e-fever-china-versus-ocidente
theme: "Hipertensão"
kind: fluxograma
summary: "PAS isolada do idoso: SHEP (clortalidona, RCT) reduz AVC; Syst-Eur (nitrendipina, RCT) reduz AVC, morte total NS; Syst-China (nitrendipina, alocação alternada) reduz AVC e morte — não equivalente ao Syst-Eur. FEVER não é PAS isolada: felodipino ER no topo de HCTZ 12,5, Δ 4/2, AVC −27%, morte −31%, IC NS, câncer secundário não vender. HYVET ≥80. Não reescreve a árvore SHEP/Syst-Eur/HYVET da casa."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Companheiro — não substitui fluxograma-has-sistolica-isolada-idoso-shep-syst-eur-hyvet. Âncoras: Syst-China PMID 9869017 (não 10647760), FEVER PMID 16269957, SHEP PMID 2046107, Syst-Eur PMID 9297994. Revisão científica concluída em 30/08/2026."
source_refs:
  - "Liu L, et al. Syst-China. J Hypertens. 1998;16(12 Pt 1):1823-1829. PMID: 9869017."
  - "Liu L, et al. FEVER. J Hypertens. 2005;23(12):2157-2172. PMID: 16269957."
  - "Documento da casa fluxograma-has-sistolica-isolada-idoso-shep-syst-eur-hyvet — árvore ocidental, não reescrita."
  - "Documento da casa shep-clortalidona-na-hipertensao-sistolica-isolada-do-idoso."
  - "Documento da casa syst-eur-nitrendipina-na-hipertensao-sistolica-isolada-do-idoso."
  - "Documento da casa tratamento-da-hipertensao-aos-80-anos-ou-mais-o-ensaio-hyvet."
---

# Fluxograma: PAS isolada e o FEVER chinês

```mermaid
flowchart TD
  R0["Hipertenso idoso ou chinês com ensaio nesta árvore"] --> D1{"Qual o fenótipo?"}

  D1 -->|"PAS isolada, Ocidente"| D2{"Qual evidência?"}
  D1 -->|"PAS isolada, China"| C1(["Syst-China: nitrendipina ± captopril ± HCTZ<br/>AVC −38% P=0,01; morte −39% P=0,003<br/>Alocação ALTERNADA — não é RCT clássico"])
  D1 -->|"HAS não isolada, China, já em HCTZ 12,5"| C2(["FEVER: felodipino ER vs placebo<br/>ΔPA 4,2/2,1; AVC −27% P=0,001<br/>Morte −31% P=0,006; IC P=0,239 NS<br/>Câncer P=0,017 — não vender"])
  D1 -->|">= 80 anos"| C3(["HYVET. Arquivo próprio.<br/>Não é SHEP nem Syst-China"])

  D2 -->|"Tiazídico"| C4(["SHEP: clortalidona<br/>AVC RR 0,64; P=0,0003<br/>Morte RR 0,87 sem p neste abstract"])
  D2 -->|"Diidropiridina"| C5(["Syst-Eur: nitrendipina<br/>AVC −42% P=0,003<br/>Morte total P=0,22 NS"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

## Mensagem prática

**PAS isolada ocidental: SHEP e Syst-Eur reduzem AVC; morte total não está fechada.** Syst-China aponta na mesma direção com nitrendipina, mas a alocação foi **alternada** — não equiparar ao Syst-Eur. FEVER é outro fenótipo (felodipino no topo de HCTZ, ΔPA pequeno, IC NS). Não reescrever a árvore SHEP/Syst-Eur/HYVET.
