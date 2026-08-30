---
title: "Fluxograma: heparina ou bivalirudina na ICP do IAM — HEAT, VALIDATE e MATRIX"
slug: fluxograma-heparina-versus-bivalirudina-na-icp-do-iam
theme: "Doença coronariana"
kind: fluxograma
summary: "HIT → bivalirudina. Fora HIT, na ICP contemporânea (radial, P2Y12 potente, GPI só de resgate): heparina em monoterapia. VALIDATE empatou em 180 d; HEAT favoreceu heparina em 28 d. HORIZONS/MATRIX não autorizam bivalirudina rotineira contra heparina sem GPI."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada nos abstracts de HEAT-PPCI (PMID 25002178) e VALIDATE-SWEDEHEART (PMID 28844201). MATRIX/HORIZONS: documento da casa já revisado, não relidos de novo nesta revisão editorial. Doses de VALIDATE não estão no abstract — a árvore não inventa dose de VALIDATE; HEAT declara 70 U/kg. Revisão científica concluída em 30/08/2026."
source_refs:
  - "Shahzad A, et al. HEAT-PPCI. Lancet. 2014;384(9957):1849-1858. PMID: 25002178."
  - "Erlinge D, et al. VALIDATE-SWEDEHEART. N Engl J Med. 2017;377(12):1132-1142. PMID: 28844201."
  - "Documentos da casa heat-ppci-heparina-versus-bivalirudina-na-icp-primaria, validate-swedeheart-bivalirudina-versus-heparina-monoterapia-no-iam e bivalirudina-vs-heparina-na-icp-primaria-do-iamcsst-trombose-de-stent-e-o-ensaio-matrix."
---

# Fluxograma: heparina ou bivalirudina na ICP do IAM

```mermaid
flowchart TD
  R0["IAM em ICP<br/>(primária ou IAMSSST)"] --> D1{"HIT confirmada ou<br/>suspeita de HIT?"}

  D1 -->|"Sim"| C1(["Bivalirudina — via HIT da casa.<br/>Não é benefício de desfecho do VALIDATE"])

  D1 -->|"Não"| D2{"Acesso radial + P2Y12 potente<br/>e GPI só de resgate<br/>(prática VALIDATE/HEAT)?"}

  D2 -->|"Sim"| C2(["Heparina em monoterapia.<br/>VALIDATE: 12,3% vs 12,8% em 180 d, P=0,54.<br/>HEAT: isquemia 28 d 5,7% vs 8,7% a favor da heparina"])

  D2 -->|"Não — protocolo ainda é<br/>heparina + GPI rotineiro"| C3(["Não usar HORIZONS para 'provar'<br/>bivalirudina rotineira hoje.<br/>O comparador de GPI mudou"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3 conduta;
```

## Mensagem prática

**Fora HIT, heparina.** VALIDATE empatou; HEAT favoreceu heparina e não sangrou mais. A geração HORIZONS comparava contra heparina+GPI — outra pergunta.
