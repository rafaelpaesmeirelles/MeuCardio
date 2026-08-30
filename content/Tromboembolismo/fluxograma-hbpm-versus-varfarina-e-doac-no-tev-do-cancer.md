---
title: "Fluxograma: HBPM vs varfarina vs DOAC no TEV do câncer — CLOT, CATCH, SELECT-D"
slug: fluxograma-hbpm-versus-varfarina-e-doac-no-tev-do-cancer
theme: "Tromboembolismo"
kind: fluxograma
summary: "Câncer + TEV agudo: CLOT (dalteparina vs cumarínico) reduz recorrência 9% vs 17% (P=0,002). CATCH (tinzaparina vs varfarina) primário NS (P=0,07) — não generalizar CLOT a toda HBPM. SELECT-D é piloto de rivaroxabana vs dalteparina (recorrência 4% vs 11%; CRNMB HR 3,76) — não confirmatório. Caravaggio e Hokusai-VTE Cancer (NI formal DOAC vs dalteparina) já estão no protocolo de Khorana; não re-dumpados aqui."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Âncoras: CLOT PMID 12853587, CATCH PMID 26284719, SELECT-D PMID 29746227. Caravaggio/Hokusai só como ponte ao protocolo já publicado. Revisão científica concluída em 30/08/2026."
source_refs:
  - "Lee AY, et al. CLOT. N Engl J Med. 2003;349(2):146-153. PMID: 12853587."
  - "Lee AYY, et al. CATCH. JAMA. 2015;314(7):677-686. PMID: 26284719."
  - "Young AM, et al. SELECT-D. J Clin Oncol. 2018;36(20):2017-2023. PMID: 29746227."
  - "Documento da casa trombose-associada-ao-cancer-escore-de-khorana-e-escolha-de-anticoagulante."
  - "Documento da casa fluxograma-escolha-do-anticoagulante-no-tev-doac-varfarina-ou-hbpm."
  - "Documento da casa hokusai-vte-cancer-edoxabana-versus-dalteparina — composto NI; sangramento maior sobe."
  - "Documento da casa caravaggio-apixabana-versus-dalteparina-no-tev-do-cancer — recorrência NI."
  - "Documento da casa fluxograma-doac-versus-dalteparina-no-tev-do-cancer."
---

# Fluxograma: CLOT não é CATCH; SELECT-D não é Caravaggio

```mermaid
flowchart TD
  R0["Câncer ativo + TEV agudo"] --> D1{"Qual confronto?"}

  D1 -->|"HBPM vs cumarínico"| D2{"Qual HBPM?"}
  D1 -->|"DOAC vs dalteparina"| D3{"Qual evidência?"}

  D2 -->|"Dalteparina 200→150 UI/kg × 6 meses"| C1(["CLOT: 27/336 vs 53/336<br/>9% vs 17%; HR 0,48; P=0,002<br/>Morte 39% vs 41% — sem p"])
  D2 -->|"Tinzaparina 175 UI/kg × 6 meses"| C2(["CATCH: 7,2% vs 10,5%<br/>HR 0,65; P=0,07 NS<br/>CRNMB P=0,004; morte NS"])

  D3 -->|"Piloto rivaroxabana"| C3(["SELECT-D: 4% vs 11%<br/>HR 0,43 (0,19–0,99)<br/>CRNMB HR 3,76 — não é NI formal"])
  D3 -->|"NI formal"| C4(["Caravaggio e Hokusai-VTE Cancer<br/>já dumpados no protocolo de Khorana<br/>Não re-dumpados aqui"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4 conduta;
```

## Mensagem prática

**CLOT justifica dalteparina vs cumarínico. CATCH não replica isso com tinzaparina.** SELECT-D é piloto: menos recorrência pontual, mais CRNMB — não atropelar Caravaggio/Hokusai nem a ressalva GI/GU.
