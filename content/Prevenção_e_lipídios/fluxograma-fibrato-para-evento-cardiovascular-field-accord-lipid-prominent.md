---
title: "Fluxograma: fibrato para reduzir evento CV? FIELD, ACCORD-Lipid e PROMINENT"
slug: fluxograma-fibrato-para-evento-cardiovascular-field-accord-lipid-prominent
theme: "Prevenção e lipídios"
kind: fluxograma
summary: "Diabetes e lipídio 'residual': fibrato não ganhou o primário em nenhum dos três. FIELD (sem estatina na entrada) P=0,16. ACCORD-Lipid (sobre sinvastatina) P=0,32. PROMINENT (TG 200–499 e HDL ≤40 já em hipolipemiante) HR 1,03. TG grave/pancreatite é outra árvore."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada nos abstracts relidos nesta revisão editorial: FIELD PMID 16310551, ACCORD-Lipid PMID 20228404, PROMINENT PMID 36342113. Cortes de TG/HDL do subgrupo do ACCORD-Lipid e o P do PROMINENT NÃO estão nos abstracts — a árvore não os inventa. Revisão científica concluída em 30/08/2026."
source_refs:
  - "Keech A, et al. FIELD. Lancet. 2005;366(9500):1849-1861. PMID: 16310551."
  - "ACCORD Study Group; Ginsberg HN, et al. ACCORD-Lipid. N Engl J Med. 2010;362(17):1563-1574. PMID: 20228404."
  - "Das Pradhan A, et al. PROMINENT. N Engl J Med. 2022;387:1923-1934. DOI: 10.1056/NEJMoa2210645. PMID: 36342113."
  - "Documentos da casa field-fenofibrato-no-diabetes-tipo-2, accord-lipid-fenofibrato-sobre-sinvastatina-no-diabetes e fibratos-e-risco-cardiovascular-residual-o-ensaio-prominent-e-o-precedente-do-accord-lipid."
---

# Fluxograma: fibrato para evento cardiovascular — os três primários

```mermaid
flowchart TD
  R0["Diabetes tipo 2 e a tentação do fibrato"] --> D1{"Qual é a pergunta?"}

  D1 -->|"TG muito alto, risco de pancreatite"| C1(["Não é FIELD/ACCORD/PROMINENT.<br/>Documento da casa de hipertrigliceridemia grave"])

  D1 -->|"Reduzir MACE, ainda sem estatina"| C2(["FIELD: primário coronariano 5,2% vs 5,9%;<br/>HR 0,89; P=0,16 — NS.<br/>Não vender CVD total P=0,035 como vitória"])

  D1 -->|"Já em estatina, somar fenofibrato"| C3(["ACCORD-Lipid: 2,2% vs 2,4%/ano;<br/>HR 0,92; P=0,32 — NS.<br/>Subgrupo TG alto/HDL baixo: P interação 0,057"])

  D1 -->|"TG 200–499 e HDL ≤40, já em hipolipemiante"| C4(["PROMINENT: pemafibrato vs placebo;<br/>572 vs 560 eventos; HR 1,03 (0,91–1,15).<br/>O subgrupo do ACCORD, testado de frente, não confirmou"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4 conduta;
```

## Mensagem prática

**Fibrato não é terapia de MACE no diabetes.** Três primários, três falhas. A estatina (e o que vier depois dela: ezetimiba, PCSK9, bempedoico) é o hipolipemiante de desfecho. TG grave continua outra conversa.
