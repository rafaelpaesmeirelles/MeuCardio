---
title: "Fluxograma: TEP agudo associado ao câncer e trombocitopenia"
slug: fluxograma-tromboembolismo-pulmonar-agudo-associado-ao-cancer-e-trombocitopenia
theme: "Cardio-oncologia"
kind: fluxograma
summary: "Árvore de decisão para TEP no paciente oncológico, separando instabilidade, sangramento ativo e risco de progressão do trombo antes de ajustar a anticoagulação à contagem de plaquetas."
review_status: revisado
review_note: "Revisado em 26/08/2026 contra as diretrizes ESC de TEP 2019 (PMID 31504429) e cardio-oncologia 2022 (PMID 36017568), além do guidance oficial da SSC/ISTH para trombose associada ao câncer com trombocitopenia (PMID 29737593). O ramo de plaquetas <50.000/µL foi corrigido para separar evento agudo de alto risco de progressão, que pode exigir LMWH/HNF terapêutica com transfusão para manter 40.000-50.000/µL, de evento de menor risco, no qual se sugere meia dose/dose profilática entre 25.000-50.000/µL e pausa abaixo de 25.000/µL. Essas estratégias são guidance de consenso, não comparação randomizada. Pendente revisão médica independente antes de uso assistencial."
source_refs: ["Konstantinides SV, Meyer G, Becattini C, et al. 2019 ESC Guidelines for the diagnosis and management of acute pulmonary embolism. Eur Heart J. 2020;41(4):543-603. DOI: 10.1093/eurheartj/ehz405. PMID: 31504429 — estratificação do TEP de alto risco e opções de reperfusão.", "Lyon AR, López-Fernández T, Couch LS, et al. 2022 ESC Guidelines on cardio-oncology. Eur Heart J. 2022;43(41):4229-4361. DOI: 10.1093/eurheartj/ehac244. PMID: 36017568 — seleção de anticoagulante, risco hemorrágico, interações e duração do tratamento do TEV associado ao câncer.", "Samuelson Bannow BT, Lee A, Khorana AA, et al. Management of cancer-associated thrombosis in patients with thrombocytopenia: guidance from the SSC of the ISTH. J Thromb Haemost. 2018;16(6):1246-1249. DOI: 10.1111/jth.14015. PMID: 29737593 — dose de anticoagulação, suporte transfusional e limiares de 50.000, 40.000-50.000 e 25.000/µL conforme risco de progressão."]
---

# TEP agudo associado ao câncer

```mermaid
flowchart TD
  R0["Paciente com câncer + TEP confirmado/suspeito"]
  D1{"Choque/hipotensão persistente?"}
  P1["TEP de alto risco: acionar equipe de TEP e<br/>avaliar reperfusão imediata; trombocitopenia,<br/>lesão intracraniana e sangramento modificam<br/>a escolha entre trombólise, cateter e cirurgia"]
  P2["Estável: iniciar estratégia anticoagulante<br/>se não houver contraindicação absoluta"]
  D2{"Há sangramento maior ativo/recente<br/>ou outra contraindicação absoluta<br/>à anticoagulação?"}
  P3["Controlar o foco e decidir em equipe<br/>multidisciplinar quando reiniciar;<br/>filtro de veia cava removível só em caso<br/>selecionado de contraindicação absoluta"]
  D3{"Plaquetas ≥50.000/µL?"}
  D4{"Tumor GI/GU luminal não operado, CrCl <15,<br/>absorção ruim ou interação importante?"}
  P4["Favorecer LMWH/estratégia alternativa<br/>compatível com função renal e interações"]
  P5["DOAC ou LMWH conforme perfil,<br/>função renal, interações e preferência"]
  D5{"Evento agudo com alto risco de progressão:<br/>TEP sintomático segmentar ou mais proximal,<br/>TVP proximal associada, ou trombose<br/>recorrente/progressiva?"}
  P6["Considerar LMWH ou HNF em dose terapêutica<br/>com transfusão de plaquetas para manter<br/>40.000-50.000/µL; frequentemente requer<br/>internação e monitorização estreita"]
  D6{"Plaquetas entre<br/>25.000 e 49.999/µL?"}
  P7["Evento de menor risco: considerar LMWH<br/>em 50% da dose terapêutica ou em dose<br/>profilática, com reavaliação frequente"]
  P8["Plaquetas <25.000/µL: sugerida pausa<br/>temporária da anticoagulação; controlar<br/>sangramento/causa e reavaliar diariamente"]
  C1(["Retomar/manter dose terapêutica quando<br/>plaquetas >50.000/µL sem suporte e não houver<br/>outra contraindicação; tratar por no mínimo<br/>6 meses e prolongar enquanto o câncer estiver ativo"])

  R0 --> D1
  D1 -->|"Sim"| P1
  D1 -->|"Não"| P2
  P1 --> D2
  P2 --> D2
  D2 -->|"Sim"| P3
  D2 -->|"Não"| D3
  D3 -->|"Sim"| D4
  D3 -->|"Não"| D5
  D4 -->|"Sim"| P4
  D4 -->|"Não"| P5
  D5 -->|"Sim"| P6
  D5 -->|"Não"| D6
  D6 -->|"Sim"| P7
  D6 -->|"Não — abaixo de 25.000/µL"| P8
  P4 --> C1
  P5 --> C1
  P6 --> C1
  P7 --> C1
  P8 --> C1

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class P3,P4,P5,P6,P7,P8,C1 conduta;
```

## Regra prática

**Instabilidade hemodinâmica define a urgência da reperfusão; abaixo de 50.000
plaquetas/µL, o risco de progressão do trombo define se a prioridade é sustentar
anticoagulação terapêutica com transfusão ou reduzir/pausar temporariamente.**

O corte de 50.000/µL não significa que todo paciente abaixo dele recebe a mesma
conduta. A SSC/ISTH considera de maior risco o TEP sintomático segmentar ou mais
proximal, a TVP proximal associada e a trombose recorrente/progressiva. TEP
subsegmentar incidental isolado e trombose relacionada a cateter integram o grupo
de menor risco, desde que não haja outro fator de progressão.

## Limites da evidência

Os ajustes de dose e o suporte transfusional em trombocitopenia grave derivam de
guidance da SSC/ISTH apoiado por evidência observacional e consenso especializado;
não foram comparados entre si em ensaio randomizado. A escolha entre LMWH e HNF,
a meta transfusional e o local de cuidado exigem hematologia/oncologia e equipe de
TEP, sobretudo quando trombocitopenia, sangramento e instabilidade coexistem.
