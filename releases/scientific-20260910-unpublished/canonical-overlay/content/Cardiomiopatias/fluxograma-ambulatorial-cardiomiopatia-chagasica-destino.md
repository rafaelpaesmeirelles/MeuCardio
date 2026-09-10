---
slug: fluxograma-ambulatorial-cardiomiopatia-chagasica-destino
title: 'Fluxograma ambulatorial: cardiomiopatia chagásica — destino PS vs. retorno'
kind: fluxograma
theme: Cardiomiopatias
summary: 'Árvore de consultório em CCC: alarme (IC/arritmia/BAV/AVC) → PS; sem alarme → ECG/exame; piora leve →
  retorno precoce; estável → plano + Rassi/vigilância — alinhada à SBC 2023 e DCEI 2023.'
tags: []
source_refs:
- 'Diretriz da SBC sobre Diagnóstico e Tratamento de Pacientes com Cardiomiopatia da Doença de Chagas – 2023. Arq
  Bras Cardiol. 2023;120(6). DOI: 10.36660/abc.20230269'
- 'Teixeira RA, Fagundes AA, Baggio Junior JM, et al. Diretriz Brasileira de Dispositivos Cardíacos Eletrônicos
  Implantáveis – 2023. Arq Bras Cardiol. 2023;120(1):e20220892. DOI: 10.36660/abc.20220892'
- 'Rassi A Jr, Rassi A, Little WC, et al. Development and validation of a risk score for predicting death in Chagas''
  heart disease. N Engl J Med. 2006;355(8):799-808. DOI: 10.1056/NEJMoa053241. PMID: 16928995'
evidence_level: null
source_tier: A
review_status: revisado
gaps: []
published: false
---

# Fluxograma ambulatorial: cardiomiopatia chagásica — destino

Prosa: [`sinalizadores-ambulatoriais-cardiomiopatia-chagasica-quando-escalar`](/biblioteca/sinalizadores-ambulatoriais-cardiomiopatia-chagasica-quando-escalar). Forma indeterminada: [`chagas-ambulatorial-forma-indeterminada-quando-escalar-avaliacao`](/biblioteca/chagas-ambulatorial-forma-indeterminada-quando-escalar-avaliacao). CDI/Rassi: [`cardiopatia-chagasica-cronica-escore-de-rassi-e-indicacao-de-cdi`](/biblioteca/cardiopatia-chagasica-cronica-escore-de-rassi-e-indicacao-de-cdi).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta: CCC conhecida<br/>ou Chagas + ECG/eco alterados"] --> D1{"Alarme urgente?<br/>IC aguda / hipoperfusão<br/>síncope recente suspeita / TV sustentada ou instável<br/>BAV avançado ou BAVT recém-detectado<br/>Déficit focal / suspeita de AVC"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["Encaminhar AGORA<br/>PS / urgência<br/>ECG + monitorização"])

  D1 -->|"Não"| P1["ECG + exame dirigido<br/>história de congestão / palpitações<br/>revisar adesão e gatilhos"]
  P1 --> D2{"Piora clínica leve<br/>ou achado novo ambulatorial?<br/>NYHA sobe · edema · TVNS<br/>FA nova · BRD+BDAS novo"}

  D2 -->|"Sim"| C2(["Retorno em prazo individualizado<br/>Holter / eco se mudou o quadro<br/>Orientação escrita de alarmes"])
  D2 -->|"Não"| D3{"TV documentada<br/>ou condução avançada<br/>a discutir dispositivo?"}

  D3 -->|"Sim"| C3(["Referir EF / dispositivos<br/>DCEI 2023 — não FEVE isolada<br/>Ver doc Rassi/CDI"])
  D3 -->|"Não"| C4(["Plano ambulatorial<br/>Reavaliar Rassi quando dados novos<br/>Alarmes escritos"])

  C2 --> D4{"Acesso e suporte garantidos?"}
  D4 -->|"Não / fragilidade"| C5(["Providenciar avaliação em serviço acessível<br/>no prazo exigido pela gravidade<br/>PS se houver alarme ou avaliação urgente indisponível"])
  D4 -->|"Sim"| C6(["Manter retorno curto<br/>Sem doses / indicação CDI aqui"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1,C5 alerta;
  class C2,C3,C4,C6 conduta;
```

## Notas

- **D1** = triagem de segurança (IC, arritmia, condução, embolia).
- **D2** = braço ambulatorial de piora — Holter/eco e retorno curto, não “eletivo distante”.
- **D3** = ponte para DCEI 2023 (TV documentada), sem reabrir a Tabela 23 neste fluxograma.
- **D4** = segurança do plano (acesso/fragilidade).
- Forma indeterminada sem CCC estabelecida: documento-irmão dedicado.
