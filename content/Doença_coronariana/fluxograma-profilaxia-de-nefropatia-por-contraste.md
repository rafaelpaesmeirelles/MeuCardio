---
title: "Fluxograma: profilaxia de nefropatia por contraste antes da angiografia"
slug: fluxograma-profilaxia-de-nefropatia-por-contraste
theme: "Doença coronariana"
kind: fluxograma
summary: "Árvore operacional: NAC e bicarbonato saem (PRESERVE). Hidratação IV não é automática em TFGe 30–59 eletivo (AMACING). TFGe <30, diálise e emergência saem da autorização do AMACING."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em PRESERVE (PMID 29130810) e AMACING (PMID 28233565). Classe de diretriz não relida. Revisão científica concluída em 30/08/2026."
source_refs:
  - "Weisbord SD, et al. PRESERVE. N Engl J Med. 2018;378(7):603-614. PMID: 29130810."
  - "Nijssen EC, et al. AMACING. Lancet. 2017;389(10076):1312-1322. PMID: 28233565."
  - "Documento da casa preserve-amacing-profilaxia-de-nefropatia-por-contraste."
---

# Fluxograma: profilaxia de nefropatia por contraste antes da angiografia

```mermaid
flowchart TD
  R0["Angiografia com contraste iodado<br/>programada"] --> D0{"Já em diálise crônica?"}

  D0 -->|"Sim"| C0(["Profilaxia de CIN não se aplica.<br/>Coordenar sessão de diálise com o serviço"])

  D0 -->|"Não"| D1{"SCA instável, choque ou anatomia<br/>que não pode esperar hidratação?"}

  D1 -->|"Sim"| C1(["Não atrase a anatomia por profilaxia.<br/>PRESERVE/AMACING não testam este ramo"])

  D1 -->|"Não — eletivo ou adiável"| D2{"N-acetilcisteína oral ou<br/>bicarbonato 1,26% no plano?"}

  D2 -->|"Sim"| C2(["Tire os dois do checklist.<br/>PRESERVE: NAC OR 1,02; bicarbonato OR 0,93<br/>para morte/diálise/Cr persistente em 90 d"])

  D2 -->|"Já fora"| D3{"TFGe"}

  D3 -->|"< 30"| C3(["AMACING excluiu este grupo.<br/>Hidratar com SF 0,9% ainda é razoável;<br/>não usar bicarbonato/NAC"])

  D3 -->|"30–59"| C4(["Não hidratar de rotina é não inferior<br/>no AMACING (CIN 2,6% vs 2,7%)<br/>e evita complicação da infusão (5,5%)"])

  D3 -->|"> 59, baixo risco"| C5(["Sem profilaxia. Volume mínimo de contraste<br/>factível. Não medicalizar o rim normal"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C0,C1,C2,C3,C4,C5 conduta;
```

## O que a árvore não mostra

ISCHEMIA-CKD decide **se** cateterizar o estável com DRC avançada, não como proteger o rim do contraste. São perguntas em sequência: primeiro “precisa da anatomia?”; depois “como não piorar o rim”.

## Mensagem prática

**NAC e bicarbonato: não. Hidratação automática em TFGe 30–59 eletivo: não. TFGe <30: não extrapolar o AMACING.**
