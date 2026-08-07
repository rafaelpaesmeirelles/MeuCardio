---
title: "Fluxograma: tamponamento cardíaco e derrame pericárdico neoplásico"
slug: fluxograma-tamponamento-cardiaco-e-derrame-pericardico-neoplasico
theme: "Cardio-oncologia"
kind: fluxograma
summary: "Árvore de decisão para paciente com câncer e derrame pericárdico, separando tamponamento instável que exige drenagem imediata do derrame estável que requer investigação etiológica."
review_status: revisado
source_refs: ["Schulz-Menger J, Collini V, Gröschel J, et al.; ESC Scientific Document Group. 2025 ESC Guidelines for the management of myocarditis and pericarditis. Eur Heart J. 2025;46(40):3952-4041. DOI: 10.1093/eurheartj/ehaf192. PMID: 40878297.", "Gevaert SA, Halvorsen S, Sinnaeve PR, et al. Evaluation and management of cancer patients presenting with acute cardiovascular disease: a Consensus Document of the Acute CardioVascular Care association and the ESC council of Cardio-Oncology-Part 1. Eur Heart J Acute Cardiovasc Care. 2021;10(8):947-959. DOI: 10.1093/ehjacc/zuab056. PMID: 34453829."]
---

# Tamponamento/derrame pericárdico em paciente com câncer

```mermaid
flowchart TD
  R0["Paciente com câncer + derrame pericárdico<br/>ou suspeita clínica de tamponamento"]
  D1{"Há choque, hipotensão persistente,<br/>hipoperfusão ou tamponamento clínico/eco?"}
  P1["Pericardiocentese urgente<br/>+ colher material diagnóstico"]
  P2["Enviar citologia pericárdica<br/>+ investigação microbiológica/etiológica conforme contexto"]
  D2{"Suspeita ou confirmação de<br/>etiologia neoplásica?"}
  P3["Manter drenagem estendida 3–6 dias<br/>e coordenar oncologia/cardio-oncologia"]
  C1(["Tratar causa não neoplásica identificada<br/>e seguir protocolo geral de pericárdio"])
  D3{"Sem instabilidade: derrame<br/>moderado/grande e etiologia incerta?"}
  P4["Eco + imagem multimodal + revisar<br/>câncer, tratamento, infecção e causas sistêmicas"]
  D4{"Diagnóstico continua não esclarecido?"}
  P5["Considerar pericardiocentese diagnóstica<br/>e citologia"]
  C2(["Acompanhar e tratar etiologia definida<br/>conforme repercussão clínica"])
  C3(["Se malignidade confirmada:<br/>tratamento antineoplásico sistêmico + prevenção de recorrência"])

  R0 --> D1
  D1 -->|"Sim"| P1
  P1 --> P2
  P2 --> D2
  D2 -->|"Sim"| P3
  D2 -->|"Não"| C1
  P3 --> C3
  D1 -->|"Não"| D3
  D3 -->|"Sim"| P4
  D3 -->|"Não"| C2
  P4 --> D4
  D4 -->|"Sim"| P5
  D4 -->|"Não"| C2
  P5 --> D2

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3 conduta;
```

## Regra prática

No paciente oncológico, **instabilidade decide a urgência; citologia decide parte da etiologia**. Não espere confirmação de malignidade para drenar tamponamento, e não presuma malignidade em todo derrame.