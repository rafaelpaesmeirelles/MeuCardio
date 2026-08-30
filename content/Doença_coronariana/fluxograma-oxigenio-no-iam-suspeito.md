---
title: "Fluxograma: oxigênio na suspeita de IAM — só se hipoxemia"
slug: fluxograma-oxigenio-no-iam-suspeito
theme: "Doença coronariana"
kind: fluxograma
summary: "Árvore da primeira decisão de O2 no IAM suspeito: medir SpO2, oferecer O2 se <90% ou hipoxemia clínica, não oferecer de rotina se ≥90% (DETO2X). Não mistura AVOID, DPOC descompensada, EAP ou pós-ROSC."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada no DETO2X (PMID 28844200) e, como contexto, no AVOID (PMID 26002889). Classe ESC 2023 de oxigênio não relida na tabela nesta revisão editorial. EAP, pós-ROSC e DPOC hipoxêmica saem da árvore de propósito. Revisão científica concluída em 30/08/2026."
source_refs:
  - "Hofmann R, et al.; DETO2X–SWEDEHEART Investigators. Oxygen Therapy in Suspected Acute Myocardial Infarction. N Engl J Med. 2017. DOI: 10.1056/NEJMoa1706222. PMID: 28844200. NCT01787110."
  - "Stub D, et al.; AVOID Investigators. Air Versus Oxygen in ST-Segment-Elevation Myocardial Infarction. Circulation. 2015;131(24):2143-2150. PMID: 26002889."
  - "Documento da casa dor-toracica-aguda-primeira-hora-no-pronto-socorro — O2 se hipoxemia, não de rotina."
  - "Documento da casa deto2x-ami-oxigenio-rotineiro-no-iam-sem-hipoxemia."
---

# Fluxograma: oxigênio na suspeita de IAM — só se hipoxemia

Oxigênio deixou de ser item automático do checklist de dor torácica. A árvore abaixo cabe na primeira hora do PS, da SAMU e da UCO. EAP, pós-ROSC e DPOC descompensada **saem** daqui — têm documentos próprios.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Suspeita de IAM ou equivalente isquêmico<br/>no primeiro contato"] --> D0{"Via aérea ameaçada, gasping,<br/>EAP franco ou pós-ROSC?"}

  D0 -->|"Sim"| C0(["Sai desta árvore.<br/>Reanimação / EAP / pós-ROSC — protocolos próprios"])

  D0 -->|"Não"| D1{"Medir SpO2 agora.<br/>SpO2 < 90% ou hipoxemia clínica<br/>(cianose, trabalho respiratório com saturação baixa)?"}

  D1 -->|"Sim"| C1(["Oferecer oxigênio suplementar<br/>e titular à saturação.<br/>Isto NÃO é o DETO2X — DETO2X excluiu hipoxêmicos"])

  D1 -->|"Não — SpO2 ≥ 90%"| D2{"Há outra indicação de O2<br/>(intoxicação por CO, anemia grave<br/>sintomática, choque com hipoperfusão)?"}

  D2 -->|"Sim"| C2(["Tratar a indicação específica.<br/>Não usar o DETO2X para omitir O2 aqui"])

  D2 -->|"Não"| C3(["NÃO oferecer oxigênio de rotina.<br/>DETO2X: morte em 1 ano 5,0% vs 5,1%<br/>HR 0,97 (0,79–1,21). Reavaliar SpO2"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C0,C1,C2,C3 conduta;
```

## O que a árvore não mostra

**AVOID não muda o ramo do hipoxêmico.** Sinal de possível dano em desfechos secundários de um ensaio menor de STEMI pré-hospitalar não autoriza deixar o paciente dessaturando.

**Alvo de saturação (94–98% versus 88–92% em risco de hipercapnia) não foi testado no DETO2X.** O ensaio comparou 6 L/min fixos versus ar. Titular faz sentido clínico; não atribuir classe ESC daqui.

**Reavaliar SpO2.** 7,7% dos alocados a ar no DETO2X ficaram hipoxêmicos depois — esses passam para o ramo C1.

## Mensagem prática

**Meça a saturação. Se ≥90% e não há outra indicação, não coloque O2 de rotina. Se <90%, coloque.**
