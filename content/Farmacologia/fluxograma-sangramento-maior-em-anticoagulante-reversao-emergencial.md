---
title: "Fluxograma: sangramento maior em paciente anticoagulado — reversão emergencial"
slug: fluxograma-sangramento-maior-em-anticoagulante-reversao-emergencial
theme: "Farmacologia"
kind: fluxograma
fonte_producao: chatgpt
summary: "Árvore de decisão para sangramento maior ou com risco de vida em paciente em uso de anticoagulante oral ou parenteral, separando sítio/gravidade crítica de sangramento não crítico e escolhendo o agente de reversão específico por classe de anticoagulante."
review_status: revisado
review_note: "Verificado em 26/08/2026: PMIDs conferidos via PubMed E-utilities (esearch/esummary) — título, revista, volume e páginas batendo integralmente com o texto citado; nenhum PMID ou dado numérico foi inventado. Doses de idarucizumabe, andexanete alfa, CCP 4F e protamina cruzadas contra as fontes primárias citadas, sem divergência encontrada."
source_refs:
  - "Tomaselli GF, Mahaffey KW, Cuker A, et al. 2020 ACC Expert Consensus Decision Pathway on Management of Bleeding in Patients on Oral Anticoagulants. J Am Coll Cardiol. 2020;76(5):594-622. PMID 32680646."
  - "Pollack CV Jr, Reilly PA, van Ryn J, et al. Idarucizumab for Dabigatran Reversal — Full Cohort Analysis. N Engl J Med. 2017;377(5):431-441. PMID 28693366."
  - "Connolly SJ, Crowther M, Eikelboom JW, et al. Full Study Report of Andexanet Alfa for Bleeding Associated with Factor Xa Inhibitors. N Engl J Med. 2019;380(14):1326-1335. PMID 30730782."
  - "Milling TJ Jr, Middeldorp S, Xu L, et al. Final Study Report of Andexanet Alfa for Major Bleeding With Factor Xa Inhibitors. Circulation. 2023;147(13):1026-1038. PMID 36802876."
---

# Fluxograma: sangramento maior em paciente anticoagulado — reversão emergencial

Sangramento maior num paciente anticoagulado não é uma única decisão — é duas: primeiro, se a gravidade e o sítio justificam reversão farmacológica específica (não todo sangramento maior precisa disso); depois, qual agente reverte qual classe de anticoagulante, porque idarucizumabe não faz nada por um inibidor do fator Xa e protamina não neutraliza um DOAC. O consenso da ACC de 2020 é explícito: reversão específica é reservada para sangramento fatal iminente ou em sítio crítico, e as medidas gerais de suporte (compressão, hemostasia local, transfusão) continuam sendo a base do tratamento em toda a árvore, não apenas no ramo sem reversão.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Sangramento maior (queda de Hb ≥2 g/dL, necessidade transfusional<br/>ou sítio crítico) em paciente em uso de anticoagulante"]
  X1["Medidas gerais imediatas: suspender o anticoagulante, ABC,<br/>dois acessos venosos calibrosos, hemograma/coagulograma/função renal,<br/>compressão mecânica ou tamponamento quando possível,<br/>acionar cirurgia/hemodinâmica/UTI conforme o sítio"]
  D1{"Sangramento é fatal iminente ou em sítio crítico<br/>(intracraniano, intraespinhal, pericárdico, retroperitoneal)?"}
  C1(["Suporte hemodinâmico e hemostático padrão (transfusão se indicado,<br/>ácido tranexâmico tópico/local quando aplicável); reservar reversão<br/>específica para instabilização ou falha das medidas gerais"])
  D2{"Qual classe de anticoagulante está em uso?"}
  C2(["Concentrado de complexo protrombínico 4 fatores IV<br/>(dose por peso e INR, conforme bula) + vitamina K 10 mg IV lento;<br/>reverificar INR em 30 minutos"])
  C3(["Idarucizumabe 5 g IV (duas infusões de 2,5 g em até 15 min<br/>de intervalo); repetir 5 g se sangramento persistir ou recorrer"])
  D3{"Andexanete alfa disponível no serviço?"}
  C4(["Andexanete alfa em bolus seguido de infusão contínua,<br/>dose conforme fármaco, dose usada e tempo desde a última tomada"])
  C5(["Concentrado de complexo protrombínico 4 fatores IV, 50 UI/kg,<br/>como alternativa quando andexanete não está disponível"])
  C6(["Protamina IV, 1 mg por 100 U de heparina recebida<br/>nas últimas 2-3h (máximo 50 mg); monitorar TTPA seriado"])
  C7(["Protamina IV: 1 mg por 1 mg de enoxaparina se <8h da última<br/>dose (dose reduzida se >8h); neutralização é apenas parcial"])

  R0 --> X1
  X1 --> D1
  D1 -->|"Não — sangramento maior mas não crítico"| C1
  D1 -->|"Sim — crítico ou risco de morte iminente"| D2
  D2 -->|"Antagonista da vitamina K (varfarina)"| C2
  D2 -->|"Inibidor direto da trombina (dabigatrana)"| C3
  D2 -->|"Inibidor do fator Xa (apixabana, rivaroxabana, edoxabana)"| D3
  D2 -->|"Heparina não fracionada"| C6
  D2 -->|"Heparina de baixo peso molecular (enoxaparina)"| C7
  D3 -->|"Sim"| C4
  D3 -->|"Não"| C5

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7 conduta;
```

## O que a árvore não mostra

- **Andexanete alfa tem disponibilidade limitada no Brasil** — o ramo que usa CCP 4F como alternativa ao inibidor do fator Xa é, na prática, o caminho mais usado na maioria dos serviços, não uma exceção rara.
- **Idarucizumabe não é ajustado por função renal na dose de reversão**, mas a dabigatrana acumula em disfunção renal — redosagem pode ser necessária se o sangramento recorrer, especialmente em ClCr baixo.
- **Carvão ativado** pode ser considerado se a ingestão do anticoagulante oral foi recente (dentro de 2-4h) e a via aérea está protegida — não é mostrado na árvore por ser medida complementar, não de reversão.
- **Reversão farmacológica não substitui hemostasia mecânica ou cirúrgica** quando o sítio permite (endoscopia, embolização, cirurgia) — a árvore trata da farmacologia, não do controle definitivo do foco de sangramento.
- **Neutralização da HBPM por protamina é sempre parcial** (reverte cerca de 60% da atividade anti-Xa) — se o sangramento persistir apesar da protamina, considerar CCP 4F como medida adjuvante, mesmo sem evidência robusta específica para esse cenário.
- **A decisão de reintroduzir o anticoagulante após o sangramento** é individualizada (risco tromboembólico vs. risco de resangramento) e está fora do escopo desta árvore, que cobre apenas a fase aguda de reversão.