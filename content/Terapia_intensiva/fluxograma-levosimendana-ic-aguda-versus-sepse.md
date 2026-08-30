---
title: "Fluxograma: levosimendana — LIDO/SURVIVE/REVIVE vs LeoPARDS"
slug: fluxograma-levosimendana-ic-aguda-versus-sepse
theme: "Terapia intensiva"
kind: fluxograma
summary: "IC aguda: LIDO ganha hemodinâmica (morte 180 d é secundário, n=203); SURVIVE morte 180 d NS; REVIVE sintoma 5 d com mais hipotensão/arritmia e morte 90 d numérica. Sepse: LeoPARDS SOFA NS, menos desmame, mais SVT. Não cruzar as populações."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em SURVIVE PMID 17473298, REVIVE PMID 24621834, LeoPARDS PMID 27705084 e no dump combinado LIDO PMID 12133653 (não relido de novo nesta revisão editorial). Revisão científica concluída em 30/08/2026."
source_refs:
  - "Documentos da casa survive-levosimendana-versus-dobutamina-na-ic-aguda, revive-levosimendana-versus-placebo-na-ic-aguda, leopards-levosimendana-na-sepse e levosimendana-na-ic-aguda-lido-survive-e-revive."
---

# Fluxograma: levosimendana

```mermaid
flowchart TD
  R0["Quer levosimendana IV?"] --> D1{"Qual o cenário?"}

  D1 -->|"Sepse<br/>(LeoPARDS)"| C1(["Não. SOFA 6,68 vs 6,06 P=0,053<br/>Menos desmame HR 0,77. Mais SVT"])

  D1 -->|"IC aguda, desfecho morte 180 d<br/>(SURVIVE vs dobutamina)"| C2(["Não para mortalidade. 26% vs 28% P=0,40"])

  D1 -->|"IC aguda, sintoma 5 d<br/>(REVIVE vs placebo)"| C3(["Sintoma ganhou P=0,015<br/>Hipotensão, arritmia, morte 90 d 49 vs 40 P=0,29"])

  D1 -->|"IC baixo débito, hemodinâmica 24 h<br/>(LIDO, n=203)"| C4(["Primário hemodinâmico ganhou<br/>Morte 180 d é secundário neste n"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4 conduta;
```

## Mensagem prática

**Sepse: não. Morte na IC: SURVIVE empatou. Sintoma: REVIVE paga arritmia.** LIDO não é ensaio de mortalidade.
