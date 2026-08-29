---
title: "Fluxograma: CREDO — 12 meses após PCI sim; ataque 3–24 h não; CURE é SCA"
slug: fluxograma-credo-12-meses-versus-ataque-pre-pci
theme: "Doença coronariana"
kind: fluxograma
summary: "PCI eletiva/alta chance: CREDO 12 meses reduz morte/IAM/AVC (P=0,02; ARD 3%). Ataque 300 mg 3–24 h: 28 d P=0,23 NS. Subgrupo ≥6 h P=0,051. CURE é NSTE. PCI-CURE é subgrupo de ICP do CURE (pré-tratamento mediano 6 d), não ataque 3–24 h. PLATO/TRITON são P2Y12 mais novos."
review_status: pendente_revisao
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em CREDO PMID 12435254, CURE PMID 11519503 e PCI-CURE PMID 11520521. Publicação sujeita à aprovação do responsável técnico."
source_refs:
  - "Steinhubl SR, et al. CREDO. JAMA. 2002;288(19):2411-2420. PMID: 12435254."
  - "Yusuf S, et al. CURE. N Engl J Med. 2001;345(7):494-502. PMID: 11519503."
  - "Mehta SR, et al. PCI-CURE. Lancet. 2001;358(9281):527-533. PMID: 11520521."
---

# Fluxograma: clopidogrel — CREDO, CURE ou PCI-CURE?

```mermaid
flowchart TD
  R0["Quer citar clopidogrel além da AAS"] --> D1{"Qual a população?"}

  D1 -->|"PCI eletiva ou alta chance de PCI"| C1(["CREDO 12 meses: RRR 26,9%; P=0,02; ARD 3%<br/>Ataque 3–24 h: 28 d P=0,23 NS<br/>≥6 h: P=0,051 — não vender"])

  D1 -->|"SCA sem supra <24 h"| C2(["CURE: 9,3% vs 11,4%; RR 0,80<br/>Sangramento maior RR 1,38. Outro arquivo"])

  D1 -->|"NSTE que foi à ICP"| C3(["PCI-CURE: subgrupo do CURE<br/>pré-tratamento mediano 6 d<br/>30 d RR 0,70 P=0,03<br/>não é ataque 3–24 h"])

  R0 --> D3{"Já é era ticagrelor/prasugrel?"}

  D3 -->|"PLATO / TRITON / ISAR-REACT 5"| C4(["Arquivos próprios da casa.<br/>Não misturar com CREDO 2002"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4 conduta;
```

## Mensagem prática

**CREDO sustenta 12 meses após PCI; não sustenta o ataque 3–24 h.** CURE é SCA. PCI-CURE é o pedaço de ICP do CURE, com pré-tratamento de dias — não o loading imediato. Os P2Y12 posteriores têm arquivo próprio.
