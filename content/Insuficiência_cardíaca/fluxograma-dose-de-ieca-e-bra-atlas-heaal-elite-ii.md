---
title: "Fluxograma: dose de IECA/BRA na ICFEr — ATLAS, HEAAL, ELITE II"
slug: fluxograma-dose-de-ieca-e-bra-atlas-heaal-elite-ii
theme: "Insuficiência cardíaca"
kind: fluxograma
summary: "IECA: não deixe em 2,5–5 mg de lisinopril (ATLAS). BRA no intolerante: 150 mg de losartana, não 50 (HEAAL); 50 mg não superou captopril (ELITE II). VAL-HeFT/CHARM-Added não autorizam BRA sobre IECA+BB hoje."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em ATLAS PMID 10587334, HEAAL PMID 19922995, ELITE II PMID 10821361, VAL-HeFT PMID 11759645. Revisão científica concluída em 30/08/2026."
source_refs:
  - "Packer M, et al. ATLAS. Circulation. 1999;100(23):2312-2318. PMID: 10587334."
  - "Konstam MA, et al. HEAAL. Lancet. 2009;374(9704):1840-1848. PMID: 19922995."
  - "Pitt B, et al. ELITE II. Lancet. 2000;355(9215):1582-1587. PMID: 10821361."
---

# Fluxograma: dose de IECA e BRA na ICFEr

```mermaid
flowchart TD
  R0["ICFEr. Alguém deixou o SRAA<br/>em dose baixa 'porque está tomando'"] --> D1{"Toma IECA e tolera?"}

  D1 -->|"Sim, em 2,5–5 mg de lisinopril<br/>ou equivalente"| C1(["Suba. ATLAS: morte P=0,128 NS;<br/>morte/internacão P=0,002 na dose alta"])

  D1 -->|"Sim, já na faixa dos ensaios<br/>ou ARNI"| C2(["Mantenha. Não some BRA por cima<br/>(VAL-HeFT tríplice; VALIANT combinação)"])

  D1 -->|"Não — tosse, angioedema"| D2{"Qual dose de losartana?"}

  D2 -->|"50 mg (dose do ELITE II)"| C3(["50 mg não superou captopril (ELITE II).<br/>HEAAL: 150 vs 50 mg, composto HR 0,90.<br/>Alvo 150 mg se tolerar K e PA"])

  D2 -->|"Candesartana (CHARM-Alternative)"| C4(["BRA vs placebo no intolerante ganhou.<br/>Não é ELITE II versus IECA"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4 conduta;
```

## Mensagem prática

**Dose de ensaio, não dose de “já está na receita”.** IECA primeiro. BRA 150 mg no intolerante. Não tríplice SRAA.
