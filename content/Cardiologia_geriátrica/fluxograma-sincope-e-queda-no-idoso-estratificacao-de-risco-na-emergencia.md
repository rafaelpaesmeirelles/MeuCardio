---
title: "Fluxograma: síncope e queda no idoso — estratificação de risco na emergência"
slug: fluxograma-sincope-e-queda-no-idoso-estratificacao-de-risco-na-emergencia
theme: "Cardiologia geriátrica"
kind: fluxograma
summary: "Árvore de decisão para síncope ou queda inexplicada em pessoa idosa, com PA ortostática, ECG, revisão medicamentosa e identificação de marcadores de alto risco cardiovascular."
review_status: revisado
source_refs: ["Brignole M, Moya A, de Lange FJ, et al. 2018 ESC Guidelines for the diagnosis and management of syncope. Eur Heart J. 2018;39:1883-1948. DOI: 10.1093/eurheartj/ehy037. PMID: 29562304."]
---

# Síncope e queda no idoso

```mermaid
flowchart TD
  R0["Idoso com síncope, pré-síncope<br/>ou queda inexplicada"]
  P1["História/testemunha + exame físico + ECG;<br/>PA ortostática; revisar medicações e volume;<br/>procurar trauma, anemia/hemorragia e distúrbio eletrolítico"]
  D1{"Há marcador de alto risco?<br/>cardiopatia importante, síncope em esforço/supina,<br/>palpitação no evento, ECG de risco,<br/>hipotensão persistente ou arritmia documentada"}
  C1(["Monitorização cardíaca imediata;<br/>avaliação intensiva/hospitalar;<br/>investigar causa arrítmica/estrutural e tratar<br/>bradicardia, BAV ou taquiarritmia conforme protocolo"])
  D2{"Hipotensão ortostática documentada<br/>sem marcador de alto risco?"}
  C2(["Corrigir hipovolemia/gatilho reversível;<br/>revisar anti-hipertensivos, diuréticos e vasodilatadores;<br/>orientar prevenção de recorrência e seguimento"])
  D3{"Evento continua inexplicado<br/>ou queda sem memória clara do mecanismo?"}
  C3(["Não rotular como queda mecânica;<br/>manter investigação de síncope e considerar<br/>monitorização ambulatorial/unidade de síncope"])
  C4(["Conduta dirigida ao diagnóstico identificado;<br/>alta apenas se baixo risco e seguimento seguro"])

  R0 --> P1
  P1 --> D1
  D1 -->|"Sim"| C1
  D1 -->|"Não"| D2
  D2 -->|"Sim"| C2
  D2 -->|"Não"| D3
  D3 -->|"Sim"| C3
  D3 -->|"Não"| C4

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4 conduta;
```

## Segurança

Em pessoa idosa, uma queda sem mecanismo claro pode ser apresentação de síncope. O rótulo “queda mecânica” não deve encerrar a avaliação antes de ECG, PA ortostática e revisão da medicação.
