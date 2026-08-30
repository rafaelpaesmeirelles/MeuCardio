---
title: "Fluxograma: CARE vs LIPID vs AFCAPS — morte total só no LIPID"
slug: fluxograma-care-lipid-afcaps-morte-versus-composto
theme: "Prevenção e lipídios"
kind: fluxograma
summary: "CARE: composto coronariano P=0,003; morte total NS. LIPID: morte coronariana e morte total P<0,001. AFCAPS: primeiro evento RR 0,63 inclui angina instável; morte ausente no abstract. 4S/WOSCOPS no combinado da casa. Não colapsar CARE com LIPID."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em CARE PMID 8801446, LIPID PMID 9841303, AFCAPS PMID 9613910. Revisão científica concluída em 30/08/2026."
source_refs:
  - "Sacks FM, et al. CARE. N Engl J Med. 1996;335(14):1001-9. PMID: 8801446."
  - "LIPID Study Group. N Engl J Med. 1998;339(19):1349-57. PMID: 9841303."
  - "Downs JR, et al. AFCAPS/TexCAPS. JAMA. 1998;279(20):1615-22. PMID: 9613910."
---

# Fluxograma: estatina clássica — o que cada um ganhou

```mermaid
flowchart TD
  R0["Quer citar pravastatina/lovastatina clássica"] --> D1{"Qual população?"}

  D1 -->|"Pós-IAM, colesterol médio<br/>(CARE)"| C1(["Primário 10,2% vs 13,2%, P=0,003<br/>Morte total NS. Não vender mortalidade"])

  D1 -->|"DAC, colesterol 155–271<br/>(LIPID)"| C2(["Morte coronariana 6,4% vs 8,3%<br/>Morte total 11,0% vs 14,1%. Primário de morte"])

  D1 -->|"Primária, colesterol médio, HDL baixo<br/>(AFCAPS)"| C3(["Primeiro evento RR 0,63 inclui angina instável<br/>Morte total ausente no abstract"])

  D1 -->|"4S / WOSCOPS"| C4(["Dump no combinado da casa<br/>Não reescrever o revisado"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4 conduta;
```

## Mensagem prática

**LIPID é o ensaio de morte.** CARE é composto, morte total empatou. AFCAPS inclui angina instável.
