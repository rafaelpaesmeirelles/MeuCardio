---
title: "Fluxograma: timing de encaminhamento ambulatorial na hipertensão resistente"
slug: fluxograma-timing-encaminhamento-ambulatorial-hipertensao-resistente
theme: "Hipertensão"
kind: fluxograma
fonte_producao: grok
summary: "Árvore pós-#828: gate de emergência feito → pseudorresistência excluída? → capacidade local vs encaminhamento de rotina vs antecipar (refratária/denervação) — além do mapa de secundária #865. Sem doses."
review_status: pendente_revisao
review_note: "Irmão de timing-de-encaminhamento-ambulatorial-na-hipertensao-resistente (07/09/2026). Além de #828 e #865; não duplica árvore da quarta droga nem tabela PA≥180/lesão aguda. Fontes: ESC 2024 PMID 39210715; SBC 2025 PMID 41294179; Carey AHA PMID 30354828; BIHS PMID 38196000 / 39653728."
source_refs:
  - "McEvoy JW, McCarthy CP, Bruno RM, et al. 2024 ESC Guidelines for the management of elevated blood pressure and hypertension. Eur Heart J. 2024;45(38):3912-4018. DOI: 10.1093/eurheartj/ehae178. PMID: 39210715"
  - "Brandão AA, Rodrigues CIS, Bortolotto LA, et al. Diretriz Brasileira de Hipertensão Arterial – 2025. Arq Bras Cardiol. 2025;122(9):e20250624. DOI: 10.36660/abc.20250624. PMID: 41294179"
  - "Carey RM, Calhoun DA, Bakris GL, et al. Resistant Hypertension: Detection, Evaluation, and Management: A Scientific Statement From the American Heart Association. Hypertension. 2018;72(5):e53-e90. DOI: 10.1161/HYP.0000000000000084. PMID: 30354828"
  - "Lewis P, George J, Kapil V, et al. Adult hypertension referral pathway and therapeutic management: British and Irish Hypertension Society position statement. J Hum Hypertens. 2024;38(1):3-7. DOI: 10.1038/s41371-023-00882-2. PMID: 38196000"
  - "Faconti L, et al. Investigation and management of resistant hypertension: British and Irish Hypertension Society position statement. J Hum Hypertens. 2024. DOI: 10.1038/s41371-024-00983-6. PMID: 39653728"
---

# Fluxograma: timing de encaminhamento ambulatorial na hipertensão resistente

Prosa: [`timing-de-encaminhamento-ambulatorial-na-hipertensao-resistente`](timing-de-encaminhamento-ambulatorial-na-hipertensao-resistente.md) · [`ponte-ambulatorial-enquanto-espera-centro-has-na-resistente`](ponte-ambulatorial-enquanto-espera-centro-has-na-resistente.md).

Gate prévio (PS vs retorno precoce): [#828](https://github.com/rafaelpaesmeirelles/MeuCardio/pull/828). Destino de secundária (especialidade): [#865](https://github.com/rafaelpaesmeirelles/MeuCardio/pull/865). Quarta droga: [`fluxograma-hipertensao-resistente-quarta-droga`](fluxograma-hipertensao-resistente-quarta-droga.md).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta ambulatorial<br/>suspeita ou rótulo de hipertensão resistente<br/>pós-gate #828"] --> D0{"Há sinal de lesão aguda<br/>de órgão-alvo?"}

  D0 -->|"Sim / dúvida"| C0(["PS / emergência AGORA<br/>Não é fila de centro de HAS<br/>Ver #828"])

  D0 -->|"Não"| D1{"Pseudorresistência excluída?<br/>técnica + adesão + MAPA/MRPA"}

  D1 -->|"Não"| C1(["Degrau 0: NÃO referir como resistente<br/>Corrigir técnica / adesão / pedir MAPA<br/>Ver docs de pseudorresistência"])

  D1 -->|"Sim — resistente verdadeira"| D2{"Serviço local consegue<br/>otimizar e monitorar com segurança?"}

  D2 -->|"Sim"| C2(["Degrau 1: ambulatório com retorno curto<br/>Otimizar conforme fluxograma 4ª droga<br/>SEM doses neste fluxograma"])

  D2 -->|"Não / secundária complexa<br/>polifarmácia / tipagem adesão"| C3(["Degrau 2: encaminhamento de ROTINA<br/>ao centro de HAS / especialista<br/>Carey 2018 · BIHS 2024 · SBC 2025"])

  C2 --> D3{"PA controlada após otimização<br/>local razoável?"}
  D3 -->|"Sim"| C4(["Manter ambulatório<br/>Reabrir se novo indicador"])
  D3 -->|"Não"| D4{"Refratária ≥5 fármacos<br/>ou candidata a denervação<br/>ou LOA progressiva?"}

  D4 -->|"Sim"| C5(["Degrau 3: ANTECIPAR<br/>encaminhamento especializado<br/>SBC Cap. 12"])
  D4 -->|"Não"| C3

  C3 --> C6(["Ponte ambulatorial enquanto espera<br/>Ver doc irmão · não abandonar oral"])
  C5 --> C6

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C0 alerta;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## Notas

- **D0** = gate de segurança (#828) — não é o gate de secundária (#865).
- **D1** = só depois disso existe "resistente verdadeira".
- **D2/D4** = escolhem **timing** (ficar / rotina / antecipar), não a dose da 4ª droga.
- Destino endocrino/nefrologia/sono quando a pista é de secundária → [#865](https://github.com/rafaelpaesmeirelles/MeuCardio/pull/865).
