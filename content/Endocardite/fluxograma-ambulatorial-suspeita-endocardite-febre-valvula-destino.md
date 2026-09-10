---
slug: fluxograma-ambulatorial-suspeita-endocardite-febre-valvula-destino
title: 'Fluxograma ambulatorial: suspeita de endocardite (febre + válvula/dispositivo) — PS agora vs. via urgente'
kind: fluxograma
theme: Endocardite
summary: 'Suspeita de endocardite: emergência se instabilidade, IC ou embolia; paciente estável precisa de investigação
  estruturada no mesmo dia. Colher hemoculturas antes de antibiótico quando viável, sem atrasar tratamento urgente.'
tags: []
source_refs:
- 'Delgado V; Ajmone Marsan N; de Waha S. 2023 ESC Guidelines for the management of endocarditis. Eur Heart J. 2023;44:3948.
  DOI: 10.1093/eurheartj/ehad193. PMID: 37622656.'
evidence_level: null
source_tier: A
review_status: revisado
gaps: []
published: true
---

# Fluxograma ambulatorial: suspeita de endocardite — destino

Prosa: [sinalizadores-ambulatoriais-suspeita-endocardite-quando-encaminhar](/biblioteca/sinalizadores-ambulatoriais-suspeita-endocardite-quando-encaminhar). Checklist: [endocardite-checklist-ambulatorial-febre-protese-dispositivo](/biblioteca/endocardite-checklist-ambulatorial-febre-protese-dispositivo). Duke: [fluxograma-endocardite-duke-iscvid-2023-aplicacao-dos-criterios](/biblioteca/fluxograma-endocardite-duke-iscvid-2023-aplicacao-dos-criterios). Visão geral: [fluxograma-endocardite-infecciosa-esc-2023](/biblioteca/fluxograma-endocardite-infecciosa-esc-2023).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta ambulatorial / contato<br/>com febre, calafrios ou síndrome<br/>infecciosa sem foco claro"] --> D1{"Há material cardíaco de risco<br/>ou história de EI / cardiopatia congênita / uso de drogas injetáveis?<br/>(prótese, TAVI, CIED, enxerto)"}

  D1 -->|"Não"| C0(["Avaliar instabilidade e suspeita clínica de EI<br/>mesmo sem fator conhecido;<br/>emergência se sepse/IC/embolia"])

  D1 -->|"Sim"| D2{"Alarme de PS?<br/>hipotensão / IC aguda / embolia<br/>déficit neurológico / bacteremia já<br/>erosão-secreção de bolso / toxemia"}

  D2 -->|"Sim ou dúvida fundamentada"| C1(["Encaminhar AGORA ao PS / emergência<br/>Obter culturas rapidamente antes de ATB<br/>se não causar atraso perigoso; tratar sepse prontamente<br/>Avisar lab + Endocarditis Team"])

  D2 -->|"Não"| D3{"Febre/síndrome infecciosa<br/>sem foco alternativo convincente?"}

  D3 -->|"Sim"| P1["Evitar antibiótico empírico sem avaliação de EI<br/>Colher culturas antes de nova terapia quando viável<br/>não atrasar tratamento urgente"]
  P1 --> D4{"Há coleta estruturada +<br/>encaminhamento no mesmo dia?"}

  D4 -->|"Não"| C2(["PS / urgência no mesmo dia<br/>Culturas antes de ATB se viável<br/>sem atrasar tratamento urgente"])
  D4 -->|"Sim"| C3(["Coletar hemoculturas agora<br/>Acionar eco/Endocarditis Team<br/>Seguir fluxograma ESC / Duke no hospital"])

  D3 -->|"Foco alternativo claro e estável"| C4(["Avaliar o foco e risco de EI no mesmo dia<br/>Culturas antes de nova terapia se suspeita persiste<br/>Plano escrito + reavaliação precoce<br/>Não excluir EI apenas por foco alternativo"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1,C2 alerta;
  class C0,C3,C4 conduta;
```

## Notas

- **D1** = gate de risco (ESC 2023: suspeita dirigida por fatores de risco + febre/sepsis sem foco).
- **D2** = segurança (instabilidade / embolia / IC / bolso infectado).
- **D3/D4** = freio ao antibiótico empírico ambulatorial; hemoculturas **antes** de ATB.
- Não decide Duke, esquema antibiótico, OPAT nem timing cirúrgico.

## Segurança da coleta e do encaminhamento

Não suspender automaticamente antibiótico já iniciado. Registrar molécula, dose, horário e motivo; colher antes de novas doses quando clinicamente seguro, deixando decisão de manter/ajustar/suspender à equipe. Em sepse/instabilidade, obter culturas prontamente sem atrasar tratamento por logística ou pelo número ideal de amostras. Em paciente estável, usar 3 conjuntos (sets), cada um com frascos aeróbio e anaeróbio conforme protocolo local.

Febre com prótese/TAVI/CIED ou EI prévia aumenta suspeita, sem confirmar diagnóstico: paciente estável pode seguir via estruturada no mesmo dia com culturas, exame, acesso rápido a eco e Endocarditis Team; sem essa estrutura, PS. Secreção purulenta e hardware exposto são alarmes independentes de febre; eritema/dor isolados têm diferenciais. Foco alternativo não encerra EI se febre persistente/recorrente, bacteremia típica, embolia ou ausência de resposta.
