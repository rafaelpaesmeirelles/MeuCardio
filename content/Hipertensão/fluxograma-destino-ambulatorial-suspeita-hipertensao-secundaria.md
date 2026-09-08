---
title: "Fluxograma: destino ambulatorial na suspeita de hipertensão secundária"
slug: fluxograma-destino-ambulatorial-suspeita-hipertensao-secundaria
theme: "Hipertensão"
kind: fluxograma
fonte_producao: grok
summary: "Destino da investigação de causas secundárias com política explícita de rastreio de aldosteronismo 2025, causas renais, AOS e encaminhamento dirigido."
review_status: revisado
review_note: "Revisão científica/adversarial 08/09/2026: findings PR865 reconstruídos; urgência, bibliografia e limites revistos. Fonte grok preservada."
source_refs:
  - "Endocrine Society. Primary Aldosteronism Clinical Practice Guideline. 2025. https://www.endocrine.org/clinical-practice-guidelines/primary-aldosteronism-2"
  - "Jones DW et al. 2025 AHA/ACC High Blood Pressure Guideline. DOI: 10.1161/CIR.0000000000001356."
  - "McEvoy JW, McCarthy CP, Bruno RM, et al. 2024 ESC Guidelines for the management of elevated blood pressure and hypertension. Eur Heart J. 2024;45(38):3912-4018. DOI: 10.1093/eurheartj/ehae178. PMID: 39210715"
  - "Brandão AA, Rodrigues CIS, Bortolotto LA, et al. Diretriz Brasileira de Hipertensão Arterial – 2025. Arq Bras Cardiol. 2025;122(9):e20250624. DOI: 10.36660/abc.20250624. PMID: 41294179"
  - "Mancia G, Kreutz R, Brunström M, et al. 2023 ESH Guidelines for the management of arterial hypertension. J Hypertens. 2023;41(12):1874-2071. DOI: 10.1097/HJH.0000000000003480. PMID: 37345492"
  - "Charles L, Triscott J, Dobbs B. Secondary Hypertension: Discovering the Underlying Cause. Am Fam Physician. 2017;96(7):453-461. PMID: 29094913"
---

# Fluxograma: destino ambulatorial na suspeita de hipertensão secundária

```mermaid
flowchart TD
 A["Hipertensão e suspeita de causa secundária"] --> B{"Emergência ou gestação?"}
 B -->|Sim| C["Via aguda ou obstétrica específica"]
 B -->|Não| D["Confirmar PA, adesão e substâncias pressoras"]
 D --> E["Rastreio de aldosteronismo conforme política 2025"]
 E --> F{"Pista de causa específica?"}
 F -->|Sim| G["Teste dirigido e especialidade correspondente"]
 F -->|Não| H["Plano de HAS e avaliação de rastreio ampliado<br/>Sem bateria indiscriminada"]
```

## Aplicação

Aplicar os critérios do protocolo irmão antes de escolher o ramo. Estabilidade atual, evolução e acesso determinam o prazo; o fluxograma não estabelece doses nem substitui o algoritmo específico.

## Navegação

- [`suspeita-ambulatorial-de-hipertensao-secundaria-quando-escalar-investigacao`](/biblioteca/suspeita-ambulatorial-de-hipertensao-secundaria-quando-escalar-investigacao)
- [`destino-da-investigacao-de-secundaria-centro-has-endocrino-nefrologia`](/biblioteca/destino-da-investigacao-de-secundaria-centro-has-endocrino-nefrologia)
- [`fluxograma-investigacao-hipertensao-secundaria-quando-suspeitar`](/biblioteca/fluxograma-investigacao-hipertensao-secundaria-quando-suspeitar)
