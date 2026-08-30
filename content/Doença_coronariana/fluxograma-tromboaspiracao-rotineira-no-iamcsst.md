---
title: "Fluxograma: tromboaspiração na ICP primária — rotina não, resgate mecânico talvez"
slug: fluxograma-tromboaspiracao-rotineira-no-iamcsst
theme: "Doença coronariana"
kind: fluxograma
summary: "TASTE e TOTAL fecham a aspiração rotineira. TOTAL aumenta AVC. Aspiração entra só se há trombo residual volumoso como causa mecânica de no-reflow — outra árvore."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em TASTE (PMID 23991656) e TOTAL (PMID 25853743). Classe ESC de trombectomia não relida nesta revisão editorial. Revisão científica concluída em 30/08/2026."
source_refs:
  - "Fröbert O, et al. TASTE. N Engl J Med. 2013;369(17):1587-1597. PMID: 23991656."
  - "Jolly SS, et al. TOTAL. N Engl J Med. 2015;372(15):1389-1398. PMID: 25853743."
  - "Documentos da casa taste-total-tromboaspiracao-rotineira-no-iamcsst e fluxograma-manejo-do-no-reflow-na-icp-primaria."
---

# Fluxograma: tromboaspiração na ICP primária

```mermaid
flowchart TD
  R0["IAMCSST em ICP primária,<br/>artéria culpada visível"] --> D1{"Há causa mecânica de fluxo ruim<br/>(dissecção, malposição, espasmo,<br/>trombo residual volumoso)?"}

  D1 -->|"Não — fluxo TIMI 3 ou no-reflow<br/>sem trombo residual óbvio"| C1(["NÃO aspirar de rotina.<br/>TASTE: morte 2,8% vs 3,0% (HR 0,94).<br/>TOTAL: composto 6,9% vs 7,0% (HR 0,99);<br/>AVC 0,7% vs 0,3% (HR 2,06)"])

  D1 -->|"Sim — trombo residual volumoso<br/>como causa mecânica"| C2(["Corrigir a causa: nova insuflação,<br/>stent, aspiração seletiva deste trombo.<br/>Não é a pergunta TASTE/TOTAL.<br/>Árvore de no-reflow da casa"])

  D1 -->|"Sim — dissecção / malposição / espasmo"| C3(["Corrigir a causa mecânica.<br/>Aspiração não trata isso"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3 conduta;
```

## Mensagem prática

**Rotina: não. Resgate de trombo residual volumoso: outra árvore (no-reflow mecânico).** O TOTAL não autoriza aspirar “para ver se o blush melhora”.
