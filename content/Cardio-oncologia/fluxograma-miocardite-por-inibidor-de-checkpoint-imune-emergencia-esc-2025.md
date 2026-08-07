---
title: "Fluxograma: miocardite por inibidor de checkpoint imune — emergência (ESC 2025)"
slug: fluxograma-miocardite-por-inibidor-de-checkpoint-imune-emergencia-esc-2025
theme: "Cardio-oncologia"
kind: fluxograma
summary: "Árvore de decisão para suspeita de miocardite por ICI com estratificação de gravidade, suspensão da imunoterapia, corticoterapia e escalada em 24–48 horas se refratária."
review_status: revisado
source_refs: ["Schulz-Menger J, Collini V, et al. 2025 ESC Guidelines for the management of myocarditis and pericarditis. Eur Heart J. 2025. DOI: 10.1093/eurheartj/ehaf192.", "Lyon AR, López-Fernández T, Couch LS, et al. 2022 ESC Guidelines on cardio-oncology. Eur Heart J. 2022;43:4229-4361. DOI: 10.1093/eurheartj/ehac244. PMID: 36017568."]
---

# Miocardite por inibidor de checkpoint imune

```mermaid
flowchart TD
  R0["Paciente em uso recente/atual de ICI<br/>com troponina elevada, alteração nova no ECG,<br/>dispneia, síncope, arritmia ou insuficiência cardíaca"]
  P1["Suspender ICI; ECG + telemetria;<br/>troponina seriada; ecocardiograma;<br/>investigar SCA/TEP/sepse e outras causas"]
  D1{"Há apresentação grave?<br/>choque/baixo débito, edema pulmonar,<br/>TV/FV, BAV avançado ou instabilidade"}
  C1(["UTI/unidade monitorizada;<br/>tratar choque/arritmia em paralelo;<br/>metilprednisolona IV 7–14 mg/kg/dia x3 dias;<br/>não atrasar por CMR/biópsia"])
  C2(["Metilprednisolona IV 500–1000 mg/dia x3 dias;<br/>monitorização clínica, ECG e troponina;<br/>CMR quando viável"])
  D2{"Resposta clínica e biomarcadora<br/>em 24–48 h?"}
  C3(["Prosseguir transição/taper de corticoide<br/>e reavaliação multidisciplinar cardio-oncologia"])
  C4(["Miocardite refratária: escalar imunossupressão<br/>em centro experiente — considerar micofenolato,<br/>ATG ou abatacepte conforme perfil clínico"])

  R0 --> P1
  P1 --> D1
  D1 -->|"Sim"| C1
  D1 -->|"Não"| C2
  C1 --> D2
  C2 --> D2
  D2 -->|"Sim"| C3
  D2 -->|"Não"| C4

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4 conduta;
```

## Segurança

FEVE preservada não exclui o diagnóstico. Em miocardite por ICI, bloqueio de condução e arritmia ventricular podem ser a manifestação predominante e justificam monitorização intensiva mesmo antes de disfunção ventricular evidente.
