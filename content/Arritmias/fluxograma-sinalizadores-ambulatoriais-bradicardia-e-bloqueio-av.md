---
slug: fluxograma-sinalizadores-ambulatoriais-bradicardia-e-bloqueio-av
title: 'Fluxograma: sinalizadores ambulatoriais de bradicardia e bloqueio AV — PS agora vs. eletivo'
kind: fluxograma
theme: Arritmias
summary: 'Árvore ambulatorial: bradicardia, pausas ou bloqueio AV no consultório — gate de PS (instabilidade, BAV
  avançado, escape precário) versus via eletiva de correlação sintoma-traçado e marca-passo definitivo.'
tags: []
source_refs:
- 'Glikson M, Nielsen JC, Kronborg MB, et al. 2021 ESC Guidelines on cardiac pacing and cardiac resynchronization
  therapy. Eur Heart J. 2021;42(35):3427-3520. DOI: 10.1093/eurheartj/ehab364. PMID: 34455430'
- 'Kusumoto FM, Schoenfeld MH, Barrett C, et al. 2018 ACC/AHA/HRS Guideline on the Evaluation and Management of
  Patients With Bradycardia and Cardiac Conduction Delay. Circulation. 2019;140(8):e382-e482. DOI: 10.1161/CIR.0000000000000628.
  PMID: 30586772'
evidence_level: null
source_tier: A
review_status: revisado
gaps: []
published: true
---

# Fluxograma: sinalizadores ambulatoriais de bradicardia e bloqueio AV

Prosa: [`sinalizadores-ambulatoriais-de-bradicardia-e-bloqueio-av-quando-escalar`](/biblioteca/sinalizadores-ambulatoriais-de-bradicardia-e-bloqueio-av-quando-escalar) e [`bloqueio-bifascicular-no-consultorio-sinais-vermelhos-quando-escalar`](/biblioteca/bloqueio-bifascicular-no-consultorio-sinais-vermelhos-quando-escalar). Agudo instável: [`fluxograma-bradicardia-sintomatica-manejo-agudo`](/biblioteca/fluxograma-bradicardia-sintomatica-manejo-agudo). Indicação definitiva: [`fluxograma-bradiarritmia-indicacao-de-marcapasso-esc-2021`](/biblioteca/fluxograma-bradiarritmia-indicacao-de-marcapasso-esc-2021).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta: bradicardia, pausas<br/>ou bloqueio AV / bifascicular"] --> D1{"Instabilidade, síncope com repercussão,<br/>escape precário ou bloqueio de alto risco recém-detectado?<br/>Mobitz II/alto grau/total ou ramo alternante"}

  D1 -->|"Sim"| C1(["PS / emergência AGORA<br/>ECG 12 derivações<br/>Sem doses neste fluxo — ver ACLS agudo"])

  D1 -->|"Não"| R1["Rever causas reversíveis e localizar BAV 2:1"]
  R1 --> D2{"Bifascicular + síncope<br/>inexplicada recente<br/>sem instabilidade atual?"}

  D2 -->|"Sim"| C2(["Avaliação célere em eletrofisiologia / dispositivos<br/>Não liberar como achado isolado"])

  D2 -->|"Não"| D3{"Sintoma atribuível<br/>documentado com bradiarritmia<br/>mesmo intermitente?"}

  D3 -->|"Sim"| C3(["Via eletiva: causa reversível<br/>+ indicação de MP definitivo<br/>ESC 2021 / ACC-AHA-HRS 2018"])

  D3 -->|"Não"| D4{"Bradicardia fisiológica confirmada?<br/>assintomático, resposta adequada ao esforço<br/>sem achado atípico ou bloqueio patológico"}

  D4 -->|"Sim"| C4(["Não escalar<br/>Educar alarmes<br/>Reavaliar se sintoma novo"])

  D4 -->|"Não / dúvida"| C5(["Holter ou monitor de eventos<br/>Eco se estrutural suspeita<br/>Retorno com correlação"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1 alerta;
  class C2,C3,C4,C5 conduta;
```

## Notas

- **D1** = triagem de segurança (instabilidade ou bloqueio de alto risco).
- **D2** = bifascicular + síncope muda o peso — ver protocolo irmão e estudo de progressão.
- **C3** = correlação sintoma-traçado antes de “MP por FC baixa”.
- Não decide atropina, estimulação temporária nem programação de dispositivo já implantado.
