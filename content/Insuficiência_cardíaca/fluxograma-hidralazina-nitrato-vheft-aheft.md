---
title: "Fluxograma: hidralazina+nitrato — V-HeFT I (vs placebo), V-HeFT II (vs enalapril), A-HeFT (adição em negros)"
slug: fluxograma-hidralazina-nitrato-vheft-aheft
theme: "Insuficiência cardíaca"
kind: fluxograma
summary: "V-HeFT I: H-ISDN vs placebo, morte 2 anos P<0,028; seguimento total borderline; prazosina NS. V-HeFT II: enalapril vs H-ISDN, morte 2 anos P=0,016; morte total P=0,08. A-HeFT: adição em negros já em neuro-hormonal; interrompido por morte. Não misturar os três."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em V-HeFT I PMID 3520315, V-HeFT II PMID 2057035, A-HeFT PMID 15533851. Revisão científica concluída em 30/08/2026."
source_refs:
  - "Cohn JN, et al. V-HeFT I. N Engl J Med. 1986;314(24):1547-1552. PMID: 3520315."
  - "Cohn JN, et al. V-HeFT II. N Engl J Med. 1991;325(5):303-310. PMID: 2057035."
  - "Taylor AL, et al. A-HeFT. N Engl J Med. 2004;351(20):2049-2057. PMID: 15533851."
---

# Fluxograma: qual ensaio da hidralazina+nitrato?

```mermaid
flowchart TD
  R0["Quer citar hidralazina + nitrato na IC"] --> D1{"Contra o quê?"}

  D1 -->|"Placebo, homens, digoxina+diurético<br/>(V-HeFT I)"| C1(["Morte 2 anos 25,6% vs 34,3% P<0,028<br/>Seguimento total borderline. Prazosina NS"])

  D1 -->|"Enalapril 20 mg<br/>(V-HeFT II)"| C2(["Morte 2 anos 18% vs 25% P=0,016<br/>Morte total P=0,08 NS. IECA ganha este marco"])

  D1 -->|"Adição em negros já em IECA/BB<br/>(A-HeFT)"| C3(["Parado por morte 6,2% vs 10,2% P=0,02<br/>Primário é escore composto, não só morte"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3 conduta;
```

## Mensagem prática

**V-HeFT I não é V-HeFT II não é A-HeFT.** Enalapril ganhou o 2.º ano contra H-ISDN. A-HeFT é adição, não substituição do IECA.
