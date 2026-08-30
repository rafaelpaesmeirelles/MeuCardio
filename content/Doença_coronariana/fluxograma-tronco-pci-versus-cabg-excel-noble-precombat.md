---
title: "Fluxograma: tronco — EXCEL, NOBLE, PRECOMBAT e o que cada primário mede"
slug: fluxograma-tronco-pci-versus-cabg-excel-noble-precombat
theme: "Doença coronariana"
kind: fluxograma
summary: "Tronco desprotegido revascularizável pelos dois. PRECOMBAT (sirolimus, N=600, margem larga) não é diretivo. EXCEL (SYNTAX ≤32): primário 5 anos morte/AVC/IAM NS (22,0% vs 19,2%); morte isolada 13,0% vs 9,9% não é o primário. NOBLE: MACCE 5 anos PCI inferior (28% vs 19%); morte 9% vs 9%; morte 10 anos 23% vs 25% NS. BEST é multiarterial, não tronco isolado."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em EXCEL 5 anos PMID 31562798, NOBLE 5 anos PMID 31879028, NOBLE 10 anos PMID 41936368, PRECOMBAT PMID 21463149, BEST PMID 25774645. Não reconciliar EXCEL e NOBLE num único 'vencedor' — primários e definições de IAM diferem. Revisão científica concluída em 30/08/2026."
source_refs:
  - "Stone GW, et al. EXCEL 5 years. N Engl J Med. 2019;381(19):1820-1830. PMID: 31562798."
  - "Holm NR, et al. NOBLE 5 years. Lancet. 2020;395(10219):191-199. PMID: 31879028."
  - "Holck EN, et al. NOBLE 10 years. Lancet. 2026;407(10536):1374-1382. PMID: 41936368."
  - "Park SJ, et al. PRECOMBAT. N Engl J Med. 2011;364(18):1718-1727. PMID: 21463149."
  - "Park SJ, et al. BEST. N Engl J Med. 2015;372(13):1204-1212. PMID: 25774645."
---

# Fluxograma: tronco — qual ensaio responde o quê

```mermaid
flowchart TD
  R0["Tronco desprotegido.<br/>Heart team: os dois dão conta"] --> D1{"Stent e N do ensaio"}

  D1 -->|"Sirolimus, N=600, margem larga<br/>(PRECOMBAT)"| C0(["Não diretivo. Os autores dizem isso.<br/>1 ano NI estatística 8,7% vs 6,7%"])

  D1 -->|"Everolimus, SYNTAX do centro ≤32<br/>(EXCEL, n=1.905)"| D2{"Qual desfecho?"}

  D2 -->|"Primário 5 anos:<br/>morte + AVC + IAM"| C1(["Empata: 22,0% vs 19,2%; P=0,13"])

  D2 -->|"Morte isolada 5 anos"| C2(["13,0% vs 9,9%<br/>diferença 3,1 pp; IC 0,2 a 6,1<br/>p NÃO publicado neste abstract<br/>NÃO é o primário"])

  D1 -->|"Biolimus/DES, MACCE com revasc<br/>e IAM NÃO procedimental (NOBLE)"| D3{"Qual horizonte?"}

  D3 -->|"5 anos MACCE"| C3(["PCI inferior: 28% vs 19%<br/>HR 1,58; P=0,0002. Morte 9% vs 9%"])

  D3 -->|"10 anos morte"| C4(["Empata: 23% vs 25%; HR 0,93; P=0,56<br/>Não apaga o MACCE de 5 anos"])

  R0 --> D4{"Multiarterial, não tronco isolado?"}

  D4 -->|"BEST (everolimus, n=880, parou cedo)"| C5(["NI 2 anos falhou 11,0% vs 7,9%<br/>P=0,32 para NI. 4,6 anos HR 1,47"])

  D4 -->|"Diabetes multiarterial"| C6(["FREEDOM: CABG. Outro arquivo"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C0,C1,C2,C3,C4,C5,C6 conduta;
```

## Mensagem prática

**EXCEL e NOBLE não se somam.** Primário, IAM e inclusão de revasc são outros. PRECOMBAT não decide. BEST não é tronco. Heart team com os dois papers na mesa, não com um slogan.
