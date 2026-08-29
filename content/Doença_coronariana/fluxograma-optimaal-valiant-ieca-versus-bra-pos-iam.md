---
title: "Fluxograma: IECA vs BRA no pós-IAM — OPTIMAAL não autoriza losartana 50"
slug: fluxograma-optimaal-valiant-ieca-versus-bra-pos-iam
theme: "Doença coronariana"
kind: fluxograma
summary: "OPTIMAAL: losartana 50 vs captopril, morte P=0,07 a favor do IECA. VALIANT: valsartana vs captopril (arquivo próprio). ELITE II e HEAAL são IC crônica, não pós-IAM. SAVE/AIRE/TRACE sustentam IECA. CAPRICORN é carvedilol; primário composto NS."
review_status: pendente_revisao
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em OPTIMAAL PMID 12241832 e CAPRICORN 11356434. VALIANT/ELITE II/HEAAL/SAVE já na casa. Publicação sujeita à aprovação do responsável técnico."
source_refs:
  - "Dickstein K, Kjekshus J. OPTIMAAL. Lancet. 2002;360(9335):752-760. PMID: 12241832."
  - "Dargie HJ. CAPRICORN. Lancet. 2001;357(9266):1385-1390. PMID: 11356434."
---

# Fluxograma: trocar o IECA no pós-IAM?

```mermaid
flowchart TD
  R0["Pós-IAM de alto risco, quer citar BRA ou carvedilol"] --> D1{"Qual a pergunta?"}

  D1 -->|"Losartana 50 vs captopril"| C1(["OPTIMAAL: morte 18% vs 16%<br/>P=0,07 — tendência contra a losartana<br/>IECA continua primeira escolha"])

  D1 -->|"Valsartana vs captopril"| C2(["VALIANT: arquivo próprio"])

  D1 -->|"Losartana na IC crônica"| C3(["ELITE II vs captopril<br/>HEAAL 150 vs 50 se intolerante a IECA<br/>não é pós-IAM"])

  D1 -->|"IECA vs placebo pós-IAM"| C4(["SAVE / AIRE / TRACE<br/>arquivos próprios"])

  D1 -->|"Carvedilol, FE ≤40%"| C5(["CAPRICORN: composto primário NS<br/>morte P=0,03 — não inverter"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

## Mensagem prática

**IECA primeiro no pós-IAM complicado.** Losartana 50 mg no OPTIMAAL não ganha. CAPRICORN não vende o composto.
