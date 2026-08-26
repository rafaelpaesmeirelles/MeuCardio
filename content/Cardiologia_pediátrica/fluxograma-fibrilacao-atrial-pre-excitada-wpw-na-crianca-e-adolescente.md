---
title: "Fluxograma: FA pré-excitada/WPW na criança e adolescente"
slug: fluxograma-fibrilacao-atrial-pre-excitada-wpw-na-crianca-e-adolescente
theme: "Cardiologia pediátrica"
kind: fluxograma
summary: "Árvore de emergência para taquicardia irregular pré-excitada, evitando adenosina e demais bloqueadores nodais."
review_status: revisado
source_refs:
  - "Brugada J, Katritsis DG, Arbelo E, et al. 2019 ESC Guidelines for the management of patients with supraventricular tachycardia, developed with the Association for European Paediatric and Congenital Cardiology. Eur Heart J. 2020;41(5):655-720. DOI: 10.1093/eurheartj/ehz467. PMID: 31504425."
  - "Lasa JJ, Dhillon GS, Duff JP, et al. Part 8: Pediatric Advanced Life Support: 2025 AHA/AAP Guidelines for CPR and ECC. Circulation. 2025;152(16_suppl_2):S479-S537. DOI: 10.1161/CIR.0000000000001368. PMID: 41122885."
review_note: "Fluxo revisado em 26/08/2026 contra ESC 2019 e PALS AHA/AAP 2025. Incluídas energia de cardioversão, contraindicação de amiodarona IV e seleção farmacológica sem dose pediátrica não sustentada; demais parâmetros operacionais permanecem vinculados ao protocolo institucional."
---

# FA pré-excitada/WPW pediátrica

```mermaid
flowchart TD
  R0["Criança/adolescente com taquicardia<br/>irregular, muito rápida e QRS largo/variável"]
  P1["Suspeitar FA pré-excitada/WPW;<br/>monitorização + acesso + ECG"]
  D1{"Instabilidade?<br/>choque, isquemia, edema pulmonar,<br/>alteração importante de consciência"}
  C1(["Sim: cardioversão sincronizada<br/>0,5–1 J/kg; se falhar, 2 J/kg"])
  D2{"Ritmo irregular com<br/>pré-excitação provável?"}
  P2["NÃO usar adenosina, digoxina,<br/>verapamil/diltiazem, beta-bloqueador<br/>isolado ou amiodarona IV"]
  P3["Estável: considerar procainamida ou ibutilida IV<br/>com especialista e biblioteca pediátrica;<br/>cardioversão se falha"]
  D3{"Degenerou para FV/sem pulso?"}
  C2(["PCR pediátrica + desfibrilação"])
  C3(["Após conversão: eletrofisiologia<br/>e avaliação de ablação da via acessória"])

  R0 --> P1
  P1 --> D1
  D1 -->|"Sim"| C1
  D1 -->|"Não"| D2
  D2 -->|"Sim"| P2
  D2 -->|"Não"| P3
  P2 --> P3
  P3 --> D3
  D3 -->|"Sim"| C2
  D3 -->|"Não"| C3
  C1 --> C3

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3 conduta;
```

## Regra prática

Adenosina é excelente em algumas TSVs pediátricas, mas **pode ser perigosa na FA pré-excitada**. A irregularidade do ritmo é a pista que muda o algoritmo. O fluxo não fornece dose farmacológica: usar referência institucional pediátrica por peso, monitorização contínua e suporte de eletrofisiologia.

## Tudo com Tudo

- [Protocolo de FA pré-excitada/WPW pediátrica](fibrilacao-atrial-pre-excitada-wpw-na-crianca-e-adolescente.md)
- [Taquiarritmia pediátrica com pulso — AHA/AAP 2025](taquiarritmia-pediatrica-com-pulso-aha-aap-2025.md)
- [Ablação por cateter na criança](ablacao-por-cateter-na-crianca-limites-de-peso-e-idade-crioablacao-e-mapeamento-eletroanatomico.md)
