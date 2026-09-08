---
title: 'Fluxograma ambulatorial: pericardite com piora — PS agora vs. retorno precoce vs. especialidade'
slug: fluxograma-ambulatorial-pericardite-piora-destino
theme: Pericárdio
kind: fluxograma
fonte_producao: grok
summary: 'Árvore ambulatorial de destino na pericardite: gate de alarme para PS/tamponamento, braço de inflamação controlável com retorno precoce, e braço
  de recorrência/falha terapêutica para referência especializada.'
review_status: revisado
review_note: 'Revisão clínica e editorial focal em 08/09/2026 do PR #846, desde seu HEAD remoto. Correções e fontes verificadas registradas em docs/revisao-cientifica-pr826-859-20260908.md.
  Prazos operacionais não equivalem a recomendações normativas; preservar avaliação individual e vias de emergência.'
source_refs:
- 'Schulz-Menger J; Collini V; Gröschel J. 2025 ESC Guidelines for the management of myocarditis and pericarditis. Eur Heart J. 2025;46:3952. DOI: 10.1093/eurheartj/ehaf192.
  PMID: 40878297.'
- 'Imazio M; Brucato A; Cemin R. A randomized trial of colchicine for acute pericarditis. N Engl J Med. 2013;369:1522. DOI: 10.1056/NEJMoa1208536. PMID:
  23992557.'
- 'Klein AL; Imazio M; Cremer P. Phase 3 Trial of Interleukin-1 Trap Rilonacept in Recurrent Pericarditis. N Engl J Med. 2021;384:31. DOI: 10.1056/NEJMoa2027892.
  PMID: 33200890.'
---

# Fluxograma ambulatorial: pericardite com piora — destino

Prosa: [[sinalizadores-ambulatoriais-pericardite-quando-encaminhar](/biblioteca/sinalizadores-ambulatoriais-pericardite-quando-encaminhar)](/biblioteca/sinalizadores-ambulatoriais-pericardite-quando-encaminhar). Checklist: [[pericardite-checklist-ambulatorial-de-alarme](/biblioteca/pericardite-checklist-ambulatorial-de-alarme)](/biblioteca/pericardite-checklist-ambulatorial-de-alarme). Escalonamento farmacológico: [[fluxograma-pericardite-recorrente-refrataria-escalonamento-terapeutico](/biblioteca/fluxograma-pericardite-recorrente-refrataria-escalonamento-terapeutico)](/biblioteca/fluxograma-pericardite-recorrente-refrataria-escalonamento-terapeutico). Tamponamento: [[fluxograma-tamponamento-cardiaco](/biblioteca/fluxograma-tamponamento-cardiaco)](/biblioteca/fluxograma-tamponamento-cardiaco).

## Árvore de decisão

```mermaid
flowchart TD
 R["Pericardite conhecida com piora"] --> A{"Instabilidade, suspeita de tamponamento,<br/>dor isquêmica, arritmia relevante,<br/>troponina com deterioração ou toxemia?"}
 A -->|Sim| E["Emergência agora; avaliar diagnósticos alternativos"]
 A -->|Não| H{"Algum marcador maior ou menor de alto risco?<br/>Ver critérios abaixo"}
 H -->|Sim| I["Avaliação hospitalar e investigação etiológica;<br/>não aguardar retorno ambulatorial habitual"]
 H -->|Não| F{"Recorrência com inflamação objetiva,<br/>falha adequada à primeira linha<br/>ou dependência de corticoide?"}
 F -->|Sim| S["Referência especializada e reavaliação precoce;<br/>escalonamento no protocolo canônico"]
 F -->|Não| P["Rever diagnóstico, adesão e inflamação;<br/>24–72 h se necessário e acesso garantido"]
 P --> Q{"Segurança e acesso viáveis?"}
 Q -->|Não| I
 Q -->|Sim| O["Orientação escrita e retorno conforme evolução"]
```

## Critérios que precedem o retorno ambulatorial

Febre >38 °C, curso subagudo, derrame grande (>20 mm ao eco), tamponamento ou ausência de resposta ao AAS/AINE após tratamento adequado são marcadores maiores; acometimento miocárdico, imunossupressão, trauma e anticoagulação oral são marcadores menores. Qualquer marcador requer avaliação hospitalar e investigação etiológica; estabilidade hemodinâmica não autoriza simplesmente aguardar consulta. Derrame grande estável ou anticoagulação isolada não equivalem a tamponamento: emergência imediata depende de repercussão/instabilidade; organizar hospitalização e avaliação rápida mesmo sem choque.

Não esperar a tríade de Beck: ela é pouco sensível. Integrar sinais vitais, perfusão, pulso paradoxal, sintomas e ecocardiograma urgente quando houver suspeita. Ausência da tríade não exclui tamponamento.

Recorrência precisa de sustentação objetiva; dor isolada não justifica anti-IL-1. Confirmar adesão, dose e duração adequadas da primeira linha no protocolo canônico. Febre/toxemia exige considerar etiologia bacteriana, tuberculose e outras causas. Restringir exercício até remissão, por pelo menos um mês, com duração e retorno individualizados (ESC 2025); envolvimento miocárdico exige orientação específica. Os prazos ambulatoriais só valem na ausência de alto risco e com acesso seguro.
