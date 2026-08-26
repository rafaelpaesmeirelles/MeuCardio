---
title: "Fluxograma: Crise de hipertensão pulmonar persistente do recém-nascido"
slug: fluxograma-crise-de-hipertensao-pulmonar-persistente-do-recem-nascido
theme: "Cardiologia pediátrica"
kind: fluxograma
summary: "Árvore de decisão para recém-nascido com hipoxemia grave e suspeita de HPPRN, priorizando estabilização, ecocardiograma para excluir cardiopatia estrutural canal-dependente e uso de iNO quando indicado."
review_status: revisado
source_refs:
  - "Sankaran D, Lakshminrusimha S. Pulmonary hypertension in the newborn-etiology and pathogenesis. Semin Fetal Neonatal Med. 2022;27(4):101381. DOI: 10.1016/j.siny.2022.101381. PMID: 35963740."
  - "Mitra S, Altit G. Inhaled nitric oxide use in newborns. Paediatr Child Health. 2023;28(2):119-126. DOI: 10.1093/pch/pxac107. PMID: 37151928. PMCID: PMC10156933."
  - "Clark RH, Kueser TJ, Walker MW, et al. Low-dose nitric oxide therapy for persistent pulmonary hypertension of the newborn. N Engl J Med. 2000;342(7):469-474. DOI: 10.1056/NEJM200002173420704. PMID: 10675427."
  - "Wild KT, Rintoul N, Kattan J, Gray B. Extracorporeal Life Support Organization (ELSO): Guidelines for Neonatal Respiratory Failure. ASAIO J. 2020;66(5):463-470. DOI: 10.1097/MAT.0000000000001153. PMID: 32282347."
review_note: "Fluxo revisado em 26/08/2026 contra a diretriz ELSO 2020. Incorporados os critérios de discussão de ECMO como conjunto, sem converter IO em gatilho automático isolado; parâmetros operacionais permanecem vinculados ao protocolo institucional."
---

# Crise de hipertensão pulmonar persistente do recém-nascido

```mermaid
flowchart TD
  R0["RN com hipoxemia grave/cianose<br/>e suspeita de HPPRN"]
  P1["Estabilizar temperatura, ventilação e oxigenação;<br/>corrigir acidose e tratar causa pulmonar/infecciosa<br/>quando presente"]
  D1{"Ecocardiograma disponível<br/>e cardiopatia estrutural crítica excluída?"}
  C1(["Se cardiopatia canal-dependente ou outra<br/>causa estrutural crítica for possível,<br/>não iniciar vasodilatação pulmonar às cegas;<br/>acionar cardiologia/neonatologia e tratar<br/>conforme a anatomia"])
  D2{"Eco compatível com HPPRN<br/>+ falência respiratória hipóxica apesar<br/>de ventilação/oxigenação otimizadas?"}
  C2(["Reavaliar diagnóstico e causa da hipoxemia;<br/>otimizar tratamento da doença pulmonar de base"])
  P2["Considerar/iniciar iNO em RN termo ou<br/>pré-termo tardio com HPPRN confirmada;<br/>dose inicial baseada em ensaios: 20 ppm"]
  D3{"Resposta clínica/oximétrica adequada?"}
  C3(["Responder: manter suporte e fazer retirada<br/>progressiva do iNO; evitar interrupção abrupta"])
  P3["Sem resposta: reavaliar recrutamento pulmonar,<br/>função de VD/VE, shunts, pneumotórax, sepse,<br/>hipoplasia pulmonar e outras causas"]
  D4{"Hipoxemia/choque permanecem refratários?"}
  C4(["Escalonar em centro neonatal avançado;<br/>discutir ECMO: IO >40 por >4 h, IO >20 sem melhora<br/>após >24 h, PaO₂ <40 refratária ou falência VD/<br/>alto suporte vasoativo — integrar elegibilidade"])
  C5(["Se estabilizou: monitorização intensiva<br/>e reavaliação ecocardiográfica conforme evolução"])

  R0 --> P1
  P1 --> D1
  D1 -->|"Não / dúvida estrutural"| C1
  D1 -->|"Sim"| D2
  D2 -->|"Não"| C2
  D2 -->|"Sim"| P2
  P2 --> D3
  D3 -->|"Sim"| C3
  D3 -->|"Não"| P3
  P3 --> D4
  D4 -->|"Sim"| C4
  D4 -->|"Não"| C5

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

## Pontos críticos

- O ecocardiograma confirma a fisiologia de HPPRN e ajuda a excluir cardiopatias congênitas cianogênicas/canal-dependentes antes da vasodilatação pulmonar.
- Em recém-nascidos a termo e pré-termo tardios com falência respiratória hipóxica associada à HPPRN, iNO é terapia baseada em evidência; **20 ppm** é a dose inicial usada em ensaios e recomendações contemporâneas.
- Uso rotineiro de iNO em prematuros não é recomendado; situações de resgate específicas exigem avaliação neonatal especializada.
- A ELSO inclui **IO >40 por mais de 4 horas** entre as possíveis indicações de ECMO neonatal, mas também inclui outros padrões de refratariedade. O número não é uma ordem automática de canulação nem deve ser aguardado para iniciar a discussão com o centro ECMO.

## Tudo com Tudo

- [Protocolo de HPPRN: diagnóstico e escada terapêutica](hipertensao-pulmonar-persistente-do-recem-nascido-fisiopatologia-diagnostico-e-escada-terapeutica.md)
- [Crise de hipertensão pulmonar pediátrica e falência aguda de VD](crise-de-hipertensao-pulmonar-pediatrica-e-falencia-aguda-de-vd.md)
