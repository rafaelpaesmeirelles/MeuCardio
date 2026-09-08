---
title: "Fluxograma: sinalizadores ambulatoriais de bradicardia e bloqueio AV — PS agora vs. eletivo"
slug: fluxograma-sinalizadores-ambulatoriais-bradicardia-e-bloqueio-av
theme: "Arritmias"
kind: fluxograma
fonte_producao: grok
summary: "Árvore ambulatorial: bradicardia, pausas ou bloqueio AV no consultório — gate de PS (instabilidade, BAV avançado, escape precário) versus via eletiva de correlação sintoma-traçado e marca-passo definitivo."
review_status: pendente_revisao
review_note: "Árvore irmã dos protocolos de bradicardia/BAV e bifascicular ambulatoriais (07/09/2026), além #839/#864. ESC 2021 PMID 34455430; ACC/AHA/HRS 2018 PMID 30586772. Sem doses."
source_refs:
  - "Glikson M, Nielsen JC, Kronborg MB, et al. 2021 ESC Guidelines on cardiac pacing and cardiac resynchronization therapy. Eur Heart J. 2021;42(35):3427-3520. DOI: 10.1093/eurheartj/ehab364. PMID: 34455430"
  - "Kusumoto FM, Schoenfeld MH, Barrett C, et al. 2018 ACC/AHA/HRS Guideline on the Evaluation and Management of Patients With Bradycardia and Cardiac Conduction Delay. Circulation. 2019;140(8):e382-e482. DOI: 10.1161/CIR.0000000000000628. PMID: 30586772"
---

# Fluxograma: sinalizadores ambulatoriais de bradicardia e bloqueio AV

Prosa: [`sinalizadores-ambulatoriais-de-bradicardia-e-bloqueio-av-quando-escalar`](sinalizadores-ambulatoriais-de-bradicardia-e-bloqueio-av-quando-escalar.md) e [`bloqueio-bifascicular-no-consultorio-sinais-vermelhos-quando-escalar`](bloqueio-bifascicular-no-consultorio-sinais-vermelhos-quando-escalar.md). Agudo instável: [`fluxograma-bradicardia-sintomatica-manejo-agudo`](fluxograma-bradicardia-sintomatica-manejo-agudo.md). Indicação definitiva: [`fluxograma-bradiarritmia-indicacao-de-marcapasso-esc-2021`](../Dispositivos/fluxograma-bradiarritmia-indicacao-de-marcapasso-esc-2021.md).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta: bradicardia, pausas<br/>ou bloqueio AV / bifascicular"] --> D1{"Há síncope, instabilidade,<br/>BAV avançado Mobitz II/2:1/3º,<br/>ou escape precário?"}

  D1 -->|"Sim"| C1(["PS / emergência AGORA<br/>ECG 12 derivações<br/>Sem doses neste fluxo — ver ACLS agudo"])

  D1 -->|"Não"| D2{"Bifascicular + síncope<br/>inexplicada recente<br/>sem instabilidade atual?"}

  D2 -->|"Sim"| C2(["EP / dispositivos urgente-eletiva rápida<br/>Não liberar como achado isolado"])

  D2 -->|"Não"| D3{"Sintoma atribuível<br/>documentado com bradiarritmia<br/>persistente?"}

  D3 -->|"Sim"| C3(["Via eletiva: causa reversível<br/>+ indicação de MP definitivo<br/>ESC 2021 / ACC-AHA-HRS 2018"])

  D3 -->|"Não"| D4{"Atleta / sono / vagotonia<br/>ECG sem BAV avançado<br/>assintomático?"}

  D4 -->|"Sim"| C4(["Não escalar<br/>Educar alarmes<br/>Reavaliar se sintoma novo"])

  D4 -->|"Não / dúvida"| C5(["Holter ou monitor de eventos<br/>Eco se estrutural suspeita<br/>Retorno com correlação"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1 alerta;
  class C2,C3,C4,C5 conduta;
```

## Notas

- **D1** = gate de segurança (instabilidade ou bloqueio de alto risco).
- **D2** = bifascicular + síncope muda o peso — ver protocolo irmão e estudo de progressão.
- **C3** = correlação sintoma-traçado antes de “MP por FC baixa”.
- Não decide atropina, estimulação temporária nem programação de dispositivo já implantado (#835).
