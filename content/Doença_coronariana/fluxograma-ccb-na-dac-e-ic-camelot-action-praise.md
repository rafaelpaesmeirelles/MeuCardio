---
title: "Fluxograma: CCB diidropiridínico na DAC e na IC — CAMELOT, ACTION, PRAISE"
slug: fluxograma-ccb-na-dac-e-ic-camelot-action-praise
theme: "Doença coronariana"
kind: fluxograma
summary: "DAC com PA ~normal: CAMELOT — amlodipina vs placebo ganhou composto largo (HR 0,69; P=0,003); enalapril NS. Angina estável: ACTION — nifedipina GITS primário HR 0,97; P=0,54. IC grave FE<30%: PRAISE primário P=0,31; subgrupo não-isquêmico não sobreviveu ao PRAISE-2 (HR 1,09; P=0,33). IONA é nicorandil, outra classe. Não vender NS nem secundário como vitória."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em CAMELOT (PMID 15536108), ACTION (PMID 15351192), PRAISE (PMID 8813041) e PRAISE-2 (PMID 24621933), abstracts relidos via PubMed efetch nesta revisão editorial. IONA (PMID 11965271) só como nota de classe distinta. Revisão científica concluída em 30/08/2026."
source_refs:
  - "Nissen SE, et al. CAMELOT. JAMA. 2004;292(18):2217-2225. PMID: 15536108."
  - "Poole-Wilson PA, et al. ACTION. Lancet. 2004;364(9437):849-857. PMID: 15351192."
  - "Packer M, et al. PRAISE. N Engl J Med. 1996;335(15):1107-1114. PMID: 8813041."
  - "Packer M, et al. PRAISE-2. JACC Heart Fail. 2013;1(4):308-314. PMID: 24621933."
---

# Fluxograma: CCB diidropiridínico na DAC e na IC

```mermaid
flowchart TD
  R0["Alguém perguntou se liga CCB diidropiridínico"] --> D1{"Qual o território?"}

  D1 -->|"DAC angiográfica, PA ~normal<br/>(perfil CAMELOT)"| C1(["CAMELOT: amlodipina 10 mg vs placebo<br/>16,6% vs 23,1%; HR 0,69; P=0,003.<br/>Enalapril vs placebo HR 0,85; P=0,16 NS.<br/>Composto largo — não é morte isolada"])

  D1 -->|"Angina estável já tratada"| C2(["ACTION: nifedipina GITS 60 mg<br/>primário HR 0,97; P=0,54.<br/>Morte HR 1,07; P=0,41.<br/>Menos cine não é o primário"])

  D1 -->|"IC grave, FE menor que 30%"| C3(["PRAISE: primário 39% vs 42%; P=0,31.<br/>Morte P=0,07 NS.<br/>Subgrupo não-isquêmico → PRAISE-2<br/>HR 1,09; P=0,33. Não é pilar"])

  D1 -->|"Antianginoso que não é CCB"| C4(["IONA: nicorandil — outra classe.<br/>Primário inclui internação por dor.<br/>Morte/IAM P=0,068 NS"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4 conduta;
```

## Mensagem prática

**Amlodipina ganhou um composto largo no CAMELOT; nifedipina GITS empatou no ACTION; amlodipina não reduz morte na IC (PRAISE/PRAISE-2).** CCB na ICFEr, se precisar para HAS ou angina, é tolerância — não é o quarto pilar.
