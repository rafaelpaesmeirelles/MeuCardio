---
title: "Fluxograma: HAS sistólica isolada no idoso — SHEP, Syst-Eur e HYVET"
slug: fluxograma-has-sistolica-isolada-idoso-shep-syst-eur-hyvet
theme: "Hipertensão"
kind: fluxograma
summary: "≥60 anos, PAS alta e PAD baixa: SHEP (clortalidona) reduz AVC (RR 0,64). Syst-Eur (nitrendipina) reduz AVC (−42%); morte total NS. ≥80 anos: HYVET (arquivo próprio). Nenhum destes autoriza vender redução de mortalidade total a partir do abstract do SHEP (RR 0,87 sem p) ou do Syst-Eur (P=0,22). SPRINT é outra técnica de medida e outra meta."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em SHEP PMID 2046107, Syst-Eur PMID 9297994 e HYVET da casa. SPRINT é outro desenho — não misturar. Revisão científica concluída em 30/08/2026."
source_refs:
  - "SHEP Cooperative Research Group. JAMA. 1991;265(24):3255-3264. PMID: 2046107."
  - "Staessen JA, et al. Syst-Eur. Lancet. 1997;350(9080):757-764. PMID: 9297994."
  - "Documento da casa tratamento-da-hipertensao-aos-80-anos-ou-mais-o-ensaio-hyvet."
---

# Fluxograma: PAS isolada no idoso

```mermaid
flowchart TD
  R0["Idoso com PAS alta e PAD baixa"] --> D1{"Idade"}

  D1 -->|">= 80 anos"| C0(["HYVET. Arquivo próprio da casa.<br/>Não é SHEP nem Syst-Eur"])

  D1 -->|"60–79 anos, PAS 160–219"| D2{"Qual evidência de desfecho?"}

  D2 -->|"Tiazídico (clortalidona)"| C1(["SHEP: AVC 5,2 vs 8,2 / 100 em 5 anos<br/>RR 0,64; P=0,0003<br/>Morte RR 0,87 — sem p neste abstract"])

  D2 -->|"Diidropiridina (nitrendipina)"| C2(["Syst-Eur: AVC −42%; P=0,003<br/>Morte total −14%; P=0,22 NS"])

  R0 --> D3{"É SPRINT?"}

  D3 -->|"Meta intensiva, medida não observada"| C3(["Outro arquivo. Não misturar<br/>técnica de medida nem meta"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C0,C1,C2,C3 conduta;
```

## Mensagem prática

**Tratar a PAS isolada do idoso reduz AVC (SHEP, Syst-Eur). A morte total não está provada nestes abstracts.** HYVET cobre o ≥80. SPRINT não entra nesta árvore.
