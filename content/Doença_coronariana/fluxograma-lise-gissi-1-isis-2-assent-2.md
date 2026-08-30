---
title: "Fluxograma: lise clássica — GISSI-1 (SK aberta), ISIS-2 (SK+AAS aditivos), ASSENT-2 (TNK ≈ t-PA)"
slug: fluxograma-lise-gissi-1-isis-2-assent-2
theme: "Doença coronariana"
kind: fluxograma
summary: "GISSI-1: SK reduz morte hospitalar 21 d (10,7% vs 13%); janela 9–12 h RR 1,19. ISIS-2: SK e AAS 160 mg somam na morte vascular 5 semanas (8,0% vs 13,2%). ASSENT-2: TNK equivalente ao t-PA na morte 30 d (6,18% vs 6,15%). Não confundir com ASSENT-4 (facilitada piora) nem com adjunto ASSENT-3."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em GISSI-1 PMID 2868337, ISIS-2 PMID 2899772, ASSENT-2 PMID 10475182. Revisão científica concluída em 30/08/2026."
source_refs:
  - "GISSI. Lancet. 1986;1(8478):397-402. PMID: 2868337."
  - "ISIS-2 Collaborative Group. Lancet. 1988;2(8607):349-360. PMID: 2899772."
  - "ASSENT-2 Investigators. Lancet. 1999;354(9180):716-722. PMID: 10475182."
  - "Documento da casa gusto-i-tpa-acelerado-versus-estreptoquinase."
  - "Documento da casa fluxograma-lise-assent-3-gusto-v-extract."
  - "Documento da casa fluxograma-icp-facilitada-assent-4-finesse."
  - "Documento da casa fluxograma-farmacoinvasiva-transfer-caress-stream-prague-2."
  - "Documento da casa fluxograma-lise-gissi-2-isis-3-gusto-i."
---

# Fluxograma: o que a lise clássica realmente mostrou

```mermaid
flowchart TD
  R0["IAM com indicação histórica de lise"] --> D1{"Qual pergunta?"}

  D1 -->|"SK reduz morte hospitalar?"| C1(["GISSI-1: 10,7% vs 13% aos 21 d<br/>p=0,0002. Aberto. RR 1,19 na janela 9–12 h"])

  D1 -->|"SK + AAS somam?"| C2(["ISIS-2: SK 9,2% vs 12,0%; AAS 9,4% vs 11,8%<br/>Os dois 8,0% vs 13,2%. Efeitos aditivos"])

  D1 -->|"TNK é melhor que t-PA?"| C3(["ASSENT-2: equivalência, não superioridade<br/>Morte 6,18% vs 6,15%. Menos sangramento não cerebral"])

  D1 -->|"TNK antes da ICP?"| C4(["Não. ASSENT-4: morte hospitalar 6% vs 3%<br/>Ver fluxograma-icp-facilitada-assent-4-finesse"])

  D1 -->|"Não chegou a tempo à ICP?"| C5(["Farmacoinvasiva: TRANSFER-AMI / CARESS / STREAM<br/>Ver fluxograma-farmacoinvasiva-transfer-caress-stream-prague-2"])

  D1 -->|"SK vs t-PA / APSAC?"| C6(["GISSI-2 e ISIS-3 empatam no esquema testado<br/>Ver fluxograma-lise-gissi-2-isis-3-gusto-i"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## Mensagem prática

**AAS 160 mg e SK reduziram morte; TNK igualou t-PA.** Facilitar ICP com lise plena fez mal. Quando a ICP atrasa, o ramo é farmacoinvasivo — outro fluxograma.
