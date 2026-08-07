---
title: "Fluxograma: SCA no idoso frágil e apresentação atípica"
slug: fluxograma-sindrome-coronariana-aguda-no-idoso-fragil-e-apresentacao-atipica
theme: "Cardiologia geriátrica"
kind: fluxograma
summary: "Árvore para suspeita de SCA no idoso com ou sem dor torácica, incorporando dispneia, síncope e confusão, diferenciação de lesão miocárdica tipo 1/tipo 2 e avaliação de fragilidade sem ageísmo terapêutico."
review_status: revisado
source_refs: ["Damluji AA, Forman DE, Wang TY, et al. Management of Acute Coronary Syndrome in the Older Adult Population: A Scientific Statement From the American Heart Association. Circulation. 2023;147(3):e32-e62. DOI: 10.1161/CIR.0000000000001112. PMID: 36503287. PMCID: PMC10312228.", "Byrne RA, Rossello X, Coughlan JJ, et al.; ESC Scientific Document Group. 2023 ESC Guidelines for the management of acute coronary syndromes. Eur Heart J. 2023;44(38):3720-3826. DOI: 10.1093/eurheartj/ehad191. PMID: 37622654."]
---

# SCA no idoso frágil/apresentação atípica

```mermaid
flowchart TD
  R0["Idoso com dor torácica OU dispneia aguda,<br/>síncope, confusão súbita, queda inexplicada,<br/>IC aguda ou instabilidade"]
  P1["ABC + ECG de 12 derivações + troponina;<br/>comparar ECG prévio quando disponível;<br/>revisar anticoagulantes/antiagregantes e função renal"]
  D1{"STEMI ou instabilidade/isquemia persistente<br/>de alto risco?"}
  C1(["Sim: conduzir reperfusão/estratégia invasiva<br/>conforme SCA; não excluir pela idade cronológica"])
  P2["Não: interpretar dinâmica de troponina + ECG<br/>+ clínica e procurar precipitantes de lesão tipo 2"]
  D2{"Há evidência convincente de SCA tipo 1/NSTEMI?"}
  P3["Sim: estimar risco isquêmico e hemorrágico<br/>+ avaliar fragilidade, cognição, função,<br/>multimorbidade e objetivos do paciente"]
  D3{"Benefício esperado de estratégia invasiva<br/>supera riscos/futilidade individual?"}
  C2(["Sim: estratégia invasiva guiada por risco,<br/>com prevenção de sangramento/lesão renal"])
  C3(["Não: manejo conservador individualizado,<br/>controle de sintomas e metas de cuidado"])
  D4{"Troponina elevada mas contexto sugere<br/>lesão miocárdica tipo 2/outra causa?"}
  C4(["Sim: tratar causa precipitante e continuar<br/>avaliação cardíaca conforme risco; não rotular<br/>automaticamente como placa rota"])
  C5(["Não/diagnóstico incerto: observação, troponina/ECG<br/>seriados e imagem conforme probabilidade clínica"])
  C6(["Antes da alta/transferência: reconciliação<br/>medicamentosa, plano funcional e seguimento"])

  R0 --> P1
  P1 --> D1
  D1 -->|"Sim"| C1
  D1 -->|"Não"| P2
  P2 --> D2
  D2 -->|"Sim"| P3
  D2 -->|"Não"| D4
  P3 --> D3
  D3 -->|"Sim"| C2
  D3 -->|"Não"| C3
  D4 -->|"Sim"| C4
  D4 -->|"Não/incerto"| C5
  C1 --> C6
  C2 --> C6
  C3 --> C6
  C4 --> C6
  C5 --> C6

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## Regra prática

No idoso, **a apresentação pode ser não dolorosa; a fragilidade entra depois que a emergência foi reconhecida**, para calibrar benefício, risco e objetivos — não para impedir o diagnóstico ou negar tratamento automaticamente.
