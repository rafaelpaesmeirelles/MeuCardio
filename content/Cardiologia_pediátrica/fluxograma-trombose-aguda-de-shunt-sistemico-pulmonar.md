---
title: "Fluxograma: trombose aguda de shunt sistêmico-pulmonar"
slug: fluxograma-trombose-aguda-de-shunt-sistemico-pulmonar
theme: "Cardiologia pediátrica"
kind: fluxograma
summary: "Árvore de emergência para criança com shunt sistêmico-pulmonar e dessaturação abrupta, priorizando confirmação rápida e reperfusão cirúrgica/percutânea."
review_status: revisado
source_refs: ["Gedicke M, Morgan G, Parry A, Martin R, Tulloh R. Heart Vessels. 2010;25(5):405-409. DOI: 10.1007/s00380-009-1219-1. PMID: 20676963.", "Moszura T, et al. Interact Cardiovasc Thorac Surg. 2010;10(5):727-731. DOI: 10.1510/icvts.2009.219741. PMID: 20139195.", "Sivakumar K, et al. Indian Heart J. 2001;53(6):743-748. PMID: 11838928."]
---

# Trombose aguda de shunt sistêmico-pulmonar

```mermaid
flowchart TD
  R0["Criança com shunt sistêmico-pulmonar<br/>+ dessaturação/cianose abrupta"]
  P1["Monitorização + O₂/suporte ventilatório<br/>+ acesso vascular + gasometria/lactato<br/>+ chamar cardiologia intervencionista e cirurgia"]
  D1{"Sinais de choque, acidose grave,<br/>rebaixamento ou PCR?"}
  P2["Suporte hemodinâmico imediato<br/>+ algoritmo de PCR pediátrica se sem pulso"]
  P3["Eco urgente: fluxo no shunt,<br/>função ventricular e anatomia"]
  D2{"Fluxo ausente/criticamente reduzido<br/>ou forte suspeita clínica de oclusão?"}
  C1(["Não: procurar causa alternativa<br/>de dessaturação aguda"])
  P4["Sim: preparar reperfusão urgente<br/>em centro congênito"]
  D3{"Hemodinâmica disponível e anatomia<br/>favorável para recanalização?"}
  C2(["Sim: cateterismo urgente<br/>± angioplastia/stent"])
  D4{"Cirurgia imediata disponível/<br/>preferível pela anatomia?"}
  C3(["Sim: revisão cirúrgica urgente"])
  C4(["Não/ponte: discutir trombólise<br/>individualizada; dose = VERIFICAÇÃO HUMANA NECESSÁRIA"])

  R0 --> P1
  P1 --> D1
  D1 -->|"Sim"| P2
  D1 -->|"Não"| P3
  P2 --> P3
  P3 --> D2
  D2 -->|"Não"| C1
  D2 -->|"Sim"| P4
  P4 --> D3
  D3 -->|"Sim"| C2
  D3 -->|"Não"| D4
  D4 -->|"Sim"| C3
  D4 -->|"Não"| C4

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4 conduta;
```

## Regra prática

Em criança com shunt sistêmico-pulmonar, **dessaturação abrupta é obstrução do shunt até prova em contrário** quando o contexto clínico é compatível. O objetivo é ganhar tempo apenas o suficiente para estabilizar e restaurar fluxo — não substituir reperfusão por suporte inespecífico.