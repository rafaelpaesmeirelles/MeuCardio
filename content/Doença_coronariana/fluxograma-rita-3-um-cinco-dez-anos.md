---
title: "Fluxograma: RITA-3 — 4 meses, 1 ano, 5 anos, 10 anos"
slug: fluxograma-rita-3-um-cinco-dez-anos
theme: "Doença coronariana"
kind: fluxograma
summary: "RITA-3 n=1.810. 4 meses: composto cai por angina refratária. 1 ano morte/IAM NS. 5 anos morte/IAM P=0,044; morte P=0,054. 10 anos morte P=0,94. Não colapsar num 'invasivo salva vida'."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em PMID 12241831, 16154018 e 26227188. Revisão independente ChatGPT concluída em 29/08/2026: desfechos primários, amostra, comparadores, PMIDs/DOIs e mensagens de segurança conferidos; liberado para publicação pelo responsável técnico."
source_refs:
  - "Fox KA, et al. RITA 3. Lancet. 2002;360(9335):743-751. PMID: 12241831."
  - "Fox KA, et al. RITA 3 5-year. Lancet. 2005;366(9489):914-920. PMID: 16154018."
  - "Henderson RA, et al. RITA-3 10-year. J Am Coll Cardiol. 2015;66(5):511-520. PMID: 26227188."
---

# Fluxograma: o que o RITA-3 realmente mostrou

```mermaid
flowchart TD
  R0["Quer citar RITA-3 na SCA sem supra"] --> D1{"Qual horizonte?"}

  D1 -->|"4 meses"| C1(["Morte/IAM/angina refratária<br/>9,6% vs 14,5%; P=0,001<br/>ganho = angina, não morte"])

  D1 -->|"1 ano"| C2(["Morte ou IAM 7,6% vs 8,3%<br/>P=0,58 NS"])

  D1 -->|"5 anos"| C3(["Morte/IAM 16,6% vs 20,0%; P=0,044<br/>Morte 12% vs 15%; P=0,054<br/>IC da morte inclui 1"])

  D1 -->|"10 anos"| C4(["Morte 25,1% vs 25,4%; P=0,94<br/>Morte CV P=0,65"])

  R0 --> D2{"É outra pergunta?"}

  D2 -->|"Invasivo vs seletivo noutro ensaio"| C5(["FRISC II / TACTICS / ICTUS<br/>arquivo e fluxograma próprios"])
  D2 -->|"Timing da angiografia"| C6(["TIMACS / VERDICT / ISAR-COOL<br/>arquivo próprio"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## Mensagem prática

**4 meses = angina; 1 ano NS; 5 anos composto limiar; 10 anos morte empata.** Não vender mortalidade.
