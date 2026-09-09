---
title: "Fluxograma ambulatorial: AOS no retorno cardiológico — rastreio e destino"
slug: fluxograma-ambulatorial-aos-rastreio-destino
theme: "Prevenção e lipídios"
kind: fluxograma
fonte_producao: grok
summary: "Árvore de consultório: pista de AOS em paciente CV → triagem STOP-Bang/história → polissonografia/sono vs plano habitual; braço de AOS conhecida → adesão CPAP vs alarme. Sem doses."
review_status: pendente_revisao
review_note: "Irmão do protocolo sinalizadores-ambulatoriais-de-aos-quando-rastrear-e-encaminhar (07/09/2026). AHA OSA 2021 PMID 34148375; STOP-Bang PMID 18431116; ESC 2024 HAS PMID 39210715; SAVE PMID 27571048. Anti-colisão #865 (só destino de secundária) e STOP-Bang perioperatório."
source_refs:
  - "Yeghiazarians Y, Jneid H, Tietjens JR, et al. Obstructive Sleep Apnea and Cardiovascular Disease: A Scientific Statement From the American Heart Association. Circulation. 2021;144(3):e56-e67. DOI: 10.1161/CIR.0000000000000988. PMID: 34148375"
  - "Chung F, Yegneswaran B, Liao P, et al. STOP Questionnaire: A Tool to Screen Patients for Obstructive Sleep Apnea. Anesthesiology. 2008;108(5):812-821. DOI: 10.1097/ALN.0b013e31816d83e4. PMID: 18431116"
  - "McEvoy JW, McCarthy CP, Bruno RM, et al. 2024 ESC Guidelines for the management of elevated blood pressure and hypertension. Eur Heart J. 2024;45(38):3912-4018. DOI: 10.1093/eurheartj/ehae178. PMID: 39210715"
  - "McEvoy RD, Antic NA, Heeley E, et al. CPAP for Prevention of Cardiovascular Events in Obstructive Sleep Apnea. N Engl J Med. 2016;375(10):919-931. DOI: 10.1056/NEJMoa1606599. PMID: 27571048"
---

# Fluxograma ambulatorial: AOS — rastreio e destino

Prosa: [`sinalizadores-ambulatoriais-de-aos-quando-rastrear-e-encaminhar`](sinalizadores-ambulatoriais-de-aos-quando-rastrear-e-encaminhar.md). AOS conhecida: [`checklist-ambulatorial-aos-conhecida-adesao-cpap-e-alarmes`](checklist-ambulatorial-aos-conhecida-adesao-cpap-e-alarmes.md). Perioperatório: [`aplicacao-do-stop-bang-na-triagem-de-apneia-obstrutiva-do-sono-pre-operatoria-em-cirurgia-cardiaca`](../Cardiologia_do_Esporte_e_do_Exercício/aplicacao-do-stop-bang-na-triagem-de-apneia-obstrutiva-do-sono-pre-operatoria-em-cirurgia-cardiaca.md).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Retorno cardiológico\nHAS / FA / IC / DAC / obesidade"] --> D0{"AOS já diagnosticada?"}

  D0 -->|"Sim"| C0(["Ir ao checklist de adesão CPAP\ne alarmes — doc irmão"])

  D0 -->|"Não / desconhecido"| D1{"Há pista clínica de AOS?\nronco, sonolência, apneia observada,\ncefaleia matinal, pescoço largo\nOU HAS resistente / FA recorrente"}

  D1 -->|"Não"| C1(["Plano CV habitual\nNão rastrear AOS de rotina\nsem pista"])

  D1 -->|"Sim"| P1["Triagem estruturada\nSTOP-Bang e/ou história dirigida"]
  P1 --> D2{"Triagem de risco aumentado?\nSTOP-Bang elevado ou história forte"}

  D2 -->|"Não / baixo risco"| C2(["Reavaliar se nova pista\nManter plano CV"])

  D2 -->|"Sim"| D3{"Sonolência grave com risco\nocupacional OU IC/HAS\nmuito descompensada?"}

  D3 -->|"Sim"| C3(["Priorizar medicina do sono\n+ estabilizar CV em paralelo\nOrientar segurança / direção"])

  D3 -->|"Não"| C4(["Encaminhar polissonografia\nou poligrafia / sono\nTriagem ≠ diagnóstico\nRetorno CV curto se resistente"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C3 alerta;
  class C0,C1,C2,C4 conduta;
```

## Notas

- **D0**: bifurca diagnóstico prévio vs primeira suspeita.
- **D1**: filtro de probabilidade — alinhado a AHA 2021 e ao papel da AOS na HAS (ESC 2024).
- **D2**: STOP-Bang é **triagem** (PMID 18431116), não fecha AOS.
- **D3/C3**: prioriza segurança e descompensação; não inventa meta de eventos do SAVE.
- Não decide pressão de CPAP, tipo de máscara nem suspender GDMT.
