---
title: "Fluxograma ambulatorial: sinalizadores no atleta — PS agora vs. restrição + investigação vs. liberar com plano"
slug: fluxograma-ambulatorial-sinalizadores-atleta-destino
theme: "Cardiologia do Esporte e do Exercício"
kind: fluxograma
fonte_producao: grok
summary: "Árvore ambulatorial de destino no atleta sintomático: gate de alarme para PS/suspensão imediata, braço de restrição com investigação dirigida, e braço de liberação com educação de alarmes — sem duplicar o fluxograma de síncope no esforço."
review_status: pendente_revisao
review_note: "Irmão do protocolo sinalizadores-ambulatoriais-no-atleta-quando-suspender-e-encaminhar (07/09/2026). PIVOT: fluxograma-ambulatorial-sincope-no-esporte-destino evitado — já existem fluxograma-sincope-durante-exercicio-atleta e prosa dedicada. Fontes: ESC sports 2020 PMID 32860412; AHA/ACC 2025 PMID 39973614; HRS 2024 PMID 38763377. Sem doses."
source_refs:
  - "Pelliccia A, Sharma S, Gati S, et al. 2020 ESC Guidelines on sports cardiology and exercise in patients with cardiovascular disease. Eur Heart J. 2021;42(1):17-96. DOI: 10.1093/eurheartj/ehaa605. PMID: 32860412"
  - "Kim JH, Baggish AL, Levine BD, et al. Clinical Considerations for Competitive Sports Participation for Athletes With Cardiovascular Abnormalities: A Scientific Statement From the American Heart Association and American College of Cardiology. Circulation. 2025. DOI: 10.1161/CIR.0000000000001297. PMID: 39973614"
  - "Lampert R, Chung EH, Ackerman MJ, et al. 2024 HRS expert consensus statement on arrhythmias in the athlete: Evaluation, treatment, and return to play. Heart Rhythm. 2024. DOI: 10.1016/j.hrthm.2024.05.018. PMID: 38763377"
---

# Fluxograma ambulatorial: sinalizadores no atleta — destino

Prosa: [`sinalizadores-ambulatoriais-no-atleta-quando-suspender-e-encaminhar`](sinalizadores-ambulatoriais-no-atleta-quando-suspender-e-encaminhar.md). Dor torácica: [`dor-toracica-no-atleta-ambulatorial-quando-escalar`](dor-toracica-no-atleta-ambulatorial-quando-escalar.md). Síncope (não duplicar): [`fluxograma-sincope-durante-exercicio-atleta`](fluxograma-sincope-durante-exercicio-atleta.md).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta / contato ambulatorial<br/>atleta com sintoma ou achado novo"] --> D1{"Alarme imediato?<br/>síncope no esforço / dor em curso<br/>arritmia com pré-síncope<br/>instabilidade / ECG vermelho + sintoma"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["Suspender exercício AGORA<br/>PS se instável / dor em curso / síncope recente<br/>Se síncope: usar fluxograma-sincope-durante-exercicio-atleta"])

  D1 -->|"Não"| D2{"Sintoma relacionado ao esforço<br/>sem instabilidade?<br/>dor de esforço / dispneia desproporcional<br/>palpitação significativa / queda de performance"}

  D2 -->|"Sim"| P1["ECG + exame; história dirigida<br/>Suspender competição / HIIT"]
  P1 --> C2(["Investigação dirigida<br/>eco ± TE máximo ± monitor ± RMC/imagem<br/>Retorno só com plano diagnóstico"])

  D2 -->|"Não"| D3{"Quadro claramente não cardíaco<br/>e ECG/exame sem red flag?"}

  D3 -->|"Sim"| C3(["Liberar com plano escrito de alarmes<br/>Reavaliar se o quadro mudar"])
  D3 -->|"Não / dúvida"| C4(["Restrição temporária prudente<br/>Reavaliação precoce 24–72 h<br/>ou cardiologia do esporte"])

  C2 --> D4{"Acesso a investigação e suporte OK?"}
  D4 -->|"Não / sintoma recorrente / master de alto risco"| C5(["Antecipar cardiologia / PS<br/>se surgir alarme da tabela"])
  D4 -->|"Sim"| C6(["Manter restrição até esclarecer<br/>Não liberar por calendário de prova"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1,C5 alerta;
  class C2,C3,C4,C6 conduta;
```

## Notas

- **D1** = gate de segurança (ESC sports 2020 / AHA/ACC 2025 / HRS 2024).
- **D2** = sintoma de esforço sem instabilidade → restrição + investigação (não “treinar até o exame”).
- **D3** = liberação só com ausência convincente de red flags.
- Síncope no esforço: **não** decidir neste fluxograma — ir ao pacote já publicado.
- Não decide doses, elegibilidade definitiva por doença estrutural nem protocolo de SCA.
