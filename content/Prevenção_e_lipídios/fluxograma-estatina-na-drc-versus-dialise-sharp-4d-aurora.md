---
title: "Fluxograma: estatina na DRC vs diálise — SHARP ganha composto; 4D e AURORA não"
slug: fluxograma-estatina-na-drc-versus-dialise-sharp-4d-aurora
theme: "Prevenção e lipídios"
kind: fluxograma
summary: "DRC avançada sem IAM/revascularização: SHARP (sinvastatina 20+ezetimiba 10) reduz evento aterosclerótico maior (P=0,0021); IAM/morte coronariana NS. HD dedicada: 4D (atorvastatina 20, DM2) primário P=0,37; AURORA (rosuvastatina 10) P=0,59. Não usar o subgrupo de diálise do SHARP para anular 4D/AURORA. Não vender P nominais nem AVC fatal do 4D como a pergunta do ensaio."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em SHARP PMID 21663949, 4D PMID 16034009 e AURORA PMID 19332456. IMPROVE-IT é SCA — outro arquivo. Revisão científica concluída em 30/08/2026."
source_refs:
  - "Baigent C, et al. SHARP. Lancet. 2011;377(9784):2181-2192. PMID: 21663949."
  - "Wanner C, et al. 4D. N Engl J Med. 2005;353(3):238-248. PMID: 16034009."
  - "Fellström BC, et al. AURORA. N Engl J Med. 2009;360(14):1395-1407. PMID: 19332456."
---

# Fluxograma: DRC ou já em diálise?

```mermaid
flowchart TD
  R0["Quer iniciar hipolipemiante para evento CV na DRC/HD?"] --> D1{"Já em hemodiálise de manutenção?"}

  D1 -->|"Sim, e a pergunta é RCT dedicado"| D2{"Qual ensaio?"}

  D2 -->|"DM2 + atorvastatina 20"| C1(["4D: primário RR 0,92; P=0,37 NS<br/>Morte P=0,33. Eventos cardíacos P=0,03 nominal<br/>AVC fatal P=0,04 — componente"])

  D2 -->|"Rosuvastatina 10, 50–80 anos"| C2(["AURORA: HR 0,96; P=0,59 NS<br/>Morte HR 0,96; P=0,51"])

  D1 -->|"DRC avançada, com ou sem diálise,<br/>sem IAM/revasc coronariana"| C3(["SHARP: 11,3% vs 13,4%; P=0,0021<br/>IAM/morte coronariana P=0,37 NS<br/>Não é RCT só de diálise"])

  R0 --> D3{"É IMPROVE-IT?"}

  D3 -->|"Pós-SCA, sinvastatina ± ezetimiba"| C4(["Outro arquivo. Não misturar SCA com DRC/HD"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4 conduta;
```

## Mensagem prática

**SHARP responde DRC mista e composto aterosclerótico — não mortalidade.** **4D e AURORA respondem HD dedicada e são NS no primário.** Não anular os dois com o subgrupo de diálise do SHARP.
