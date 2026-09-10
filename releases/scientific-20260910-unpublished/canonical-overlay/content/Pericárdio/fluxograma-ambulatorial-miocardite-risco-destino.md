---
slug: fluxograma-ambulatorial-miocardite-risco-destino
title: 'Fluxograma ambulatorial: miocardite — risco ESC 2025 e destino'
kind: fluxograma
theme: Pericárdio
summary: 'Miocardite suspeita ou confirmada: apresentação aguda intermediária/alta exige avaliação hospitalar; internação
  também deve ser considerada no baixo risco. Seguimento após estabilização inclui restrição de exercício e reavaliação
  estruturada.'
tags: []
source_refs:
- 'Schulz-Menger J; Collini V; Gröschel J. 2025 ESC Guidelines for the management of myocarditis and pericarditis.
  Eur Heart J. 2025;46:3952. DOI: 10.1093/eurheartj/ehaf192. PMID: 40878297.'
evidence_level: null
source_tier: A
review_status: revisado
gaps: []
published: false
---

# Fluxograma ambulatorial: miocardite — risco e destino

Prosa: [sinalizadores-ambulatoriais-miocardite-quando-encaminhar](/biblioteca/sinalizadores-ambulatoriais-miocardite-quando-encaminhar). Checklist: [miocardite-checklist-ambulatorial-de-alarme](/biblioteca/miocardite-checklist-ambulatorial-de-alarme). Diagnóstico/EMB: [miocardite-diagnostico-estratificacao-de-risco-e-biopsia-endomiocardica-esc-2025](/biblioteca/miocardite-diagnostico-estratificacao-de-risco-e-biopsia-endomiocardica-esc-2025).

## Árvore de decisão

```mermaid
flowchart TD
 R["Suspeita ou miocardite conhecida"] --> I{"Exposição a inibidor de checkpoint imune?"}
 I -->|Sim| CI["Suspender ICI e avaliação hospitalar monitorizada;<br/>protocolo dedicado de miocardite por ICI"]
 I -->|Não| A{"Apresentação aguda tipo SCA ou instabilidade?"}
 A -->|Sim| E["Emergência: excluir SCA/DAC/SCAD conforme hipótese;<br/>estabilizar antes da estratificação completa"]
 A -->|Não| H{"Alto risco: IC aguda/choque, síncope/parada,<br/>TV sustentada/FV, BAV avançado,<br/>FEVE nova <40% OU LGE extenso?"}
 H -->|Sim| E
 H -->|Não| M{"Intermediário: dispneia progressiva, TVNS,<br/>troponina persistente/recidivante,<br/>FEVE recém-reduzida 41–49% ou alteração segmentar,<br/>ou FEVE ≥50% com LGE ≥2 segmentos?"}
 M -->|Sim| O["Avaliação hospitalar/internação se agudo;<br/>ECG/eco/RMC e monitorização conforme quadro"]
 M -->|Não ou dados incompletos| L{"Baixo risco realmente documentado?<br/>Estável, FEVE ≥50%, LGE ausente/<2 segmentos,<br/>sem qualquer critério superior"}
 L -->|Não| O
 L -->|Sim| B{"Novo episódio agudo?"}
 B -->|Sim| C["Considerar internação; decisão especializada<br/>com acesso e segurança documentados"]
 B -->|Seguimento após estabilização| F["Seguimento precoce e reavaliação completa em até seis meses;<br/>restrição de exercício e alarmes escritos"]
```

## Etapas obrigatórias antes de concluir baixo risco

Suspeita de SCA requer investigação coronária conforme probabilidade; troponina não confirma miocardite isoladamente. Se exposição a ICI, usar imediatamente [via específica](/biblioteca/miocardite-por-inibidor-de-checkpoint-imune-emergencia-esc-2025), com suspensão do ICI e avaliação hospitalar monitorizada. RMC integra confirmação e estratificação quando apropriada; dados incompletos não equivalem a baixo risco.

Na suspeita aguda intermediária, priorizar avaliação hospitalar/internação; casos baixos também exigem considerar internação. Seguimento ambulatorial pressupõe estabilidade e via estruturada. FEVE exatamente 40% não está explicitada no corte da tabela citada: não classificá-la como baixo risco; resolver pelo quadro completo e avaliação especializada. LGE extenso é critério alto independente, sem inventar número de segmentos. EMB exige decisão especializada por apresentação/etiologia e impacto terapêutico, não automatismo por um achado.

Após miocardite confirmada, planejar reavaliação clínica, biomarcadores, ECG, eco, Holter, RMC e teste de esforço quando clinicamente seguro, dentro de seis meses. Restringir exercício até remissão e por pelo menos um mês, com retorno individualizado no protocolo próprio; não realizar teste na fase ativa apenas para cumprir calendário.
