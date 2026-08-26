---
title: "Fluxograma: JET pós-operatória pediátrica"
slug: fluxograma-taquicardia-juncional-ectopica-pos-operatoria-jet
theme: "Cardiologia pediátrica"
kind: fluxograma
summary: "Árvore de decisão para taquicardia juncional ectópica após cirurgia congênita, com correção de gatilhos, controle de frequência e restauração de sincronia AV."
review_status: revisado
source_refs:
  - "Sasikumar N, Kumar RK, Balaji S. Diagnosis and management of junctional ectopic tachycardia in children. Ann Pediatr Cardiol. 2021;14(3):372-381. DOI: 10.4103/apc.apc_35_21. PMID: 34667411. PMCID: PMC8457265."
  - "Arvind B, Kothari SS, Juneja R, et al. Ivabradine Versus Amiodarone in the Management of Postoperative Junctional Ectopic Tachycardia. JACC Clin Electrophysiol. 2021;7(8):1052-1060. DOI: 10.1016/j.jacep.2021.01.020. PMID: 33812837."
review_note: "Fluxo revisado em 26/08/2026 contra revisão pediátrica e ensaio randomizado aberto. Ivabradina foi incluída como alternativa possível, sem dose ou temperatura-alvo universal não sustentada; demais parâmetros operacionais permanecem vinculados ao protocolo institucional."
---

# JET pós-operatória pediátrica

```mermaid
flowchart TD
  R0["Pós-operatório de cirurgia congênita<br/>+ taquicardia persistente"]
  P1["ECG/eletrograma atrial se disponível;<br/>procurar dissociação AV"]
  D1{"JET provável/confirmada?"}
  C1(["Não: migrar para algoritmo<br/>da taquiarritmia identificada"])
  P2["Corrigir febre, K/Mg, acidose, hipóxia;<br/>sedação/analgesia + reduzir catecolaminas<br/>quando possível"]
  D2{"Baixo débito/hipotensão<br/>ou deterioração?"}
  C2(["Não: monitorização e<br/>correção de gatilhos"])
  P3["Sim: controle de frequência;<br/>considerar amiodarona/procainamida;<br/>ivabradina é alternativa possível em centro experiente"]
  P4["Considerar resfriamento controlado<br/>e pacing para restaurar sincronia AV"]
  D3{"Choque persiste apesar<br/>da estratégia multipontual?"}
  C3(["Não: manter pacing/monitorização<br/>até recuperação do ritmo"])
  C4(["Sim: eletrofisiologia + cirurgia;<br/>considerar ECMO/ECLS em refratariedade"])

  R0 --> P1
  P1 --> D1
  D1 -->|"Não"| C1
  D1 -->|"Sim"| P2
  P2 --> D2
  D2 -->|"Não"| C2
  D2 -->|"Sim"| P3
  P3 --> P4
  P4 --> D3
  D3 -->|"Não"| C3
  D3 -->|"Sim"| C4

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4 conduta;
```

## Regra prática

JET pós-operatória é frequentemente uma arritmia de **baixo débito por perda de sincronia AV**. Corrigir a fisiologia e reduzir a frequência pode ser mais importante, inicialmente, do que perseguir conversão elétrica repetida.

## Tudo com Tudo

- [Protocolo de JET pós-operatória pediátrica](taquicardia-juncional-ectopica-pos-operatoria-jet.md)
- [Taquiarritmia pediátrica com pulso — AHA/AAP 2025](taquiarritmia-pediatrica-com-pulso-aha-aap-2025.md)
- [Síndrome de baixo débito após cirurgia cardíaca congênita](sindrome-de-baixo-debito-pos-cirurgia-cardiaca-congenita.md)
