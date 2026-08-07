---
title: "Fluxograma: HAP descompensada na gestação e no puerpério"
slug: fluxograma-hipertensao-pulmonar-descompensada-na-gestacao-e-puerperio
theme: "Gravidez"
kind: fluxograma
summary: "Árvore de emergência para gestante/puérpera com HAP, síncope, hipoxemia ou falência direita, priorizando correção de gatilhos que elevam RVP, preservação da pressão sistêmica e escalada precoce para suporte avançado."
review_status: revisado
source_refs: ["De Backer J, Haugaa KH, Hasselberg NE, et al.; ESC Scientific Document Group. 2025 ESC Guidelines for the management of cardiovascular disease and pregnancy. Eur Heart J. 2025;46(43):4462-4568. DOI: 10.1093/eurheartj/ehaf193. PMID: 40878294.", "Humbert M, Kovacs G, Hoeper MM, et al.; ESC/ERS Scientific Document Group. 2022 ESC/ERS Guidelines for the diagnosis and treatment of pulmonary hypertension. Eur Heart J. 2022;43(38):3618-3731. DOI: 10.1093/eurheartj/ehac237. PMID: 36017548."]
---

# HAP descompensada na gestação/puerpério

```mermaid
flowchart TD
  R0["Gestante/puérpera com HAP conhecida ou suspeita<br/>+ síncope, hipoxemia, hipotensão, baixo débito<br/>ou sinais de falência aguda de VD"]
  P1["Acionar equipe de HP + Pregnancy Heart Team;<br/>monitorização + eco à beira do leito;<br/>procurar TEP, infecção, hemorragia/anemia,<br/>arritmia e interrupção de terapia"]
  D1{"Há hipóxia, hipercapnia, acidose,<br/>dor/agitação ou gatilho reversível?"}
  P2["Corrigir gatilho rapidamente;<br/>otimizar oxigenação/ventilação e analgesia;<br/>evitar aumento adicional da RVP"]
  D2{"Hipotensão/baixo débito ou falência de VD?"}
  C1(["Não: manter tratamento especializado,<br/>monitorização intensiva e reavaliar eco/perfusão"])
  P3["Sim: preservar pressão sistêmica/perfusão coronária<br/>do VD + otimizar pré-carga com cautela;<br/>vasopressor/inotrópico individualizado"]
  P4["Considerar vasodilatação pulmonar de ação rápida<br/>e restabelecer terapia de HAP interrompida<br/>conforme centro especializado"]
  D3{"Necessidade de intubação?"}
  C2(["Não: evitar hipóxia/hipercapnia e<br/>seguir suporte hemodinâmico especializado"])
  P5["Sim: intubação de alto risco com equipe experiente;<br/>otimizar pressão/oxigenação antes da indução;<br/>preparar suporte vasoativo/resgate"]
  D4{"Choque/falência direita persiste apesar<br/>de terapia otimizada?"}
  C3(["Não: manter vigilância intensiva,<br/>especialmente no puerpério"])
  P6["Sim: discutir ECMO/MCS precocemente<br/>antes de falência multiorgânica irreversível"]
  D5{"Parada cardíaca?"}
  C4(["Sim: protocolo de PCR gestante/adulto<br/>+ considerar ECPR em centro capacitado"])
  C5(["Não: suporte avançado como ponte para<br/>recuperação, parto/intervenção ou terapia definitiva"])

  R0 --> P1
  P1 --> D1
  D1 -->|"Sim"| P2
  D1 -->|"Não/sem gatilho evidente"| D2
  P2 --> D2
  D2 -->|"Não"| C1
  D2 -->|"Sim"| P3
  P3 --> P4
  P4 --> D3
  D3 -->|"Não"| C2
  D3 -->|"Sim"| P5
  C2 --> D4
  P5 --> D4
  D4 -->|"Não"| C3
  D4 -->|"Sim"| P6
  P6 --> D5
  D5 -->|"Sim"| C4
  D5 -->|"Não"| C5

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

## Regra prática

Na HAP descompensada, o objetivo não é apenas “subir a pressão”: é **reduzir a carga do VD sem perder perfusão sistêmica**. Volume excessivo, intubação não preparada e interrupção abrupta de terapia pulmonar podem precipitar colapso.
