---
title: "Fluxograma: destino ambulatorial na suspeita de hipertensão secundária"
slug: fluxograma-destino-ambulatorial-suspeita-hipertensao-secundaria
theme: "Hipertensão"
kind: fluxograma
fonte_producao: grok
summary: "Árvore pós-#828: gate de emergência já feito → há indicador de secundária? → exame dirigido no serviço vs encaminhar endocrino/nefrologia/sono/centro de HAS vs plano habitual."
review_status: pendente_revisao
review_note: "Irmão dos protocolos suspeita-ambulatorial e destino-centro-has-endocrino-nefrologia (07/09/2026). Além de #828; não duplica árvore pista→exame nem tabela PA≥180/lesão aguda. Fontes: ESC 2024 PMID 39210715; SBC 2025 PMID 41294179; ESH 2023 PMID 37345492; Charles AFP PMID 29094913."
source_refs:
  - "McEvoy JW, McCarthy CP, Bruno RM, et al. 2024 ESC Guidelines for the management of elevated blood pressure and hypertension. Eur Heart J. 2024;45(38):3912-4018. DOI: 10.1093/eurheartj/ehae178. PMID: 39210715"
  - "Brandão AA, Rodrigues CIS, Bortolotto LA, et al. Diretriz Brasileira de Hipertensão Arterial – 2025. Arq Bras Cardiol. 2025;122(9):e20250624. DOI: 10.36660/abc.20250624. PMID: 41294179"
  - "Mancia G, Kreutz R, Brunström M, et al. 2023 ESH Guidelines for the management of arterial hypertension. J Hypertens. 2023;41(12):1874-2071. DOI: 10.1097/HJH.0000000000003480. PMID: 37345492"
  - "Charles L, Triscott J, Dobbs B. Secondary Hypertension: Discovering the Underlying Cause. Am Fam Physician. 2017;96(7):453-461. PMID: 29094913"
---

# Fluxograma: destino ambulatorial na suspeita de hipertensão secundária

Prosa: [`suspeita-ambulatorial-de-hipertensao-secundaria-quando-escalar-investigacao`](suspeita-ambulatorial-de-hipertensao-secundaria-quando-escalar-investigacao.md) · [`destino-da-investigacao-de-secundaria-centro-has-endocrino-nefrologia`](destino-da-investigacao-de-secundaria-centro-has-endocrino-nefrologia.md).

Gate prévio (PS vs retorno precoce): [#828](https://github.com/rafaelpaesmeirelles/MeuCardio/pull/828) / [`fluxograma-sinais-de-alarme-ambulatoriais-hipertensao`](fluxograma-sinais-de-alarme-ambulatoriais-hipertensao.md). Pista→exame: [`fluxograma-investigacao-hipertensao-secundaria-quando-suspeitar`](fluxograma-investigacao-hipertensao-secundaria-quando-suspeitar.md).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta ambulatorial<br/>pós-gate de emergência / PA muito elevada<br/>(pacote #828 já aplicado)"] --> D1{"Há indicador de<br/>hipertensão secundária?<br/>início jovem · instalação abrupta<br/>resistente verdadeira · hipoK<br/>pista endócrina / AOS / renovascular"}

  D1 -->|"Não"| C1(["HAS essencial provável<br/>Plano e retorno habituais<br/>Não rastrear secundária de rotina"])

  D1 -->|"Sim"| D2{"Pista clínica específica<br/>já aponta um caminho?"}

  D2 -->|"Sim — endócrina<br/>hipoK / ARR / feo / Cushing / tireoide"| C2(["Exame inicial dirigido<br/>+ Endocrinologia / HAS com expertise<br/>Feo em crise → PS (#828)"])

  D2 -->|"Sim — AOS"| C3(["Sono / polissonografia<br/>Tratar AOS antes de escalonar sem fim"])

  D2 -->|"Sim — renovascular / coartação"| C4(["Imagem dirigida<br/>+ Nefrologia ± vascular / congênita"])

  D2 -->|"Não / múltiplas pistas<br/>ou resistente confirmada"| C5(["Centro de HAS / referência<br/>Painel mínimo + reavaliação<br/>Ver fluxograma pista→exame"])

  C2 --> D3{"Resultado inicial<br/>fecha o caso no serviço?"}
  C3 --> D3
  C4 --> D3
  C5 --> D3

  D3 -->|"Não / positivo complexo"| C6(["Manter oral + retorno curto<br/>até especialidade absorver<br/>Não abandonar controle"])
  D3 -->|"Sim / negativo e sem alarme"| C7(["Reintegrar ao plano ambulatorial<br/>Reabrir se novo indicador"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C2 alerta;
  class C1,C3,C4,C5,C6,C7 conduta;
```

## Notas

- **D1** = gate de secundária (não é o gate de lesão aguda do #828).
- **D2** = escolhe **destino**, não o corte laboratorial confirmatório.
- **Não decide** metas IV, doses, quarta droga nem painel “tudo junto”.
