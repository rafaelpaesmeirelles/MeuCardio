---
title: "Fluxograma: bivalirudina — HERO-2 (lise, morte NS), REPLACE-2 (ICP, NI), HEAT/VALIDATE (IAM)"
slug: fluxograma-bivalirudina-hero-2-replace-2-heat
theme: "Doença coronariana"
kind: fluxograma
summary: "Lise com estreptoquinase: HERO-2 morte 30 d P=0,85. ICP eletiva/urgente: REPLACE-2 primário P=0,32, menos sangramento maior contra HNF+GPI. IAM com ICP: HEAT/VALIDATE/EUROMAX — arquivos próprios. Não vender reinfarto de 96 h nem NI sem margem."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em HERO-2 PMID 11741625 e REPLACE-2 PMID 12588269. Publicação sujeita à aprovação do responsável técnico. Revisão independente ChatGPT concluída em 29/08/2026: desfechos primários, amostra, comparadores, PMIDs/DOIs e mensagens de segurança conferidos; liberado para publicação pelo responsável técnico."
source_refs:
  - "White H, et al. HERO-2. Lancet. 2001;358(9296):1855-1863. PMID: 11741625."
  - "Lincoff AM, et al. REPLACE-2. JAMA. 2003;289(7):853-863. PMID: 12588269."
---

# Fluxograma: onde a bivalirudina foi testada

```mermaid
flowchart TD
  R0["Quer citar bivalirudina"] --> D1{"Qual o cenário?"}

  D1 -->|"IAMCSST com estreptoquinase"| C1(["HERO-2: morte 30 d 10,8% vs 10,9%; P=0,85<br/>Reinfarto 96 h é secundário"])

  D1 -->|"ICP eletiva ou urgente"| C2(["REPLACE-2: primário P=0,32<br/>Isquêmico P=0,40<br/>Sangramento maior 2,4% vs 4,1%<br/>Margem de NI ausente no abstract"])

  D1 -->|"ICP primária / SCA invasiva"| C3(["HEAT, VALIDATE, EUROMAX, ACUITY<br/>Arquivos próprios. Não misturar com HERO-2"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3 conduta;
```

## Mensagem prática

**Lise: morte NS. ICP eletiva: empate isquêmico, menos sangra contra GPI planejada. IAM contemporâneo: ler HEAT/VALIDATE.**
