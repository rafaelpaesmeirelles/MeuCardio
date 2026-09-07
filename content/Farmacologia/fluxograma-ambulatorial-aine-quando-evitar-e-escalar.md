---
title: "Fluxograma ambulatorial: AINE — quando evitar e escalar"
slug: fluxograma-ambulatorial-aine-quando-evitar-e-escalar
theme: "Farmacologia"
kind: fluxograma
fonte_producao: grok
summary: "Árvore de consultório: paciente cardiológico usa ou pede AINE → filtro IC/SCA/HAS/DRC/sangramento → suspender vs alternativa vs coordenar prescritor. Sem doses."
review_status: pendente_revisao
review_note: "Irmão do protocolo sinalizadores-ambulatoriais-de-aine-no-paciente-cardiologico (07/09/2026). CNT PMID 23726390; PRECISION PMID 27752637; AHA 2007 PMID 17325246; ESC HF 2021. Anti-colisão com ensaio CNT (Geral), #842 IC, #828 HAS, #860 DOAC."
source_refs:
  - "Coxib and traditional NSAID Trialists' (CNT) Collaboration, Bhala N, Emberson J, Merhi A, et al. Vascular and upper gastrointestinal effects of non-steroidal anti-inflammatory drugs: meta-analyses of individual participant data from randomised trials. Lancet. 2013;382(9894):769-779. DOI: 10.1016/S0140-6736(13)60900-9. PMID: 23726390"
  - "Nissen SE, Yeomans ND, Solomon DH, et al. Cardiovascular Safety of Celecoxib, Naproxen, or Ibuprofen for Arthritis (PRECISION). N Engl J Med. 2016;375(26):2519-2529. DOI: 10.1056/NEJMoa1611593. PMID: 27752637"
  - "Antman EM, Bennett JS, Daugherty A, Furberg C, Roberts H, Taubert KA. Use of nonsteroidal antiinflammatory drugs: an update for clinicians: a scientific statement from the American Heart Association. Circulation. 2007;115(12):1634-1642. DOI: 10.1161/CIRCULATIONAHA.106.181646. PMID: 17325246"
  - "McDonagh TA, Metra M, Adamo M, et al. 2021 ESC Guidelines for the diagnosis and treatment of acute and chronic heart failure. Eur Heart J. 2021;42(36):3599-3726. DOI: 10.1093/eurheartj/ehab368"
---

# Fluxograma ambulatorial: AINE — quando evitar e escalar

Prosa: [`sinalizadores-ambulatoriais-de-aine-no-paciente-cardiologico`](sinalizadores-ambulatoriais-de-aine-no-paciente-cardiologico.md). Checklist: [`checklist-ambulatorial-aine-no-retorno-cardiologico`](checklist-ambulatorial-aine-no-retorno-cardiologico.md). Magnitude CNT: [`anti-inflamatorios-nao-esteroidais-aines-e-risco-cardiovascular-metanalise-cnt`](../Geral/anti-inflamatorios-nao-esteroidais-aines-e-risco-cardiovascular-metanalise-cnt.md).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Retorno cardiológico\nIC / DAC / HAS / anticoagulado / idoso"] --> D0{"Usa ou pede AINE\n(OTC ou prescrito)?"}

  D0 -->|"Não"| C0(["Plano habitual\nReforçar: evitar automedicação\nem IC/SCA"])

  D0 -->|"Sim"| D1{"Filtro duro?\nIC / SCA-stent recente /\nHAS descontrolada / DRC grave /\nsangramento recente"}

  D1 -->|"Sim"| D2{"Já há alarme clínico?\nedema+dispneia / dor torácica /\nHDA ou anemia aguda"}

  D2 -->|"Sim"| C1(["Suspender AINE agora\n+ via IC [#842] ou SCA\nou sangramento [#860]"])
  D2 -->|"Não"| C2(["Suspender / não iniciar AINE\nAlternativa analgésica\nCoordenar prescritor se crônico"])

  D1 -->|"Não"| D3{"Uso contínuo\npor outra especialidade?"}
  D3 -->|"Sim"| C3(["Contato coordenado\nMenor exposição possível\nGastroproteção se indicada\nDocumentar freio CV"])
  D3 -->|"Não / esporádico"| C4(["Educar OTC\nPreferir não-AINE\nSe inevitável e sem IC:\nmenor tempo; naproxeno\nrelativo na CNT — não isento"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1 alerta;
  class C0,C2,C3,C4 conduta;
```

## Notas

- **D1**: ESC HF 2021 (evitar AINE na IC) + AHA 2007 (escada e freio pós-SCA) + CNT (IC de classe).
- **D2**: alarme clínico manda o destino; o AINE é precipitante, não diagnóstico diferencial completo.
- **C4**: PRECISION não autoriza liberalizar AINE em IC; só contextualiza comparação entre moléculas em artrite selecionada.
- Não decide dose, duração reumatológica nem substitui antiplaquetário/anticoagulante.
