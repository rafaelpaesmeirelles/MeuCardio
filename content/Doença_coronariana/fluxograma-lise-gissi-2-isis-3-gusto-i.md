---
title: "Fluxograma: SK vs t-PA — GISSI-2 e ISIS-3 empatam; GUSTO-I testa outro esquema"
slug: fluxograma-lise-gissi-2-isis-3-gusto-i
theme: "Doença coronariana"
kind: fluxograma
summary: "GISSI-2: t-PA 3 h vs SK, composto NS; heparina SC NS. ISIS-3: SK vs APSAC morte NS; heparina SC morte 35 d NS; t-PA vs SK truncado no MEDLINE. GUSTO-I é t-PA acelerado + HNF EV. Não fundir os três."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em GISSI-2 PMID 1975321, ISIS-3 PMID 1347801, GUSTO-I da casa. Revisão científica concluída em 30/08/2026."
source_refs:
  - "GISSI-2. Lancet. 1990;336(8707):65-71. PMID: 1975321."
  - "ISIS-3 Collaborative Group. Lancet. 1992;339(8796):753-770. PMID: 1347801."
  - "Documento da casa gusto-i-tpa-acelerado-versus-estreptoquinase."
  - "Documento da casa fluxograma-lise-gissi-1-isis-2-assent-2."
---

# Fluxograma: SK contra t-PA — qual ensaio, qual esquema

```mermaid
flowchart TD
  R0["Comparar fibrinolíticos"] --> D1{"Qual o esquema?"}

  D1 -->|"t-PA 3 h vs SK + heparina SC 12 h depois"| C1(["GISSI-2: composto 23,1% vs 22,5% NS<br/>Heparina SC não muda o primário"])

  D1 -->|"SK vs duteplase vs APSAC + heparina SC"| C2(["ISIS-3: SK vs APSAC morte 10,6% vs 10,5%<br/>Heparina SC morte 35 d NS. t-PA vs SK truncado"])

  D1 -->|"t-PA acelerado + HNF EV"| C3(["GUSTO-I — outro arquivo<br/>Não misturar com GISSI-2/ISIS-3"])

  D1 -->|"SK + AAS contra nada"| C4(["GISSI-1 / ISIS-2<br/>Ver fluxograma-lise-gissi-1-isis-2-assent-2"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4 conduta;
```

## Mensagem prática

**GISSI-2 e ISIS-3 não mostram superioridade do t-PA no esquema que testaram.** GUSTO-I muda dose, velocidade e heparina. Não fundir os três numa frase só.
