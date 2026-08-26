---
title: "Fluxograma: oclusão do apêndice atrial esquerdo (LAAO) versus anticoagulação prolongada em contraindicação relativa"
slug: fluxograma-laao-vs-anticoagulacao-contraindicacao-relativa
theme: "Fibrilação atrial"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Verificado por Claude em 26/08/2026: PMID/DOI conferidos via PubMed E-utilities (esearch/esummary/efetch) nesta sessão — PROTECT AF PMID 19683639, PREVAIL PMID 24998121, PRAGUE-17 (resultado primário) PMID 32586585 e (4 anos) PMID 34748929, Diretriz Brasileira de Fibrilação Atrial 2025 PMID 41294177, LAAOS III PMID 33999547 — todos com título/revista/ano batendo exatamente o abstract. A classe e o nível de recomendação (exclusão cirúrgica Classe I/B; oclusão percutânea Classe IIa/B, exigindo alto risco tromboembólico E contraindicação absoluta/falha do anticoagulante) foram reaproveitados do Quadro 12 da Diretriz Brasileira de FA 2025, já lido na íntegra e registrado nos documentos 'oclusao-do-apendice-atrial-esquerdo-protect-af-e-prevail.md' e 'diretriz-brasileira-de-fibrilacao-atrial-2025-sbc-sobrac.md' desta mesma pasta — não reextraído de memória. Confirmado por WebFetch que os resumos da ACC e da EP Europace sobre a ESC 2024/AF-CARE não trazem critérios/classe para oclusão percutânea de apêndice em contraindicação a anticoagulante (só citam fechamento cirúrgico associado à ablação híbrida) — por isso a diretriz brasileira, e não a ESC 2024, é a fonte da classe de recomendação usada nesta árvore, exatamente como já registrado nos documentos citados."
source_refs:
  - "Cintra FD, Pisani CF, Rezende AGS, Henz BD, Armaganijan LV, Pimentel M, Lopes RD, et al. Diretriz Brasileira de Fibrilação Atrial – 2025. Arq Bras Cardiol. 2025;122(9):e20250618. DOI: 10.36660/abc.20250618. PMID: 41294177 — Quadro 12, recomendações de oclusão do apêndice atrial esquerdo."
  - "Whitlock RP, Belley-Cote EP, Paparella D, Healey JS, Brady K, et al; LAAOS III Investigators. Left Atrial Appendage Occlusion during Cardiac Surgery to Prevent Stroke. N Engl J Med. 2021;384(22):2081-2091. DOI: 10.1056/NEJMoa2101897. PMID: 33999547."
  - "Holmes DR, Reddy VY, Turi ZG, et al; PROTECT AF Investigators. Percutaneous closure of the left atrial appendage versus warfarin therapy for prevention of stroke in patients with atrial fibrillation (PROTECT AF). Lancet. 2009;374(9689):534-542. DOI: 10.1016/S0140-6736(09)61343-X. PMID: 19683639."
  - "Holmes DR Jr, Kar S, Price MJ, et al. Prospective randomized evaluation of the Watchman left atrial appendage closure device in patients with atrial fibrillation versus long-term warfarin therapy (PREVAIL). J Am Coll Cardiol. 2014;64(1):1-12. DOI: 10.1016/j.jacc.2014.04.029. PMID: 24998121."
  - "Osmancik P, Herman D, Neuzil P, et al; PRAGUE-17 Trial Investigators. Left Atrial Appendage Closure Versus Direct Oral Anticoagulants in High-Risk Patients With Atrial Fibrillation. J Am Coll Cardiol. 2020;75(25):3122-3135. DOI: 10.1016/j.jacc.2020.04.067. PMID: 32586585."
  - "Osmancik P, Herman D, Neuzil P, et al; PRAGUE-17 Trial Investigators. 4-Year Outcomes After Left Atrial Appendage Closure Versus Nonwarfarin Oral Anticoagulation for Atrial Fibrillation. J Am Coll Cardiol. 2022;79(1):1-14. DOI: 10.1016/j.jacc.2021.10.023. PMID: 34748929."
  - "Derivado dos documentos já publicados no acervo 'Oclusão do Apêndice Atrial Esquerdo: PROTECT AF e PREVAIL' e 'Diretriz Brasileira de Fibrilação Atrial 2025 (SBC/SOBRAC)' (content/Fibrilação_atrial/), que já traziam o Quadro 12 lido na íntegra e a citação do LAAOS III."
---

