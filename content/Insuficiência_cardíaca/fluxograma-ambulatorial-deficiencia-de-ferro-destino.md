---
title: "Fluxograma ambulatorial: deficiência de ferro na IC — destino"
slug: fluxograma-ambulatorial-deficiencia-de-ferro-destino
theme: "Insuficiência cardíaca"
kind: fluxograma
fonte_producao: grok
summary: "Árvore de consultório: urgência primeiro; deficiência de ferro + IC sintomática com fenótipo elegível → ferro EV; pós-alta AFFIRM-AHF restrito a FEVE<50%; ICFEp não é extrapolada."
review_status: revisado
review_note: "Revisão clínica final 08/09/2026. Corrigido escape Mermaid da FEVE; AFFIRM-AHF restrito a FEVE <50%; hipersensibilidade grave anterior ao produto impede reexposição rotineira; sem extrapolação para ICFEp."
source_refs:
  - "McDonagh TA, Metra M, Adamo M, et al. ESC HF 2021. PMID: 34447992"
  - "McDonagh TA, Metra M, Adamo M, et al. ESC HF Focused Update 2023. PMID: 37622666"
  - "Ponikowski P, van Veldhuisen DJ, Comin-Colet J, et al. CONFIRM-HF. PMID: 25176939"
---

# Fluxograma ambulatorial: deficiência de ferro na IC — destino

```mermaid
flowchart TD
  R0["Consulta de IC + suspeita/deficiência de ferro"] --> D1{"Instabilidade, sangramento ativo<br/>ou reação de hipersensibilidade aguda?"}
  D1 -->|"Sim"| C1(["PS / urgência AGORA"])

  D1 -->|"Não"| D2{"Deficiência de ferro confirmada<br/>pelos critérios ESC?"}
  D2 -->|"Não/desconhecido"| C2(["Rastrear: hemograma + ferritina + TSAT<br/>Investigar causa"])

  D2 -->|"Sim"| D3{"IC sintomática com FEVE &lt; 50%<br/>ou outro fenótipo explicitamente elegível<br/>no fluxo ESC canônico?"}
  D3 -->|"Não"| C3(["Não extrapolar ensaios para ICFEp<br/>Investigar/tratar causa caso a caso"])

  D3 -->|"Sim"| D4{"Hipersensibilidade grave prévia<br/>ao mesmo produto de ferro EV?"}
  D4 -->|"Sim"| C4(["Não reexpor rotineiramente<br/>Avaliação especializada/agent-specific"])

  D4 -->|"Não"| D5{"Já há plano/ciclo de ferro EV<br/>em acompanhamento?"}
  D5 -->|"Sim"| C5(["Manter plano e janela de reavaliação"])
  D5 -->|"Não"| C6(["Encaminhar para ferro EV conforme<br/>fluxo ESC canônico — sem doses aqui"])

  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C4 alerta;
  class C2,C3,C5,C6 conduta;
```

## Pós-alta
O contexto AFFIRM-AHF não é um ramo independente para qualquer IC: exige população compatível, incluindo **FEVE <50%**. FEVE >=50% não deve ser enviada automaticamente a ferro EV com base nesse ensaio.

Sem doses ou formulações neste fluxograma.
