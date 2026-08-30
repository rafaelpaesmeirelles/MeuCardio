---
title: "Fluxograma: o que não vender no TEV do câncer — ADAM-VTE, Planquette 2022, SELECT-D"
slug: fluxograma-nao-vender-ensaio-pequeno-no-tev-do-cancer
theme: "Tromboembolismo"
kind: fluxograma
summary: "ADAM-VTE: primário de sangramento maior NS (0% vs 1,4%; P=0,138); recorrência é secundário. Planquette 2022 (NCT02746185): n=158, NI não atingida. SELECT-D: piloto. CLOT ganhou vs cumarínico; CATCH não replicou com tinzaparina. NI formal DOAC vs dalteparina = Caravaggio/Hokusai no protocolo de Khorana."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Âncoras: ADAM-VTE PMID 31630479, Planquette PMID 34627853, SELECT-D PMID 29746227, CLOT PMID 12853587, CATCH PMID 26284719. Sem acrônimo CASTA-DIVA (TITLE search 0). Revisão científica concluída em 30/08/2026."
source_refs:
  - "McBane RD, et al. ADAM VTE. J Thromb Haemost. 2020;18(2):411-421. PMID: 31630479."
  - "Planquette B, et al. Chest. 2022;161(3):781-790. PMID: 34627853. NCT02746185."
  - "Documento da casa select-d-rivaroxabana-versus-dalteparina-no-tev-associado-ao-cancer."
  - "Documento da casa clot-dalteparina-versus-cumarinico-no-tev-associado-ao-cancer."
  - "Documento da casa catch-tinzaparina-versus-varfarina-no-tev-associado-ao-cancer."
  - "Documento da casa trombose-associada-ao-cancer-escore-de-khorana-e-escolha-de-anticoagulante."
---

# Fluxograma: ensaio pequeno não atropela NI formal

```mermaid
flowchart TD
  R0["Câncer + TEV: alguém cita um oral vs HBPM"] --> D1{"O ensaio fecha o que promete?"}

  D1 -->|"Primário de sangramento, n~300, 0 eventos"| C1(["ADAM-VTE: P=0,138 NS<br/>Recorrência P=0,0281 é SECUNDÁRIO"])
  D1 -->|"NI formal, n=158, 3 meses"| C2(["Planquette 2022: NI NÃO atingida<br/>SHR 0,75 (0,21–2,66)"])
  D1 -->|"Piloto, amostra para ±4,5%"| C3(["SELECT-D: 4% vs 11%<br/>CRNMB HR 3,76 — não é NI"])
  D1 -->|"HBPM vs cumarínico"| C4(["CLOT ganhou (P=0,002)<br/>CATCH não replicou (P=0,07)"])
  D1 -->|"NI formal, n>1.000"| C5(["Caravaggio / Hokusai-VTE Cancer<br/>já no protocolo de Khorana"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

## Mensagem prática

**Não promover secundário de ensaio pequeno, nem NI que o n não fechou.** Caravaggio e Hokusai continuam sendo o confronto oral vs dalteparina com tamanho. CLOT não autoriza toda HBPM — CATCH é o recado.
