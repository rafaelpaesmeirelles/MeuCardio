---
title: "Fluxograma ambulatorial: aortopatia em VAB e EA assintomática grave — quando escalar"
slug: fluxograma-ambulatorial-bicuspide-aortopatia-e-ea-assintomatica-quando-escalar
theme: "Valvopatias"
kind: fluxograma
fonte_producao: grok
summary: "Árvore de consultório além #840/#866: PS agora vs. cardiologia/aorta/Heart Team em dias vs. vigilância na aortopatia da bicúspide e na EA grave sem sintomas espontâneos."
review_status: pendente_revisao
review_note: "Irmão dos protocolos de aortopatia VAB e EA assintomática vigilância (07/09/2026). Não cria hub; não compete com #717/#718. Fontes: ESC 2024 PMID 39210722; ESC/EACTS 2021 PMID 34453165; ACC/AHA 2020 PMID 33332150."
source_refs:
  - "Mazzolai L, Teixido-Tura G, Lanzi S, et al. 2024 ESC Guidelines for the management of peripheral arterial and aortic diseases. Eur Heart J. 2024;45(36):3538-3700. DOI: 10.1093/eurheartj/ehae179. PMID: 39210722"
  - "Vahanian A, Beyersdorf F, Praz F, et al. 2021 ESC/EACTS Guidelines for the management of valvular heart disease. Eur Heart J. 2022;43(7):561-632. DOI: 10.1093/eurheartj/ehab395. PMID: 34453165"
  - "Otto CM, Nishimura RA, Bonow RO, et al. 2020 ACC/AHA Guideline for the Management of Patients With Valvular Heart Disease. Circulation. 2021;143(5):e72-e227. DOI: 10.1161/CIR.0000000000000923. PMID: 33332150"
---

# Fluxograma ambulatorial: aortopatia em VAB e EA assintomática grave — quando escalar

Prosa: [`sinalizadores-ambulatoriais-de-aortopatia-em-valva-aortica-bicuspide-quando-escalar`](sinalizadores-ambulatoriais-de-aortopatia-em-valva-aortica-bicuspide-quando-escalar.md) e [`sinalizadores-ambulatoriais-de-estenose-aortica-assintomatica-grave-vigilancia`](sinalizadores-ambulatoriais-de-estenose-aortica-assintomatica-grave-vigilancia.md).

Complementa (não substitui) [`fluxograma-ambulatorial-valvopatia-quando-escalar-para-heart-team`](fluxograma-ambulatorial-valvopatia-quando-escalar-para-heart-team.md) (#840) e os fluxogramas de **timing** de intervenção na EA assintomática já na pasta.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta ambulatorial:<br/>VAB ± dilatação aórtica<br/>OU EA grave 'assintomática'"] --> D1{"Instabilidade ou alarme agudo?<br/>(dor torácica/dorsal súbita, síncope,<br/>edema pulmonar, choque, assimetria)"}

  D1 -->|"Sim"| C1(["PS / emergência AGORA<br/>Imagem / eco no ambiente adequado"])

  D1 -->|"Não"| D2{"Qual o cenário principal?"}

  D2 -->|"VAB / aortopatia"| D3{"Diâmetro perto de limiar,<br/>crescimento rápido, fenótipo raiz,<br/>imagem incompleta, HF dissecção,<br/>ou gestação planejada?"}

  D3 -->|"Sim"| C2(["Cardiologia / equipe de aorta<br/>em DIAS — não meses<br/>Completar TC/RM se preciso"])
  D3 -->|"Não — estável sob limiar"| C3(["Vigilância: eco periódico<br/>Educar sinais de síndrome aórtica<br/>Ver protocolo ESC 2024 ACHD"])

  D2 -->|"EA grave sem sintoma espontâneo"| D4{"Dúvida de sintoma, FEVE caindo,<br/>progressão rápida, teste esforço<br/>anormal, ou BNP muito alto?"}

  D4 -->|"Sim"| C4(["Cardiologia / Heart Team em DIAS<br/>Não 'mais 6 meses' sem reavaliar"])
  D4 -->|"Não — verdadeiramente estável"| C5(["Vigilância estruturada<br/>Reavaliar sintomas a cada visita<br/>Eco periódico + educação de alarme"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  classDef equipe fill:#e8f0fe,stroke:#1a56db,color:#0b1f4d;
  class C1 alerta;
  class C3,C5 conduta;
  class C2,C4 equipe;
```

## Notas

- **D1** = gate de segurança (síndrome aórtica / EA descompensando).
- **D3** = destino da aortopatia VAB (ESC 2024 PMID 39210722) — limiares finos no protocolo ACHD, não nesta árvore.
- **D4** = red flags da EA “assintomática” (ESC/EACTS 2021 PMID 34453165) antes da árvore completa de Classes I/IIa.
- Não escolhe TAVI/SAVR, técnica de raiz nem doses; não compete com hubs #717/#718.
