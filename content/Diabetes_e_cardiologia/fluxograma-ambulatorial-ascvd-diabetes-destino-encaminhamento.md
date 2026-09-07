---
title: "Fluxograma ambulatorial: ASCVD no diabetes — PS vs retorno vs Heart Team"
slug: fluxograma-ambulatorial-ascvd-diabetes-destino-encaminhamento
theme: "Diabetes e cardiologia"
kind: fluxograma
fonte_producao: grok
summary: "Árvore ambulatorial de destino no diabético com ASCVD: gate de SCA/instabilização → PS; gatilhos de revascularização (angina persistente, isquemia >10% VE, multiarterial) → Heart Team em prazo curto; limítrofe → retorno precoce — além de #826/#855, sem doses."
review_status: pendente_revisao
review_note: "Irmão dos protocolos ASCVD-encaminhar e angina-CCS-persistente (07/09/2026). PIVOT: tempo/destino de encaminhamento ASCVD+diabetes. Evita #826/#855. Fontes: ESC 2023 PMID 37622656; ESC 2024 CCS PMID 39210710; ESC/EACTS 2018 PMID 30165437; FREEDOM PMID 23121323. Sem doses."
source_refs:
  - "Marx N, Federici M, Schütt K, et al. 2023 ESC Guidelines for the management of cardiovascular disease in patients with diabetes. Eur Heart J. 2023;44(39):4043-4140. DOI: 10.1093/eurheartj/ehad192. PMID: 37622656"
  - "Vrints C, Andreotti F, Koskinas KC, et al. 2024 ESC Guidelines for the management of chronic coronary syndromes. Eur Heart J. 2024;45(36):3415-3537. DOI: 10.1093/eurheartj/ehae177. PMID: 39210710"
  - "Neumann FJ, Sousa-Uva M, Ahlsson A, et al; ESC Scientific Document Group. 2018 ESC/EACTS Guidelines on myocardial revascularization. Eur Heart J. 2019;40(2):87-165. DOI: 10.1093/eurheartj/ehy394. PMID: 30165437"
  - "Farkouh ME, Domanski M, Sleeper LA, et al; FREEDOM Trial Investigators. Strategies for multivessel revascularization in patients with diabetes. N Engl J Med. 2012;367(25):2375-2384. DOI: 10.1056/NEJMoa1211585. PMID: 23121323"
---

# Fluxograma ambulatorial: ASCVD no diabetes — destino de encaminhamento

Prosa: [`sinalizadores-ambulatoriais-ascvd-no-diabetes-quando-encaminhar`](sinalizadores-ambulatoriais-ascvd-no-diabetes-quando-encaminhar.md) · [`angina-ccs-persistente-no-diabetes-quando-discutir-revascularizacao`](angina-ccs-persistente-no-diabetes-quando-discutir-revascularizacao.md).

Não substitui #826 (lesão de órgão-alvo / IC-FA), #855 (hipoglicemia / iSGLT2-GLP1), FREEDOM detalhado nem vias hospitalares de SCA.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta / teleatendimento<br/>diabético com ASCVD conhecida<br/>ou altamente suspeita"] --> D1{"Alarme de SCA / instabilização?<br/>repouso · crescendo · nitrato sem alívio<br/>ECG isquêmico novo · equivalentes graves"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["PS / urgência AGORA<br/>Não teste ergometrico ambulatorial<br/>Não esperar retorno longo"])

  D1 -->|"Não"| D2{"Gatilho de revascularização?<br/>angina CCS persistente<br/>isquemia documentada >10% VE<br/>multiarterial / alto SYNTAX + diabetes"}

  D2 -->|"Sim"| P1["Confirmar estabilidade<br/>Listar alarmes por escrito"]
  P1 --> C2(["Heart Team / discussão de<br/>revascularização em prazo CURTO<br/>dias–poucas semanas conforme rede<br/>Sem escolher CABG vs PCI isolado"])

  D2 -->|"Não"| D3{"Sintoma limítrofe ou dúvida<br/>de adesão / precipitanes?"}

  D3 -->|"Sim"| C3(["Retorno precoce<br/>Orientação escrita de alarmes<br/>Sem inventar doses neste fluxo"])
  D3 -->|"Não"| C4(["Plano escrito + retorno programado<br/>Manter prevenção secundária já prescrita"])

  C2 --> D4{"Acesso a Heart Team / avaliação<br/>de isquemia-anatomia OK?"}
  D4 -->|"Não / piora / novo alarme"| C5(["Antecipar PS<br/>se surgir linha da tabela de SCA"])
  D4 -->|"Sim"| C6(["Completar articulação<br/>Não diluir em retorno de 6 meses"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1,C5 alerta;
  class C2,C3,C4,C6 conduta;
```

## Notas

- **D1** = gate de segurança SCA (ESC 2024 CCS / ESC 2023 diabetes).
- **D2** = gatilho de revascularização ambulatorial (angina persistente, isquemia >10% VE, multiarterial — ESC 2023 + FREEDOM/Heart Team).
- **D3–D4** = limítrofe vs estável; prazos curtos são operacionais de rede.
- **Não decide** doses, SCORE2, rastreio IC/FA (#826), alarmes iSGLT2 (#855) nem a escolha final CABG vs PCI.
