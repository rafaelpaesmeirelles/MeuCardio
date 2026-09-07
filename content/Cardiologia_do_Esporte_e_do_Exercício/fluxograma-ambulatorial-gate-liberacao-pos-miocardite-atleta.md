---
title: "Fluxograma ambulatorial: gate de liberação pós-miocardite no atleta"
slug: fluxograma-ambulatorial-gate-liberacao-pos-miocardite-atleta
theme: "Cardiologia do Esporte e do Exercício"
kind: fluxograma
fonte_producao: grok
summary: "Árvore ambulatorial da visita de reavaliação pós-miocardite: instabilidade→PS; exames incompletos→manter restrição; red flags→escalar/reter; gate verde→retorno progressivo com plano — sem duplicar os fluxogramas RTP clínicos já revisados."
review_status: pendente_revisao
review_note: "Irmão do protocolo gate-ambulatorial-liberacao-retorno-pos-miocardite-no-atleta (07/09/2026). Além #848/#877. Fontes: AHA/ACC 2025 PMID 39973614; ESC sports 2020 PMID 32860412; HRS 2024 PMID 38763377; ACC ECDP 2024 PMID 39665703. Sem doses."
source_refs:
  - "Kim JH, Baggish AL, Levine BD, et al. Clinical Considerations for Competitive Sports Participation for Athletes With Cardiovascular Abnormalities: A Scientific Statement From the American Heart Association and American College of Cardiology. Circulation. 2025;151(11):e716-e761. DOI: 10.1161/CIR.0000000000001297. PMID: 39973614"
  - "Pelliccia A, Sharma S, Gati S, et al. 2020 ESC Guidelines on sports cardiology and exercise in patients with cardiovascular disease. Eur Heart J. 2021;42(1):17-96. DOI: 10.1093/eurheartj/ehaa605. PMID: 32860412"
  - "Lampert R, Chung EH, Ackerman MJ, et al. 2024 HRS expert consensus statement on arrhythmias in the athlete: evaluation, treatment, and return to play. Heart Rhythm. 2024;21(10):e151-e252. DOI: 10.1016/j.hrthm.2024.05.018. PMID: 38763377"
  - "Drazner MH, Bozkurt B, Cooper LT, et al. 2024 ACC Expert Consensus Decision Pathway on Strategies and Criteria for the Diagnosis and Management of Myocarditis. J Am Coll Cardiol. 2025;85(4):391-431. DOI: 10.1016/j.jacc.2024.10.080. PMID: 39665703"
---

# Fluxograma ambulatorial: gate de liberação pós-miocardite no atleta

Prosa: [`gate-ambulatorial-liberacao-retorno-pos-miocardite-no-atleta`](gate-ambulatorial-liberacao-retorno-pos-miocardite-no-atleta.md). Braço exames: [`exames-pendentes-antes-da-liberacao-pos-miocardite-ambulatorial`](exames-pendentes-antes-da-liberacao-pos-miocardite-ambulatorial.md). Critérios clínicos detalhados: [`fluxograma-miocardite-retorno-esporte-atleta`](fluxograma-miocardite-retorno-esporte-atleta.md).

Não duplica: [`fluxograma-ambulatorial-sinalizadores-atleta-destino`](fluxograma-ambulatorial-sinalizadores-atleta-destino.md) (#848) nem [`fluxograma-ambulatorial-hipertensao-atleta-destino`](fluxograma-ambulatorial-hipertensao-atleta-destino.md) (#877).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Visita ambulatorial de reavaliação\npós-miocardite — candidato a RTP"] --> D1{"Instabilidade, IC aguda,\narritmia sustentada ou síncope recente?"}

  D1 -->|"Sim"| C1(["PS / urgência agora\nNão liberar esporte"])

  D1 -->|"Não"| D2{"Pacote mínimo disponível?\n(sintomas + biomarcadores + eco\n+ Holter + esforço ± RMC indicada)"}

  D2 -->|"Não / incompleto"| C2(["Manter restrição de esforço intenso\nAgendar exames faltantes\nOrientação escrita de alarmes"])

  D2 -->|"Sim"| D3{"Há red flag?\nSintomas ativos, FEVE residual,\narritmia complexa, inflamação ativa,\nrecorrência / síncope-parada / genética"}

  D3 -->|"Sim — elétrico / síncope / recorrência"| C3(["Não liberar\nEscalar EP / cardiomiopatias\nVer árvore RTP clínica"])
  D3 -->|"Sim — inflamação / FEVE / biomarcadores"| C4(["Manter restrição\nTratar / vigiar\nReavaliar até resolução da fase ativa"])
  D3 -->|"Só LGE discreto isolado"| C5(["Decisão compartilhada\nMonitorização adicional\nNão = liberação automática"])
  D3 -->|"Não"| C6(["Liberar retorno PROGRESSIVO\ncom plano escrito + alarmes\nReavaliar se sintomas / arritmia"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1,C3 alerta;
  class C2,C4,C5,C6 conduta;
```

## Notas

- **D1** = gate de segurança (não é visita de liberação se há urgência).
- **D2** = exames incompletos bloqueiam liberação (ACC ECDP / AHA/ACC 2025).
- **D3** = red flags clínicos já detalhados nos fluxogramas RTP revisados; este fluxograma só roteia destino ambulatorial.
- Retorno é sempre **progressivo**, nunca “volta amanhã à final”.
- Não decide doses, WADA, nem elegibilidade por calendário isolado.
