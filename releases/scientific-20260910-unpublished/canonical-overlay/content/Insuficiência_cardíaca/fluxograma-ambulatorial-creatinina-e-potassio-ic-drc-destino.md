---
slug: fluxograma-ambulatorial-creatinina-e-potassio-ic-drc-destino
title: 'Fluxograma ambulatorial: creatinina e potássio na IC com DRC — destino'
kind: fluxograma
theme: Insuficiência cardíaca
summary: 'IC com DRC: K >=6,5 mmol/L ou sinais de instabilidade exigem avaliação hospitalar imediata, com confirmação
  em paralelo. K 6,0–6,4 e deterioração renal seguem avaliação urgente contextual.'
tags: []
source_refs:
- UK Kidney Association. Hyperkalaemia guideline, atualização julho 2026; recomendações 1.2.2 e 1.2.3. https://www.ukkidney.org/health-professionals/guidelines/treatment-acute-hyperkalaemia-adults-0
- KDIGO. Acute Kidney Injury guideline 2012; estadiamento por creatinina e diurese.
- 'McDonagh TA, Metra M, Adamo M, et al. ESC HF 2021. PMID: 34447992'
- 'McDonagh TA, Metra M, Adamo M, et al. ESC HF Focused Update 2023. PMID: 37622666'
- 'KDIGO 2024 CKD Guideline. PMID: 38490803'
- 'Butler J, Anker SD, Lund LH, et al. DIAMOND. PMID: 35900838'
evidence_level: null
source_tier: A
review_status: revisado
gaps: []
published: false
---

# Fluxograma ambulatorial: creatinina e potássio na IC com DRC

```mermaid
flowchart TD
  R0["IC + DRC com creatinina/TFGe ou K alterados"] --> D0{"K >=6,5 mmol/L reportado?"}
  D0 -->|"Sim"| C0(["PS / emergência AGORA<br/>mesmo sem sintomas ou ECG alterado"])

  D0 -->|"Não"| D1{"AKI grave ou deterioração rápida?<br/>ex. creatinina >=3x basal, oligúria/anúria,<br/>hipoperfusão, edema pulmonar"}
  D1 -->|"Sim"| C1(["Avaliação urgente no mesmo dia<br/>Complicações, instabilidade ou via insegura: PS imediato"])

  D1 -->|"Não"| D2{"Outro alarme?<br/>fraqueza grave, bradicardia/síncope,<br/>ECG hiperK, confusão/instabilidade"}
  D2 -->|"Sim"| C0

  D2 -->|"Não"| D3{"Laboratório confirmado?"}
  D3 -->|"Não"| C2(["Repetir lab sem atrasar urgência se houver piora"])

  D3 -->|"Sim"| DK{"K entre 6,0 e 6,4 mmol/L?"}
  DK -->|"Sim"| CK(["Contato clínico rápido e repetição em até 1 dia<br/>Doença aguda/LRA ou via insegura: hospital"])
  DK -->|"Não"| D4{"Declínio persistente de TFGe,<br/>DRC avançada/complexa ou K recorrente<br/>limitando terapia?"}
  D4 -->|"Sim"| C3(["Discutir/encaminhar nefrologia<br/>Plano cardio-renal"])
  D4 -->|"Não"| C4(["Revisar volume, PA, AINE/contraste,<br/>intercorrências e tendência<br/>Rechecagem proporcional ao risco"])

  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C0,C1 alerta;
  class C2,C3,C4,CK conduta;
```

## Notas
- K 6,0–6,4 mmol/L: contato clínico rápido e repetição em até 1 dia; doença aguda/LRA ou falta de via segura exige avaliação hospitalar.
- Resultado grave com possível hemólise: confirmação em paralelo, sem atrasar avaliação urgente. Um ECG normal não exclui risco por hiperpotassemia.
- **K >=6,5 mmol/L** não depende de sintoma/ECG para destino emergencial.
- AKI pode ser grave mesmo sem oligúria.
- Creatinina subindo geralmente acompanha **TFGe caindo**, não subindo.
- Não fornece doses nem manda interromper GDMT automaticamente.

## Conteúdo relacionado
- [Hiperpotassemia grave: segurança](/biblioteca/hipercalemia-na-uco-gravidade-ecg-e-gates-de-seguranca).
- [LRA: critérios KDIGO](/biblioteca/lesao-renal-aguda-na-uco-criterios-kdigo-creatinina-e-diurese).
