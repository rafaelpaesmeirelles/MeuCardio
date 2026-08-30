---
title: "Fluxograma: farmacoinvasiva (TRANSFER/CARESS) ≠ facilitada (ASSENT-4/FINESSE) ≠ transporte para ICP (DANAMI-2/PRAGUE-2)"
slug: fluxograma-farmacoinvasiva-transfer-caress-stream-prague-2
theme: "Doença coronariana"
kind: fluxograma
summary: "TRANSFER-AMI: composto 30 d P=0,004 (inclui isquemia/IC). CARESS: P=0,004 (inclui isquemia; meia-dose+GPI). STREAM: lise vs ICP primária, P=0,21. ASSENT-4 facilitada piora. PRAGUE-2 morte ITT P=0,12. DANAMI-2 composto sim, morte NS."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em TRANSFER-AMI PMID 19553646, CARESS PMID 18280326, STREAM PMID 23473396, PRAGUE-2 PMID 12559941, ASSENT-4 PMID 16488800, DANAMI-2 PMID 12930925. Revisão científica concluída em 30/08/2026."
source_refs:
  - "Cantor WJ, et al. TRANSFER-AMI. N Engl J Med. 2009;360(26):2705-2718. PMID: 19553646."
  - "Di Mario C, et al. CARESS-in-AMI. Lancet. 2008;371(9612):559-568. PMID: 18280326."
  - "Armstrong PW, et al. STREAM. N Engl J Med. 2013;368(15):1379-1387. PMID: 23473396."
  - "Widimský P, et al. PRAGUE-2. Eur Heart J. 2003;24(1):94-104. PMID: 12559941."
  - "Bøhmer E, et al. NORDISTEMI. J Am Coll Cardiol. 2010;55(2):102-10. PMID: 19747792."
  - "Le May MR, et al. CAPITAL-AMI. J Am Coll Cardiol. 2005;46(3):417-24. PMID: 16053952."
  - "Documento da casa gracia-1-angiografia-rotineira-em-24-h-apos-lise — n=500; composto inclui revascularização."
  - "Documento da casa siam-iii-stent-imediato-versus-eletivo-em-2-semanas-apos-lise — n=197; composto inclui TLR."
  - "Documento da casa pact-bolus-de-50-mg-de-tpa-antes-da-angioplastia — perviedade, FE igual."
  - "Documento da casa fluxograma-lise-mais-cateter-pact-siam-gracia."
  - "Documento da casa prague-1-transporte-para-icp-versus-lise-versus-lise-no-caminho."
  - "Documento da casa fluxograma-icp-primaria-versus-lise-pami-prague-air."
---

# Fluxograma: lise e depois o quê?

```mermaid
flowchart TD
  R0["IAMCSST. Hospital sem ICP. Qual pergunta?"] --> D1{"O que foi testado?"}

  D1 -->|"Já lisou. Transferir agora para ICP?<br/>(TRANSFER-AMI, CARESS)"| C1(["Composto 30 d cai. Inclui isquemia.<br/>Morte isolada: TRANSFER ausente; CARESS n=600"])

  D1 -->|"Lise plena imediatamente antes da ICP primária<br/>(ASSENT-4)"| C2(["Piora. Não fazer"])

  D1 -->|"Meia reteplase+abciximabe para 'facilitar' ICP primária<br/>(FINESSE)"| C3(["Primário NS. Resolução de ST não conta"])

  D1 -->|"Lise pré-hospitalar vs ICP primária<br/>(STREAM)"| C4(["Primário P=0,21. Mais ICH antes da emenda"])

  D1 -->|"Transportar para ICP primária vs lise no local<br/>(DANAMI-2 / PRAGUE-2)"| C5(["DANAMI-2: composto sim, morte NS<br/>PRAGUE-2: morte ITT P=0,12"])

  D1 -->|"Lise rural, atraso >90 min, 12 meses<br/>(NORDISTEMI)"| C6(["Primário P=0,19 (inclui isquemia nova)<br/>6% vs 16% é secundário. n=266"])

  D1 -->|"TNK+ICP imediata vs TNK isolada<br/>(CAPITAL-AMI)"| C7(["n=170. Composto P=0,04 puxado por isquemia<br/>Não é vs ICP primária. Não anula ASSENT-4"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7 conduta;
```

## Mensagem prática

**Farmacoinvasiva não é ICP facilitada.** ASSENT-4 piorou. PRAGUE-2 não ganhou mortalidade no ITT. NORDISTEMI (primário NS) e CAPITAL-AMI (n=170 vs lise sozinha) não reabrem facilitada.
