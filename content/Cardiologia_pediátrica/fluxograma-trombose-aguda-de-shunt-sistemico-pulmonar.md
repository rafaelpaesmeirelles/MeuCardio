---
title: "Fluxograma: trombose aguda de shunt sistêmico-pulmonar"
slug: fluxograma-trombose-aguda-de-shunt-sistemico-pulmonar
theme: "Cardiologia pediátrica"
kind: fluxograma
summary: "Árvore de emergência para criança com shunt sistêmico-pulmonar e dessaturação abrupta, priorizando confirmação rápida e reperfusão cirúrgica/percutânea."
review_status: pendente_revisao
source_refs: ["Gedicke M, Morgan G, Parry A, Martin R, Tulloh R. Heart Vessels. 2010;25(5):405-409. DOI: 10.1007/s00380-009-1219-1. PMID: 20676963.", "Moszura T, et al. Interact Cardiovasc Thorac Surg. 2010;10(5):727-731. DOI: 10.1510/icvts.2009.219741. PMID: 20139195.", "Sivakumar K, et al. Indian Heart J. 2001;53(6):743-748. PMID: 11838928.", "Monagle P, Chan AKC, Goldenberg NA, et al. Antithrombotic Therapy in Neonates and Children: Antithrombotic Therapy and Prevention of Thrombosis, 9th ed: American College of Chest Physicians Evidence-Based Clinical Practice Guidelines. Chest. 2012;141(2 Suppl):e737S-e801S. PMID: 22315277 — **a diretriz NÃO define tratamento específico da oclusão aguda/trombose estabelecida de shunt de Blalock-Taussig modificado (MBTS)**. O que ela cobre, especificamente para MBTS, é tromboprofilaxia: heparina não fracionada intraoperatória (Grau 2C) e, no pós-operatório, aspirina ou nenhuma terapia antitrombótica versus HBPM prolongada ou antagonista de vitamina K (Grau 2C) — recomendação fraca, de evidência de baixa qualidade, mas específica desse cenário. A afirmação de que a decisão terapêutica na oclusão aguda deve ser individualizada é um princípio geral do documento sobre trombose pediátrica, não uma recomendação Grau/nível específica de trombólise em MBTS ocluído. Nenhum esquema de dose de trombólise foi extraído desta fonte."]
review_note: "Lote 1B-correção (2026-08-24): corrige a citação do CHEST 2012 — a diretriz não define tratamento da oclusão aguda de MBTS, só tromboprofilaxia (heparina intraoperatória, aspirina ou nenhuma terapia no pós-operatório, ambas Grau 2C); essas duas recomendações de tromboprofilaxia foram separadas das orientações gerais sobre trombólise pediátrica (que não são específicas de MBTS). O nó de conduta continua sem dose de alteplase/heparina/HBPM, por não existir esquema trombolítico único validado para este cenário. Pendente de validação médica final."
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
  C4(["Não/ponte: anticoagulação, trombólise<br/>dirigida/sistêmica conforme protocolo<br/>institucional — sem esquema único validado"])

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

**Tromboprofilaxia (prevenção) não é o mesmo problema que trombólise (tratamento da oclusão já instalada).** O CHEST 2012 (Monagle et al., PMID 22315277) tem recomendação específica só para a primeira: heparina não fracionada intraoperatória e, no pós-operatório, aspirina ou nenhuma terapia antitrombótica (ambas Grau 2C, evidência fraca). Para o cenário deste fluxograma — shunt já ocluído, em emergência — a diretriz não define esquema de trombólise; a decisão de reperfusão (cirúrgica, percutânea ou farmacológica) é institucional, não um protocolo publicado único.