# Fluxograma: oclusão do apêndice atrial esquerdo (LAAO) versus anticoagulação prolongada em contraindicação relativa

A diretriz ESC 2024 (AF-CARE) cita a oclusão do apêndice atrial esquerdo como alternativa em quem tem contraindicação à anticoagulação de longo prazo, mas os critérios de indicação e a classe de recomendação para o dispositivo percutâneo não têm fonte de acesso aberto localizada nesta biblioteca — o que a ESC 2024 detalha com classe/nível é só o fechamento **cirúrgico** associado à ablação híbrida. A lacuna prática é fechada pela **Diretriz Brasileira de Fibrilação Atrial 2025** (SOBRAC/SBC), referência de conduta nacional: ela exige **dois critérios simultâneos** para indicar o dispositivo percutâneo — alto risco tromboembólico **e** contraindicação absoluta ou falha real da terapia anticoagulante — e trata a exclusão cirúrgica do apêndice, quando há cirurgia cardíaca indicada por outro motivo, como recomendação de força bem maior (Classe I) que a via percutânea isolada (Classe IIa). Este fluxograma segue essa lógica de dois critérios, começando pela pergunta que resolve a maior parte dos casos sem entrar em debate sobre risco hemorrágico: o paciente já vai para cirurgia cardíaca por outro motivo?

## Árvore de decisão

```mermaid
flowchart TD
  R0["Paciente com FA e indicação de anticoagulação oral para prevenção de AVC (CHA2DS2-VA ≥2, ou ≥1 em decisão compartilhada)"] --> D1{"Paciente terá cirurgia cardíaca indicada por outro motivo (ex.: troca valvar, revascularização)?"}

  D1 -->|"Sim"| C1(["Exclusão cirúrgica do apêndice atrial esquerdo associada à anticoagulação oral perio/pós-operatória — Classe I, Nível B (Diretriz Brasileira de FA 2025).<br/>LAAOS III: menos AVC/embolia sistêmica com oclusão associada à anticoagulação vs. anticoagulação isolada (N Engl J Med 2021)"])

  D1 -->|"Não"| D2{"Há sangramento maior/clinicamente relevante sob anticoagulante, alto risco hemorrágico documentado sem fator reversível, ou falha/intolerância confirmada a mais de uma classe de anticoagulante oral?"}

  D2 -->|"Não, sem contraindicação relativa nem falha"| C2(["Manter anticoagulação oral crônica — DOAC como preferência sobre varfarina (salvo valvopatia reumática moderada/grave ou prótese valvar mecânica).<br/>Não há indicação de oclusão do apêndice neste momento"])

  D2 -->|"Sim"| D3{"Já foram esgotadas as medidas de otimização (trocar classe de DOAC, ajustar dose pelos critérios de redução validados, tratar a causa do sangramento, revisar interação medicamentosa)?"}

  D3 -->|"Não"| C3(["Otimizar a anticoagulação primeiro — trocar classe/dose de DOAC, tratar a causa do sangramento, revisar interação medicamentosa.<br/>Reavaliar a indicação de oclusão do apêndice se a intolerância/o risco persistir depois da otimização"])

  D3 -->|"Sim, otimização já esgotada"| D4{"Persiste contraindicação absoluta ou falha real do anticoagulante, COM risco tromboembólico que ainda justifica proteção antitrombótica (CHA2DS2-VA elevado)?"}

  D4 -->|"Não — risco tromboembólico baixo na reavaliação"| C4(["Não indicar oclusão do apêndice atrial esquerdo.<br/>Seguimento clínico com reavaliação periódica do risco tromboembólico e hemorrágico"])

  D4 -->|"Sim — os dois critérios da diretriz brasileira presentes: alto risco tromboembólico E contraindicação absoluta/falha"| D5{"ETE ou TC cardíaca confirmam ausência de trombo no apêndice atrial esquerdo e anatomia compatível com o dispositivo de oclusão percutânea disponível?"}

  D5 -->|"Não — trombo presente ou anatomia desfavorável"| C5(["Contraindicação técnica à oclusão percutânea no momento.<br/>Se houver trombo: anticoagular sob o regime mais seguro tolerado e repetir a imagem antes de reconsiderar.<br/>Se anatomia desfavorável: avaliar dispositivo alternativo ou via cirúrgica de exclusão do apêndice"])

  D5 -->|"Sim — trombo excluído e anatomia favorável"| D6{"Paciente tolera algum grau de antitrombótico no período periprocedimento, mesmo sendo intolerante à anticoagulação crônica?"}

  D6 -->|"Sim, tolera curso transitório"| C6(["Oclusão percutânea do apêndice atrial esquerdo (Watchman/Amulet) — Classe IIa, Nível B (Diretriz Brasileira de FA 2025).<br/>Anticoagulação periprocedimento transitória conforme protocolo do dispositivo, até a endotelização, com ETE de controle antes de suspender.<br/>Não inferior a DOAC no desfecho composto no PRAGUE-17 (sHR 0,84 aos 20 meses; sHR 0,81 aos 4 anos) e a varfarina no PROTECT AF/PREVAIL"])

  D6 -->|"Não — contraindicação mesmo a curso transitório"| C7(["Oclusão percutânea do apêndice atrial esquerdo com estratégia antitrombótica alternativa pós-procedimento (antiagregação isolada ou dupla, conforme risco hemorrágico, em decisão compartilhada).<br/>ETE seriada para excluir trombo relacionado ao dispositivo antes de reduzir a proteção antitrombótica"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7 conduta;
```

