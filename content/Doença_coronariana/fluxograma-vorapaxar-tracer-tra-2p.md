---
title: "Fluxograma: vorapaxar — TRACER na SCA, TRA 2P na estável"
slug: fluxograma-vorapaxar-tracer-tra-2p
theme: "Doença coronariana"
kind: fluxograma
summary: "SCA sem supra: TRACER, primário NS e HIC 1,1% vs 0,2%. Aterosclerose estável (IAM/AVC/DAP): TRA 2P ganha morte CV/IAM/AVC (9,3% vs 10,5%) e paga HIC; DSMB parou o AVC prévio. Não é P2Y12. Não primeira linha."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em TRACER PMID 22077816 e TRA 2P PMID 22443427. Revisão científica concluída em 30/08/2026."
source_refs:
  - "Tricoci P, et al. TRACER. N Engl J Med. 2012;366(1):20-33. PMID: 22077816."
  - "Morrow DA, et al. TRA 2P–TIMI 50. N Engl J Med. 2012;366(15):1404-1413. PMID: 22443427."
---

# Fluxograma: vorapaxar

```mermaid
flowchart TD
  R0["Quer somar antagonista de PAR-1<br/>(vorapaxar) à terapia padrão?"] --> D1{"Qual o cenário?"}

  D1 -->|"SCA sem supra<br/>(TRACER)"| C1(["Não. Primário NS 18,5% vs 19,9%<br/>P=0,07. HIC 1,1% vs 0,2%"])

  D1 -->|"IAM, AVC isquêmico ou DAP estáveis<br/>(TRA 2P)"| D2{"Já teve AVC?"}

  D2 -->|"Sim"| C2(["Não. DSMB mandou parar<br/>por HIC neste subgrupo"])

  D2 -->|"Não"| C3(["Primário ganhou 9,3% vs 10,5%<br/>mas HIC 1,0% vs 0,5%.<br/>Não é P2Y12. Não é primeira linha"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3 conduta;
```

## Mensagem prática

**TRACER não autoriza vorapaxar na SCA. TRA 2P ganha isquemia na estável e cobra HIC.** Quem já teve AVC saiu do ensaio por segurança.
