---
title: "Fluxograma: estenose mitral descompensada na gestação"
slug: fluxograma-estenose-mitral-descompensada-na-gestacao-e-edema-pulmonar
theme: "Gravidez"
kind: fluxograma
summary: "Árvore de decisão para gestante com estenose mitral, congestão ou edema pulmonar, integrando controle de frequência, diurese, anticoagulação quando indicada e encaminhamento para comissurotomia percutânea se refratária."
review_status: revisado
source_refs: ["De Backer J, Haugaa KH, Hasselberg NE, et al.; ESC Scientific Document Group. 2025 ESC Guidelines for the management of cardiovascular disease and pregnancy. Eur Heart J. 2025;46(43):4462-4568. DOI: 10.1093/eurheartj/ehaf193. PMID: 40878294.", "2025 ESC/EACTS Guidelines for the management of valvular heart disease. Eur Heart J. 2025;46(44):4635-4734. DOI: 10.1093/eurheartj/ehaf194 — manejo da estenose mitral durante gestação conferido nesta revisão."]
---

# Estenose mitral descompensada na gestação

```mermaid
flowchart TD
  R0["Gestante com estenose mitral + dispneia,<br/>congestão, edema pulmonar ou HP"]
  P1["Monitorização + ECG + eco;<br/>área valvar por planimetria, PSAP,<br/>IM e anatomia/subvalvar"]
  D1{"Edema pulmonar/IC aguda<br/>ou instabilidade?"}
  P2["Suporte de IC aguda + decongestão;<br/>evitar expansão volêmica liberal;<br/>Pregnancy Heart Team"]
  D2{"Taquicardia/FA contribuindo?"}
  P3["Controle de frequência com estratégia<br/>compatível com gestação + tratar precipitantes"]
  D3{"FA, trombo em AE ou embolia prévia?"}
  P4["Anticoagulação terapêutica conforme<br/>protocolo específico da gestação"]
  D4{"Persistem NYHA III/IV, sintomas relevantes<br/>ou PSAP >50 mmHg apesar de tratamento?"}
  P5["Avaliar comissurotomia mitral percutânea<br/>em centro experiente; preferencialmente após 20 semanas"]
  D5{"Anatomia inadequada, procedimento impossível<br/>ou falhou com ameaça à vida materna?"}
  P6["Discussão de cirurgia/parto conforme<br/>viabilidade fetal e risco materno"]
  C1(["Resposta clínica: manter seguimento estreito<br/>e planejar parto/puerpério com Heart Team"])
  C2(["Intervenção bem-sucedida:<br/>monitorização materno-fetal e seguimento"])

  R0 --> P1
  P1 --> D1
  D1 -->|"Sim"| P2
  D1 -->|"Não"| D2
  P2 --> D2
  D2 -->|"Sim"| P3
  D2 -->|"Não"| D3
  P3 --> D3
  D3 -->|"Sim"| P4
  D3 -->|"Não"| D4
  P4 --> D4
  D4 -->|"Não"| C1
  D4 -->|"Sim"| P5
  P5 --> D5
  D5 -->|"Não"| C2
  D5 -->|"Sim"| P6
  P6 --> C2

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2 conduta;
```

## Regra prática

Na gestante com estenose mitral, **taquicardia e volume pioram rapidamente a pressão atrial esquerda**. Se sintomas importantes ou PSAP >50 mmHg persistirem apesar do tratamento clínico, a estratégia deve migrar cedo para avaliação de comissurotomia percutânea.