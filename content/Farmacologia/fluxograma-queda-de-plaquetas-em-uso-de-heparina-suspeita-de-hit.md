---
title: "Fluxograma: Queda de plaquetas em uso de heparina/enoxaparina — suspeita de HIT"
slug: fluxograma-queda-de-plaquetas-em-uso-de-heparina-suspeita-de-hit
theme: "Farmacologia"
kind: fluxograma
summary: "Árvore de conduta imediata para queda de plaquetas ≥50% e/ou trombose nova em paciente usando heparina ou enoxaparina: cálculo do 4Ts, suspensão de toda fonte de heparina e escolha do anticoagulante não heparínico diante de probabilidade intermediária ou alta de HIT."
review_status: revisado
source_refs: ["Cuker A, Arepally GM, Chong BH, Cines DB, Greinacher A, Gruel Y, et al. American Society of Hematology 2018 guidelines for management of venous thromboembolism: heparin-induced thrombocytopenia. Blood Adv. 2018;2(22):3360-3392. DOI: 10.1182/bloodadvances.2018024489. PMID: 30482768. PMCID: PMC6258919 — texto integral lido no PMC, incluindo a Tabela 1 (as 5 fases da HIT), a tabela de dosagem dos anticoagulantes não heparínicos e a tabela de sensibilidade/especificidade do escore 4Ts", "Lo GK, Juhl D, Warkentin TE, Sigouin CS, Eichler P, Greinacher A. Evaluation of pretest clinical score (4 T's) for the diagnosis of heparin-induced thrombocytopenia in two clinical settings. J Thromb Haemost. 2006;4(4):759-765. DOI: 10.1111/j.1538-7836.2006.01787.x. PMID: 16634744 — validação do escore 4Ts em 2 centros (Hamilton, Canadá, n=100; Greifswald, Alemanha, n=236), abstract lido por E-utilities", "Capuano I, Riccio E, Buonanno P, Tufano A, Pisani A. Heparin-induced thrombocytopenia: a challenging diagnosis in haemodialysis — state of art and review of the literature. Clin Kidney J. 2026;19(4):sfag062. DOI: 10.1093/ckj/sfag062. PMID: 42111239. PMCID: PMC13153468 — texto integral em acesso aberto lido no PMC, Tabela 1, para os critérios de pontuação linha a linha do escore 4Ts", "Thein KZ, Elsaim SA, Ma MQ, Rojas Hernandez CM, Elsayem A. Heparin-Induced Thrombocytopenia at the Emergency Department Due to Intermittent Heparin Flush in a Patient Undergoing Stem Cell Transplant. Cureus. 2022;14(11):e31798. DOI: 10.7759/cureus.31798. PMID: 36569714 — relato de caso lido no PMC (PMC9780017), usado como evidência de que heparina em dose de flush de cateter, isoladamente, é exposição suficiente para desencadear HIT — sustenta a orientação de suspender toda fonte de heparina, não só a infusão terapêutica, diante de suspeita (a diretriz ASH 2018 recomenda 'descontinuar heparina' sem detalhar fontes menores; este relato de caso é a fonte específica para o detalhe do flush)"]
---

# Fluxograma: Queda de plaquetas em uso de heparina/enoxaparina — suspeita de HIT

A trombocitopenia induzida por heparina (HIT) é protrombótica, não hemorrágica: o paciente que cai a plaqueta em vigência de heparina ou enoxaparina não está sangrando mais, está coagulando mais. O risco diário de trombose, amputação ou morte sem tratamento (5% a 10%, segundo a diretriz da ASH) é por isso que a decisão de suspender heparina e trocar o anticoagulante costuma ser tomada **antes** da confirmação laboratorial, com base só na probabilidade clínica pelo escore 4Ts.

## Escore 4Ts: probabilidade pré-teste

| Critério | 0 pontos | 1 ponto | 2 pontos |
|---|---|---|---|
| **T**rombocitopenia | Queda <30% ou nadir <10 × 10⁹/L | Queda 30-50% ou nadir 10-19 × 10⁹/L | Queda >50% **e** nadir ≥20 × 10⁹/L |
| **T**iming (momento da queda) | ≤4 dias, sem exposição recente à heparina | Provavelmente 5-10 dias mas não definido, início após o dia 10, ou ≤1 dia com exposição prévia à heparina 30-100 dias antes | 5-10 dias, ou ≤1 dia com exposição prévia à heparina nos últimos 30 dias |
| **T**rombose ou outra sequela | Nenhuma | Trombose progressiva ou recorrente, trombose suspeita, ou lesão de pele eritematosa não necrosante | Trombose nova confirmada, necrose de pele, ou reação sistêmica aguda após bolus IV de heparina |
| oT**her** causas de plaquetopenia | Definida (outra causa clara) | Possível | Nenhuma outra causa aparente |

