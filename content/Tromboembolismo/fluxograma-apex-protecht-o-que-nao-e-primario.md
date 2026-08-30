---
title: "Fluxograma: APEX sequencial NS e PROTECHT com p unilateral — o que não é primário"
slug: fluxograma-apex-protecht-o-que-nao-e-primario
theme: "Tromboembolismo"
kind: fluxograma
summary: "Clínico agudo: APEX betrixabana — primário coorte D-dímero P=0,054 NS; overall P=0,006 é exploratório. MARINER já no Padua. Câncer ambulatorial em quimio sem Khorana: PROTECHT (nadroparina, composto venoso+arterial, p unilateral 0,02) vs SAVE-ONCO (semuloparina, venoso). Khorana ≥2: AVERT ganhou; CASSINI primário 180 d NS."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Âncoras: APEX PMID 27232649, PROTECHT PMID 19726226, SAVE-ONCO PMID 22335737, AVERT PMID 30511879, CASSINI PMID 30786186. MAGELLAN não citado — PMID primário não fechado. Revisão científica concluída em 30/08/2026."
source_refs:
  - "Cohen AT, et al. APEX. N Engl J Med. 2016;375(6):534-544. PMID: 27232649."
  - "Agnelli G, et al. PROTECHT. Lancet Oncol. 2009;10(10):943-949. PMID: 19726226."
  - "Documento da casa profilaxia-de-tev-no-paciente-clinico-hospitalizado-escore-de-padua-e-profilaxia-estendida."
  - "Documento da casa save-onco-semuloparina-na-profilaxia-primaria-durante-quimioterapia."
  - "Documento da casa avert-apixabana-na-profilaxia-primaria-ambulatorial-khorana-2."
  - "Documento da casa cassini-rivaroxabana-na-profilaxia-primaria-ambulatorial-khorana-2."
---

# Fluxograma: sequencial, unilateral, suporte — nenhum substitui o primário

```mermaid
flowchart TD
  R0["Profilaxia: alguém cita um p baixo"] --> D1{"Qual cenário?"}

  D1 -->|"Clínico internado, estendida"| D2{"Qual ensaio?"}
  D1 -->|"Câncer ambulatorial em quimio"| D3{"Seleção?"}

  D2 -->|"Betrixabana 35–42 d"| C1(["APEX: coorte D-dímero P=0,054 NS<br/>Overall P=0,006 é EXPLORATÓRIO"])
  D2 -->|"Rivaroxabana pós-alta"| C2(["MARINER já no Padua da casa<br/>Composto com morte por TEV NS"])

  D3 -->|"Sem Khorana"| C3(["PROTECHT: p unilateral 0,02<br/>composto venoso+arterial<br/>SAVE-ONCO: venoso, semuloparina"])
  D3 -->|"Khorana >= 2"| C4(["AVERT ganhou TEV, sangramento sobe<br/>CASSINI primário 180 d NS"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4 conduta;
```

## Mensagem prática

**P exploratório, p unilateral e análise de suporte não viram primário.** APEX não autoriza betrixabana estendida. PROTECHT não autoriza HBPM genérica nem TEV isolado. CASSINI não autoriza rivaroxabana 10 mg em 180 dias.
