---
title: "Fluxograma ambulatorial: suspeita de endocardite (febre + válvula/dispositivo) — PS agora vs. via urgente"
slug: fluxograma-ambulatorial-suspeita-endocardite-febre-valvula-destino
theme: "Endocardite"
kind: fluxograma
fonte_producao: grok
summary: "Árvore ambulatorial de destino na suspeita de EI: gate de alarme para PS (instabilidade/embolia/IC), braço febre + material cardíaco sem foco → hemoculturas antes de antibiótico, e freio explícito contra tratamento empírico no consultório."
review_status: pendente_revisao
review_note: "Irmão do protocolo sinalizadores-ambulatoriais-suspeita-endocardite-quando-encaminhar (07/09/2026). ESC 2023 PMID 37622656. Sem doses; anti-colisão com Duke, profilaxia e timing cirúrgico."
source_refs:
  - "Delgado V, Ajmone Marsan N, de Waha S, et al. 2023 ESC Guidelines for the management of endocarditis. Eur Heart J. 2023;44(39):3948-4042. DOI: 10.1093/eurheartj/ehad193. PMID: 37622656"
---

# Fluxograma ambulatorial: suspeita de endocardite — destino

Prosa: [`sinalizadores-ambulatoriais-suspeita-endocardite-quando-encaminhar`](sinalizadores-ambulatoriais-suspeita-endocardite-quando-encaminhar.md). Checklist: [`endocardite-checklist-ambulatorial-febre-protese-dispositivo`](endocardite-checklist-ambulatorial-febre-protese-dispositivo.md). Duke: [`fluxograma-endocardite-duke-iscvid-2023-aplicacao-dos-criterios`](fluxograma-endocardite-duke-iscvid-2023-aplicacao-dos-criterios.md). Visão geral: [`fluxograma-endocardite-infecciosa-esc-2023`](fluxograma-endocardite-infecciosa-esc-2023.md).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta ambulatorial / contato\ncom febre, calafrios ou síndrome\ninfecciosa sem foco claro"] --> D1{"Há material cardíaco de risco\nou história de EI / CHD de risco / UDI?\n(prótese, TAVI, CIED, enxerto)"}

  D1 -->|"Não"| C0(["Triagem infecciosa usual\nReavaliar se surgir material/risco\nou bacteremia sem foco"])

  D1 -->|"Sim"| D2{"Alarme de PS?\nhipotensão / IC aguda / embolia\ndéficit neurológico / bacteremia já\nerosão-secreção de bolso / toxemia"}

  D2 -->|"Sim ou dúvida fundamentada"| C1(["Encaminhar AGORA ao PS / emergência\nHemoculturas ≥3 pares ANTES de antibiótico\nAvisar lab + Endocarditis Team"])

  D2 -->|"Não"| D3{"Febre/síndrome infecciosa\nsem foco alternativo convincente?"}

  D3 -->|"Sim"| P1["NÃO iniciar antibiótico ambulatorial\nPriorizar hemoculturas + via de EI"]
  P1 --> D4{"Há coleta estruturada +\nencaminhamento no mesmo dia?"}

  D4 -->|"Não"| C2(["PS / urgência no mesmo dia\nMesma regra: culturas antes de ATB"])
  D4 -->|"Sim"| C3(["Coletar hemoculturas agora\nAcionar eco/Endocarditis Team\nSeguir fluxograma ESC / Duke no hospital"])

  D3 -->|"Foco alternativo claro e estável"| C4(["Tratar o foco com prudência\nPlano escrito de alarmes\nReavaliar se febre persiste 24–48 h"])

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
