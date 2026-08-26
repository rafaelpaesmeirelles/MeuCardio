---
title: "Fluxograma: pericardite e derrame pericárdico associados a ICI"
slug: fluxograma-pericardite-e-derrame-pericardico-associados-a-ici
theme: "Cardio-oncologia"
kind: fluxograma
summary: "Árvore para doença pericárdica por ICI, separando tamponamento, miocardite concomitante e pericardite não complicada."
review_status: revisado
source_refs: ["Lyon AR, López-Fernández T, Couch LS, et al. 2022 ESC Guidelines on cardio-oncology. Eur Heart J. 2022;43(41):4229-4361. DOI: 10.1093/eurheartj/ehac244. PMID: 36017568."]
review_note: "Revisado em 26/08/2026 contra as seções 6.10.1-6.10.2 da diretriz ESC 2022 de cardio-oncologia (PMID 36017568). O ramo de tamponamento, que terminava após pericardiocentese, passou a retornar à investigação etiológica, exclusão de miocardite concomitante e tratamento da pericardite grave; a drenagem deve gerar material para citologia/microbiologia conforme o contexto. Preservada a distinção entre pericardite grave por ICI com derrame moderado/grave — suspender ICI e metilprednisolona 1 mg/kg/dia com ou sem colchicina — e pericardite não complicada, na qual AINE/colchicina e manutenção selecionada do ICI podem ser considerados. Incluída escalada imunossupressora para doença refratária sem inventar agente preferencial. Pendente revisão médica independente antes de uso assistencial."
---

# Pericardite/derrame por ICI

```mermaid
flowchart TD
  R0["Paciente em ICI + dor pericárdica,<br/>dispneia ou novo derrame"]
  P1["ECG + troponina + TTE; CMR/CT conforme dúvida<br/>+ excluir progressão maligna, infecção<br/>e outras causas do derrame"]
  D1{"Tamponamento/instabilidade?"}
  C1(["Pericardiocentese eco-guiada imediata;<br/>colher citologia/microbiologia conforme contexto<br/>e suspender ICI durante a emergência"])
  D1A{"Após estabilização/investigação,<br/>toxicidade pericárdica por ICI é provável?"}
  C5(["Não: tratar etiologia maligna, infecciosa<br/>ou alternativa no fluxo específico"])
  D2{"Troponina elevada, disfunção VE,<br/>BAV/TV ou CMR sugere miocardite?"}
  C2(["Sim: migrar para protocolo<br/>de miocardite por ICI"])
  D3{"Pericardite grave com<br/>derrame moderado/importante?"}
  P2["Suspender ICI + metilprednisolona<br/>1 mg/kg/dia ± colchicina"]
  P3["Não complicada: AINE/colchicina<br/>se apropriado; ICI pode ser mantido<br/>em caso selecionado"]
  D4{"Resposta clínica e redução<br/>do derrame/inflamação?"}
  P4["Refratária: discutir imunossupressão adicional<br/>em cardio-oncologia/oncologia"]
  D5{"ICI foi suspenso e precisa ser retomado<br/>após resolução da doença pericárdica?"}
  C3(["Discussão MDT + rechallenge<br/>sob monitorização estreita"])
  C4(["Manter seguimento pericárdico<br/>e investigar etiologia alternativa"])

  R0 --> P1
  P1 --> D1
  D1 -->|"Sim"| C1
  D1 -->|"Não"| D1A
  C1 --> D1A
  D1A -->|"Sim"| D2
  D1A -->|"Não"| C5
  D2 -->|"Sim"| C2
  D2 -->|"Não"| D3
  D3 -->|"Sim"| P2
  D3 -->|"Não"| P3
  P2 --> D4
  P3 --> D4
  D4 -->|"Não"| P4
  D4 -->|"Sim"| D5
  P4 --> D4
  D5 -->|"Sim"| C3
  D5 -->|"Não"| C4

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

## Regra prática

No paciente em ICI, **troponina e ecocardiograma decidem se você está diante de pericardite isolada ou de uma emergência miopericárdica**.

Se houver suspeita miocárdica, usar o [fluxograma de miocardite por ICI](fluxograma-miocardite-por-inibidor-de-checkpoint-imune-emergencia-esc-2025.md), que contém a estratificação cardíaca e a sequência de imunossupressão.
