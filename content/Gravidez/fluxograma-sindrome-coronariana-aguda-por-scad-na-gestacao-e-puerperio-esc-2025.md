---
title: "Fluxograma: SCA por SCAD na gestação e no puerpério (ESC 2025)"
slug: fluxograma-sindrome-coronariana-aguda-por-scad-na-gestacao-e-puerperio-esc-2025
theme: "Gravidez"
kind: fluxograma
summary: "Árvore de decisão para dor torácica/SCA na gestante ou puérpera com suspeita de dissecção espontânea de coronária, distinguindo SCAD estável de cenários que exigem revascularização urgente."
review_status: revisado
source_refs: ["De Backer J, Haugaa KH, et al. 2025 ESC Guidelines for the management of cardiovascular disease and pregnancy. Eur Heart J. 2025;46(43):4462-4568. DOI: 10.1093/eurheartj/ehaf193. Seções 12.1 e 12.2.1.3.", "Hayes SN, Kim ESH, Saw J, et al. Spontaneous Coronary Artery Dissection: Current State of the Science. Circulation. 2018;137(19):e523-e557. DOI: 10.1161/CIR.0000000000000564. PMID: 29472380. PMCID: PMC5957087."]
---

# SCA por SCAD na gestação e no puerpério

```mermaid
flowchart TD
  R0["Gestante ou puérpera com dor torácica,<br/>dispneia, arritmia, choque ou suspeita de SCA"]
  P1["ECG + troponina + avaliação clínica;<br/>ecocardiograma conforme apresentação.<br/>Não atribuir sintomas automaticamente à gestação"]
  D1{"Há evidência de SCA/isquemia aguda?"}
  C1(["Não: investigar outros diagnósticos graves<br/>(TEP, síndrome aórtica, PPCM, pré-eclâmpsia etc.)"])
  P2["SCA confirmada/suspeita: acionar cardiologia intervencionista<br/>e Pregnancy Heart Team quando disponível;<br/>angiografia coronária conforme indicação clínica"]
  D2{"Angiografia compatível com SCAD?"}
  C2(["Não: manejar SCA conforme etiologia identificada<br/>e recomendações específicas da gestação"])
  D3{"SCAD com instabilidade hemodinâmica,<br/>isquemia ativa/persistente ou anatomia de alto risco?"}
  C3(["Não: preferir estratégia conservadora,<br/>monitorização hospitalar e reavaliação clínica/ECG;<br/>evitar PCI automática em lesão estável"])
  P3["Sim: discussão imediata de revascularização<br/>em centro experiente; individualizar PCI vs CABG<br/>conforme anatomia e condição materna"]
  D4{"Tronco de coronária esquerda ou<br/>vasos proximais complexos?"}
  C4(["Sim: CABG pode ser considerada conforme<br/>viabilidade técnica e experiência local"])
  C5(["Não: PCI pode ser necessária para controlar<br/>isquemia/instabilidade, reconhecendo maior risco<br/>de extensão da dissecção/hematoma"])
  P4["Após reconhecer SCAD: rever terapias iniciadas<br/>como SCA aterotrombótica; na ausência de outra indicação,<br/>considerar interromper anticoagulação sistêmica;<br/>não usar fibrinólise para SCAD confirmada"]
  C6(["Estabilização: seguimento por equipe multidisciplinar<br/>e planejamento obstétrico/puerperal individualizado"])

  R0 --> P1
  P1 --> D1
  D1 -->|"Não"| C1
  D1 -->|"Sim"| P2
  P2 --> D2
  D2 -->|"Não"| C2
  D2 -->|"Sim"| D3
  D3 -->|"Não"| C3
  D3 -->|"Sim"| P3
  P3 --> D4
  D4 -->|"Sim"| C4
  D4 -->|"Não"| C5
  C3 --> P4
  C4 --> P4
  C5 --> P4
  P4 --> C6

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## Regra prática

A diferença essencial é: **SCAD estável sem isquemia persistente favorece tratamento conservador**. Instabilidade, isquemia contínua ou anatomia de alto risco mudam o balanço para revascularização urgente individualizada.
