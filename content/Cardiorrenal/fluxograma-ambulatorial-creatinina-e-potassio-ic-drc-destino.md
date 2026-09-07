---
title: "Fluxograma ambulatorial: creatinina e potássio na IC com DRC — destino (PS vs. retorno vs. nefrologia)"
slug: fluxograma-ambulatorial-creatinina-e-potassio-ic-drc-destino
theme: "Insuficiência cardíaca"
kind: fluxograma
fonte_producao: grok
summary: "Árvore ambulatorial de destino no eixo IC+DRC: gate de alarme para PS, braço de reavaliação precoce de creatinina/K sob GDMT, e gatilho para nefrologia — sem doses."
review_status: pendente_revisao
review_note: "Irmão dos protocolos piora-de-creatinina-sob-gdmt e hiperpotassemia-ambulatorial-quando-escalar (07/09/2026). ESC 2021 PMID 34447992; ESC 2023 PMID 37622666; KDIGO 2024 PMID 38490803; DIAMOND PMID 35900838. Anti-colisão #829/#692/#842."
source_refs:
  - "McDonagh TA, Metra M, Adamo M, et al. 2021 ESC Guidelines for the diagnosis and treatment of acute and chronic heart failure. Eur Heart J. 2021;42(36):3599-3726. DOI: 10.1093/eurheartj/ehab368. PMID: 34447992"
  - "McDonagh TA, Metra M, Adamo M, et al. 2023 Focused Update of the 2021 ESC Guidelines for the diagnosis and treatment of acute and chronic heart failure. Eur Heart J. 2023;44(37):3627-3639. DOI: 10.1093/eurheartj/ehad195. PMID: 37622666"
  - "Kidney Disease: Improving Global Outcomes (KDIGO) CKD Work Group. KDIGO 2024 Clinical Practice Guideline for the Evaluation and Management of Chronic Kidney Disease. Kidney Int. 2024;105(4S):S117-S314. DOI: 10.1016/j.kint.2023.10.018. PMID: 38490803"
  - "Butler J, Anker SD, Lund LH, et al. Patiromer for the management of hyperkalemia in heart failure with reduced ejection fraction: the DIAMOND trial. Eur Heart J. 2022;43(41):4362-4373. DOI: 10.1093/eurheartj/ehac401. PMID: 35900838"
---

# Fluxograma ambulatorial: creatinina e potássio na IC com DRC — destino

Prosa creatinina: [`piora-de-creatinina-sob-gdmt-ambulatorial-quando-encaminhar-nefrologia`](piora-de-creatinina-sob-gdmt-ambulatorial-quando-encaminhar-nefrologia.md). Prosa K: [`hiperpotassemia-ambulatorial-na-ic-com-drc-quando-escalar`](hiperpotassemia-ambulatorial-na-ic-com-drc-quando-escalar.md). Conceito segurança K (#829): não duplicar aqui.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta ambulatorial IC+DRC<br/>com creatinina e/ou K alterados"] --> D1{"Há alarme de PS?<br/>oligúria / hipoperfusão / confusão<br/>fraqueza grave / bradicardia-síncope<br/>edema pulmonar / K ameaçador com sintomas"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["Encaminhar AGORA ao PS / emergência<br/>Manejo agudo institucional<br/>Não titular GDMT neste fluxograma"])

  D1 -->|"Não"| D2{"Lab confirmado?<br/>repetir se dúvida/hemólise"}

  D2 -->|"Não confirmado"| C2(["Repetir lab + clínica<br/>Orientar alarmes por escrito"])

  D2 -->|"Confirmado"| D3{"Piora progressiva de TFGe<br/>ou K recorrente limitando terapia<br/>ou DRC complexa/avançada?"}

  D3 -->|"Sim"| C3(["Discutir / encaminhar nefrologia<br/>Plano conjunto cardio-renal<br/>KDIGO 2024 / rede local"])

  D3 -->|"Não / estável com contexto"| P1["Revisar volume, AINE, contraste,<br/>adesão, PA, congestão vs depleção"]
  P1 --> C4(["Retorno clínico/lab em dias<br/>Não abandonar GDMT por ponto isolado<br/>Reforçar sinais de alarme"])

  C4 --> D4{"Acesso e suporte garantidos?"}
  D4 -->|"Não / fragilidade / piora rápida"| C5(["Antecipar retorno 24–72 h ou PS<br/>se surgir alarme da tabela"])
  D4 -->|"Sim"| C6(["Manter plano de rechecagem<br/>Registrar tendência TFGe/K"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1,C5 alerta;
  class C2,C3,C4,C6 conduta;
```

## Notas

- **D1** = gate de segurança (destino, não dose).
- **D2** = confirmação laboratorial antes de decisões permanentes.
- **D3** = gatilho de nefrologia / complexidade (KDIGO CGA + recorrência de K).
- Não decide doses de GDMT, quelantes, diurético IV nem ultrafiltração.
