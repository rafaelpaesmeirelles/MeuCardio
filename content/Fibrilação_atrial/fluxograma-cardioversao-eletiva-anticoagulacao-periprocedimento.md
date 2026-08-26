---
title: "Fluxograma: cardioversão eletiva na FA — via de anticoagulação e janela pós-procedimento (ESC 2024)"
slug: fluxograma-cardioversao-eletiva-anticoagulacao-periprocedimento
theme: "Fibrilação atrial"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Verificado por Claude em 26/08/2026: fonte primaria conferida; conteudo derivado de documento(s) ja publicado(s) no acervo, listado(s) em source_refs."
source_refs:
  - "Van Gelder IC, Rienstra M, Bunting KV, et al. 2024 ESC Guidelines for the management of atrial fibrillation developed in collaboration with the EACTS. European Heart Journal. 2024;45(36):3314-3414. DOI: 10.1093/eurheartj/ehae176. PMID: 39210723."
  - "Derivado do documento já publicado no acervo 'Cardioversão Eletiva e Anticoagulação Periprocedimento (ESC 2024)' (content/Fibrilação_atrial/cardioversao-eletiva-e-anticoagulacao-periprocedimento-esc-2024.md), que cita a mesma fonte acima."
---

# Fluxograma: cardioversão eletiva na FA — via de anticoagulação e janela pós-procedimento (ESC 2024)

A cardioversão eletiva de FA — fora da janela aguda de início recente — organiza-se em três janelas temporais de anticoagulação, e a que mais surpreende na prática é a última: mesmo o paciente jovem sem nenhum fator de risco (CHA2DS2-VA de 0), que nunca precisaria de anticoagulação crônica, precisa de 4 semanas de anticoagulação terapêutica depois do procedimento. A razão não é o risco tromboembólico basal — é o atordoamento atrial mecânico transitório que a própria cardioversão causa.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Paciente com FA e indicação de cardioversão eletiva (fora do contexto agudo de FA de início recente)"] --> D1{"Tempo de anticoagulação terapêutica documentada antes da data planejada"}

  D1 -->|"3 semanas ou mais de anticoagulação terapêutica comprovada (adesão a DOAC, ou RIN consistentemente maior que 2 em antagonista de vitamina K)"| C1(["Realizar a cardioversão eletiva; manter anticoagulação terapêutica por pelo menos 4 semanas depois, independentemente do CHA2DS2-VA"])

  D1 -->|"Menos de 3 semanas documentadas, ou desejo de cardiovertir mais cedo"| P1["Solicitar ecocardiograma transesofágico (ETE) para excluir trombo em apêndice atrial esquerdo"]
  P1 --> D2{"O ETE exclui trombo em apêndice atrial esquerdo?"}
  D2 -->|"Sim, e o paciente já está em anticoagulação terapêutica no momento do procedimento"| C2(["Cardioverter imediatamente; manter anticoagulação terapêutica por pelo menos 4 semanas depois, independentemente do CHA2DS2-VA"])
  D2 -->|"Não (trombo presente, ou exclusão não confiável)"| C3(["Adiar a cardioversão; manter/otimizar a anticoagulação terapêutica e reavaliar com novo ETE antes de nova tentativa"])

  classDef conduta fill:#eef5f8,stroke:#1c7293,color:#0b2e45;
  class C1,C2,C3 conduta;
```

## O que a árvore não mostra

**As duas vias de preparo (3 semanas de anticoagulação comprovada, ou ETE para excluir trombo e cardioverter mais cedo) são estratégias equivalentes**, escolhidas conforme a urgência clínica e a disponibilidade do exame — uma não é atalho que dispensa a outra.

**Depois das 4 semanas pós-cardioversão, a decisão de manter ou suspender a anticoagulação volta a seguir o escore de risco tromboembólico crônico (CHA2DS2-VA)** — não mais a regra periprocedimento representada nesta árvore.

**Este fluxograma cobre a cardioversão eletiva, não a FA aguda de início recente.** O corte de 24 horas para cardioversão sem necessidade de ETE, usado na FA aguda, é um cenário clínico distinto com estratégia de anticoagulação própria.