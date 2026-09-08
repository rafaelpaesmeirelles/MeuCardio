---
title: "Fluxograma ambulatorial: gate de liberação pós-miocardite no atleta"
slug: fluxograma-ambulatorial-gate-liberacao-pos-miocardite-atleta
theme: "Cardiologia do Esporte e do Exercício"
kind: fluxograma
fonte_producao: grok
summary: "Árvore da reavaliação pós-miocardite: emergência atual→via aguda; exames indicados incompletos→restrição; biomarcador/inflamação/arritmia→não liberar; LGE residual→decisão contextual; gate completo→retorno progressivo."
review_status: revisado
review_note: "Revisão clínica/editorial concluída em 08/09/2026. Separada síncope histórica estável de emergência atual; LGE residual ganhou nó próprio; biomarcadores devem estar normalizados; RMC indicada pendente bloqueia liberação; fatores históricos podem reentrar no gate após avaliação especializada satisfatória; removidas referências a PRs #848/#877 ainda não presentes na árvore."
source_refs:
  - "Kim JH, Baggish AL, Levine BD, et al. Clinical Considerations for Competitive Sports Participation for Athletes With Cardiovascular Abnormalities: A Scientific Statement From the American Heart Association and American College of Cardiology. Circulation. 2025;151(11):e716-e761. DOI: 10.1161/CIR.0000000000001297. PMID: 39973614"
  - "Pelliccia A, Sharma S, Gati S, et al. 2020 ESC Guidelines on sports cardiology and exercise in patients with cardiovascular disease. Eur Heart J. 2021;42(1):17-96. DOI: 10.1093/eurheartj/ehaa605. PMID: 32860412"
  - "Lampert R, Chung EH, Ackerman MJ, et al. 2024 HRS expert consensus statement on arrhythmias in the athlete: evaluation, treatment, and return to play. Heart Rhythm. 2024;21(10):e151-e252. DOI: 10.1016/j.hrthm.2024.05.018. PMID: 38763377"
  - "Drazner MH, Bozkurt B, Cooper LT, et al. 2024 ACC Expert Consensus Decision Pathway on Strategies and Criteria for the Diagnosis and Management of Myocarditis. J Am Coll Cardiol. 2025;85(4):391-431. DOI: 10.1016/j.jacc.2024.10.080. PMID: 39665703"
---

# Fluxograma ambulatorial: gate de liberação pós-miocardite no atleta

Prosa: [`gate-ambulatorial-liberacao-retorno-pos-miocardite-no-atleta`](gate-ambulatorial-liberacao-retorno-pos-miocardite-no-atleta.md). Exames: [`exames-pendentes-antes-da-liberacao-pos-miocardite-ambulatorial`](exames-pendentes-antes-da-liberacao-pos-miocardite-ambulatorial.md). Critérios clínicos detalhados: [`fluxograma-miocardite-retorno-esporte-atleta`](fluxograma-miocardite-retorno-esporte-atleta.md).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Visita de reavaliação pós-miocardite<br/>candidato a retorno ao esporte"] --> D1{"Há emergência ATUAL?<br/>instabilidade, IC aguda, arritmia sustentada<br/>ou sintomas de alto risco em curso"}

  D1 -->|"Sim"| C1(["PS / urgência agora<br/>Não liberar esporte"])
  D1 -->|"Não"| D1B{"Há síncope/PCR/recorrência histórica<br/>ou suspeita genética ainda NÃO esclarecida?"}

  D1B -->|"Sim"| C1B(["Manter restrição<br/>Avaliação EP/cardiomiopatias/genética<br/>Sem PS automático se atualmente estável"])
  C1B --> D1C{"Avaliação especializada concluída<br/>sem contraindicação residual?"}
  D1C -->|"Não / pendente"| C1D(["Continuar restrição e investigação"])
  D1C -->|"Sim"| D2
  D1B -->|"Não"| D2{"Pacote de reavaliação INDICADO completo?<br/>clínica + biomarcadores + eco<br/>+ monitorização + esforço ± RMC indicada"}

  D2 -->|"Não"| C2(["Manter restrição<br/>Completar exames necessários<br/>Não liberar enquanto resultado indicado está pendente"])
  D2 -->|"Sim"| D3{"Biomarcadores normalizados,<br/>função recuperada e sem inflamação ativa?"}

  D3 -->|"Não"| C3(["Não liberar<br/>Tratar / vigiar / reavaliar"])
  D3 -->|"Sim"| D4{"Holter/monitorização e esforço<br/>sem arritmia clinicamente relevante?"}

  D4 -->|"Não"| C4(["Não liberar<br/>Escalar EP conforme achado"])
  D4 -->|"Sim"| D5{"Há LGE residual na RMC<br/>sem edema/inflamação ativa?"}

  D5 -->|"Sim"| C5(["Decisão compartilhada<br/>Interpretar extensão/localização + risco elétrico<br/>Monitorização adicional quando apropriada<br/>Não é liberação automática"])
  D5 -->|"Não"| C6(["Gate verde completo<br/>Retorno PROGRESSIVO com plano escrito<br/>Interromper e reavaliar se sintomas/arritmia"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1,C1D,C2,C3,C4 alerta;
  class C1B,C5,C6 conduta;
```

## Notas

- **D1** pergunta por emergência atual; síncope histórica estável não é, sozinha, motivo para PS imediato.
- **D1B/D1C** permitem que fatores históricos reentrem no gate após investigação especializada satisfatória, em vez de funcionarem como bloqueio vitalício.
- **D2**: se uma RMC foi considerada indicada para fechar a decisão, o laudo deve estar disponível e revisado antes da liberação.
- **D3**: biomarcador relevante ainda elevado, mesmo em queda, não cumpre gate verde.
- **D5** impede que LGE residual isolado seja confundido com “sem red flag” e levado diretamente à liberação.
- O backend converte links Markdown relativos canônicos para rotas `/biblioteca/<slug>`; referências a documentos ainda ausentes foram deliberadamente removidas.
