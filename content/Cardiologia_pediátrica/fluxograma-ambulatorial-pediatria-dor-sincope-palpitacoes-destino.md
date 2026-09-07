---
title: "Fluxograma ambulatorial pediátrico: dor torácica / síncope / palpitações — PS vs. especialista"
slug: fluxograma-ambulatorial-pediatria-dor-sincope-palpitacoes-destino
theme: "Cardiologia pediátrica"
kind: fluxograma
fonte_producao: grok
summary: "Árvore ambulatorial de destino: gate de alto risco (esforço/decúbito/ECG/HF/instabilidade) para PS; braço estável com alarme para cardiologia pediátrica; braço baixo risco com retorno precoce — sem doses."
review_status: pendente_revisao
review_note: "Irmão do protocolo sinalizadores-ambulatoriais-pediatria-dor-sincope-palpitacoes-ps-vs-especialista (07/09/2026). ACC/AHA/HRS 2017 PMID 28280231; ESC 2018 PMID 29562304; Fogliazza PMID 39597803; Sanatani PMID 27838109."
source_refs:
  - "Shen WK, Sheldon RS, Benditt DG, et al. 2017 ACC/AHA/HRS Guideline for the Evaluation and Management of Patients With Syncope. Circulation. 2017;136(5):e60-e122. DOI: 10.1161/CIR.0000000000000499. PMID: 28280231"
  - "Brignole M, Moya A, de Lange FJ, et al. 2018 ESC Guidelines for the diagnosis and management of syncope. Eur Heart J. 2018;39(21):1883-1948. DOI: 10.1093/eurheartj/ehy037. PMID: 29562304"
  - "Fogliazza F, Cifaldi M, Antoniol G, Canducci N, Esposito S. Approaches to Pediatric Chest Pain: A Narrative Review. J Clin Med. 2024;13(22):6659. DOI: 10.3390/jcm13226659. PMID: 39597803"
  - "Sanatani S, Chau V, Fournier A, et al. Canadian Cardiovascular Society and Canadian Pediatric Cardiology Association Position Statement on the Approach to Syncope in the Pediatric Patient. Can J Cardiol. 2017;33(2):189-198. DOI: 10.1016/j.cjca.2016.09.006. PMID: 27838109"
---

# Fluxograma ambulatorial pediátrico: dor / síncope / palpitações — destino

Prosa: [`sinalizadores-ambulatoriais-pediatria-dor-sincope-palpitacoes-ps-vs-especialista`](sinalizadores-ambulatoriais-pediatria-dor-sincope-palpitacoes-ps-vs-especialista.md). Palpitações: [`palpitacoes-ambulatoriais-na-crianca-quando-ps-vs-cardiologista-pediatrico`](palpitacoes-ambulatoriais-na-crianca-quando-ps-vs-cardiologista-pediatrico.md).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta ambulatorial\ndor torácica / síncope / pré-síncope / palpitações\nna criança ou adolescente"] --> D1{"Há alarme de PS?\nesforço ou decúbito / palpitações → síncope\ninstabilidade / ECG de risco\nHF morte súbita ou canalopatia\nKawasaki/cardiopatia com sintoma novo grave"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["Encaminhar AGORA ao PS\nInterromper exercício competitivo\nNão esperar Holter/eco eletivo"])

  D1 -->|"Não"| D2{"Há alarme estável de história/exame/ECG\nsem instabilidade?"}

  D2 -->|"Sim"| P1["ECG se ainda não feito\nDocumentar alarmes\nOrientação escrita de PS"]
  P1 --> C2(["Cardiologia pediátrica prioritária\n(dias a ≤2 semanas operacional)\nPS se novo alarme"])

  D2 -->|"Não / baixo risco aparente"| D3{"Queixa isolada tipicamente benigna\n(ex. precordial catch) com exame normal?"}

  D3 -->|"Sim"| C3(["Educação + alarmes por escrito\nRetorno ≤7 dias ou conforme rede"])
  D3 -->|"Equívoco / episódio recente"| C4(["ECG se dúvida residual\nRetorno 24–72 h\nNão eco de rotina sem alarme"])

  C2 --> D4{"Acesso ao especialista garantido?"}
  D4 -->|"Não / novo evento / piora"| C5(["Antecipar ou PS\nse surgir alarme da tabela"])
  D4 -->|"Sim"| C6(["Manter plano ambulatorial\nSem doses neste fluxograma"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1,C5 alerta;
  class C2,C3,C4,C6 conduta;
```

## Notas

- **D1** = gate de segurança (ACC/AHA/HRS 2017 / ESC 2018 / Sanatani + alarmes de dor Fogliazza).
- **D2** = alarme estável → especialista, não alta sem plano.
- **D3** = baixo risco aparente ainda recebe educação de alarmes; eco não é rastreio indiscriminado.
- Não decide doses, ablação, CDI nem indicação cirúrgica.
