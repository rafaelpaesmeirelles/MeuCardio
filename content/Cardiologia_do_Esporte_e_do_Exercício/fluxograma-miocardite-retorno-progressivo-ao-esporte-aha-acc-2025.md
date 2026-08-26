---
title: "Fluxograma: miocardite e retorno progressivo ao esporte — ACC 2024/AHA-ACC 2025"
slug: fluxograma-miocardite-retorno-progressivo-ao-esporte-aha-acc-2025
theme: "Cardiologia do Esporte e do Exercício"
kind: fluxograma
summary: "Árvore para suspeita de miocardite, estratificação inicial, restrição durante atividade da doença e reavaliação multiparamétrica antes do retorno ao esporte."
tags: ["atleta", "miocardite", "ressonância cardíaca", "arritmia", "retorno ao esporte", "exercício"]
review_status: revisado
review_note: "Fontes ACC, AHA e PubMed conferidas em 26/08/2026. Fluxo autoral; não usa calendário fixo como único critério e não reproduz figuras originais."
source_refs: ["Drazner MH, Bozkurt B, Cooper LT, et al. 2024 ACC Expert Consensus Decision Pathway on Strategies and Criteria for the Diagnosis and Management of Myocarditis. J Am Coll Cardiol. 2025;85(4):391-431. DOI: 10.1016/j.jacc.2024.10.080. PMID: 39665703.", "Kim JH, Baggish AL, Levine BD, et al. Clinical Considerations for Competitive Sports Participation for Athletes With Cardiovascular Abnormalities. Circulation. 2025;151(11):e716-e761. DOI: 10.1161/CIR.0000000000001297. PMID: 39973614.", "American College of Cardiology. 2024 ACC Expert Consensus Decision Pathway on Strategies and Criteria for the Diagnosis and Management of Myocarditis. https://www.acc.org/Guidelines/Guidelines/2024/09/24/12/05/Myocarditis"]
legacy_source: "Lacuna comprovada em 26/08/2026: havia síntese clínica de retorno após miocardite, mas nenhuma árvore de decisão conectando suspeita, gravidade, seguimento e retorno progressivo."
---

# Miocardite no atleta: da suspeita ao retorno

```mermaid
flowchart TD
  A["Atleta com dor torácica, palpitação/síncope<br/>ou insuficiência cardíaca/choque,<br/>especialmente após infecção ou outra exposição"]
  B(["Suspender exercício intenso durante avaliação"])
  C["Avaliação inicial dirigida:<br/>ECG, troponina de alta sensibilidade,<br/>biomarcadores pertinentes e ecocardiograma"]
  D{"Instabilidade, choque, disfunção importante<br/>ou arritmia ventricular/sustentada?"}
  E(["Internação e manejo em centro com suporte<br/>de insuficiência cardíaca/arritmia avançada"])
  F["Confirmar e estratificar conforme o caso:<br/>RMC; biópsia endomiocárdica quando indicada;<br/>investigar causa e predisposição"]
  G{"Miocardite ativa ou anormalidade<br/>clínica, funcional ou elétrica relevante?"}
  H(["Manter restrição de esforço intenso,<br/>tratar e programar vigilância longitudinal"])
  I["Reavaliar recuperação:<br/>sintomas + biomarcadores + função ventricular<br/>+ ritmo no esforço/monitorização + RMC se indicada"]
  J{"Recuperação clínica e funcional,<br/>sem arritmia relevante e sem atividade<br/>inflamatória que impeça progressão?"}
  K(["Não retornar; rever diagnóstico, tratamento,<br/>cicatriz, genética e risco residual"])
  L(["Retorno gradual, supervisionado e<br/>específico da modalidade + decisão compartilhada"])
  M["Seguimento e nova avaliação se sintomas,<br/>queda de desempenho ou arritmia"]

  A --> B --> C --> D
  D -->|"Sim"| E --> F
  D -->|"Não"| F
  F --> G
  G -->|"Sim"| H --> I
  G -->|"Não, diagnóstico alternativo"| M
  I --> J
  J -->|"Não"| K --> H
  J -->|"Sim"| L --> M
```

## Como interpretar

- A apresentação clássica pode ser dor torácica, arritmia/síncope ou insuficiência cardíaca/choque.
- Troponina normal não exclui isoladamente todos os casos; a probabilidade clínica e os demais testes importam.
- Ressonância cardíaca é central para diagnóstico não invasivo e estratificação; biópsia é reservada para indicações clínicas específicas.
- Retorno não deve depender somente do número de meses transcorridos. Recuperação clínica, função, ritmo e atividade inflamatória precisam ser integrados.
- Cicatriz residual e incerteza prognóstica devem entrar na decisão compartilhada e no plano de seguimento.

## Conteúdo conectado

- [Diretriz AHA/ACC 2025 sobre participação esportiva](/biblioteca/diretriz-participacao-esportiva-aha-acc-2025)
- [Miocardite no atleta e retorno ao esporte](/biblioteca/miocardite-retorno-ao-esporte)
- [COVID-19, miocardite pós-viral e triagem](/biblioteca/covid-19-miocardite-pos-viral-atleta-triagem-retorno-esporte)
- [Imagem avançada no atleta](/biblioteca/imagem-avancada-atleta-rmc-tc-nuclear-2026)

## Limite

O fluxo não substitui manejo etiológico da miocardite nem define autorização esportiva para um caso individual. Instabilidade ou arritmia grave exige atendimento emergencial.
