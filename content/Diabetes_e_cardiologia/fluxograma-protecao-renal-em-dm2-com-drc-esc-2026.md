---
title: 'Fluxograma: proteção renal no DM2 com DRC — ESC 2026 CVD-CKD'
slug: fluxograma-protecao-renal-em-dm2-com-drc-esc-2026
theme: Diabetes e cardiologia
kind: fluxograma
review_status: revisado
source_refs:
- 'Damman K, Herrington WG, ter Maaten JM, et al. 2026 ESC Guidelines for the management of cardiovascular disease and chronic
  kidney disease, in collaboration with the European Renal Association (ERA). Eur Heart J. 2026. DOI: 10.1093/eurheartj/ehag098.
  PMID: 42661426.'
- 'Perkovic V, Tuttle KR, Rossing P, et al. Effects of Semaglutide on Chronic Kidney Disease in Patients with Type 2 Diabetes.
  N Engl J Med. 2024;391(2):109-121. DOI: 10.1056/NEJMoa2403347. PMID: 38785209. NCT03819153.'
- 'Bakris GL, Agarwal R, Anker SD, et al.; FIDELIO-DKD Investigators. Effect of Finerenone on Chronic Kidney Disease Outcomes
  in Type 2 Diabetes. N Engl J Med. 2020;383(23):2219-2229. DOI: 10.1056/NEJMoa2025845. PMID: 33264825. NCT02540993.'
- FDA. Kerendia (finerenone) prescribing information, 2025. https://www.accessdata.fda.gov/drugsatfda_docs/label/2025/215341s009lbl.pdf
- FLOW baseline SGLT2 analysis. PMID:38914124. DOI:10.1038/s41591-024-03133-0
- SOUL. PMID:40162642. DOI:10.1056/NEJMoa2501006
review_note: 'ESC2026tabelas farmacológicas conferidas; reconectadafolhaIECA/BRA ao restodofluxo; separadocritérioK≤4.8ensaios
  deK≤5bula; FIGAROcompostoCVnãoMACE3p. Vínculos conferidos por slug e pertinência clínica: flow-semaglutida-dm2-e-doenca-renal-cronica,
  finearts-nao-e-figaro-nem-fidelio, fluxograma-stamp-on-ckd-esc-2026.'
summary: 'Pergunta desta árvore: neste paciente com diabetes tipo 2 e DRC, o que a ESC 2026 (Damman, PMID 42661426) recomenda
  para reduzir falência renal e eventos cardiovasculares? Folhas verdes são condutas. Não mistura dose de semaglutida (1,0
  mg SC ≠ 14 mg oral ≠ 2,4 mg). Não suspende IECA/BRA para “abrir espaço”.'
tags: []
source_tier: A
gaps: []
published: true
---

# Fluxograma: proteção renal no DM2 com DRC — ESC 2026 CVD-CKD

Pergunta desta árvore: **neste paciente com diabetes tipo 2 e DRC, o que a ESC 2026 (Damman, PMID 42661426) recomenda para reduzir falência renal e eventos cardiovasculares?** Folhas verdes são condutas. Não mistura dose de semaglutida (1,0 mg SC ≠ 14 mg oral ≠ 2,4 mg). Não suspende IECA/BRA para “abrir espaço”.

A porta de rastreio (todo paciente com DCV, TFGe + RAC) está no fluxograma STAMP ([Fluxograma STAMP-on-CKD: rastreio e conduta na diretriz ESC 2026 de DCV e DRC](/biblioteca/fluxograma-stamp-on-ckd-esc-2026)). Esta árvore começa **depois** do diagnóstico de DRC no DM2.

## Árvore de decisão

