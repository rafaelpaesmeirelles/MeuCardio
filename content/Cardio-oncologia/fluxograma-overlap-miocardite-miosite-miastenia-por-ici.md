---
title: "Fluxograma: overlap miocardite–miosite–miastenia por ICI"
slug: fluxograma-overlap-miocardite-miosite-miastenia-por-ici
theme: "Cardio-oncologia"
kind: fluxograma
summary: "Árvore de emergência para toxicidade cardio-neuromuscular por ICI, com corticoide precoce, avaliação respiratória e escalada se resistente."
review_status: revisado
source_refs: ["Schulz-Menger J, Collini V, Gröschel J, et al. 2025 ESC Guidelines for the management of myocarditis and pericarditis. Eur Heart J. 2025;46(40):3952-4041. DOI: 10.1093/eurheartj/ehaf192. PMID: 40878297.", "Lyon AR, López-Fernández T, Couch LS, et al. 2022 ESC Guidelines on cardio-oncology. DOI: 10.1093/eurheartj/ehac244. PMID: 36017568.", "Schneider BJ, Naidoo J, Santomasso BD, et al. Management of Immune-Related Adverse Events in Patients Treated With Immune Checkpoint Inhibitor Therapy: ASCO Guideline Update. J Clin Oncol. 2021;39(36):4073-4126. DOI: 10.1200/JCO.21.01440. PMID: 34724392.", "Pathak R, et al. Oncologist. 2021;26(12):1052-1061. DOI: 10.1002/onco.13931. PMID: 34378270."]
review_note: "Revisado em 26/08/2026 contra a diretriz ESC 2025 de miocardite (PMID 40878297), a ESC 2022 de cardio-oncologia (PMID 36017568) e a atualização ASCO 2021 de toxicidades por ICI (PMID 34724392). Corrigida a sequência que esperava três dias e uma queda isolada de troponina >50% antes de procurar gravidade miastênica: disfagia, fraqueza facial/respiratória ou progressão rápida agora acionam imediatamente unidade com capacidade de UTI e IVIG ou plasmaférese, em paralelo ao corticoide. A função respiratória passou a incluir capacidade vital e força inspiratória negativa seriadas. A resposta cardíaca é reavaliada em 24-48 horas por clínica/hemodinâmica, disfunção ventricular, bloqueio/arritmia e troponina, sem usar biomarcador isolado. Pendente revisão médica independente antes de uso assistencial."
---

# Overlap por ICI

```mermaid
flowchart TD
  R0["Paciente em ICI com suspeita de miocardite<br/>(troponina/ECG/sintomas cardíacos) + fraqueza,<br/>ptose, disfagia, dispneia ou CK elevada"]
  P1["Suspender ICI + telemetria + ECG/troponina/CK<br/>+ TTE + neurologia; medir capacidade vital<br/>e força inspiratória negativa de forma seriada"]
  D1{"Instabilidade, BAV completo,<br/>TV ou falência respiratória?"}
  P2["UTI imediata + suporte elétrico/<br/>hemodinâmico/ventilatório conforme necessidade"]
  P3["Miocardite provável: iniciar corticoide de alta dose<br/>sem aguardar CMR/biópsia; dose e pulso<br/>conforme gravidade no fluxo específico de miocardite"]
  D2{"Disfagia, fraqueza facial/respiratória<br/>ou progressão rápida?"}
  P4["Unidade com capacidade de UTI + IVIG 2 g/kg<br/>em 5 dias OU plasmaférese por 5 dias,<br/>em paralelo ao corticoide e à neurologia"]
  P5["Sem critério grave: neurologia + avaliação seriada<br/>bulbar, capacidade vital e força inspiratória negativa"]
  D3{"Em 24–48 h há melhora clínica/hemodinâmica,<br/>de disfunção ventricular, BAV/TV<br/>e queda de troponina?"}
  C1(["Sim: transição/taper especializado<br/>+ vigilância cardíaca, bulbar e respiratória"])
  P6["Não: miocardite refratária;<br/>escalar imunossupressão em centro experiente"]
  C2(["MDT cardio-onco-neuro;<br/>não reexpor automaticamente ao ICI"])

  R0 --> P1
  P1 --> D1
  D1 -->|"Sim"| P2
  D1 -->|"Não"| P3
  P2 --> P3
  P3 --> D2
  D2 -->|"Sim"| P4
  D2 -->|"Não"| P5
  P4 --> D3
  P5 --> D3
  D3 -->|"Sim"| C1
  D3 -->|"Não"| P6
  C1 --> C2
  P6 --> C2

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2 conduta;
```

## Regra prática

No overlap por ICI, **o próximo órgão a falhar pode ser o coração ou a musculatura respiratória**; ambos precisam ser monitorados desde a chegada. O tratamento da miastenia grave não deve aguardar a definição de refratariedade da miocardite. Evitar, quando possível, fármacos que podem piorar a transmissão neuromuscular, como betabloqueadores, magnésio IV, fluoroquinolonas, aminoglicosídeos e macrolídeos; qualquer necessidade crítica deve ser discutida com neurologia e a equipe de emergência.

O detalhamento de dose por gravidade cardíaca e de segunda linha está no [fluxograma de miocardite por ICI](fluxograma-miocardite-por-inibidor-de-checkpoint-imune-emergencia-esc-2025.md), evitando que este fluxo de overlap replique uma sequência divergente.
