---
title: "Fluxograma ambulatorial: HAP — quando escalar ou referenciar"
slug: fluxograma-ambulatorial-hap-quando-escalar-ou-referenciar
theme: "Hipertensão pulmonar"
kind: fluxograma
fonte_producao: grok
summary: "Árvore de consultório para HAP conhecida: alarme urgente vs reavaliação de risco vs manter com reforço — apontando para estratificação ESC/ERS 2022 e centro especializado, sem doses."
review_status: pendente_revisao
review_note: "Irmão do protocolo sinalizadores-ambulatoriais-de-piora-na-hap (07/09/2026). ESC/ERS 2022 PMID 36017548."
source_refs:
  - "Humbert M, Kovacs G, Hoeper MM, et al; ESC/ERS Scientific Document Group. 2022 ESC/ERS Guidelines for the diagnosis and treatment of pulmonary hypertension. Eur Heart J. 2022;43(38):3618-3731. DOI: 10.1093/eurheartj/ehac237. PMID: 36017548"
  - "Corpus MeuCardio: sinalizadores-ambulatoriais-de-piora-na-hap.md; fluxograma-hap-estratificacao-risco-terapia-combinada-inicial.md; estratificacao-de-risco-e-terapia-combinada-inicial-na-hipertensao-arterial-pulmonar.md."
---

# Fluxograma ambulatorial: HAP — quando escalar ou referenciar

Prosa: [`sinalizadores-ambulatoriais-de-piora-na-hap`](sinalizadores-ambulatoriais-de-piora-na-hap.md). Armadilha de fenótipo: [`sinalizadores-ambulatoriais-nao-tratar-hp-grupo-2-3-como-hap`](sinalizadores-ambulatoriais-nao-tratar-hp-grupo-2-3-como-hap.md).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Retorno ambulatorial: HAP conhecida<br/>em terapia específica"] --> D0{"Há alarme urgente?<br/>síncope · hemoptise · falência direita franca<br/>hipoxemia grave · instabilidade"}

  D0 -->|"Sim"| C0(["Via urgente / emergência<br/>Contatar centro de HP<br/>Não aguardar retorno eletivo"])

  D0 -->|"Não"| D1{"Fenótipo ainda compatível com HAP?<br/>Ou suspeita forte de grupo 2/3/5?"}

  D1 -->|"Dúvida de grupo / HP pós-capilar"| C1(["Não escalar vasodilatador HAP<br/>Rever diagnóstico (eco, comorbidades)<br/>Ver doc armadilha grupo 2/3"])

  D1 -->|"HAP plausível"| D2{"Classe funcional, sintomas<br/>ou biomarcador pioraram<br/>em relação ao basal?"}

  D2 -->|"Não — estável em baixo risco"| C2(["Manter plano<br/>Reforçar adesão e sinais de alarme<br/>Manter calendário de risco ESC/ERS"])

  D2 -->|"Sim / risco intermediário-alto ou alto"| C3(["Antecipar reavaliação de risco<br/>Discussão com centro especializado<br/>Considerar intensificação / avançados<br/>Sem inventar doses neste fluxograma"])

  D2 -->|"Adesão falhou ou precipitante óbvio"| C4(["Corrigir adesão / precipitante<br/>Reavaliar cedo<br/>Se não melhorar → tratar como C3"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  classDef neutro fill:#eef2f7,stroke:#3d5a80,color:#102a43;
  class C0,C1 alerta;
  class C2 conduta;
  class C3,C4 neutro;
```

## Notas

- **D0** = gate de segurança ambulatorial (síncope e falência direita não são "ajuste de agenda").
- **D1** = evita iatrogenia: vasodilatador arterial pulmonar em HP do grupo 2 pode precipitar edema — detalhe no doc irmão e nos docs de grupo 2/3 do corpus ([`sildenafila-na-hipertensao-pulmonar-do-grupo-2-o-ensaio-siovac`](sildenafila-na-hipertensao-pulmonar-do-grupo-2-o-ensaio-siovac.md), [`hipertensao-pulmonar-do-grupo-3-dpoc-e-dpi-criterios-prognostico-e-risco-do-vasodilatador-especifico`](hipertensao-pulmonar-do-grupo-3-dpoc-e-dpi-criterios-prognostico-e-risco-do-vasodilatador-especifico.md)).
- **D2/C3** = lógica ESC/ERS 2022 de risco dinâmico e meta de baixo risco; a intensificação farmacológica ocorre no centro, não neste fluxograma.
- Não substitui [`fluxograma-hap-estratificacao-risco-terapia-combinada-inicial`](fluxograma-hap-estratificacao-risco-terapia-combinada-inicial.md).
