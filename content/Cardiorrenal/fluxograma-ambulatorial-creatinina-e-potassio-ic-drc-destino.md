---
title: "Fluxograma ambulatorial: creatinina e potássio na IC com DRC — destino"
slug: fluxograma-ambulatorial-creatinina-e-potassio-ic-drc-destino
theme: "Insuficiência cardíaca"
kind: fluxograma
fonte_producao: grok
summary: "Árvore IC+DRC: K >=6,5 confirmado ou AKI grave → emergência; demais alterações confirmadas seguem reavaliação contextual ou nefrologia."
review_status: revisado
review_note: "Revisão clínica final 08/09/2026. K >=6,5 mmol/L confirmado virou gate emergencial independente de sintomas/ECG; AKI grave não oligúrica foi incluída no gate; removidas dependências a conteúdos ainda não publicados e prazos rígidos não normativos."
source_refs:
  - "UK Kidney Association. Hyperkalaemia guideline, atualização julho 2026; recomendações 1.2.2 e 1.2.3."
  - "KDIGO. Acute Kidney Injury guideline 2012; estadiamento por creatinina e diurese."
  - "McDonagh TA, Metra M, Adamo M, et al. ESC HF 2021. PMID: 34447992"
  - "McDonagh TA, Metra M, Adamo M, et al. ESC HF Focused Update 2023. PMID: 37622666"
  - "KDIGO 2024 CKD Guideline. PMID: 38490803"
  - "Butler J, Anker SD, Lund LH, et al. DIAMOND. PMID: 35900838"
---

# Fluxograma ambulatorial: creatinina e potássio na IC com DRC

```mermaid
flowchart TD
  R0["IC + DRC com creatinina/TFGe ou K alterados"] --> D0{"K confirmado >=6,5 mmol/L?"}
  D0 -->|"Sim"| C0(["PS / emergência AGORA<br/>mesmo sem sintomas ou ECG alterado"])

  D0 -->|"Não"| D1{"AKI grave ou deterioração rápida?<br/>ex. creatinina >=3x basal, oligúria/anúria,<br/>hipoperfusão, edema pulmonar"}
  D1 -->|"Sim"| C1(["Avaliação no mesmo dia / PS<br/>PS se complicações ou sem via segura"])

  D1 -->|"Não"| D2{"Outro alarme?<br/>fraqueza grave, bradicardia/síncope,<br/>ECG hiperK, confusão/instabilidade"}
  D2 -->|"Sim"| C1

  D2 -->|"Não"| D3{"Laboratório confirmado?"}
  D3 -->|"Não"| C2(["Repetir lab sem atrasar urgência se houver piora"])

  D3 -->|"Sim"| D4{"Declínio persistente de TFGe,<br/>DRC avançada/complexa ou K recorrente<br/>limitando terapia?"}
  D4 -->|"Sim"| C3(["Discutir/encaminhar nefrologia<br/>Plano cardio-renal"])
  D4 -->|"Não"| C4(["Revisar volume, PA, AINE/contraste,<br/>intercorrências e tendência<br/>Rechecagem proporcional ao risco"])

  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C0,C1 alerta;
  class C2,C3,C4 conduta;
```

## Notas
- K 6,0–6,4 mmol/L: contato clínico rápido e repetição em até 1 dia; doença aguda/LRA ou falta de via segura exige avaliação hospitalar.
- Resultado grave com possível hemólise: confirmação em paralelo, sem atrasar avaliação urgente.
- **K >=6,5 mmol/L** não depende de sintoma/ECG para destino emergencial.
- AKI pode ser grave mesmo sem oligúria.
- Creatinina subindo geralmente acompanha **TFGe caindo**, não subindo.
- Não fornece doses nem manda interromper GDMT automaticamente.

## Conteúdo relacionado
- [Hiperpotassemia grave: segurança](/biblioteca/hipercalemia-na-uco-gravidade-ecg-e-gates-de-seguranca).
- [LRA: critérios KDIGO](/biblioteca/lesao-renal-aguda-na-uco-criterios-kdigo-creatinina-e-diurese).
