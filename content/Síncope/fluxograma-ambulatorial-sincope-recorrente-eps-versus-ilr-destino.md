---
title: "Fluxograma ambulatorial: síncope recorrente — destino EPS vs. ILR vs. PS"
slug: fluxograma-ambulatorial-sincope-recorrente-eps-versus-ilr-destino
theme: "Síncope"
kind: fluxograma
fonte_producao: grok
summary: "Árvore ambulatorial pós-avaliação inicial: alarme → PS; substrato selecionado → eletrofisiologia/EPS; sem alto risco com recorrência provável → ILR/monitorização; candidato a avaliação de CDI → encaminhar risco de MSC."
review_status: pendente_revisao
review_note: "Irmão de sinalizadores-ambulatoriais-sincope-recorrente-inexplicada-quando-referir-eletrofisiologia (07/09/2026). Além de #859. ESC 2018 PMID 29562304; ACC/AHA/HRS 2017 PMID 28280231. Anti-colisão com fluxograma-sincope-inexplicada-recorrente-monitor-de-eventos-implantavel. Sem doses."
source_refs:
  - "Brignole M, Moya A, de Lange FJ, et al.; ESC Scientific Document Group. 2018 ESC Guidelines for the diagnosis and management of syncope. Eur Heart J. 2018;39(21):1883-1948. DOI: 10.1093/eurheartj/ehy037. PMID: 29562304"
  - "Brignole M, Moya A, de Lange FJ, et al. Practical Instructions for the 2018 ESC Guidelines for the diagnosis and management of syncope. Eur Heart J. 2018;39(21):e43-e80. DOI: 10.1093/eurheartj/ehy071"
  - "Shen WK, Sheldon RS, Benditt DG, et al. 2017 ACC/AHA/HRS Guideline for the Evaluation and Management of Patients With Syncope. Circulation. 2017;136(5):e60-e122. DOI: 10.1161/CIR.0000000000000499. PMID: 28280231"
---

# Fluxograma ambulatorial: síncope recorrente — EPS vs. ILR vs. PS

Prosa: [`sinalizadores-ambulatoriais-sincope-recorrente-inexplicada-quando-referir-eletrofisiologia`](sinalizadores-ambulatoriais-sincope-recorrente-inexplicada-quando-referir-eletrofisiologia.md). Gate CDI: [`candidatos-ambulatoriais-avaliacao-cdi-apos-sincope-quando-encaminhar`](candidatos-ambulatoriais-avaliacao-cdi-apos-sincope-quando-encaminhar.md). Monitorização detalhada: [`fluxograma-sincope-inexplicada-recorrente-monitor-de-eventos-implantavel`](fluxograma-sincope-inexplicada-recorrente-monitor-de-eventos-implantavel.md). Pós-alta (#859): [`fluxograma-ambulatorial-sincope-pos-avaliacao-destino`](fluxograma-ambulatorial-sincope-pos-avaliacao-destino.md).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta ambulatorial<br/>síncope recorrente sem diagnóstico definido<br/>após avaliação inicial"] --> D1{"Novo alarme de alto risco?<br/>esforço / decúbito / sem pródromo + trauma<br/>ECG alarmante / hipoperfusão<br/>dispositivo + síncope sem interrogação"}

  D1 -->|"Sim"| C1(["Encaminhar AGORA<br/>PS / urgência / unidade de síncope"])

  D1 -->|"Não"| D2{"Há indicação convencional<br/>de avaliar CDI / risco de MSC?<br/>(FE reduzida + cardiomiopatia,<br/>VA documentada, canalopatia/HCM<br/>de alto risco conhecido)"}

  D2 -->|"Sim"| C2(["Encaminhar avaliação de CDI / EP<br/>EPS não é pré-requisito automático<br/>se já há indicação de prevenção primária"])

  D2 -->|"Não"| D3{"Substrato selecionado para EPS?<br/>bifascicular + síncope inexplicada<br/>IAM/cicatriz/estrutura + origem incerta<br/>palpitações antes / bradicardia<br/>sem correlação não invasiva"}

  D3 -->|"Sim"| C3(["Referir eletrofisiologia<br/>EPS selecionado<br/>Não protocolar ablação/MP/doses aqui"])

  D3 -->|"Não"| D4{"ECG normal, sem estrutura,<br/>sem palpitações,<br/>recorrência ainda provável?"}

  D4 -->|"Sim — baixo risco estrutural"| C4(["Preferir monitorização / ILR<br/>conforme frequência dos sintomas<br/>Ver fluxograma ILR da pasta"])
  D4 -->|"Incerto / nem claro"| C5(["Unidade de síncope / retorno curto<br/>Reavaliar hipótese; não forçar EPS"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1 alerta;
  class C2,C3,C4,C5 conduta;
```

## Notas

- **D1** = gate de segurança (reabre alto risco ESC 2018 / pacote #859).
- **D2** = candidato a **avaliação** de CDI/MSC — ver documento-gate irmão; não decide implante.
- **D3** = EPS só com **pré-teste elevada** (ESC 2018; ACC/AHA/HRS 2017).
- **D4** = na ausência de substrato, o fluxograma de ILR desta pasta manda na escolha Holter vs. loop externo vs. ILR.
- Este fluxograma **não** duplica o protocolo de tilt nem restrições legais de direção.
