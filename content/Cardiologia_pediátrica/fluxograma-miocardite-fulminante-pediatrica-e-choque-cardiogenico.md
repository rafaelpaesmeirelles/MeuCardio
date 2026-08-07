---
title: "Fluxograma: Miocardite fulminante pediátrica e choque cardiogênico"
slug: fluxograma-miocardite-fulminante-pediatrica-e-choque-cardiogenico
theme: "Cardiologia pediátrica"
kind: fluxograma
summary: "Árvore de decisão para criança com suspeita de miocardite e deterioração, separando casos estáveis de choque/arritmia de alto risco e enfatizando transferência e MCS precoces na refratariedade."
review_status: revisado
source_refs: ["Schulz-Menger J, Collini V, Gröschel J, et al.; ESC Scientific Document Group. 2025 ESC Guidelines for the management of myocarditis and pericarditis. Eur Heart J. 2025;46(40):3952-4041. DOI: 10.1093/eurheartj/ehaf192. PMID: 40878297. Diretriz endossada pela AEPC.", "Law YM, Lal AK, Chen S, et al. Diagnosis and Management of Myocarditis in Children: A Scientific Statement From the American Heart Association. Circulation. 2021;144(6):e123-e135. DOI: 10.1161/CIR.0000000000001001. PMID: 34229446."]
---

# Miocardite fulminante pediátrica

```mermaid
flowchart TD
  R0["Criança/lactente com IC aguda, choque,<br/>troponina elevada, arritmia/BAV ou<br/>deterioração após pródromo infeccioso"]
  P1["ABC + ECG + troponina + eco urgente;<br/>monitorização contínua; excluir cardiopatia estrutural<br/>e outras causas de choque"]
  D1{"Choque, hipoperfusão progressiva,<br/>TV/FV, BAV alto grau ou rápida piora ventricular?"}
  C1(["Não: investigação de miocardite com CMR<br/>quando estável + vigilância e tratamento de IC<br/>conforme fenótipo"])
  P2["Sim: transferir/acionar centro terciário capaz de<br/>UTI cardíaca pediátrica, EMB e MCS/ECMO"]
  P3["Suporte ventilatório/metabólico + vasoativo/inotrópico<br/>individualizado; corrigir eletrólitos e tratar arritmias"]
  D2{"Perfusão e função estabilizam rapidamente?"}
  C2(["Sim: manter suporte, monitorização e<br/>definir etiologia/CMR/EMB conforme risco"])
  P4["Não: discutir MCS temporário PRECOCEMENTE;<br/>VA-ECMO é modalidade frequentemente usada<br/>na miocardite fulminante"]
  D3{"EMB indicada e centro experiente disponível?"}
  C3(["Sim: realizar EMB precoce sem atrasar MCS;<br/>buscar células gigantes/eosinofílica/outros subtipos"])
  C4(["Não/imediatamente inviável: priorizar estabilização<br/>e transferir para centro capaz de definir etiologia"])
  D4{"Subtipo com indicação específica<br/>de imunossupressão confirmado/sustentado?"}
  C5(["Sim: terapia etiológica/imunossupressora<br/>especializada além do suporte"])
  C6(["Não: não usar imunossupressão universal;<br/>continuar suporte e investigação"])
  D5{"Parada cardíaca?"}
  C7(["Sim: PCR pediátrica + considerar ECPR<br/>em cenário selecionado/centro apropriado"])

  R0 --> P1
  P1 --> D1
  D1 -->|"Não"| C1
  D1 -->|"Sim"| P2
  P2 --> P3
  P3 --> D2
  D2 -->|"Sim"| C2
  D2 -->|"Não"| P4
  P4 --> D5
  D5 -->|"Sim"| C7
  D5 -->|"Não"| D3
  D3 -->|"Sim"| C3
  D3 -->|"Não"| C4
  C3 --> D4
  C4 --> D4
  D4 -->|"Sim"| C5
  D4 -->|"Não"| C6

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7 conduta;
```

## Regra prática

Na criança em rápida deterioração, **CMR não vem antes da estabilização e a discussão de ECMO não deve esperar falência multiorgânica**. A etiologia é refinada em paralelo, com EMB precoce nos casos de alto risco em centro experiente.
