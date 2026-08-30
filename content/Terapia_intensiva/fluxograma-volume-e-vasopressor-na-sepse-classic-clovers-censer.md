---
title: "Fluxograma: volume e vasopressor na sepse — CLASSIC, CLOVERS, CENSER, SEPSISPAM"
slug: fluxograma-volume-e-vasopressor-na-sepse-classic-clovers-censer
theme: "Terapia intensiva"
kind: fluxograma
summary: "Hipotensão por sepse: CLOVERS (24 h cedo) e CLASSIC (já na UTI) empataram restritivo vs liberal em morte. CENSER (centro único) melhorou controle em 6 h com noradrenalina precoce, sem reduzir morte 28 d. PAM 80 vs 65 é SEPSISPAM — neutro. 65-trial é o idoso, outra árvore."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada nos abstracts de CLOVERS (PMID 36688507), CLASSIC (PMID 35709019), CENSER (PMID 30704260) e SEPSISPAM (PMID 24635770). Revisão científica concluída em 30/08/2026."
source_refs:
  - "Shapiro NI, et al. CLOVERS. N Engl J Med. 2023;388(6):499-510. PMID: 36688507."
  - "Meyhoff TS, et al. CLASSIC. N Engl J Med. 2022;386(26):2459-2470. PMID: 35709019."
  - "Permpikul C, et al. CENSER. Am J Respir Crit Care Med. 2019;199(9):1097-1105. PMID: 30704260."
  - "Asfar P, et al. SEPSISPAM. N Engl J Med. 2014;370(17):1583-93. PMID: 24635770."
  - "Documento da casa feast-bolus-de-fluido-aumenta-morte-em-crianca-africana — criança, outro cenário."
  - "Documento da casa vanish-vasopressina-precoce-versus-noradrenalina-no-choque-septico — primário renal NS."
  - "Documento da casa fluxograma-bolus-feast-versus-volume-adulto."
---

# Fluxograma: volume e vasopressor na sepse

```mermaid
flowchart TD
  R0["Sepse com hipotensão"] --> D1{"Já está na UTI com ≥1 L<br/>e choque ≤12 h (molde CLASSIC)?"}

  D1 -->|"Sim"| C1(["CLASSIC: restringir vs padrão,<br/>morte 90 d 42,3% vs 42,1%, P=0,96"])

  D1 -->|"Não — fase precoce, 1–3 L já dados"| D2{"≤4 h da hipotensão refratária<br/>(molde CLOVERS)?"}

  D2 -->|"Sim"| C2(["CLOVERS: restritivo vs liberal 24 h.<br/>Morte até alta dia 90: 14,0% vs 14,9%, P=0,61"])

  D2 -->|"Não"| D3{"A pergunta é PAM 80 vs 65?"}

  D3 -->|"Sim"| C3(["SEPSISPAM: 36,6% vs 34,0% dia 28, P=0,57.<br/>Não empurrar 80 por rotina"])

  D3 -->|"Não"| C4(["Noradrenalina é o vasopressor (SOAP-II).<br/>CENSER: controle 6 h melhor, morte 28 d NS.<br/>Não vender mortalidade do CENSER"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4 conduta;
```

## Mensagem prática

**Nem restringir volume nem puxar PAM a 80 salvou vidas nestes ensaios.** Noradrenalina cedo controla pressão (CENSER); mortalidade é outra conversa.
