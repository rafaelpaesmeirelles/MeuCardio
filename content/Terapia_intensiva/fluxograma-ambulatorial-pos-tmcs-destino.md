---
title: "Fluxograma ambulatorial: pós-tMCS — PS vs retorno precoce vs plano"
slug: fluxograma-ambulatorial-pos-tmcs-destino
theme: "Terapia intensiva"
kind: fluxograma
fonte_producao: grok
summary: "Árvore de destino após explante de suporte circulatório mecânico temporário: gate de alarme (hipoperfusão, congestão aguda, sítio vascular, neurológico), braço de piora/trajetória pós-ponte com retorno precoce + IC avançada, e braço estável com plano — sem doses."
review_status: pendente_revisao
review_note: "Irmão dos protocolos pós-tMCS 07/09/2026. PIVOT: lacuna destino ambulatorial BEYOND #861. Anti-colisão através de #894+; não reescreve SCAI/vasoativos/indicação-desmame de tMCS. Fontes: ACVC/ESC tMCS PMID 37315190; ACC 2025 CS PMID 40100174; HFA/ESC CS PMID 32469155; ESC HF 2021 PMID 34447992. Sem doses."
source_refs:
  - "Møller JE, Sionis A, Aissaoui N, et al. Step by step daily management of short-term mechanical circulatory support for cardiogenic shock in adults in the intensive cardiac care unit: a clinical consensus statement of the Association for Acute CardioVascular Care of the ESC, the European Society of Intensive Care Medicine, the European branch of the Extracorporeal Life Support Organization, and the European Association for Cardio-Thoracic Surgery. Eur Heart J Acute Cardiovasc Care. 2023;12(7):475-485. DOI: 10.1093/ehjacc/zuad064. PMID: 37315190"
  - "Sinha SS, Morrow DA, Kapur NK, Kataria R, Roswell RO. 2025 Concise Clinical Guidance: An ACC Expert Consensus Statement on the Evaluation and Management of Cardiogenic Shock. J Am Coll Cardiol. 2025;85(16):1618-1641. DOI: 10.1016/j.jacc.2025.02.018. PMID: 40100174"
  - "Chioncel O, Parissis J, Mebazaa A, et al. Epidemiology, pathophysiology and contemporary management of cardiogenic shock – a position statement from the Heart Failure Association of the European Society of Cardiology. Eur J Heart Fail. 2020;22(8):1315-1341. DOI: 10.1002/ejhf.1922. PMID: 32469155"
  - "McDonagh TA, Metra M, Adamo M, et al. 2021 ESC Guidelines for the diagnosis and treatment of acute and chronic heart failure. Eur Heart J. 2021;42(36):3599-3726. DOI: 10.1093/eurheartj/ehab368. PMID: 34447992"
---

# Fluxograma ambulatorial: pós-tMCS — destino

Prosa: [`seguimento-ambulatorial-pos-tmcs-ponte-temporaria-quando-escalar`](seguimento-ambulatorial-pos-tmcs-ponte-temporaria-quando-escalar.md). Eixos sítio + IC avançada: [`sinalizadores-ambulatoriais-pos-tmcs-sitio-vascular-ic-avancada`](sinalizadores-ambulatoriais-pos-tmcs-sitio-vascular-ic-avancada.md).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta / teleatendimento<br/>após explante de tMCS<br/>(IABP / Impella / VA-ECMO)"] --> D1{"Alarme imediato?<br/>hipoperfusão / congestão aguda<br/>sítio: sangramento / isquemia / sepse<br/>déficit neurológico"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["PS / urgência AGORA<br/>Avisar time de choque/UCO se possível<br/>Não ajustar em casa"])

  D1 -->|"Não"| D2{"Piora ou trajetória pós-ponte?<br/>IC leve-moderada / sítio duvidoso<br/>bridge-to-decision sem plano<br/>dúvida de recuperação / terapia avançada"}

  D2 -->|"Sim"| P1["História focada: sítio + IC<br/>Precipitantes + exame dirigido"]
  P1 --> C2(["Retorno precoce<br/>+ IC avançada / centro de choque<br/>Sem inventar doses neste fluxo"])

  D2 -->|"Não"| D3{"Estável?<br/>sítio cicatrizando, sem congestão<br/>plano de IC já agendado"}

  D3 -->|"Sim"| C3(["Plano escrito de alarmes<br/>(inclui sítio vascular)<br/>Retorno programado + continuidade IC"])
  D3 -->|"Não / dúvida"| C4(["Retorno curto prudente<br/>ou cardiologia / IC avançada"])

  C2 --> D4{"Acesso a reavaliação OK<br/>e sem piora em horas?"}
  D4 -->|"Não / piora"| C5(["Antecipar PS<br/>se surgir alarme da tabela"])
  D4 -->|"Sim"| C6(["Completar investigação dirigida<br/>Não esperar retorno longo de rotina"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1,C5 alerta;
  class C2,C3,C4,C6 conduta;
```

## Notas

- **D1** = gate de segurança (hipoperfusão, congestão aguda, sítio vascular crítico, neurológico).
- **D2** = piora ambulatorial ou trajetória pós-ponte sem plano de IC avançada → retorno precoce + rede (ACC 2025 níveis de cuidado; ESC HF 2021 continuidade).
- **Não decide** doses, anticoagulação sob suporte, indicação/escalonamento/desmame de tMCS nem estadiamento SCAI.
- Complementa — não substitui — o fluxograma pós-UTI geral do pacote #861.
