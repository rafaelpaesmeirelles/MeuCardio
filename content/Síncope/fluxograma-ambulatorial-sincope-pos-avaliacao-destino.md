---
title: 'Fluxograma ambulatorial: síncope pós-avaliação — destino PS vs. retorno precoce'
slug: fluxograma-ambulatorial-sincope-pos-avaliacao-destino
theme: Síncope
kind: fluxograma
fonte_producao: grok
summary: 'Árvore ambulatorial pós-alta/pós-avaliação: alarme de alto risco → PS; recorrência ‘benigna’ → retorno precoce; baixo risco estável → plano ambulatorial
  — alinhada à ESC 2018.'
review_status: revisado
review_note: 'Revisão clínica e editorial focal em 08/09/2026 do PR #859, desde seu HEAD remoto. Correções e fontes verificadas registradas em docs/revisao-cientifica-pr826-859-20260908.md.
  Prazos operacionais não equivalem a recomendações normativas; preservar avaliação individual e vias de emergência.'
source_refs:
- 'Brignole M; Moya A; de Lange FJ. 2018 ESC Guidelines for the diagnosis and management of syncope. Eur Heart J. 2018;39:1883. DOI: 10.1093/eurheartj/ehy037.
  PMID: 29562304.'
- 'Brignole M, Moya A, de Lange FJ, et al. Practical Instructions for the 2018 ESC Guidelines for the diagnosis and management of syncope. Eur Heart J.
  2018;39(21):e43-e80. DOI: 10.1093/eurheartj/ehy071'
---

# Fluxograma ambulatorial: síncope pós-avaliação — destino

Prosa: [[sinalizadores-ambulatoriais-sincope-pos-alta-quando-retornar](/biblioteca/sinalizadores-ambulatoriais-sincope-pos-alta-quando-retornar)](/biblioteca/sinalizadores-ambulatoriais-sincope-pos-alta-quando-retornar). Gate atividades: [[sincope-gate-ambulatorial-retorno-atividades-trabalho-direcao](/biblioteca/sincope-gate-ambulatorial-retorno-atividades-trabalho-direcao)](/biblioteca/sincope-gate-ambulatorial-retorno-atividades-trabalho-direcao). Estratificação no DE: [[fluxograma-sincope-criterios-de-alto-risco-emergencia-esc-2018-eusem-2024](/biblioteca/fluxograma-sincope-criterios-de-alto-risco-emergencia-esc-2018-eusem-2024)](/biblioteca/fluxograma-sincope-criterios-de-alto-risco-emergencia-esc-2018-eusem-2024).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta ambulatorial / pós-alta do DE<br/>síncope já estratificada como baixo risco<br/>ou seguimento após avaliação inicial"] --> D1{"Novo alarme de alto risco?<br/>síncope em esforço / decúbito / sentado<br/>cardiopatia estrutural/coronariana grave<br/>história familiar de morte súbita precoce<br/>trauma / dor torácica / dispneia aguda<br/>ECG alarmante / suspeita de falha de dispositivo<br/>hipoperfusão"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["Encaminhar AGORA<br/>PS / urgência / unidade de síncope<br/>Reabrir Tabelas 5–7 ESC 2018"])

  D1 -->|"Não"| D2{"Recorrência com pródromo típico<br/>ou pré-síncope frequente<br/>sem critérios de PS?"}

  D2 -->|"Sim"| P1["História + exame + PA supina/em pé<br/>Revisar / repetir ECG se mudança"]
  P1 --> C2["Retorno proporcional ao risco<br/>Alarmes escritos<br/>Educação de gatilhos / pródromo"]

  D2 -->|"Não"| D3{"Baixo risco mantido?<br/>causa reflexa/situacional/ortostática plausível<br/>sem recorrência alarmante<br/>ECG e exame estáveis"}

  D3 -->|"Sim"| C3(["Plano ambulatorial<br/>Orientação escrita de alarmes<br/>Gate separado para trabalho/direção"])
  D3 -->|"Incerto / nem alto nem baixo"| C4(["Observação no DE ou unidade de síncope<br/>ESC: Classe I B"])

  C2 --> D4{"Acesso e suporte garantidos?"}
  D4 -->|"Não / piora rápida"| C5(["Avaliação presencial em serviço acessível;<br/>piora/instabilidade: emergência"])
  D4 -->|"Sim"| C6(["Manter seguimento individualizado<br/>Não protocolar doses / ILR / MP aqui"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1,C5 alerta;
  class C2,C3,C4,C6 conduta;
```

## Notas

- **D1** = gate de segurança (reabertura de alto risco ESC 2018).
- **D2** = recorrência “benigna” → destino clínico precoce, não alta sem plano.
- **D3** = baixo risco só com dados coerentes; se nem alto nem baixo, observação no DE/unidade de síncope.
- Trabalho, direção e altura ficam no documento-gate irmão (sem inventar legislação).

## Reabrir risco e definir investigação

Baixo risco na alta descreve aquele momento. Novo fenótipo, trauma relevante, cardiopatia estrutural/coronariana grave, ECG alterado ou história familiar de morte súbita precoce reabrem estratificação. Ausência de pródromo isolada não determina alto risco; considerar os demais achados. Síncope durante esforço, supina ou sentada exige particular atenção. Se nem alto nem baixo risco após reavaliação, a recomendação ESC é observação no DE/unidade de síncope, não retorno curto rotulado Classe I.

Em portador de dispositivo estável, providenciar interrogação rápida com correlação clínica; instabilidade, choque de CDI, trauma, suspeita de BAV/pausas ou falta de acesso rápido exigem via urgente. Convulsão prolongada, confusão persistente ou déficit focal seguem emergência neurológica apropriada. Recorrência inexplicada exige investigação com monitorização prolongada/ILR ou estudo eletrofisiológico conforme substrato, em vez de retornos curtos indefinidos.

Síncope ao dirigir é freio específico à liberação, mesmo em condutor particular. Regras ocupacionais/legais dependem de jurisdição, licença, causa e recorrência; não derivar prazo legal da janela clínica de retorno.
