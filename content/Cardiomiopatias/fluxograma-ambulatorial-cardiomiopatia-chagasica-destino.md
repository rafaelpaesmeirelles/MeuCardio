---
title: "Fluxograma ambulatorial: cardiomiopatia chagásica — destino PS vs. retorno"
slug: fluxograma-ambulatorial-cardiomiopatia-chagasica-destino
theme: "Cardiomiopatias"
kind: fluxograma
fonte_producao: grok
summary: "Árvore de consultório em CCC: alarme (IC/arritmia/BAV/AVC) → PS; sem alarme → ECG/exame; piora leve → retorno precoce; estável → plano + Rassi/vigilância — alinhada à SBC 2023 e DCEI 2023."
review_status: pendente_revisao
review_note: "Irmão do pacote sinalizadores Chagas ambulatory (07/09/2026). SBC Chagas 2023 DOI 10.36660/abc.20230269; DCEI 2023 DOI 10.36660/abc.20220892; Rassi PMID 16928995. Sem doses."
source_refs:
  - "Diretriz da SBC sobre Diagnóstico e Tratamento de Pacientes com Cardiomiopatia da Doença de Chagas – 2023. Arq Bras Cardiol. 2023;120(6). DOI: 10.36660/abc.20230269"
  - "Teixeira RA, Fagundes AA, Baggio Junior JM, et al. Diretriz Brasileira de Dispositivos Cardíacos Eletrônicos Implantáveis – 2023. Arq Bras Cardiol. 2023;120(1):e20220892. DOI: 10.36660/abc.20220892"
  - "Rassi A Jr, Rassi A, Little WC, et al. Development and validation of a risk score for predicting death in Chagas' heart disease. N Engl J Med. 2006;355(8):799-808. DOI: 10.1056/NEJMoa053241. PMID: 16928995"
---

# Fluxograma ambulatorial: cardiomiopatia chagásica — destino

Prosa: [`sinalizadores-ambulatoriais-cardiomiopatia-chagasica-quando-escalar`](sinalizadores-ambulatoriais-cardiomiopatia-chagasica-quando-escalar.md). Forma indeterminada: [`chagas-ambulatorial-forma-indeterminada-quando-escalar-avaliacao`](chagas-ambulatorial-forma-indeterminada-quando-escalar-avaliacao.md). CDI/Rassi: [`cardiopatia-chagasica-cronica-escore-de-rassi-e-indicacao-de-cdi`](../Dispositivos/cardiopatia-chagasica-cronica-escore-de-rassi-e-indicacao-de-cdi.md).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta: CCC conhecida\nou Chagas + ECG/eco alterados"] --> D1{"Alarme urgente?\nIC aguda / hipoperfusão\nsíncope ou TV / choque CDI\nBAV avançado sintomático\nDéficit focal / suspeita de AVC"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["Encaminhar AGORA\nPS / urgência\nECG + monitorização"])

  D1 -->|"Não"| P1["ECG + exame dirigido\nhistória de congestão / palpitações\nrevisar adesão e gatilhos"]
  P1 --> D2{"Piora clínica leve\nou achado novo ambulatorial?\nNYHA sobe · edema · TVNS\nFA nova · BRD+BDAS novo"}

  D2 -->|"Sim"| C2(["Retorno 24–72 h\nHolter / eco se mudou o quadro\nOrientação escrita de alarmes"])
  D2 -->|"Não"| D3{"TV documentada\nou condução avançada\na discutir dispositivo?"}

  D3 -->|"Sim"| C3(["Referir EF / dispositivos\nDCEI 2023 — não FEVE isolada\nVer doc Rassi/CDI"])
  D3 -->|"Não"| C4(["Plano ambulatorial\nReavaliar Rassi quando dados novos\nAlarmes escritos"])

  C2 --> D4{"Acesso e suporte garantidos?"}
  D4 -->|"Não / fragilidade"| C5(["Antecipar retorno 24 h\nou PS se surgir alarme"])
  D4 -->|"Sim"| C6(["Manter retorno curto\nSem doses / indicação CDI aqui"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1,C5 alerta;
  class C2,C3,C4,C6 conduta;
```

## Notas

- **D1** = gate de segurança (IC, arritmia, condução, embolia).
- **D2** = braço ambulatorial de piora — Holter/eco e retorno curto, não “eletivo distante”.
- **D3** = ponte para DCEI 2023 (TV documentada), sem reabrir a Tabela 23 neste fluxograma.
- **D4** = segurança do plano (acesso/fragilidade).
- Forma indeterminada sem CCC estabelecida: documento-irmão dedicado.
