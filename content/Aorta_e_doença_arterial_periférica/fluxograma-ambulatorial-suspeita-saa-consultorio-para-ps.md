---
title: "Fluxograma ambulatorial: suspeita de SAA — consultório para PS imediato"
slug: fluxograma-ambulatorial-suspeita-saa-consultorio-para-ps
theme: "Aorta e doença arterial periférica"
kind: fluxograma
fonte_producao: grok
summary: "Árvore curta de destino no consultório diante de dor torácica/dorsal/abdominal súbita ou síncope com traços de SAA: PS agora vs outros pacotes ambulatoriais (CLTI/AAA, carótida) vs investigação eletiva quando a suspeita de SAA for descartada clinicamente."
review_status: pendente_revisao
review_note: "Irmão do protocolo sinalizadores-ambulatoriais-suspeita-sindrome-aortica-aguda-ps-imediato (07/09/2026). ESC 2024 PMID 39210722; ADD-RS PMID 21555704; ADvISED PMID 29030346. Além de #833 e #868."
source_refs:
  - "Mazzolai L, Teixido-Tura G, Lanzi S, et al. 2024 ESC Guidelines for the management of peripheral arterial and aortic diseases. Eur Heart J. 2024;45(36):3538-3700. DOI: 10.1093/eurheartj/ehae179. PMID: 39210722"
  - "Rogers AM, Hermann LK, Booher AM, et al. Sensitivity of the aortic dissection detection risk score, a novel guideline-based tool for identification of acute aortic dissection at initial presentation: results from the international registry of acute aortic dissection. Circulation. 2011;123(20):2213-2218. DOI: 10.1161/CIRCULATIONAHA.110.988568. PMID: 21555704"
  - "Nazerian P, Mueller C, Soeiro AM, et al. Diagnostic Accuracy of the Aortic Dissection Detection Risk Score Plus D-Dimer for Acute Aortic Syndromes: The ADvISED Prospective Multicenter Study. Circulation. 2018;137(3):250-258. DOI: 10.1161/CIRCULATIONAHA.117.029457. PMID: 29030346"
---

# Fluxograma ambulatorial: suspeita de SAA — consultório → PS

Prosa: [`sinalizadores-ambulatoriais-suspeita-sindrome-aortica-aguda-ps-imediato`](sinalizadores-ambulatoriais-suspeita-sindrome-aortica-aguda-ps-imediato.md). Checklist: [`checklist-ambulatorial-suspeita-de-sindrome-aortica-aguda-antes-do-ps`](checklist-ambulatorial-suspeita-de-sindrome-aortica-aguda-antes-do-ps.md). Hub hospitalar: [`sindrome-aortica-aguda-dissecacao-diagnostico-e-manejo`](sindrome-aortica-aguda-dissecacao-diagnostico-e-manejo.md).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta ambulatorial:<br/>dor tórax/dorso/abdome,<br/>síncope ou déficit de perfusão"] --> D1{"Há traços de SAA?<br/>dor súbita máxima ± predisposição<br/>± exame de alto risco (ADD-RS)"}

  D1 -->|"Sim / dúvida com SAA no diferencial"| C1(["PS IMEDIATO<br/>Comunicar suspeita de SAA<br/>Não aguardar D-dímero/TC eletiva"])

  D1 -->|"Não"| D2{"Déficit neurológico focal<br/>sem dor aórtica?"}

  D2 -->|"Sim"| C2(["Pacote carótida/AIT (#868)<br/>ou via AVC — não esta árvore"])

  D2 -->|"Não"| D3{"CLTI, ameaça de membro<br/>ou AAA com sinais de ameaça?"}

  D3 -->|"Sim"| C3(["Pacote CLTI/AAA (#833)"])

  D3 -->|"Não"| D4{"Dor anginosa típica<br/>sem traços de SAA?"}

  D4 -->|"Sim"| C4(["Fluxo SCA / coronária:<br/>PS se instável ou SCA suspeita"])
  D4 -->|"Não"| C5(["Ambulatorial dirigido<br/>ao diagnóstico alternativo;<br/>reabrir SAA se surgirem alarmes"])

  C1 --> N1["No PS: algoritmo ESC 2024<br/>ADD-RS ± D-dímero + angio-TC<br/>ECG-gated (hub/fluxograma SAA)"]

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1,C2 alerta;
  class C3,C4,C5,N1 conduta;
```

## Resumo de destinos

| Achado | Destino |
|---|---|
| Suspeita de SAA (dor súbita ± predisposição ± exame) | **PS imediato** |
| Déficit focal isolado | #868 / via AVC |
| CLTI ou AAA com ameaça | #833 |
| Angina típica sem SAA | Fluxo SCA |
| Sem alarmes aórticos | Ambulatorial etiológico |

## Notas

- **D1** = gate de segurança aórtica: na dúvida, PS.
- ADD-RS + D-dímero (ADvISED) pertence ao **PS**, não ao consultório.
- Não lista doses; não decide tipo A/B nem TEVAR.
- `review_status: pendente_revisao`.
