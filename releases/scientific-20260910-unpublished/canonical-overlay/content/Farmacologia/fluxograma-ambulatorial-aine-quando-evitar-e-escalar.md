---
slug: fluxograma-ambulatorial-aine-quando-evitar-e-escalar
title: 'Fluxograma ambulatorial: AINE — quando evitar e escalar'
kind: fluxograma
theme: Farmacologia
summary: 'Árvore de consultório: paciente cardiológico usa ou pede AINE → filtro IC/SCA/HAS/DRC/sangramento → suspender
  vs alternativa vs coordenar prescritor. Sem doses.'
tags: []
source_refs:
- FDA. Information about Taking Ibuprofen and Aspirin Together. https://www.fda.gov/drugs/safe-use-aspirin/information-about-taking-ibuprofen-and-aspirin-together
- 'Coxib and traditional NSAID Trialists'' (CNT) Collaboration, Bhala N, Emberson J, Merhi A, et al. Vascular and
  upper gastrointestinal effects of non-steroidal anti-inflammatory drugs: meta-analyses of individual participant
  data from randomised trials. Lancet. 2013;382(9894):769-779. DOI: 10.1016/S0140-6736(13)60900-9. PMID: 23726390'
- 'Nissen SE, Yeomans ND, Solomon DH, et al. Cardiovascular Safety of Celecoxib, Naproxen, or Ibuprofen for Arthritis
  (PRECISION). N Engl J Med. 2016;375(26):2519-2529. DOI: 10.1056/NEJMoa1611593. PMID: 27959716'
- 'Antman EM, Bennett JS, Daugherty A, Furberg C, Roberts H, Taubert KA. Use of nonsteroidal antiinflammatory drugs:
  an update for clinicians: a scientific statement from the American Heart Association. Circulation. 2007;115(12):1634-1642.
  DOI: 10.1161/CIRCULATIONAHA.106.181424. PMID: 17325246'
- 'McDonagh TA, Metra M, Adamo M, et al. 2021 ESC Guidelines for the diagnosis and treatment of acute and chronic
  heart failure. Eur Heart J. 2021;42(36):3599-3726. DOI: 10.1093/eurheartj/ehab368'
evidence_level: null
source_tier: A
review_status: revisado
gaps: []
published: false
---

# Fluxograma ambulatorial: AINE — quando evitar e escalar

Prosa: [sinalizadores-ambulatoriais-de-aine-no-paciente-cardiologico](/biblioteca/sinalizadores-ambulatoriais-de-aine-no-paciente-cardiologico). Checklist: [checklist-ambulatorial-aine-no-retorno-cardiologico](/biblioteca/checklist-ambulatorial-aine-no-retorno-cardiologico). Magnitude CNT: [anti-inflamatorios-nao-esteroidais-aines-e-risco-cardiovascular-metanalise-cnt](/biblioteca/anti-inflamatorios-nao-esteroidais-aines-e-risco-cardiovascular-metanalise-cnt).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Retorno cardiológico<br/>IC / DAC / HAS / anticoagulado / idoso"] --> D0{"Usa ou pede AINE<br/>(OTC ou prescrito)?"}

  D0 -->|"Não"| C0(["Plano habitual<br/>Reforçar: evitar automedicação<br/>em IC/SCA"])

  D0 -->|"Sim"| D2
  D1{"Filtro duro?<br/>IC / SCA-stent recente /<br/>HAS descontrolada / DRC grave /<br/>sangramento recente / anticoagulação com alto risco GI"}

  D2{"Já há alarme clínico?<br/>edema+dispneia / dor torácica /<br/>HDA ou anemia aguda / déficit focal / encefalopatia / oligúria"}

  D2 -->|"Sim"| C1(["Suspender AINE agora<br/>+ via IC aguda ou SCA<br/>ou sangramento maior"])
  D2 -->|"Não"| D1
  D1 -->|"Sim"| C2(["Não iniciar; revisar retirada com prescritor<br/>Alternativa analgésica<br/>Coordenar prescritor se crônico"])

  D1 -->|"Não"| DA{"AAS / antiplaquetário / anticoagulante?"}
  DA -->|"Sim"| CA(["Revisar interação, horários e risco GI<br/>Preferir alternativa antes de liberar uso"])
  DA -->|"Não"| D3{"Uso contínuo<br/>por outra especialidade?"}
  D3 -->|"Sim"| C3(["Contato coordenado<br/>Menor exposição possível<br/>Gastroproteção se indicada<br/>Documentar freio CV"])
  D3 -->|"Não / esporádico"| C4(["Educar OTC<br/>Preferir não-AINE<br/>Se inevitável e sem IC:<br/>menor tempo; naproxeno<br/>relativo na CNT — não isento"])

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

## Interações e limites do filtro

Antes de qualquer uso esporádico, perguntar AAS, outros antiplaquetários e anticoagulantes. Ibuprofeno pode reduzir o efeito antiplaquetário do AAS conforme formulação e horários: preferir alternativa e, se necessário, revisar a administração com médico/farmacêutico. Separar horários não elimina risco GI, renal ou de IC. Não suspender AAS cardioprotetor nem anticoagulante por conta própria.

O filtro se destina à analgesia musculoesquelética e automedicação. Pericardite e outras indicações anti-inflamatórias específicas exigem decisão individual com o prescritor. Sangramento, isquemia, dispneia importante, déficit focal, encefalopatia ou oligúria aguda exigem avaliação imediata; a retirada do AINE não substitui essa avaliação. PA muito alta sem lesão aguda de órgão-alvo tem destino diferente de emergência hipertensiva.

O [PRECISION canônico](/biblioteca/anti-inflamatorios-nao-esteroidais-e-risco-cardiovascular-o-ensaio-precision) já cobre segurança, PA, rim e interação com AAS. Este pacote acrescenta a triagem e o destino, sem criar uma declaração nova de superioridade entre AINEs.
