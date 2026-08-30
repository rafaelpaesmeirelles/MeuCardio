---
title: "Fluxograma: intensidade de estatina após SCA e na DAC estável — PROVE-IT e TNT"
slug: fluxograma-intensidade-de-estatina-apos-sca-e-na-dac-estavel
theme: "Prevenção e lipídios"
kind: fluxograma
summary: "SCA recente: atorvastatina 80 (PROVE-IT), não pravastatina 40. DAC estável: 80 vs 10 reduz o composto, mortalidade total igual, mais ALT (TNT). Nenhum dos dois é IMPROVE-IT (ezetimiba) nem FOURIER (PCSK9)."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada nos abstracts de PROVE-IT TIMI 22 (PMID 15007110) e TNT (PMID 15755765). Componentes isolados do PROVE-IT e morte CV isolada do TNT NÃO estão nos abstracts — a árvore não os inventa. Revisão científica concluída em 30/08/2026."
source_refs:
  - "Cannon CP, et al. PROVE-IT TIMI 22. N Engl J Med. 2004;350(15):1495-1504. PMID: 15007110."
  - "LaRosa JC, et al. TNT. N Engl J Med. 2005;352(14):1425-1435. PMID: 15755765."
  - "Documentos da casa prove-it-timi-22-atorvastatina-80-versus-pravastatina-40-pos-sca e tnt-atorvastatina-80-versus-10-na-dac-estavel."
---

# Fluxograma: intensidade de estatina — SCA versus DAC estável

```mermaid
flowchart TD
  R0["Indicação de estatina em quem já tem placa"] --> D1{"Quando foi o evento?"}

  D1 -->|"SCA nos últimos dias"| C1(["Atorvastatina 80 (ou equivalente de alta intensidade).<br/>PROVE-IT: LDL 62 vs 95; composto 22,4% vs 26,3%; P=0,005.<br/>Não pravastatina 40"])

  D1 -->|"DAC estável, LDL já <130"| C2(["80 mg reduz o composto contra 10 mg.<br/>TNT: 8,7% vs 10,9%; HR 0,78.<br/>Mortalidade total igual; ALT 1,2% vs 0,2%"])

  D1 -->|"Já em alta intensidade<br/>e ainda acima da meta"| C3(["Não é pergunta do PROVE-IT/TNT.<br/>IMPROVE-IT, CLEAR, FOURIER/ODYSSEY<br/>são documentos da casa"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3 conduta;
```

## Mensagem prática

**SCA: ir fundo cedo. Estável: 80 vs 10 reduz evento, não mortalidade total.** A meta numérica mudou; a mensagem de intensidade não.
