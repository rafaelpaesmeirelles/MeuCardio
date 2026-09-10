---
slug: fluxograma-ambulatorial-carotida-ps-versus-vascular-neurovascular
title: 'Fluxograma ambulatorial: carótida — PS agora vs vascular/neurovascular vs retorno'
kind: fluxograma
theme: Aorta e doença arterial periférica
summary: 'Destino no consultório diante de déficit focal, AIT ou estenose carotídea: avaliação emergencial do evento
  neurológico, encaminhamento neurovascular prioritário e seguimento eletivo. A janela de até 14 dias refere-se
  à endarterectomia quando indicada após AIT ou AVC não incapacitante.'
tags: []
source_refs:
- 'Amin HP et al. Diagnosis, Workup, Risk Reduction of Transient Ischemic Attack in the Emergency Department Setting.
  AHA Scientific Statement. 2023. DOI: 10.1161/STR.0000000000000418.'
- 'Mazzolai L, Teixido-Tura G, Lanzi S, et al. 2024 ESC Guidelines for the management of peripheral arterial and
  aortic diseases. Eur Heart J. 2024;45(36):3538-3700. DOI: 10.1093/eurheartj/ehae179. PMID: 39210722'
- 'Kleindorfer DO, Towfighi A, Chaturvedi S, et al. 2021 Guideline for the Prevention of Stroke in Patients With
  Stroke and Transient Ischemic Attack: A Guideline From the American Heart Association/American Stroke Association.
  Stroke. 2021;52(7):e364-e467. DOI: 10.1161/STR.0000000000000375. PMID: 34024117'
evidence_level: null
source_tier: A
review_status: revisado
gaps: []
published: false
---

# Fluxograma ambulatorial: carótida — PS vs vascular/neurovascular vs retorno

Prosa: [sinalizadores-ambulatoriais-ait-deficit-focal-estenose-carotidea-quando-encaminhar](/biblioteca/sinalizadores-ambulatoriais-ait-deficit-focal-estenose-carotidea-quando-encaminhar). Janela 14 dias: [estenose-carotidea-sintomatica-janela-de-14-dias-destino-ambulatorial](/biblioteca/estenose-carotidea-sintomatica-janela-de-14-dias-destino-ambulatorial). Hub: [estenose-de-carotida-diagnostico-e-indicacao-de-revascularizacao-esc-2024](/biblioteca/estenose-de-carotida-diagnostico-e-indicacao-de-revascularizacao-esc-2024).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta ambulatorial:<br/>déficit focal, AIT ou estenose carotídea"] --> D1{"Déficit neurológico focal<br/>em curso agora?"}

  D1 -->|"Sim"| C1(["PS / via AVC AGORA<br/>Não aguardar duplex eletivo"])

  D1 -->|"Não"| D2{"Houve AIT ou AVC menor<br/>nas últimas horas–dias?"}

  D2 -->|"Sim"| D3{"Estenose carotídea ipsilateral<br/>≥50% NASCET já documentada<br/>ou altamente suspeita?"}

  D3 -->|"Sim"| C2(["Via AVC/neurovascular no mesmo dia<br/>imagem cerebral e vasos + etiologia<br/>Vascular em paralelo; preservar janela ≤14 dias<br/>para endarterectomia, se indicada (ESC 2024)"])
  D3 -->|"Não / grau desconhecido"| C3(["Urgência mesma data:<br/>imagem cérebro + vasos<br/>+ decisão etiológica;<br/>não retorno eletivo longo"])

  D2 -->|"Não"| D4{"Estenose assintomática<br/>estável, sem novos sintomas?"}

  D4 -->|"Sim"| C4(["Ambulatorial eletivo:<br/>OMT + educação de alarmes<br/>Revascularização NÃO automática"])
  D4 -->|"Não / sopro isolado / dúvida"| C5(["Duplex eletivo se decisão muda;<br/>PS imediato se surgir déficit focal"])

  C2 --> D5{"Ainda dentro da janela<br/>de 14 dias do evento?"}
  D5 -->|"Sim"| C6(["Acelerar agenda vascular;<br/>comunicar data do evento índice"])
  D5 -->|"Não / janela estourada"| C7(["Ainda encaminhar vascular;<br/>benefício residual individualizado<br/>— não abandonar OMT"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1,C2,C3 alerta;
  class C4,C5,C6,C7 conduta;
```

## Resumo de destinos

| Achado | Destino |
|---|---|
| Déficit focal em curso | PS / via AVC agora |
| AIT/AVC menor recente + estenose ipsilateral ≥50% | Via AVC/neurovascular no mesmo dia; vascular em paralelo e CEA precoce se indicada |
| AIT recente sem grau conhecido | Urgência mesma data (imagem + etiologia) |
| Estenose assintomática estável | Ambulatorial + OMT + alarmes |
| Dor isquêmica no membro, lesão trófica ou sintomas de aneurisma aórtico | Avaliação vascular específica conforme ameaça ao membro ou à vida; não utilizar esta árvore carotídea |

## Notas

- **D1** = gate de segurança neurológica.
- **D3/D5** = janela ESC 2024 para revascularização sintomática quando indicada.
- Não decide CEA vs CAS vs TCAR; não lista doses.
