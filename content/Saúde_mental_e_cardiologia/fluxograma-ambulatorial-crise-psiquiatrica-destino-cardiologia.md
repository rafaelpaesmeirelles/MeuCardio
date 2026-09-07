---
title: "Fluxograma ambulatorial: crise psiquiátrica no cardiopata — crise agora vs. retorno precoce vs. Psycho-Cardio"
slug: fluxograma-ambulatorial-crise-psiquiatrica-destino-cardiologia
theme: "Saúde mental e cardiologia"
kind: fluxograma
fonte_producao: grok
summary: "Árvore ambulatorial de destino: gate de segurança (ideacao/plano/psicose) para via de crise/PS; braço de sofrimento intenso com retorno precoce; braço de stepped care / Psycho-Cardio sem risco iminente."
review_status: pendente_revisao
review_note: "Irmão do protocolo sinalizadores-ambulatoriais-crise-psiquiatrica-no-consultorio-de-cardiologia (07/09/2026). ESC 2025 PMID 40878270; AHA 2008 PMID 18824640. Sem doses; anti-colisão com fluxograma ACTIVE e depressão pós-SCA."
source_refs:
  - "Bueno H, Deaton C, Farrero M, et al. 2025 ESC Clinical Consensus Statement on mental health and cardiovascular disease: developed under the auspices of the ESC Clinical Practice Guidelines Committee. Eur Heart J. 2025;46(41):4156-4225. DOI: 10.1093/eurheartj/ehaf191. PMID: 40878270"
  - "Lichtman JH, Bigger JT Jr, Blumenthal JA, et al. Depression and coronary heart disease: recommendations for screening, referral, and treatment: a science advisory from the American Heart Association. Circulation. 2008;118(17):1768-1775. DOI: 10.1161/CIRCULATIONAHA.108.190769. PMID: 18824640"
---

# Fluxograma ambulatorial: crise psiquiátrica — destino

Prosa: [`sinalizadores-ambulatoriais-crise-psiquiatrica-no-consultorio-de-cardiologia`](sinalizadores-ambulatoriais-crise-psiquiatrica-no-consultorio-de-cardiologia.md). Checklist: [`checklist-ambulatorial-alarme-crise-psiquiatrica-cardiopata`](checklist-ambulatorial-alarme-crise-psiquiatrica-cardiopata.md). Rastreamento ACTIVE: [`fluxograma-rastreamento-saude-mental-cuidado-escalonado-esc-2025`](fluxograma-rastreamento-saude-mental-cuidado-escalonado-esc-2025.md).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta ambulatorial de cardiologia<br/>com sofrimento mental referido<br/>ou rastreamento positivo"] --> D1{"Há alarme de crise?<br/>ideacao ativa / plano / meios<br/>autolesão recente / tentativa<br/>psicose / agitação extrema<br/>ameaca a si ou a outros"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["Acionar AGORA via local de crise<br/>/ emergência de saúde mental<br/>Não deixar sozinho se risco iminente<br/>Preservar plano cardiovascular em paralelo"])

  D1 -->|"Não"| D2{"Sofrimento intenso sem risco iminente?<br/>desesperança / adesão em risco<br/>rede frágil / escore elevado<br/>sem item de ideacao positivo"}

  D2 -->|"Sim"| P1["Avaliar suporte, adesão e preferências<br/>Oferecer referência a profissional qualificado<br/>(AHA 2008) — sem doses aqui"]
  P1 --> C2(["Retorno ambulatorial 24–72 h<br/>Orientação escrita de alarmes de crise"])

  D2 -->|"Não / sintomas leves-moderados"| D3{"Precisa Psycho-Cardio / stepped care<br/>ou revisão de psicofármaco/QT?"}

  D3 -->|"Sim"| C3(["Referência Psycho-Cardio / saúde mental<br/>Usar fluxograma ACTIVE e, se fármaco,<br/>protocolos de QT/antidepressivo — sem doses"])
  D3 -->|"Não"| C4(["Plano usual + educação de alarmes<br/>Reavaliar em contatos regulares<br/>(ESC 2025 Check)"])

  C2 --> D4{"Acesso e suporte garantidos?"}
  D4 -->|"Não / piora / ideacao surge"| C5(["Antecipar contato 24 h ou via de crise<br/>se surgir alarme da tabela"])
  D4 -->|"Sim"| C6(["Manter retorno 24–72 h<br/>Não protocolar psicofármaco neste fluxograma"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1,C5 alerta;
  class C2,C3,C4,C6 conduta;
```

## Notas

- **D1** = gate de segurança (ESC 2025: urgência segue protocolo local; AHA 2008: ideacao no rastreamento → avaliação imediata).
- **D2** = sofrimento ambulatorial controlável com rede → destino clínico precoce + referência qualificada.
- **D3** = ponte para ACTIVE / Psycho-Cardio e para pacotes de QT/antidepressivo já existentes, **sem** decidir fármaco aqui.
- Não decide doses, ponto de corte único de escala nem periodicidade universal de rastreamento.