**Soma:** 0-3 pontos = baixa probabilidade (<5%); 4-5 pontos = intermediária (14%); ≥6 pontos = alta (64%).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Paciente em uso de heparina ou<br/>enoxaparina (SCA, angioplastia,<br/>cirurgia cardíaca) com queda de<br/>plaquetas ≥50% e/ou trombose nova"]
  P1["Calcular o escore 4Ts<br/>(ver tabela acima)"]
  D1{"Probabilidade pré-teste pelo 4Ts?"}
  C1(["Manter heparina.<br/>Não solicitar anti-PF4 nem iniciar<br/>tratamento empírico — investigar<br/>outra causa de plaquetopenia"])
  P2["Suspender IMEDIATAMENTE toda fonte<br/>de heparina — incluindo flush de<br/>cateter e heparina de circuito de<br/>diálise/ECMO — e solicitar anti-PF4<br/>(se positivo, teste funcional confirmatório)"]
  D2{"Qual o contexto clínico predominante?"}
  D3{"Bivalirudina disponível,<br/>com experiência institucional?"}
  C2(["Bivalirudina IV: sem bolus,<br/>0,15 mg/kg/h; ajustar por<br/>TTPA 1,5-2,5× o basal"])
  C3(["Argatroban IV: sem bolus,<br/>2 µg/kg/min (0,5-1,2 µg/kg/min se<br/>disfunção hepática, IC, anasarca ou<br/>pós-cirurgia cardíaca); ajustar por<br/>TTPA 1,5-3,0× o basal"])
  D4{"Disfunção hepática moderada<br/>a grave (Child-Pugh B ou C)?"}
  C4(["Bivalirudina IV: sem bolus,<br/>0,15 mg/kg/h (considerar redução se<br/>disfunção renal/hepática); ajustar<br/>por TTPA 1,5-2,5× o basal"])
  C5(["Argatroban IV: sem bolus,<br/>2 µg/kg/min; ajustar por<br/>TTPA 1,5-3,0× o basal"])
  C6(["Fondaparinux SC: <50kg 5mg 1×/dia;<br/>50-100kg 7,5mg 1×/dia; >100kg<br/>10mg 1×/dia — sem monitorização<br/>laboratorial"])

  R0 --> P1
  P1 --> D1
  D1 -->|"Baixa (0-3 pontos)"| C1
  D1 -->|"Intermediária (4-5) ou alta (≥6)"| P2
  P2 --> D2
  D2 -->|"Vai a angioplastia coronária (HIT aguda/subaguda A)"| D3
  D2 -->|"Criticamente enfermo, sangramento aumentado ou procedimento urgente possível"| D4
  D2 -->|"Estável, risco de sangramento médio, sem procedimento urgente previsto"| C6
  D3 -->|"Sim"| C2
  D3 -->|"Não"| C3
  D4 -->|"Sim"| C4
  D4 -->|"Não"| C5

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## Transfusão de plaquetas: nunca profilática

Ponto que contraria a intuição de "repor o que está baixo": em HIT (isolada ou com trombose) e risco hemorrágico médio, a diretriz da ASH **recomenda contra a transfusão profilática de plaquetas** — o problema não é a falta de plaqueta, é a ativação plaquetária, e transfundir pode, em tese, alimentar mais substrato para o processo protrombótico. Transfusão de plaquetas fica reservada para **sangramento ativo ou alto risco hemorrágico**, em qualquer um dos ramos acima.

## Depois da fase aguda: recuperação de plaqueta e transição

Em todos os ramos de tratamento, a anticoagulação não heparínica é mantida, no mínimo, **até a recuperação da contagem de plaquetas** (em geral ≥150 × 10⁹/L, o que marca a fase subaguda A). A partir daí, a diretriz sugere transicionar para via oral com **preferência por um DOAC em vez de antagonista de vitamina K (varfarina)** nessa fase. Na HIT isolada (sem trombose documentada), não há indicação de prolongar o tratamento por ≥3 meses de rotina, a menos que haja trombose persistente ou outra indicação.
