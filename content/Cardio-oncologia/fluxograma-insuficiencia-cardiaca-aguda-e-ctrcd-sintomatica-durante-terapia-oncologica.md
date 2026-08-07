---
title: "Fluxograma: insuficiência cardíaca aguda e CTRCD durante terapia oncológica"
slug: fluxograma-insuficiencia-cardiaca-aguda-e-ctrcd-sintomatica-durante-terapia-oncologica
theme: "Cardio-oncologia"
kind: fluxograma
summary: "Árvore de decisão para paciente com câncer e insuficiência cardíaca aguda, combinando estabilização hemodinâmica, exclusão de causas concorrentes, investigação de cardiotoxicidade e decisão sobre pausa/reexposição da terapia oncológica."
review_status: revisado
source_refs: ["Lyon AR, López-Fernández T, Couch LS, et al.; ESC Scientific Document Group. 2022 ESC Guidelines on cardio-oncology. Eur Heart J. 2022;43(41):4229-4361. DOI: 10.1093/eurheartj/ehac244. PMID: 36017568.", "Gevaert SA, Halvorsen S, Sinnaeve PR, et al. Evaluation and management of cancer patients presenting with acute cardiovascular disease: a Clinical Consensus Statement of the ACVC and ESC Council of Cardio-Oncology-part 2. Eur Heart J Acute Cardiovasc Care. 2022;11(11):865-874. DOI: 10.1093/ehjacc/zuac107. PMID: 36226746."]
---

# IC aguda/CTRCD durante terapia oncológica

```mermaid
flowchart TD
  R0["Paciente com câncer + dispneia/congestão,<br/>baixo débito ou nova disfunção ventricular"]
  D1{"Choque ou hipoperfusão?"}
  P1["Protocolo de choque/IC aguda:<br/>monitorização + suporte hemodinâmico<br/>+ eco à beira do leito"]
  P2["Congesto sem choque:<br/>decongestão e tratamento de IC aguda<br/>conforme pressão e função renal"]
  P3["ECG + troponina/BNP + hemograma/renal/eletrólitos<br/>+ ecocardiograma; buscar precipitante"]
  D2{"Há causa concorrente prioritária?<br/>SCA, TEP, sepse, FA rápida,<br/>tamponamento, anemia etc."}
  P4["Tratar causa concorrente específica<br/>em paralelo ao suporte de IC"]
  D3{"Terapia oncológica é causa provável<br/>ou contribui para a emergência?"}
  P5["Pausar temporariamente agente causal<br/>+ acionar cardio-oncologia/oncologia"]
  D4{"Sinais de miocardite por checkpoint?<br/>troponina + BAV/TV/alteração ECG etc."}
  P6["Seguir protocolo específico de<br/>miocardite por ICI"]
  P7["CTRCD: iniciar/titular terapia de IC<br/>após estabilização hemodinâmica"]
  C1(["Após recuperação: MDT decide<br/>reexposição, redução ou alternativa oncológica"])
  C2(["Se terapia não causal: manter/ajustar<br/>tratamento oncológico conforme MDT e evolução"])

  R0 --> D1
  D1 -->|"Sim"| P1
  D1 -->|"Não"| P2
  P1 --> P3
  P2 --> P3
  P3 --> D2
  D2 -->|"Sim"| P4
  D2 -->|"Não"| D3
  P4 --> D3
  D3 -->|"Sim"| P5
  D3 -->|"Não"| C2
  P5 --> D4
  D4 -->|"Sim"| P6
  D4 -->|"Não"| P7
  P6 --> C1
  P7 --> C1

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2 conduta;
```

## Regra prática

No paciente oncológico com IC aguda, **estabilização e etiologia caminham juntas**: trate a síndrome de IC imediatamente, mas não deixe a terapia antineoplásica causal continuar por inércia durante uma emergência cardiovascular.