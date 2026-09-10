---
slug: fluxograma-timing-encaminhamento-ambulatorial-hipertensao-resistente
title: 'Fluxograma: timing de encaminhamento ambulatorial na hipertensão resistente'
kind: fluxograma
theme: Hipertensão
summary: 'Encaminhamento na hipertensão resistente: excluir emergência, pseudorresistência e tratamento insuficiente;
  a resistência verdadeira confirmada exige avaliação em centro especializado, mantendo o cuidado local enquanto
  o encaminhamento é organizado.'
tags: []
source_refs:
- 'McEvoy JW, McCarthy CP, Bruno RM, et al. 2024 ESC Guidelines for the management of elevated blood pressure and
  hypertension. Eur Heart J. 2024;45(38):3912-4018. DOI: 10.1093/eurheartj/ehae178. PMID: 39210715'
- 'Brandão AA, Rodrigues CIS, Bortolotto LA, et al. Diretriz Brasileira de Hipertensão Arterial – 2025. Arq Bras
  Cardiol. 2025;122(9):e20250624. DOI: 10.36660/abc.20250624. PMID: 41294179'
- 'Carey RM, Calhoun DA, Bakris GL, et al. Resistant Hypertension: Detection, Evaluation, and Management. Hypertension.
  2018;72(5):e53-e90. PMID: 30354828'
- 'Lewis P, George J, Kapil V, et al. Adult hypertension referral pathway and therapeutic management. J Hum Hypertens.
  2024;38(1):3-7. PMID: 38196000'
- 'Faconti L, et al. Investigation and management of resistant hypertension: BIHS position statement. J Hum Hypertens.
  2024. PMID: 39653728'
evidence_level: null
source_tier: A
review_status: revisado
gaps: []
published: false
---

# Fluxograma: timing de encaminhamento ambulatorial na hipertensão resistente

Prosa: [timing-de-encaminhamento-ambulatorial-na-hipertensao-resistente](/biblioteca/timing-de-encaminhamento-ambulatorial-na-hipertensao-resistente) · [ponte-ambulatorial-enquanto-espera-centro-has-na-resistente](/biblioteca/ponte-ambulatorial-enquanto-espera-centro-has-na-resistente).

```mermaid
flowchart TD
  R0["Consulta com suspeita/rótulo de HAS resistente"] --> D0{"Lesão aguda de órgão-alvo?"}
  D0 -->|"Sim/dúvida"| C0(["PS / emergência AGORA<br/>Ver fluxograma-emergencia-hipertensiva"])

  D0 -->|"Não"| OB{"Gestação/puerpério<br/>PAS >=160 OU PAD >=110 confirmada prontamente?"}
  OB -->|"Sim"| COB(["Via obstétrica/hospitalar urgente<br/>Ver fluxo de eclâmpsia/HTA grave"])
  OB -->|"Não"| OB2{"Ainda em gestação/puerpério?"}
  OB2 -->|"Sim"| CO2(["Avaliação obstétrica conforme risco<br/>Não aplicar esquema adulto geral"])
  OB2 -->|"Não"| D1{"Pseudorresistência e inércia excluídas?<br/>técnica + adesão + MAPA/MRPA<br/>+ esquema adequado + doses otimizadas<br/>+ tempo suficiente"}

  D1 -->|"Não"| C1(["Não rotular como resistente verdadeira<br/>Corrigir técnica/adesão/composição/titulação<br/>Referir se não for possível esclarecer/otimizar<br/>sem exigir confirmação prévia completa"])

  D1 -->|"Sim"| D2{"Serviço local consegue otimizar<br/>e monitorar com segurança?"}
  D2 -->|"Sim"| C2(["Otimizar e monitorar localmente<br/>como ponte; programar avaliação<br/>especializada se resistência confirmada"])
  D2 -->|"Não / secundária complexa / polifarmácia"| C3(["Encaminhamento ao centro de HAS/especialista"])

  C2 --> D3{"Controle adequado após otimização?"}
  D3 -->|"Sim"| C4(["Manter seguimento compartilhado<br/>Reabrir se novo indicador"])
  D3 -->|"Não"| D4{"Persistência apesar de >=5 classes<br/>adequadas/otimizadas + adesão + MAPA/MRPA<br/>ou LOA progressiva / alta complexidade?"}
  D4 -->|"Não"| C3
  D4 -->|"Sim"| C5(["Priorizar centro especializado<br/>Reavaliar secundárias e adesão<br/>Procedimento não é automático"])

  C3 --> C6(["Manter ponte ambulatorial enquanto espera"])
  C5 --> C6

  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C0,COB alerta;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## Notas

- `MAPA/MRPA + adesão` **não bastam** se o esquema estiver subdosado/inadequado.
- Gestação/puerpério com PA grave segue regra própria antes do algoritmo de resistente.
- `>=5 classes` só é relevante quando composição, titulação, adesão e confirmação fora do consultório estão adequadas.
- Denervação/qualquer procedimento depende de avaliação especializada e não é consequência automática da refratariedade.

Na gestação/puerpério, mesmo abaixo do limiar grave, usar avaliação obstétrica própria; sintomas de pré-eclâmpsia ou deterioração requerem urgência. Não aplicar automaticamente fármacos do algoritmo adulto geral. A confirmação de resistência pode ser realizada no centro especializado quando faltarem recursos locais; a investigação não deve impedir encaminhamento necessário. Refratariedade exige composição adequada, usualmente incluindo diurético tiazídico de longa ação e antagonista mineralocorticoide quando tolerados/indicados; número de classes isolado não define o quadro.
Resistência confirmada é indicação de avaliação especializada; capacidade local de monitorar permite manter tratamento seguro enquanto se organiza essa avaliação, sem precisar esperar falha de cinco classes.
