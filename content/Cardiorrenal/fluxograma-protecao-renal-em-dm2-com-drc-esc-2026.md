---
kind: fluxograma
published: true
review_note: Conferidos ensaios primários e tabelas ESC 2026 pertinentes; corrigidos
  limites de população, segurança, doses ou interpretação quando aplicável.
review_status: revisado
slug: fluxograma-protecao-renal-em-dm2-com-drc-esc-2026
source_refs:
- 'Damman K, Herrington WG, ter Maaten JM, et al. 2026 ESC Guidelines for the management
  of cardiovascular disease and chronic kidney disease, in collaboration with the
  European Renal Association (ERA). Eur Heart J. 2026. DOI: 10.1093/eurheartj/ehag098.
  PMID: 42661426.'
- 'Perkovic V, Tuttle KR, Rossing P, et al. Effects of Semaglutide on Chronic Kidney
  Disease in Patients with Type 2 Diabetes. N Engl J Med. 2024;391(2):109-121. DOI:
  10.1056/NEJMoa2403347. PMID: 38785209. NCT03819153.'
- 'Bakris GL, Agarwal R, Anker SD, et al.; FIDELIO-DKD Investigators. Effect of Finerenone
  on Chronic Kidney Disease Outcomes in Type 2 Diabetes. N Engl J Med. 2020;383(23):2219-2229.
  DOI: 10.1056/NEJMoa2025845. PMID: 33264825. NCT02540993.'
- FDA. Kerendia prescribing information, 07/2025, seções 2 e 4. https://www.accessdata.fda.gov/drugsatfda_docs/label/2025/215341s009lbl.pdf
- Pitt B, et al. FIGARO-DKD. PMID 34449181.
- McGuire DK, et al. SOUL. PMID 40162642.
theme: Diabetes e cardiologia
title: 'Fluxograma: proteção renal no DM2 com DRC — ESC 2026 CVD-CKD'
---

# Fluxograma: proteção renal no DM2 com DRC — ESC 2026 CVD-CKD

Pergunta desta árvore: **neste paciente com diabetes tipo 2 e DRC, o que a ESC 2026 (Damman, PMID 42661426) recomenda para reduzir falência renal e eventos cardiovasculares?** Folhas verdes são condutas. Não mistura dose de semaglutida (1,0 mg SC ≠ 14 mg oral ≠ 2,4 mg). Não suspende IECA/BRA para “abrir espaço”.

A porta de rastreio (todo paciente com DCV, TFGe + RAC) está no fluxograma STAMP ([Fluxograma STAMP-on-CKD: rastreio e conduta na diretriz ESC 2026 de DCV e DRC](/biblioteca/fluxograma-stamp-on-ckd-esc-2026)). Esta árvore começa **depois** do diagnóstico de DRC no DM2.

## Árvore de decisão

```mermaid
flowchart TD
 R0["DM2 e DRC confirmada: avaliar cada camada em paralelo"] --> D0{"IECA/BRA indicado e tolerado?"}
 D0 -->|Sim| A0(["Titular um IECA OU um BRA conforme pressão, K e TFGe. Não combinar os dois."])
 D0 -->|Não| A1(["Documentar motivo e avaliar as demais opções sem atrasar proteção indicada."])
 R0 --> D1{"TFGe ≥20 mL/min/1,73 m²?"}
 D1 -->|Sim| A2(["Considerar segurança e iniciar iSGLT2 para DRC com DM2: I A, independentemente da glicemia."])
 D1 -->|Não| A3(["Não iniciar por este ramo. Distinguir início de continuação e discutir nefrologia."])
 R0 --> D2{"TFGe ≥25, RAC ≥30 mg/g, K ≤5,0 e sem contraindicação à finerenona?"}
 D2 -->|Sim| A4(["Finerenona: I A para DRC com DM2. Monitorar K, TFGe e interações; não duplicar ARM."])
 D2 -->|Não| A5(["Não iniciar finerenona por esta indicação; resolver fatores reversíveis e avaliar outras indicações."])
 R0 --> D3{"TFGe 25–49 com RAC ≥100 mg/g OU TFGe 50–74 com RAC ≥300 mg/g?"}
 D3 -->|Sim| A6(["Semaglutida SC 1,0 mg semanal após titulação: I A. Avaliar contraindicações e tolerância."])
 D3 -->|Não| A7(["Não extrapolar o benefício renal do FLOW a outra dose ou população. Avaliar indicação glicêmica/CV separadamente."])
 classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
 class A0,A1,A2,A3,A4,A5,A6,A7 conduta;
```

## O que a árvore não mostra

**Camadas, não rodízio.** IECA/BRA + iSGLT2 + finerenona + semaglutida 1,0 mg SC podem ser combinados quando indicados e tolerados, sem presumir soma matemática dos benefícios. O FLOW não autoriza suspender iSGLT2: o uso basal de iSGLT2 não era universal; a avaliação da combinação não substitui a evidência própria de cada fármaco.

**SOUL não substitui C6.** Semaglutida oral 14 mg reduziu MACE (12,0% vs 13,8%; HR 0,86; 0,77–0,96; P=0,006; n=9.650). O composto renal do SOUL **não** foi positivo. Quem recusa injeção recebe o SOUL pela porta de MACE, não por esta folha renal.

**Finerenona e hipercalemia.** FIDELIO-DKD: descontinuação por hipercalemia **2,3% vs 0,9%**. FIGARO-DKD (Pitt, PMID 34449181): descontinuação **1,2% vs 0,4%**; composto de morte CV, IAM/AVC não fatais ou internação por IC de 12,4% vs 14,2%; HR 0,87 (0,76–0,98). FIDELIO/FIGARO usaram K ≤4,8 mmol/L na seleção; a bula FDA não recomenda iniciar se K >5,0 e exige monitoramento. Não intercambiar critério de ensaio e de prescrição.

**iSGLT2 sem diabetes.** A ESC 2026 também recomenda iSGLT2 em DRC **sem** diabetes com TFGe ≥20 e RAC ≥20 mg/mmol (≥200 mg/g) — Classe I A. Esse ramo não está nesta árvore porque a raiz é DM2.

## Números que cabem nas folhas

- FLOW (PMID 38785209): n=3.533; 331 vs 410; HR 0,76 (0,66–0,88); P=0,0003; mediana 3,4 anos; dose 1,0 mg SC semanal.
- FIDELIO-DKD (PMID 33264825): 504/2.833 (17,8%) vs 600/2.841 (21,1%); HR 0,82 (0,73–0,93); P=0,001; mediana 2,6 anos.
- Classes I A da ESC 2026 CVD-CKD: iSGLT2; finerenona no recorte TFGe ≥25 + RAC ≥3 mg/mmol; semaglutida SC 1,0 mg no recorte FLOW da tabela.

## Tudo com Tudo

Cardiorrenal · Diabetes e cardiologia · Insuficiência cardíaca · Farmacologia · Prevenção e lipídios · Comunicação clínica.
