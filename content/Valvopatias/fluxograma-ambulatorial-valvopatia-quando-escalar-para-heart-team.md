---
slug: fluxograma-ambulatorial-valvopatia-quando-escalar-para-heart-team
title: 'Fluxograma ambulatorial: valvopatia — quando escalar para Heart Team'
kind: fluxograma
theme: Valvopatias
summary: 'Árvore de consultório: PS agora vs. avaliação cardiológica prioritária vs. Heart Team para decisão de
  intervenção em valvopatia — complemento dos protocolos de sinalizadores de EA sintomática e IM descompensando.'
tags: []
source_refs:
- 'Corrigendum to: 2025 ESC/EACTS Guidelines for valvular heart disease. Eur J Cardiothorac Surg. 2026;68:ezag193.
  DOI: 10.1093/ejcts/ezag193. Correção de texto duplicado na seção de lacunas de evidência do PDF, lida em 08/09/2026.'
- 'Praz F; Borger MA; Lanz J. 2025 ESC/EACTS Guidelines for the management of valvular heart disease. Eur Heart
  J. 2025;46:4635. DOI: 10.1093/eurheartj/ehaf194. PMID: 40878295.'
- 'Otto CM; Nishimura RA; Bonow RO. 2020 ACC/AHA Guideline for the Management of Patients With Valvular Heart Disease:
  A Report of the American College of Cardiology/American Heart Association Joint Committee on Clinical Practice
  Guidelines. Circulation. 2021;143:e72. DOI: 10.1161/CIR.0000000000000923. PMID: 33332150.'
evidence_level: null
source_tier: A
review_status: revisado
gaps: []
published: true
---

# Fluxograma ambulatorial: valvopatia — quando escalar para Heart Team

Prosa: [sinalizadores-ambulatoriais-de-estenose-aortica-sintomatica-quando-encaminhar](/biblioteca/sinalizadores-ambulatoriais-de-estenose-aortica-sintomatica-quando-encaminhar) e [sinalizadores-ambulatoriais-de-insuficiencia-mitral-descompensando](/biblioteca/sinalizadores-ambulatoriais-de-insuficiencia-mitral-descompensando).

ESC/EACTS 2025 e ACC/AHA 2020 situam o **Heart Team** como nó central quando há indicação potencial de intervenção ou anatomia/risco complexos.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta ambulatorial com valvopatia<br/>conhecida ou sopro + sintomas"] --> D1{"Instabilidade ou sinal de alarme<br/>(edema pulmonar, síncope, choque,<br/>regurgitação aguda importante,<br/>endocardite com complicação aguda)?"}

  D1 -->|"Sim"| C1(["PS / emergência AGORA<br/>Eco urgente no ambiente adequado"])

  D1 -->|"Não"| D2{"Valvopatia grave documentada<br/>OU suspeita forte de gravidade?"}

  D2 -->|"Sopro sem caracterização<br/>ou sintomas novos com gravidade discordante"| NEW["ECG, ecocardiograma transtorácico e avaliação cardiológica prioritária"]
  D2 -->|"Leve-moderada já documentada, estável"| C2(["Seguimento ambulatorial<br/>Eco periódico conforme diretriz<br/>Educar sinais de alarme"])

  D2 -->|"Sim"| D3{"Sintomas atribuíveis à valva<br/>OU gatilho específico da lesão<br/>OU dúvida de sintomas?"}

  D3 -->|"Não — assintomático estável"| C3(["Cardiologia / eco de vigilância<br/>Teste funcional apenas se<br/>EA grave aparentemente assintomática<br/>EA grave de alto gradiente e baixo risco: discutir intervenção precoce<br/>Heart Team e decisão compartilhada versus vigilância"])

  D3 -->|"Sim"| D4{"Decisão de intervenção<br/>ou escolha de modalidade<br/>(TAVI/SAVR/reparo) em jogo?"}

  D4 -->|"Sim"| C4(["Escalar para HEART TEAM<br/>Centro com volume adequado<br/>Não decidir modalidade isolado"])
  D4 -->|"Ainda não claro"| C5(["Avaliação cardiológica prioritária +<br/>eco completo / ETE se preciso<br/>Reentrar na árvore após fenotipagem"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  classDef equipe fill:#e8f0fe,stroke:#1a56db,color:#0b1f4d;
  class C1 alerta;
  class C2,C3,C5 conduta;
  class C4 equipe;
```

## Notas

- **D1** = gate de segurança. Suspeita de endocardite sem instabilidade exige via diagnóstica urgente estruturada no mesmo dia, com hemoculturas/eco conforme contexto; PS se houver complicação aguda ou se essa avaliação não for acessível. Não aguardar consulta eletiva.
- **D3** = o que muda o destino na EA/IM graves nas diretrizes (sintomas e critérios específicos por valvopatia; dilatação isolada não é gatilho genérico de EA).
- **D4 / C4** = Heart Team quando intervenção está sobre a mesa (ESC/EACTS 2025; ACC/AHA 2020).
- Não escolhe prótese, anticoagulação nem doses; não compete com hubs de doença abertos.