## O que a árvore não mostra

**A diretriz brasileira exige os dois critérios juntos para a via percutânea, não um ou outro isoladamente.** Alto risco tromboembólico sem contraindicação/falha do anticoagulante não indica oclusão — indica manter anticoagulação (ramo `C2`). Contraindicação ao anticoagulante sem risco tromboembólico relevante também não indica oclusão — indica só seguimento (ramo `C4`). É a combinação dos dois que sustenta a Classe IIa, Nível B.

**Exclusão cirúrgica (Classe I) e oclusão percutânea (Classe IIa) não são a mesma força de recomendação.** Quando há cirurgia cardíaca indicada por outro motivo, a diretriz brasileira trata a exclusão do apêndice como recomendação bem mais forte que a via percutânea isolada — sustentada pelo LAAOS III (4.770 pacientes, redução de AVC/embolia sistêmica com a oclusão associada à anticoagulação vs. anticoagulação isolada). Fora do contexto cirúrgico, a via percutânea segue os critérios acima.

**PROTECT AF e PREVAIL não são resultados idênticos, e a árvore não repete essa distinção no momento da conduta.** O PROTECT AF (2009) estabeleceu não inferioridade para o desfecho composto amplo, mas com sinal de segurança periprocedimento real (eventos primários de segurança mais frequentes com o dispositivo: 7,4 vs. 4,4 por 100 pacientes-ano). O PREVAIL (2014), desenhado para corrigir esse ponto, melhorou a segurança de forma expressiva, mas **não** confirmou não inferioridade no desfecho composto amplo — só no desfecho mais restrito de AVC/embolismo após 7 dias do procedimento.

**PRAGUE-17 comparou o dispositivo com DOAC, não com varfarina**, em população de alto risco (CHA2DS2-VASc médio 4,7; HAS-BLED médio 3,1) com história de sangramento significativo ou de evento cardioembólico sob anticoagulante. O desfecho composto (AVC/AIT, embolia sistêmica, morte cardiovascular, sangramento maior/clinicamente relevante, complicação do procedimento) foi não inferior aos 20 meses (sHR 0,84; IC95% 0,53-1,31; p de não inferioridade = 0,004) e permaneceu não inferior aos 4 anos (sHR 0,81; IC95% 0,56-1,18), com redução significativa de sangramento não relacionado ao procedimento no seguimento longo (sHR 0,55; IC95% 0,31-0,97; p=0,039).

**A "contraindicação absoluta ou falha da terapia anticoagulante" não tem lista fechada e universal na diretriz brasileira** — a árvore ilustra os cenários mais citados na prática (sangramento maior recorrente, alto risco hemorrágico sem causa reversível, intolerância confirmada a mais de uma classe), mas a decisão final é clínica e individualizada, tomada em conjunto com o paciente.

**Regime antitrombótico pós-procedimento na vida real diverge do regime aprovado em bula.** A própria diretriz brasileira registra que só cerca de 12% dos pacientes recebem o regime pós-implante aprovado pela FDA na prática clínica — a maioria usa AVK ou DOAC isolados durante a endotelização (30-90 dias), com taxas relatadas de trombose de dispositivo em torno de 3,8% em metanálise de mais de 10.000 pacientes, risco maior com hipercoagulabilidade, efusão pericárdica, disfunção renal, profundidade de implante maior que 10 mm e FA não paroxística — fatores que a árvore não desenvolve, por serem de manejo pós-procedimento e não de indicação inicial.
