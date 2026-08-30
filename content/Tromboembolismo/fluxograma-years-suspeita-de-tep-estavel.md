---
title: "Fluxograma: algoritmo YEARS na suspeita de TEP no paciente estável"
slug: fluxograma-years-suspeita-de-tep-estavel
theme: "Tromboembolismo"
kind: fluxograma
summary: "Árvore do YEARS no estável: três itens, D-dímero 1000 vs 500, angiotomografia só se o corte falhar. Instável e gestante saem. Não substitui o fluxograma ESC 2019 da casa."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em van der Hulle PMID 28549662. Gestação e instabilidade explicitamente fora. Revisão científica concluída em 30/08/2026."
source_refs:
  - "van der Hulle T, et al. The YEARS study. Lancet. 2017;390(10091):289-297. PMID: 28549662."
  - "Documentos da casa years-algoritmo-simplificado-para-excluir-tep-suspeito e fluxograma-tromboembolismo-pulmonar-diagnostico-esc-2019."
---

# Fluxograma: algoritmo YEARS na suspeita de TEP no paciente estável

O fluxograma ESC 2019 da casa decide **instável vs estável**. Esta árvore só abre no estável, como alternativa ao Wells + D-dímero.

```mermaid
flowchart TD
  R0["Suspeita de TEP"] --> D0{"Instabilidade hemodinâmica<br/>ou gestante?"}

  D0 -->|"Instável"| C0(["Sai desta árvore.<br/>Fluxograma ESC 2019 — anatomia imediata"])

  D0 -->|"Gestante"| C1(["Sai desta árvore.<br/>YEARS da gravidez: documento próprio da casa"])

  D0 -->|"Estável, não gestante"| D1{"Itens YEARS:<br/>sinais de TVP, hemoptise,<br/>TEP é o mais provável"}

  D1 -->|"Zero itens"| D2{"D-dímero < 1000 ng/mL?"}

  D2 -->|"Sim"| C2(["TEP excluído sem angiotomografia.<br/>YEARS: TEV em 3 meses 0,61%"])

  D2 -->|"Não"| C3(["Angiotomografia"])

  D1 -->|"Um ou mais itens"| D3{"D-dímero < 500 ng/mL?"}

  D3 -->|"Sim"| C4(["TEP excluído sem angiotomografia"])

  D3 -->|"Não"| C5(["Angiotomografia"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C0,C1,C2,C3,C4,C5 conduta;
```

## Mensagem prática

**Estável, não gestante: 3 itens. Zero itens corta em 1000; algum item corta em 500. O resto vai à tomografia.** Instável não espera D-dímero.
