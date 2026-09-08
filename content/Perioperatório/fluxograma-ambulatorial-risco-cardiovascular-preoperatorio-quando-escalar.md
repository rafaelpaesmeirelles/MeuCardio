---
title: 'Fluxograma ambulatorial: risco cardiovascular pré-operatório — quando escalar'
slug: fluxograma-ambulatorial-risco-cardiovascular-preoperatorio-quando-escalar
theme: Perioperatório
kind: fluxograma
fonte_producao: grok
summary: 'Árvore de consultório: emergência vs eletiva, gate de instabilidade (adiar), quando escalar para escore/biomarcadores/prova funcional e quando
  discutir timing pós-stent — sem duplicar RCRI detalhado.'
review_status: revisado
review_note: 'Revisão clínica e editorial focal em 08/09/2026 do PR #836, desde seu HEAD remoto. Correções e fontes verificadas registradas em docs/revisao-cientifica-pr826-859-20260908.md.
  Prazos operacionais não equivalem a recomendações normativas; preservar avaliação individual e vias de emergência.'
source_refs:
- 'Thompson A; Fleischmann KE; Smilowitz NR. 2024 AHA/ACC/ACS/ASNC/HRS/SCA/SCCT/SCMR/SVM Guideline for Perioperative Cardiovascular Management for Noncardiac
  Surgery: A Report of the American College of Cardiology/American Heart Association Joint Committee on Clinical Practice Guidelines. Circulation. 2024;150:e351.
  DOI: 10.1161/CIR.0000000000001285. PMID: 39316661.'
- 'Halvorsen S; Mehilli J; Cassese S. 2022 ESC Guidelines on cardiovascular assessment and management of patients undergoing non-cardiac surgery. Eur Heart
  J. 2022;43:3826. DOI: 10.1093/eurheartj/ehac270. PMID: 36017553.'
- 'Gualandro DM, Fornari LS, Caramelli B, et al. Diretriz de Avaliação Cardiovascular Perioperatória da Sociedade Brasileira de Cardiologia – 2024. Arq
  Bras Cardiol. 2024;121(9):e20240590. DOI: 10.36660/abc.20240590'
- 'Duceppe E; Parlow J; MacDonald P. Canadian Cardiovascular Society Guidelines on Perioperative Cardiac Risk Assessment and Management for Patients Who
  Undergo Noncardiac Surgery. Can J Cardiol. 2017;33:17. DOI: 10.1016/j.cjca.2016.09.008. PMID: 27865641.'
---

# Fluxograma ambulatorial: quando escalar o risco cardiovascular pré-operatório

Prosa: [[sinalizadores-ambulatoriais-para-adiar-cirurgia-eletiva-nao-cardiaca](/biblioteca/sinalizadores-ambulatoriais-para-adiar-cirurgia-eletiva-nao-cardiaca)](/biblioteca/sinalizadores-ambulatoriais-para-adiar-cirurgia-eletiva-nao-cardiaca). Timing stent: [[stent-coronario-recente-e-cirurgia-eletiva-janela-de-risco-ambulatorial](/biblioteca/stent-coronario-recente-e-cirurgia-eletiva-janela-de-risco-ambulatorial)](/biblioteca/stent-coronario-recente-e-cirurgia-eletiva-janela-de-risco-ambulatorial).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta ambulatorial pré-operatória<br/>cirurgia não cardíaca"] --> D0{"Urgência da cirurgia?"}

  D0 -->|"Emergência / urgência vital"| C0(["Prosseguir com proteção CV proporcional<br/>Não atrasar por escore/exame eletivo"])

  D0 -->|"Eletiva ou tempo-sensível"| D1{"Há condição cardíaca aguda/instável?<br/>SCA, IC descompensada, arritmia instável,<br/>valva grave sintomática, PA com lesão aguda"}

  D1 -->|"Sim"| C1(["Adiar eletiva se possível<br/>Estabilizar + discussão multidisciplinar<br/>Ver protocolo de sinalizadores"])

  D1 -->|"Não"| D2{"PCI recente, inclusive balão sem stent,<br/>ou interrupção de antiagregação após stent?"}

  D2 -->|"Sim / dúvida"| C2(["Aplicar janela de timing<br/>pci-stent-dapt-timing + doc ambulatorial stent<br/>Não inventar regime DAPT aqui"])

  D2 -->|"Não"| D3{"Cirurgia de risco intermediário/alto<br/>ou paciente com fatores de risco CV?"}

  D3 -->|"Baixo risco procedimento + paciente estável"| C3(["Em geral liberar sem escalação<br/>Orientar sinais de alarme"])

  D3 -->|"Sim"| RISK["Estimar risco com ferramenta validada<br/>e avaliar se exames mudariam a conduta"]
  RISK --> D4{"Capacidade funcional adequada<br/>e sem modificador de alto risco?"}

  D4 -->|"Sim / clara"| C4["Estimar risco com ferramenta validada<br/>RCRI / AUB-HAS2 / VSG-CRI conforme tipo<br/>Prosseguir se baixo; monitorizar se intermediário"]

  D4 -->|"Não / incerta / modificador"| C5["Risco elevado e exame muda conduta?<br/>Considerar exame dirigido; não painel automático<br/>Eco só com indicação própria<br/>Fragilidade, valvopatia, HP, CIED, AVC recente"]

  C4 --> D5{"Risco elevado E exame adicional<br/>pode mudar conduta?"}
  D5 -->|"Não"| C6(["Plano perioperatório + data cirúrgica"])
  D5 -->|"Sim"| C5
  C5 --> C7(["Decisão compartilhada: otimizar,<br/>mudar local/monitorização ou adiar"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  classDef neutro fill:#eef2f7,stroke:#3d5a80,color:#102a43;
  class C1,C2 alerta;
  class C0,C3,C4,C6 conduta;
  class C5,C7 neutro;
```

## Notas

- **D1** = gate de segurança (AHA/ACC 2024; SBC 2024) — precede qualquer escore.
- **D2** = modificador PCI/stent; detalhes em docs de timing existentes (sem doses neste fluxograma).
- **D4/C5** = escalação só quando muda conduta (ESC 2022; CCS 2017 para biomarcadores em risco intermediário/alto).
- Não substitui [[algoritmo-integrado-avaliacao-cardiovascular-pre-operatoria-aha-acc-2024](/biblioteca/algoritmo-integrado-avaliacao-cardiovascular-pre-operatoria-aha-acc-2024)](/biblioteca/algoritmo-integrado-avaliacao-cardiovascular-pre-operatoria-aha-acc-2024) nem [[fluxograma-avaliacao-cardiovascular-pre-operatoria-esc-2022](/biblioteca/fluxograma-avaliacao-cardiovascular-pre-operatoria-esc-2022)](/biblioteca/fluxograma-avaliacao-cardiovascular-pre-operatoria-esc-2022).
