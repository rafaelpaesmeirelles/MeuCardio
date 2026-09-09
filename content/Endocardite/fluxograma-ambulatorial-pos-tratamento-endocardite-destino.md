---
title: "Fluxograma ambulatorial: pós-tratamento de endocardite — PS agora vs. reavaliação urgente"
slug: fluxograma-ambulatorial-pos-tratamento-endocardite-destino
theme: "Endocardite"
kind: fluxograma
fonte_producao: grok
summary: "Árvore ambulatorial após EI tratada: gate de alarme para PS, braço febre/síndrome infecciosa → hemoculturas antes de antibiótico, e freio explícito contra empirismo no consultório; link para educação odontológica sem regimes."
review_status: pendente_revisao
review_note: "Irmão do protocolo sinalizadores-ambulatoriais-pos-tratamento-endocardite-quando-escalar (07/09/2026). ESC 2023 PMID 37622656. Sem doses; além de #853 (suspeita pré-diagnóstico); anti-colisão com recidiva/definições, profilaxia com regimes e Duke."
source_refs:
  - "Delgado V, Ajmone Marsan N, de Waha S, et al. 2023 ESC Guidelines for the management of endocarditis. Eur Heart J. 2023;44(39):3948-4042. DOI: 10.1093/eurheartj/ehad193. PMID: 37622656"
---

# Fluxograma ambulatorial: pós-tratamento de endocardite — destino

Prosa: [`sinalizadores-ambulatoriais-pos-tratamento-endocardite-quando-escalar`](sinalizadores-ambulatoriais-pos-tratamento-endocardite-quando-escalar.md). Checklist: [`checklist-ambulatorial-pos-ei-higiene-oral-e-alarmes`](checklist-ambulatorial-pos-ei-higiene-oral-e-alarmes.md). Suspeita pré-diagnóstico (não confundir): [`fluxograma-ambulatorial-suspeita-endocardite-febre-valvula-destino`](fluxograma-ambulatorial-suspeita-endocardite-febre-valvula-destino.md). Recidiva (definições): [`recidiva-da-endocardite-infecciosa-relapso-versus-reinfeccao`](recidiva-da-endocardite-infecciosa-relapso-versus-reinfeccao.md).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta / contato ambulatorial\npós-EI tratada ou em seguimento\n(1º ano / pós-alta)"] --> D1{"Há alarme de PS?\nhipotensão / IC aguda / embolia\ndéficit neurológico / bacteremia já\nerosão-secreção de bolso / toxemia"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["Encaminhar AGORA ao PS / emergência\nHemoculturas ≥3 pares ANTES de antibiótico\nAvisar lab + Endocarditis Team"])

  D1 -->|"Não"| D2{"Febre / síndrome infecciosa\nsem foco alternativo convincente?"}

  D2 -->|"Sim"| P1["NÃO iniciar antibiótico ambulatorial\nPriorizar hemoculturas + via de EI\nConsiderar recidiva (ver slug dedicado)"]
  P1 --> D3{"Há coleta estruturada +\nencaminhamento no mesmo dia?"}

  D3 -->|"Não"| C2(["PS / urgência no mesmo dia\nMesma regra: culturas antes de ATB"])
  D3 -->|"Sim"| C3(["Coletar hemoculturas agora\nAcionar eco/Endocarditis Team\nNão protocolar doses neste fluxo"])

  D2 -->|"Foco alternativo claro e estável"| C4(["Tratar o foco com prudência\nPlano escrito de alarmes\nReavaliar se febre persiste 24–48 h"])

  D2 -->|"Sem infecção — consulta eletiva"| C5(["Reforçar higiene oral + alarmes\nCoordenar dentista/cardiologia\nantes de procedimento de risco\n(sem regimes neste fluxo)"])

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
