---
title: "Fluxograma: o que não prescrever para esforço na ICFEp"
slug: fluxograma-o-que-nao-prescrever-para-esforco-na-icfep
theme: "Insuficiência cardíaca"
kind: fluxograma
summary: "ICFEp com intolerância ao esforço. Sildenafila (RELAX) VO2 NS. Mononitrato (NEAT) reduz horas de atividade. Nitrito inalado (INDIE) VO2 NS. Vericiguat (VITALITY) KCCQ-PLS NS — e VICTORIA é ICFEr. Espironolactona 100 mg na agudização (ATHENA-HF) não baixa NT-proBNP. Dopamina/nesiritida 'renal' (ROSE) NS."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em RELAX PMID 23478662, NEAT PMID 26549714, INDIE PMID 30398602, VITALITY PMID 33079152, ATHENA-HF PMID 28700781, ROSE PMID 24247300. Não promover STEP/SUMMIT (incretina) neste fluxograma — outros arquivos. Revisão científica concluída em 30/08/2026."
source_refs:
  - "Redfield MM, et al. RELAX. JAMA. 2013;309(12):1268-1277. PMID: 23478662."
  - "Redfield MM, et al. NEAT-HFpEF. N Engl J Med. 2015;373(24):2314-2324. PMID: 26549714."
  - "Borlaug BA, et al. INDIE-HFpEF. JAMA. 2018;320(17):1764-1773. PMID: 30398602."
  - "Armstrong PW, et al. VITALITY-HFpEF. JAMA. 2020;324(15):1512-1521. PMID: 33079152."
  - "Butler J, et al. ATHENA-HF. JAMA Cardiol. 2017;2(9):950-958. PMID: 28700781."
  - "Chen HH, et al. ROSE-AHF. JAMA. 2013;310(23):2533-2543. PMID: 24247300."
---

# Fluxograma: ICFEp — o que o esforço **não** pede

```mermaid
flowchart TD
  R0["ICFEp e queixa de esforço ou congestão"] --> D1{"O que alguém quer prescrever?"}

  D1 -->|"Sildenafila / PDE-5"| C1(["RELAX: VO2 −0,20 vs −0,20; P=0,90"])

  D1 -->|"Mononitrato de isossorbida"| C2(["NEAT: menos horas ativas; P=0,02<br/>Primário do acelerômetro P=0,06 contra o nitrato"])

  D1 -->|"Nitrito inalado"| C3(["INDIE: VO2 13,5 vs 13,7; P=0,27"])

  D1 -->|"Vericiguat"| C4(["VITALITY: KCCQ-PLS NS.<br/>VICTORIA/VICTOR são ICFEr"])

  D1 -->|"Espironolactona 100 mg na agudização"| C5(["ATHENA-HF: NT-proBNP 96 h P=0,57<br/>Não é TOPCAT, não é RALES"])

  D1 -->|"Dopamina ou nesiritida 'dose renal'"| C6(["ROSE-AHF: diurese e cistatina NS"])

  classDef conduta fill:#f8e8e8,stroke:#8a2f2f,color:#3a1010;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## Mensagem prática

**A via NO/cGMP na ICFEp de esforço acumulou negativos (RELAX, NEAT, INDIE, VITALITY).** Não improvisar vasodilatador, nitrato ou MRA de 100 mg na agudização com esses papers na gaveta.
