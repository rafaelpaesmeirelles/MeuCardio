---
title: "Fluxograma: sangramento maior em paciente anticoagulado — reversão emergencial"
slug: fluxograma-sangramento-maior-em-anticoagulante-reversao-emergencial
theme: "Farmacologia"
kind: fluxograma
fonte_producao: chatgpt
summary: "Árvore de decisão para sangramento maior ou com risco de vida em paciente em uso de anticoagulante oral ou parenteral, separando sítio/gravidade crítica de sangramento não crítico e escolhendo o agente de reversão específico por classe de anticoagulante."
review_status: revisado
review_note: "Auditoria científica em 26/08/2026: PMIDs e doses conferidos. Corrigidos a definição de sangramento maior, a indicação de reversão também quando o sangramento maior não responde à abordagem inicial e os critérios para redose de idarucizumabe; retirada estratégia não sustentada após protamina na HBPM. Mantida pendência de revisão médica antes da publicação clínica."
source_refs:
  - "Tomaselli GF, Mahaffey KW, Cuker A, et al. 2020 ACC Expert Consensus Decision Pathway on Management of Bleeding in Patients on Oral Anticoagulants. J Am Coll Cardiol. 2020;76(5):594-622. PMID 32680646."
  - "Pollack CV Jr, Reilly PA, van Ryn J, et al. Idarucizumab for Dabigatran Reversal — Full Cohort Analysis. N Engl J Med. 2017;377(5):431-441. PMID 28693366."
  - "Connolly SJ, Crowther M, Eikelboom JW, et al. Full Study Report of Andexanet Alfa for Bleeding Associated with Factor Xa Inhibitors. N Engl J Med. 2019;380(14):1326-1335. PMID 30730782."
  - "Milling TJ Jr, Middeldorp S, Xu L, et al. Final Study Report of Andexanet Alfa for Major Bleeding With Factor Xa Inhibitors. Circulation. 2023;147(13):1026-1038. PMID 36802876."
---

# Fluxograma: sangramento maior em paciente anticoagulado — reversão emergencial

Sangramento maior num paciente anticoagulado exige controle imediato da fonte e decisão sobre reversão. O consenso ACC 2020 considera agente de reversão no sangramento com risco de vida e também no sangramento maior que não se resolve com a abordagem inicial; ele não deve ser usado na maioria dos sangramentos não maiores. A escolha depende do anticoagulante e da presença de efeito farmacológico clinicamente relevante.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Sangramento maior: sítio crítico, instabilidade hemodinâmica,<br/>queda de Hb ≥2 g/dL ou transfusão de ≥2 concentrados<br/>em paciente em uso de anticoagulante"]
  X1["Medidas gerais imediatas: suspender anticoagulante, ABC,<br/>acessos venosos, hemograma/coagulograma/função renal/tipagem;<br/>obter tempo de trombina ou anti-Xa específico se disponível,<br/>sem atrasar controle da fonte ou reversão de emergência"]
  D1{"Sangramento tem risco de vida/sítio crítico OU<br/>permanece maior apesar das medidas iniciais?"}
  C1(["Suporte hemodinâmico e hemostático padrão (transfusão se indicado,<br/>ácido tranexâmico tópico/local quando aplicável); reservar reversão<br/>específica para instabilização ou falha das medidas gerais"])
  D2{"Qual classe de anticoagulante está em uso?"}
  C2(["Concentrado de complexo protrombínico 4 fatores IV<br/>(dose por peso e INR, conforme bula) + vitamina K 10 mg IV lento;<br/>reverificar INR em 30 minutos"])
  C3(["Idarucizumabe 5 g IV (duas doses de 2,5 g consecutivas);<br/>considerar nova dose apenas se ressurgir sangramento relevante<br/>com testes de coagulação novamente prolongados"])
  D3{"Andexanete alfa disponível no serviço?"}
  C4(["Andexanete alfa em bolus seguido de infusão contínua,<br/>dose conforme fármaco, dose usada e tempo desde a última tomada"])
  C5(["Concentrado de complexo protrombínico 4 fatores IV, 50 UI/kg,<br/>como alternativa quando andexanete não está disponível"])
  C6(["Protamina IV, 1 mg por 100 U de heparina recebida<br/>nas últimas 2-3h (máximo 50 mg); monitorar TTPA seriado"])
  C7(["Protamina IV: 1 mg por 1 mg de enoxaparina se menos de 8h;<br/>0,5 mg por 1 mg se 8–12h; após 12h pode não ser necessária,<br/>conforme função renal; neutralização é parcial"])

  R0 --> X1
  X1 --> D1
  D1 -->|"Não — respondeu à abordagem inicial"| C1
  D1 -->|"Sim"| D2
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
- **Neutralização da HBPM por protamina é parcial** (aproximadamente 60% da atividade anti-Xa). Persistência exige controle da fonte, suporte e consulta hematológica/toxicológica; não há antídoto específico que complete a reversão.
- **A decisão de reintroduzir o anticoagulante após o sangramento** é individualizada (risco tromboembólico vs. risco de resangramento) e está fora do escopo desta árvore, que cobre apenas a fase aguda de reversão.
