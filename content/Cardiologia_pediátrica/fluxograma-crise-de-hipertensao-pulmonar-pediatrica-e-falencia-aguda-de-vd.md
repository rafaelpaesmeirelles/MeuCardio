---
title: "Fluxograma: Crise de hipertensão pulmonar pediátrica e falência aguda de VD"
slug: fluxograma-crise-de-hipertensao-pulmonar-pediatrica-e-falencia-aguda-de-vd
theme: "Cardiologia pediátrica"
kind: fluxograma
summary: "Árvore de emergência para criança com hipertensão pulmonar e deterioração aguda, focando correção de gatilhos que aumentam RVP, suporte do VD, vasodilatação pulmonar especializada e ECMO precoce em refratariedade."
review_status: revisado
source_refs: ["Wyckoff MH, Greif R, Morley PT, et al. 2024 International Consensus on Cardiopulmonary Resuscitation and Emergency Cardiovascular Care Science With Treatment Recommendations. Circulation. 2024;150(24):e580-e664. DOI: 10.1161/CIR.0000000000001288.", "Bernier ML, Romer LH, Bembea MM. Spectrum of Current Management of Pediatric Pulmonary Hypertensive Crisis. Crit Care Explor. 2020;2(1):e0037. DOI: 10.1097/CCE.0000000000000037. PMID: 32166278. PMCID: PMC7063944.", "Abman SH, Hansmann G, Archer SL, et al. Pediatric Pulmonary Hypertension: Guidelines From the American Heart Association and American Thoracic Society. Circulation. 2015;132(21):2037-2099. DOI: 10.1161/CIR.0000000000000329. PMID: 26534956."]
---

# Crise de hipertensão pulmonar pediátrica

```mermaid
flowchart TD
  R0["Criança/neonato com HP conhecida ou suspeita<br/>+ hipoxemia, hipotensão, síncope, baixo débito<br/>ou falência aguda de VD"]
  P1["UTI/cardiologia pediátrica + monitorização;<br/>eco à beira do leito conforme disponibilidade;<br/>identificar gatilho e terapia de HP interrompida"]
  D1{"Há hipóxia, hipercapnia, acidose,<br/>dor/agitação, infecção, anemia, arritmia,<br/>desidratação ou sobrecarga volêmica?"}
  P2["Corrigir gatilhos rapidamente;<br/>oxigenar/ventilar e fornecer analgesia/sedação<br/>adequadas; evitar estímulos que elevem RVP"]
  D2{"Instabilidade/baixo débito ou falência de VD?"}
  C1(["Não: manter terapia específica, tratar causa<br/>e reavaliar clínica/eco em ambiente monitorizado"])
  P3["Sim: preservar pressão sistêmica/perfusão coronária<br/>do VD + suporte vasoativo/inotrópico individualizado"]
  P4["Considerar vasodilatação pulmonar de ação rápida,<br/>incluindo iNO, conforme centro/protocolo;<br/>restituir terapia específica se interrompida"]
  D3{"Precisa intubação/ventilação invasiva?"}
  C2(["Não: manter suporte e evitar hipercapnia/acidemia"])
  P5["Sim: intubação de alto risco com equipe experiente;<br/>evitar hipóxia, hipercapnia, dor/agitação e queda<br/>de pressão durante indução e ventilação"]
  D4{"Resposta à terapia médica otimizada?"}
  C3(["Sim: manter tratamento do gatilho e<br/>desmame cuidadoso de terapia inalada/IV;<br/>evitar retirada abrupta"])
  P6["Não: discutir ECMO antes da PCR em caso selecionado,<br/>como ponte para recuperação ou terapia definitiva"]
  D5{"Evoluiu para parada cardíaca?"}
  C4(["Sim: PALS + corrigir hipercapnia;<br/>restabelecer terapia pulmonar interrompida;<br/>considerar iNO/prostaciclina conforme experiência;<br/>ECPR em caso selecionado"])
  C5(["Não: transferência/manutenção em centro de HP<br/>pediátrica e escalada especializada"])

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
  D4 -->|"Sim"| C3
  D4 -->|"Não"| P6
  P6 --> D5
  D5 -->|"Sim"| C4
  D5 -->|"Não"| C5

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

## Nota de evidência

O ILCOR 2024 oferece bons princípios para deterioração e parada em crianças com hipertensão pulmonar, mas a prática farmacológica de crise ainda varia muito entre centros. Por isso, a árvore **não força doses universais de iNO, prostaciclina, milrinona ou vasopressor**.
