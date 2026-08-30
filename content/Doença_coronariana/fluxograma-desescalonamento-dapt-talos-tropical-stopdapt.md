---
title: "Fluxograma: desescalonar DAPT — TALOS, TROPICAL ou STOPDAPT-2?"
slug: fluxograma-desescalonamento-dapt-talos-tropical-stopdapt
theme: "Doença coronariana"
kind: fluxograma
summary: "Não é a árvore de duração da DAPT da casa. Aqui: IAM estável no mês 1 sem evento → TALOS (troca ticagrelor→clopidogrel sem teste). SCA em prasugrel com PFT disponível → TROPICAL. 1 mês e depois clopidogrel sozinho é STOPDAPT-2 (Japão, comparador AAS+clopidogrel). Tirar AAS e manter P2Y12 potente é TWILIGHT/ULTIMATE, outra árvore."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada nos abstracts de TALOS-AMI (PMID 34627490), TROPICAL-ACS (PMID 28855078) e STOPDAPT-2 (PMID 31237644). Não substitui fluxograma-duracao-e-desescalonamento-da-dapt-apos-icp. Revisão científica concluída em 30/08/2026."
source_refs:
  - "Kim CJ, et al. TALOS-AMI. Lancet. 2021;398(10308):1305-1316. PMID: 34627490."
  - "Sibbing D, et al. TROPICAL-ACS. Lancet. 2017;390(10104):1747-1757. PMID: 28855078."
  - "Watanabe H, et al. STOPDAPT-2. JAMA. 2019;321(24):2414-2427. PMID: 31237644."
  - "Documentos da casa talos-ami-desescalonamento-nao-guiado-ticagrelor-para-clopidogrel, tropical-acs-desescalonamento-guiado-por-funcao-plaquetaria, stopdapt-2-dapt-de-1-mes-seguida-de-clopidogrel-monoterapia, twilight-ticagrelor-monoterapia-apos-3-meses-de-dapt."
---

# Fluxograma: desescalonar DAPT — TALOS, TROPICAL ou STOPDAPT-2?

Não é a árvore de **quanto tempo** durar a DAPT. Aqui é **como** descer a potência depois do mês 1.

```mermaid
flowchart TD
  R0["SCA/IAM com DAPT após ICP,<br/>sem FA (sem anticoagulante)"] --> D1{"Quer tirar o AAS e manter<br/>P2Y12 potente?"}

  D1 -->|"Sim"| C0(["Sai desta árvore.<br/>TWILIGHT / ULTIMATE-DAPT / NEO-MINDSET"])

  D1 -->|"Não — quer trocar o P2Y12<br/>ou encurtar a dupla"| D2{"IAM estabilizado no mês 1,<br/>sem isquemia e sem sangramento,<br/>em ticagrelor+AAS?"}

  D2 -->|"Sim"| C1(["TALOS-AMI: clopidogrel+AAS<br/>sem loading e sem teste.<br/>Primário 4,6% vs 8,2%; isquemia P=0,15"])

  D2 -->|"Não"| D3{"SCA em prasugrel e o laboratório<br/>tem teste de função plaquetária?"}

  D3 -->|"Sim"| C2(["TROPICAL-ACS: desescalar guiado por PFT<br/>a partir do dia 14.<br/>Primário 7% vs 9%, não inferior; BARC P=0,23"])

  D3 -->|"Não"| D4{"População no molde STOPDAPT-2<br/>(Japão, comparador AAS+clopidogrel 12 meses)?"}

  D4 -->|"Sim"| C3(["1 mês de DAPT → clopidogrel monoterapia.<br/>Primário 2,36% vs 3,70%. Generalizar com cautela"])

  D4 -->|"Não"| C4(["Manter a DAPT potente 12 meses<br/>ou usar a árvore de duração/HBR da casa"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C0,C1,C2,C3,C4 conduta;
```

## Mensagem prática

**TALOS = troca não guiada de ticagrelor. TROPICAL = troca guiada de prasugrel. STOPDAPT-2 = tira o AAS e fica no clopidogrel (Japão).** Não misturar com TWILIGHT.
