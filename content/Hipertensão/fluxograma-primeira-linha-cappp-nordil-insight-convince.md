---
title: "Fluxograma: primeira linha — CAPPP, NORDIL, INSIGHT, CONVINCE, STOP-2 (primários NS)"
slug: fluxograma-primeira-linha-cappp-nordil-insight-convince
theme: "Hipertensão"
kind: fluxograma
summary: "CAPPP captopril P=0,52 (mais AVC). NORDIL diltiazem P=0,97 (AVC secundário). INSIGHT nifedipina GITS P=0,35. CONVINCE verapamil COER não demonstrou equivalência (patrocinador parou). STOP-2 convencional vs novo P=0,89. SCOPE primário P=0,19. ALLHAT/ASCOT/ACCOMPLISH são o outro arquivo."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em CAPPP PMID 10030325, NORDIL PMID 10972367, INSIGHT PMID 10972368, CONVINCE PMID 12709465, STOP-2 PMID 10577635. Revisão científica concluída em 30/08/2026."
source_refs:
  - "Hansson L, et al. CAPPP. Lancet. 1999;353(9153):611-616. PMID: 10030325."
  - "Hansson L, et al. NORDIL. Lancet. 2000;356(9227):359-365. PMID: 10972367."
  - "Brown MJ, et al. INSIGHT. Lancet. 2000;356(9227):366-372. PMID: 10972368."
  - "Black HR, et al. CONVINCE. JAMA. 2003;289(16):2073-2082. PMID: 12709465."
  - "Hansson L, et al. STOP-2. Lancet. 1999;354(9192):1751-1756. PMID: 10577635."
---

# Fluxograma: primeira linha que empatou

```mermaid
flowchart TD
  R0["Quer citar classe de 1ª linha nestes RCTs"] --> D1{"Qual ensaio?"}

  D1 -->|"Captopril vs diurético/BB (CAPPP)"| C1(["Primário RR 1,05; P=0,52<br/>Mais AVC; PA inicial não está no abstract"])

  D1 -->|"Diltiazem vs diurético/BB (NORDIL)"| C2(["Primário RR 1,00; P=0,97<br/>AVC P=0,04 é secundário"])

  D1 -->|"Nifedipina GITS vs co-amilozida (INSIGHT)"| C3(["Primário RR 1,10; P=0,35<br/>Mais edema com GITS"])

  D1 -->|"Verapamil COER (CONVINCE)"| C4(["Equivalência NÃO demonstrada<br/>Patrocinador parou. Hemorragia não-AVC sobe"])

  D1 -->|"Idoso 70–84, 'novo' vs convencional (STOP-2)"| C5(["Primário RR 0,99; P=0,89<br/>IECA e BCC misturados no braço novo"])

  D1 -->|"ALLHAT / ASCOT / ACCOMPLISH"| C6(["Outro arquivo da casa — não misturar"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## Mensagem prática

**Nesta leva o primário empatou.** Não vender AVC de NORDIL/CAPPP/SCOPE como vitória de classe. ALLHAT continua no combinado.
