---
title: "Fluxograma: escolha do inibidor de P2Y12 na síndrome coronariana aguda"
slug: fluxograma-escolha-do-p2y12-na-sca
theme: "Doença coronariana"
kind: fluxograma
summary: "Árvore operacional: NSTE sem anatomia — não pré-tratar com prasugrel (ACCOAST); SCA mista — ticagrelor > clopidogrel (PLATO); PCI programada — prasugrel > clopidogrel (TRITON) com preço hemorrágico; invasiva planejada — prasugrel vs ticagrelor (ISAR-REACT 5, aberto). THEMIS fica fora (DAC estável). TWILIGHT/ULTIMATE entram depois, não na escolha do ataque."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada nos abstracts de PLATO (PMID 19717846), TRITON-TIMI 38 (PMID 17982182), ACCOAST (PMID 23991622), ISAR-REACT 5 (PMID 31475799) e THEMIS (PMID 31475798). Classe ESC 2023 de P2Y12 não relida na tabela nesta revisão editorial. Contraindicação de prasugrel em AVC/AIT: monografia da casa, não o abstract do TRITON. Revisão científica concluída em 30/08/2026."
source_refs:
  - "Wallentin L, et al. PLATO. N Engl J Med. 2009;361(11):1045-1057. PMID: 19717846."
  - "Wiviott SD, et al. TRITON-TIMI 38. N Engl J Med. 2007;357(20):2001-2015. PMID: 17982182."
  - "Montalescot G, et al. ACCOAST. N Engl J Med. 2013;369(11):999-1010. PMID: 23991622."
  - "Schüpke S, et al. ISAR-REACT 5. N Engl J Med. 2019;381(16):1524-1534. PMID: 31475799."
  - "Steg PG, et al. THEMIS. N Engl J Med. 2019;381(14):1309-1320. PMID: 31475798."
  - "Documentos da casa twilight-ticagrelor-monoterapia-apos-3-meses-de-dapt e fluxograma-duracao-e-desescalonamento-da-dapt-apos-icp — duração, não escolha do ataque."
---

# Fluxograma: escolha do inibidor de P2Y12 na síndrome coronariana aguda

Esta árvore escolhe **qual P2Y12 no ataque**. Duração, monoterapia aos 1–3 meses e manutenção crônica (TWILIGHT, ULTIMATE-DAPT, HOST-EXAM) são documentos próprios.

## Árvore de decisão

```mermaid
flowchart TD
  R0["SCA — escolher o P2Y12"] --> D0{"É DAC estável / diabete sem IAM,<br/>sem evento agudo?"}

  D0 -->|"Sim"| C0(["Sai desta árvore.<br/>THEMIS: ticagrelor + AAS reduz pouco<br/>isquemia e mais que dobra TIMI maior"])

  D0 -->|"Não — SCA verdadeira"| D1{"NSTE, anatomia AINDA não vista?"}

  D1 -->|"Sim"| C1(["NÃO carregar prasugrel agora.<br/>ACCOAST: HR isquêmico 1,02; TIMI maior HR 1,90.<br/>Ticagrelor (PLATO) ou esperar a cine"])

  D1 -->|"Não — supra, ou anatomia já conhecida"| D2{"Há AVC/AIT prévio, ou a via será clínica<br/>sem PCI?"}

  D2 -->|"AVC/AIT prévio"| C2(["Prasugrel contraindicado na bula<br/>(monografia da casa). Ticagrelor (PLATO)<br/>ou clopidogrel se alto risco hemorrágico"])

  D2 -->|"Estratégia clínica, sem PCI"| C3(["Ticagrelor > clopidogrel (PLATO).<br/>TRITON não se aplica — exigia PCI programada"])

  D2 -->|"PCI programada / invasiva planejada"| D3{"Escolher entre os dois potentes?"}

  D3 -->|"Sim, anatomia já vista"| C4(["ISAR-REACT 5: prasugrel 6,9% vs<br/>ticagrelor 9,3% morte/IAM/AVC em 1 ano;<br/>BARC maior sem diferença. Ensaio aberto"])

  D3 -->|"Comparador é clopidogrel"| C5(["PCI programada: TRITON (prasugrel HR 0,81,<br/>mais sangramento fatal 0,4% vs 0,1%).<br/>População mista: PLATO (ticagrelor HR 0,84,<br/>menos morte total)"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C0,C1,C2,C3,C4,C5 conduta;
```

## O que a árvore não mostra

**Clopidogrel permanece** no alto risco hemorrágico, na fibrinolise (PLATO não testou), na necessidade de DOAC (via própria) e quando o potente não está disponível. **ISAR-REACT 5 é aberto** e o timing do ataque não foi relido no PDF. **5 mg de prasugrel** em ≥75 anos / <60 kg é bula, não desfecho do TRITON neste abstract.

## Mensagem prática

**NSTE sem anatomia: não prasugrel. SCA: potente > clopidogrel (PLATO/TRITON). Entre potentes após a cine: o ISAR-REACT 5 puxa para prasugrel, com as reservas do desenho aberto. THEMIS não entra no PS.**
