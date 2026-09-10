---
slug: fluxograma-ambulatorial-hap-quando-escalar-ou-referenciar
title: 'Fluxograma ambulatorial: HAP — quando escalar ou referenciar'
kind: fluxograma
theme: Hipertensão pulmonar
summary: 'Árvore de consultório para HAP conhecida: alarme urgente vs reavaliação de risco vs manter com reforço
  — apontando para estratificação ESC/ERS 2022 e centro especializado, sem doses.'
tags: []
source_refs:
- 'Humbert M; Kovacs G; Hoeper MM. 2022 ESC/ERS Guidelines for the diagnosis and treatment of pulmonary hypertension.
  Eur Heart J. 2022;43:3618. DOI: 10.1093/eurheartj/ehac237. PMID: 36017548.'
evidence_level: null
source_tier: A
review_status: revisado
gaps: []
published: false
---

# Fluxograma ambulatorial: HAP — quando escalar ou referenciar

Prosa: [sinalizadores-ambulatoriais-de-piora-na-hap](/biblioteca/sinalizadores-ambulatoriais-de-piora-na-hap). Armadilha de fenótipo: [sinalizadores-ambulatoriais-nao-tratar-hp-grupo-2-3-como-hap](/biblioteca/sinalizadores-ambulatoriais-nao-tratar-hp-grupo-2-3-como-hap).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Retorno ambulatorial: HAP conhecida<br/>em terapia específica"] --> D0{"Há alarme urgente?<br/>síncope com risco imediato, hemoptise importante<br/>falência direita com hipoperfusão<br/>hipoxemia grave · instabilidade"}

  D0 -->|"Sim"| C0(["Via urgente / emergência<br/>Contatar centro de HP<br/>Não aguardar retorno eletivo"])

  D0 -->|"Não"| SPEC{"Gestação ou interrupção/falha<br/>de prostaciclina parenteral contínua?"}
  SPEC -->|"Falha de infusão"| C0
  SPEC -->|"Gestação"| PREG["Centro de HP e Pregnancy Heart Team prontamente<br/>Rever riscos maternos e terapia"]
  SPEC -->|"Não"| D1{"Fenótipo ainda compatível com HAP?<br/>Ou suspeita forte de grupo 2/3/5?"}

  D1 -->|"Dúvida de grupo / HP pós-capilar"| C1(["Não escalar vasodilatador HAP<br/>Rever história, eco/imagem, PFT/DLCO,<br/>V/Q e RHC quando indicado no centro<br/>Ver doc armadilha grupo 2/3"])

  D1 -->|"HAP plausível"| D2{"Avaliar tendência clínica e risco atual em4estratos<br/>CF, TC6min, BNP/NT-proBNP e variáveis adicionais"}

  D2 -->|"Intermediário-baixo sem deterioração"| OPT["Otimizar plano no centro de HP<br/>Objetivo: baixo risco; reavaliar"]
  D2 -->|"Estável em baixo risco"| C2(["Manter plano<br/>Reforçar adesão e sinais de alarme<br/>Manter calendário de risco ESC/ERS"])

  D2 -->|"Piora clínica / intermediário-alto ou alto"| C3(["Antecipar reavaliação de risco<br/>Discussão com centro especializado<br/>Considerar intensificação / avançados<br/>Sem inventar doses neste fluxograma"])

  D2 -->|"Adesão falhou ou precipitante óbvio"| C4(["Corrigir adesão / precipitante em paralelo<br/>Reavaliar risco e necessidade de intensificação<br/>Não atrasar C3 se deterioração"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  classDef neutro fill:#eef2f7,stroke:#3d5a80,color:#102a43;
  class C0,C1 alerta;
  class C2 conduta;
  class C3,C4 neutro;
```

## Notas

- **D0** = gate de segurança ambulatorial (síncope e falência direita não são "ajuste de agenda").
- **D1** = evita iatrogenia: vasodilatador arterial pulmonar em HP do grupo 2 pode precipitar edema — detalhe no doc irmão e nos docs de grupo 2/3 do corpus ([sildenafila-na-hipertensao-pulmonar-do-grupo-2-o-ensaio-siovac](/biblioteca/sildenafila-na-hipertensao-pulmonar-do-grupo-2-o-ensaio-siovac), [hipertensao-pulmonar-do-grupo-3-dpoc-e-dpi-criterios-prognostico-e-risco-do-vasodilatador-especifico](/biblioteca/hipertensao-pulmonar-do-grupo-3-dpoc-e-dpi-criterios-prognostico-e-risco-do-vasodilatador-especifico)).
- **D2/C3** = lógica ESC/ERS 2022 de risco dinâmico e meta de baixo risco; a intensificação farmacológica ocorre no centro, não neste fluxograma.
- Não substitui [fluxograma-hap-estratificacao-risco-terapia-combinada-inicial](/biblioteca/fluxograma-hap-estratificacao-risco-terapia-combinada-inicial).

## Segurança e fenótipo

Hemoptise pequena autolimitada ou congestão estável exige contato rápido com o centro; hemoptise relevante, hipoxemia, hipotensão, hipoperfusão ou deterioração rápida exige emergência. Falha/interrupção de prostaciclina parenteral contínua é emergência potencial por rebote; não improvisar suspensão ou transição. Gestação estável pede manejo especializado imediato, sem PS automático; deterioração impõe urgência.

Não escalar empiricamente fármacos de HAP em HP por doença esquerda; tratar a causa e discutir CpcPH complexo no centro. PH-ILD selecionada pode ter indicação específica, inclusive treprostinil inalado; grupo 3 não é proibição absoluta de toda terapia. Edema após vasodilatador também levanta PVOD/PCH. Na HP suspeita/nova, manter V/Q visível para excluir doença tromboembólica, mesmo com pistas de grupo 2/3; completar função pulmonar/DLCO, imagem e hemodinâmica conforme necessidade.