```mermaid
flowchart TD
    R0["DM2 com DRC confirmada<br/>TFGe + RAC persistentes ≥3 meses"] --> D1{"IECA ou BRA na dose máxima tolerada?"}

    D1 -->|"Não, e não há contraindicação"| C1(["Iniciar ou titular IECA ou BRA.<br/>Base da proteção renal na DRC albuminúrica.<br/>Não substituir por iSGLT2 nem por GLP-1."])
    C1 --> D2
    D1 -->|"Sim, ou intolerância documentada"| D2{"iSGLT2 indicado pela TFGe?"}

    D2 -->|"TFGe ≥20 mL/min/1,73 m²"| C2(["iSGLT2 recomendado — Classe I A<br/>na ESC 2026 CVD-CKD.<br/>Não suspender por causa do GLP-1."])
    D2 -->|"TFGe abaixo do recorte da tabela"| C3(["Não iniciar iSGLT2 por este fluxograma.<br/>Rever tabela da diretriz e nefrologia.<br/>Não inventar corte."])

    C2 --> D3{"Finerenona — ARM não esteroide"}
    C3 --> D3

    D3 -->|"TFGe ≥25 e RAC ≥3 mg/mmol<br/>≥30 mg/g"| C4(["Finerenona recomendada — Classe I A.<br/>FIDELIO-DKD: 504/2833 vs 600/2841<br/>HR 0,82; IC95% 0,73–0,93; P=0,001.<br/>Avaliar K antes e após início.<br/>Não iniciar se K acima de 5,0 mmol/L."])
    D3 -->|"Fora deste recorte"| C5(["Finerenona não entra por esta linha da ESC 2026.<br/>Se houver IC, ir à ficha de ARM independente da FEVE."])

    C4 --> D4{"Semaglutida 1,0 mg SC semanal"}
    C5 --> D4

    D4 -->|"TFGe 25–49 e RAC ≥10 mg/mmol<br/>≥100 mg/g<br/>OU TFGe 50–74 e RAC ≥30 mg/mmol<br/>≥300 mg/g"| C6(["GLP-1 RA: semaglutida SC 1,0 mg/semana<br/>após titulação — Classe I A.<br/>FLOW: 331 vs 410; HR 0,76;<br/>IC95% 0,66–0,88; P=0,0003.<br/>Não é oral 14 mg. Não é 2,4 mg."])
    D4 -->|"Fora do recorte FLOW da tabela"| C7(["Não usar FLOW para autorizar outra dose.<br/>SOUL (oral 14 mg) é MACE, não composto renal positivo."])

    classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
    class C1,C2,C3,C4,C5,C6,C7 conduta;
```

## O que a árvore não mostra

**Camadas, não rodízio.** IECA/BRA + iSGLT2 + finerenona + semaglutida 1,0 mg SC somam-se quando cada recorte é preenchido. O FLOW não autoriza suspender iSGLT2: o subgrupo com iSGLT2 basal foi pequeno (n=550) e o P de interação para o primário foi 0,109.

**SOUL não substitui C6.** Semaglutida oral 14 mg reduziu MACE (12,0% vs 13,8%; HR 0,86; 0,77–0,96; P=0,006; n=9.650). O composto renal do SOUL **não** foi positivo. Para quem prefere via oral, a evidência do SOUL pode embasar discussão da prevenção de MACE, conforme indicação e elegibilidade, não por esta folha renal.

**Finerenona e hipercalemia.** FIDELIO-DKD: descontinuação por hipercalemia **2,3% vs 0,9%**. FIGARO-DKD (Pitt, PMID 34449181): descontinuação **1,2% vs 0,4%**; composto CV incluindo hospitalização por IC: 12,4% vs 14,2%; HR 0,87 (0,76–0,98). A bula FDA não recomenda iniciar finerenona com TFGe <25 e orienta não iniciar com K >5,0 mmol/L; no FIDELIO/FIGARO, o limite de K para entrada no ensaio foi ≤4,8. Não confundir critérios de ensaio com bula. Reavaliar K/função renal em quatro semanas e após ajustes.

**iSGLT2 sem diabetes.** A ESC 2026 também recomenda iSGLT2 em DRC **sem** diabetes com TFGe ≥20 e RAC ≥20 mg/mmol (≥200 mg/g) — Classe I A. Esse ramo não está nesta árvore porque a raiz é DM2.

## Números que cabem nas folhas

- FLOW (PMID 38785209): n=3.533; 331 vs 410; HR 0,76 (0,66–0,88); P=0,0003; mediana 3,4 anos; dose 1,0 mg SC semanal.
- FIDELIO-DKD (PMID 33264825): 504/2.833 (17,8%) vs 600/2.841 (21,1%); HR 0,82 (0,73–0,93); P=0,001; mediana 2,6 anos.
- Classes I A da ESC 2026 CVD-CKD: iSGLT2; finerenona no recorte TFGe ≥25 + RAC ≥3 mg/mmol; semaglutida SC 1,0 mg no recorte FLOW da tabela.

## Tudo com Tudo

Cardiorrenal · Diabetes e cardiologia · Insuficiência cardíaca · Farmacologia · Prevenção e lipídios · Comunicação clínica.

### Leituras conectadas

- [FLOW: semaglutida 1,0 mg subcutânea e desfechos renais e cardiovasculares no DM2 com DRC](/biblioteca/flow-semaglutida-dm2-e-doenca-renal-cronica)
- [FINEARTS-HF não é FIGARO-DKD nem FIDELIO-DKD](/biblioteca/finearts-nao-e-figaro-nem-fidelio)
- [Fluxograma STAMP-on-CKD: rastreio e conduta na diretriz ESC 2026 de DCV e DRC](/biblioteca/fluxograma-stamp-on-ckd-esc-2026)
