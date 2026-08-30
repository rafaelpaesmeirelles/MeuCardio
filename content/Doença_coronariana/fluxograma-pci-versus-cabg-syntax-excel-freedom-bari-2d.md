---
title: "Fluxograma: PCI ou CABG — SYNTAX, EXCEL, FREEDOM e BARI 2D"
slug: fluxograma-pci-versus-cabg-syntax-excel-freedom-bari-2d
theme: "Doença coronariana"
kind: fluxograma
summary: "Trivascular/tronco não selecionado: SYNTAX, CABG ganha MACCE em 12 meses. Tronco SYNTAX ≤32: EXCEL 3 anos NI (5 anos não relido). Diabetes multiarterial: FREEDOM. Diabetes estável, anatomia de CABG: BARI 2D reduz MACE no estrato cirúrgico. PCI vs médica no estrato PCI do BARI 2D empata."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em SYNTAX PMID 19228612, EXCEL PMID 27797291 (3 anos), FREEDOM da casa, BARI 2D PMID 19502645. EXCEL 5 anos e NOBLE não relidos. Revisão científica concluída em 30/08/2026."
source_refs:
  - "Serruys PW, et al. SYNTAX. N Engl J Med. 2009;360(10):961-972. PMID: 19228612."
  - "Stone GW, et al. EXCEL. N Engl J Med. 2016;375(23):2223-2235. PMID: 27797291."
  - "Documentos da casa revascularizacao-multiarterial-no-diabetes-cabg-versus-pci-o-ensaio-freedom e bari-2d-revascularizacao-versus-terapia-medica-no-diabetes-com-dac-estavel."
---

# Fluxograma: PCI ou CABG

```mermaid
flowchart TD
  R0["DAC multiarterial ou tronco.<br/>Os dois times dizem que dá para revascularizar"] --> D1{"Diabetes + multiarterial<br/>(FREEDOM)?"}

  D1 -->|"Sim"| C1(["CABG. FREEDOM é o RCT de PCI vs CABG<br/>nesta população"])

  D1 -->|"Não"| D2{"Tronco isolado ou dominante,<br/>SYNTAX do centro ≤32 (EXCEL)?"}

  D2 -->|"Sim"| C2(["PCI everolimus não-inferior em 3 anos<br/>(15,4% vs 14,7%). 5 anos NÃO relido aqui"])

  D2 -->|"Não — trivascular ± tronco,<br/>não selecionado (SYNTAX)"}| C3(["CABG. MACCE 12 meses 12,4% vs 17,8%.<br/>NI da PCI falhou. AVC maior na CABG"])

  R0 --> D3{"Diabetes + DAC estável,<br/>sem indicação urgente (BARI 2D)?"}

  D3 -->|"Anatomia já de CABG"| C4(["CABG reduz MACE 22,4% vs 30,5%<br/>no estrato cirúrgico. Morte do conjunto NS"])

  D3 -->|"Anatomia já de PCI"| C5(["Médica empata com PCI no estrato.<br/>Não cateterizar 'para salvar vida'"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

## Mensagem prática

**CABG é o padrão da trivascular não selecionada e do diabetes multiarterial. PCI de tronco no EXCEL é 3 anos, não é 5 anos relido. BARI 2D não autoriza revasc imediata para mortalidade.**
