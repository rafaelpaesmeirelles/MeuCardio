---
slug: fluxograma-ambulatorial-pos-tratamento-endocardite-destino
title: 'Fluxograma ambulatorial: pós-tratamento de endocardite — PS agora vs. reavaliação urgente'
kind: fluxograma
theme: Endocardite
summary: 'Árvore ambulatorial após EI tratada: gate de alarme para PS, braço febre/síndrome infecciosa → hemoculturas
  antes de antibiótico, e freio explícito contra empirismo no consultório; link para educação odontológica sem regimes.'
tags: []
source_refs:
- 'Delgado V, Ajmone Marsan N, de Waha S, et al. 2023 ESC Guidelines for the management of endocarditis. Eur Heart
  J. 2023;44(39):3948-4042. DOI: 10.1093/eurheartj/ehad193. PMID: 37622656'
evidence_level: null
source_tier: A
review_status: revisado
gaps: []
published: false
---

# Fluxograma ambulatorial: pós-tratamento de endocardite — destino

Prosa: [sinalizadores-ambulatoriais-pos-tratamento-endocardite-quando-escalar](/biblioteca/sinalizadores-ambulatoriais-pos-tratamento-endocardite-quando-escalar). Checklist: [checklist-ambulatorial-pos-ei-higiene-oral-e-alarmes](/biblioteca/checklist-ambulatorial-pos-ei-higiene-oral-e-alarmes). Suspeita pré-diagnóstico (não confundir): [esc-2023-diretriz-endocardite-infecciosa](/biblioteca/esc-2023-diretriz-endocardite-infecciosa). Recidiva (definições): [recidiva-da-endocardite-infecciosa-relapso-versus-reinfeccao](/biblioteca/recidiva-da-endocardite-infecciosa-relapso-versus-reinfeccao).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta / contato ambulatorial<br/>pós-EI tratada ou em seguimento<br/>(1º ano / pós-alta)"] --> D1{"Há alarme de PS?<br/>hipotensão / IC aguda / embolia<br/>déficit neurológico / bacteremia já<br/>erosão-secreção de bolso / toxemia"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["Encaminhar AGORA ao PS / emergência<br/>Culturas prontamente se viável<br/>NÃO atrasar ressuscitação/ATB para completar pares<br/>Avisar lab + Endocarditis Team"])

  D1 -->|"Não"| D2{"Febre / síndrome infecciosa<br/>sem foco alternativo convincente?"}

  D2 -->|"Sim"| P1["Não iniciar antibiótico oral empírico isolado<br/>Culturas e via de EI no mesmo dia<br/>Não atrasar terapia urgente<br/>Considerar recidiva (ver slug dedicado)"]
  P1 --> D3{"Há coleta estruturada +<br/>encaminhamento no mesmo dia?"}

  D3 -->|"Não"| C2(["PS / urgência no mesmo dia<br/>Culturas antes de novo ATB se viável<br/>Sem atrasar tratamento urgente"])
  D3 -->|"Sim"| C3(["Coletar hemoculturas agora<br/>Acionar eco/Endocarditis Team<br/>Não protocolar doses neste fluxo"])

  D2 -->|"Foco alternativo claro e estável"| C4(["Avaliar culturas antes de novo ATB<br/>Tratar o foco com prudência<br/>Plano escrito de alarmes<br/>Reavaliar se febre persiste 24–48 h"])

  D2 -->|"Sem infecção — consulta eletiva"| C5(["Reforçar higiene oral + alarmes<br/>Coordenar dentista/cardiologia<br/>antes de procedimento de risco<br/>(sem regimes neste fluxo)"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1,C2 alerta;
  class C3,C4,C5 conduta;
```

## Notas

- **D1** = segurança (instabilidade / embolia / IC / bolso / toxemia).
- **D2/D3** = freio ao antibiótico empírico; hemoculturas **antes** de ATB.
- **C5** = braço educativo (ESC 2023 follow-up); regimes ficam no slug de profilaxia.
- Não decide Duke, esquema, OPAT, timing cirúrgico nem relapso vs reinfecção pelo agente.

## Culturas e tratamento em curso

Febre isolada em paciente estável após EI exige avaliação estruturada no mesmo dia, com hemoculturas e contato com a equipe; usar urgência/PS se essa estrutura não existir. Instabilidade, sepse, IC aguda ou embolia exigem emergência imediata. Foco urinário, respiratório ou dentário plausível não exclui bacteremia/recidiva: colher culturas antes de novo antibiótico quando possível, sem atrasar ressuscitação ou tratamento urgente.

Não interromper OPAT nem tratamento oral parcial prescrito para melhorar rendimento de culturas por iniciativa do paciente. Informar nomes, horários e última dose à equipe. Na suspeita de falha, a equipe decide coleta e ajuste imediato do esquema. A recomendação de culturas pré-antibiótico refere-se à coleta rápida antes de nova terapia quando viável, e não à suspensão indiscriminada da terapia em curso.
