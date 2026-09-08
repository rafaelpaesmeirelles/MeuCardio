---
title: "Fluxograma ambulatorial: valvopatia — quando escalar para Heart Team"
slug: fluxograma-ambulatorial-valvopatia-quando-escalar-para-heart-team
theme: "Valvopatias"
kind: fluxograma
fonte_producao: grok
summary: "Árvore de consultório: PS agora vs. cardiologia em dias vs. Heart Team para decisão de intervenção em valvopatia — complemento dos protocolos de sinalizadores de EA sintomática e IM descompensando."
review_status: pendente_revisao
review_note: "Irmão dos protocolos sinalizadores EA e IM (07/09/2026). Não cria hub de doença; não compete com #717/#718. Fontes: ESC/EACTS 2021 PMID 34453165; ACC/AHA 2020 PMID 33332150."
source_refs:
  - "Vahanian A, Beyersdorf F, Praz F, et al. 2021 ESC/EACTS Guidelines for the management of valvular heart disease. Eur Heart J. 2022;43(7):561-632. DOI: 10.1093/eurheartj/ehab395. PMID: 34453165"
  - "Otto CM, Nishimura RA, Bonow RO, et al. 2020 ACC/AHA Guideline for the Management of Patients With Valvular Heart Disease. Circulation. 2021;143(5):e72-e227. DOI: 10.1161/CIR.0000000000000923. PMID: 33332150"
---

# Fluxograma ambulatorial: valvopatia — quando escalar para Heart Team

Prosa: [`sinalizadores-ambulatoriais-de-estenose-aortica-sintomatica-quando-encaminhar`](sinalizadores-ambulatoriais-de-estenose-aortica-sintomatica-quando-encaminhar.md) e [`sinalizadores-ambulatoriais-de-insuficiencia-mitral-descompensando`](sinalizadores-ambulatoriais-de-insuficiencia-mitral-descompensando.md).

ESC/EACTS 2021 e ACC/AHA 2020 situam o **Heart Team** como nó central quando há indicação potencial de intervenção ou anatomia/risco complexos.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta ambulatorial com valvopatia<br/>conhecida ou sopro + sintomas"] --> D1{"Instabilidade ou sinal de alarme<br/>(edema pulmonar, síncope, choque,<br/>IM/EA aguda suspeita, endocardite)?"}

  D1 -->|"Sim"| C1(["PS / emergência AGORA<br/>Eco urgente no ambiente adequado"])

  D1 -->|"Não"| D2{"Valvopatia grave documentada<br/>OU suspeita forte de gravidade?"}

  D2 -->|"Não / leve-moderada estável"| C2(["Seguimento ambulatorial<br/>Eco periódico conforme diretriz<br/>Educar sinais de alarme"])

  D2 -->|"Sim"| D3{"Sintomas atribuíveis à valva<br/>OU FEVE caindo / dilatação<br/>OU dúvida de sintomas?"}

  D3 -->|"Não — assintomático estável"| C3(["Cardiologia / eco de vigilância<br/>Discutir teste funcional se EA grave<br/>Reavaliar gatilhos de intervenção"])

  D3 -->|"Sim"| D4{"Decisão de intervenção<br/>ou escolha de modalidade<br/>(TAVI/SAVR/reparo) em jogo?"}

  D4 -->|"Sim"| C4(["Escalar para HEART TEAM<br/>Centro com volume adequado<br/>Não decidir modalidade isolado"])
  D4 -->|"Ainda não claro"| C5(["Cardiologia em dias +<br/>eco completo / ETTE se preciso<br/>Reentrar na árvore após fenotipagem"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  classDef equipe fill:#e8f0fe,stroke:#1a56db,color:#0b1f4d;
  class C1 alerta;
  class C2,C3,C5 conduta;
  class C4 equipe;
```

## Notas

- **D1** = gate de segurança (alarme agudo).
- **D3** = o que muda o destino na EA/IM graves nas diretrizes (sintomas, função/dilatação, sintomas duvidosos).
- **D4 / C4** = Heart Team quando intervenção está sobre a mesa (ESC/EACTS 2021; ACC/AHA 2020).
- Não escolhe prótese, anticoagulação nem doses; não compete com hubs de doença abertos.
