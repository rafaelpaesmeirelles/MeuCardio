---
title: "Fluxograma ambulatorial: seguimento pós-Kawasaki / MIS-C — PS vs. especialista"
slug: fluxograma-ambulatorial-seguimento-kawasaki-mis-c-destino
theme: "Cardiologia pediátrica"
kind: fluxograma
fonte_producao: grok
summary: "Árvore ambulatorial de destino no seguimento pós-Kawasaki/MIS-C: gate de isquemia/trombose/instabilidade para PS; braço estável com residual para cardiologia pediátrica; braço baixo residual com retorno precoce — sem doses."
review_status: pendente_revisao
review_note: "Irmão do protocolo sinalizadores-ambulatoriais-seguimento-pos-kawasaki-e-mis-c-ps-vs-especialista (07/09/2026). AHA 2017 PMID 28356445; JCS 2020 PMID 32641591; Brogan PMID 31843876; Alvarado-Gamarra PMID 41721085."
source_refs:
  - "McCrindle BW, Rowley AH, Newburger JW, et al. Diagnosis, Treatment, and Long-Term Management of Kawasaki Disease: A Scientific Statement for Health Professionals From the American Heart Association. Circulation. 2017;135(17):e927-e999. DOI: 10.1161/CIR.0000000000000484. PMID: 28356445"
  - "Fukazawa R, Kobayashi J, Ayusawa M, et al. JCS/JSCS 2020 Guideline on Diagnosis and Management of Cardiovascular Sequelae in Kawasaki Disease. Circ J. 2020;84(8):1348-1407. DOI: 10.1253/circj.CJ-19-1094. PMID: 32641591"
  - "Brogan P, Burns JC, Cornish J, et al. Lifetime cardiovascular management of patients with previous Kawasaki disease. Heart. 2020;106(6):411-420. DOI: 10.1136/heartjnl-2019-315925. PMID: 31843876"
  - "Alvarado-Gamarra G, Alcala-Marcos K, Celis CR, et al. Post-MIS-C cardiovascular outcomes: a systematic review. Eur J Pediatr. 2026;185(3). DOI: 10.1007/s00431-026-06798-6. PMID: 41721085"
---

# Fluxograma ambulatorial: seguimento pós-Kawasaki / MIS-C — destino

Prosa: [`sinalizadores-ambulatoriais-seguimento-pos-kawasaki-e-mis-c-ps-vs-especialista`](sinalizadores-ambulatoriais-seguimento-pos-kawasaki-e-mis-c-ps-vs-especialista.md). Braço dor/síncope com CAL: [`dor-toracica-ou-sincope-no-seguimento-pos-cal-kawasaki-destino-ambulatorial`](dor-toracica-ou-sincope-no-seguimento-pos-cal-kawasaki-destino-ambulatorial.md).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta ambulatorial\ncriança/adolescente em seguimento\npós-Kawasaki ou pós-MIS-C\ncom sintoma novo ou dúvida"] --> D1{"Há alarme de PS?\ndor/sintoma atípico de isquemia\nsíncope/colapso de esforço\ninstabilidade / ECG de risco\nCAL/CAA médio-gigante + sintoma grave"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["Encaminhar AGORA ao PS\nNão esperar eco/Holter eletivo\nInterromper exercício competitivo"])

  D1 -->|"Não"| D2{"Há residual relevante\n(CAL/CAA, estenose, disfunção)\nou atraso de seguimento\ncom sintoma equívoco estável?"}

  D2 -->|"Sim"| P1["Documentar residual e sintoma\nOrientar alarmes por escrito"]
  P1 --> C2(["Cardiologia pediátrica prioritária\n(dias a ≤1–2 semanas)\nPS se novo alarme"])

  D2 -->|"Não / residual baixo"| D3{"Queixa tipicamente benigna\nexame normal\nsem CAL residual?"}

  D3 -->|"Sim"| C3(["Educação + alarmes escritos\nRetorno ≤7 dias ou conforme rede"])
  D3 -->|"Equívoco / episódio recente"| C4(["Retorno 24–72 h\nContatar equipe de seguimento\nse já houver vínculo"])

  C2 --> D4{"Acesso ao especialista garantido?"}
  D4 -->|"Não / novo evento / piora"| C5(["Antecipar ou PS\nse surgir alarme da tabela"])
  D4 -->|"Sim"| C6(["Manter plano ambulatorial\nSem doses neste fluxograma"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1,C5 alerta;
  class C2,C3,C4,C6 conduta;
```

## Notas

- **D1** = gate de segurança (Brogan PMID 31843876 + AHA 2017 / JCS 2020).
- **D2** = residual coronariano/miocárdico ou atraso de calendário → especialista, não alta sem plano.
- **D3** = baixo residual ainda recebe educação de alarmes; não confunde com pacote geral #863.
- Não decide doses, anticoagulação, trombólise nem indicação de cateterismo.
