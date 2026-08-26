---
title: "Fluxograma: Síndrome de liberação de citocinas por CAR-T com hipotensão/choque"
slug: fluxograma-sindrome-de-liberacao-de-citocinas-car-t-com-choque
theme: "Cardio-oncologia"
kind: fluxograma
summary: "Árvore de decisão para CRS após CAR-T, usando graduação ASTCT sem convertê-la automaticamente em tratamento: grau 2 segue protocolo específico, enquanto graus 3-4 exigem UTI, terapia anti-IL-6 e suporte intensivo."
review_status: revisado
review_note: "Revisado em 26/08/2026 contra o consenso ASTCT de graduação (PMID 30592986), a diretriz ESC 2022 de cardio-oncologia (PMID 36017568), a coorte cardiovascular de Alvi et al. (PMID 31856966) e a seção de CRS da bula FDA do tocilizumabe. Corrigida a seta que transformava 'considerar tocilizumabe' em administração obrigatória para todo CRS grau 2: a graduação ASTCT não é algoritmo terapêutico, e o grau 2 deve seguir o protocolo da terapia CAR-T e a evolução clínica. O regime posológico da bula ficou ligado aos graus 3-4 e ao grau 2 somente quando o produto/protocolo indicar; investigação e tratamento de infecção/sepse permanecem paralelos. Pendente revisão médica independente antes de uso assistencial."
source_refs: ["Lee DW, Santomasso BD, Locke FL, et al. ASTCT Consensus Grading for Cytokine Release Syndrome and Neurologic Toxicity Associated with Immune Effector Cells. Biol Blood Marrow Transplant. 2019;25(4):625-638. DOI: 10.1016/j.bbmt.2018.12.758. PMID: 30592986 — definição e graduação, não prescrição terapêutica.", "Lyon AR, López-Fernández T, Couch LS, et al. 2022 ESC Guidelines on cardio-oncology. Eur Heart J. 2022;43(41):4229-4361. DOI: 10.1093/eurheartj/ehac244. PMID: 36017568 — avaliação cardiovascular no CAR-T, diferencial e manejo cardiovascular associado ao CRS.", "Alvi RM, Frigault MJ, Fradley MG, et al. Cardiovascular Events Among Adults Treated With Chimeric Antigen Receptor T-Cells. J Am Coll Cardiol. 2019;74(25):3099-3108. DOI: 10.1016/j.jacc.2019.10.038. PMID: 31856966 — associação de CRS, troponina e eventos cardiovasculares.", "U.S. Food and Drug Administration. ACTEMRA (tocilizumab) Prescribing Information, seção Cytokine Release Syndrome — dose, infusão, limite por dose e intervalo de redose."]
---

# Síndrome de liberação de citocinas por CAR-T com hipotensão/choque

```mermaid
flowchart TD
  R0["Paciente após CAR-T com febre ≥38°C<br/>e suspeita de CRS"]
  D1{"Hipotensão ou hipoxemia?"}
  C1(["ASTCT grau 1 se sem hipotensão e sem hipoxemia:<br/>suporte, investigação de infecção e vigilância clínica"])
  P1["Monitorização contínua, acesso venoso,<br/>perfusão/lactato, ECG e troponina; culturas e<br/>tratamento de sepse se infecção não foi excluída;<br/>eco se houver repercussão cardiovascular"]
  D2{"Gravidade pelo pior componente ASTCT"}
  C2(["Grau 2: hipotensão sem vasopressor<br/>ou O2 por baixo fluxo ≤6 L/min;<br/>suporte e decisão sobre tocilizumabe conforme<br/>produto/protocolo CAR-T e evolução — não<br/>administrar automaticamente só pelo grau"])
  D2A{"Tocilizumabe indicado pelo protocolo<br/>do produto CAR-T, ou CRS em progressão?"}
  C3(["Grau 3: 1 vasopressor ± vasopressina<br/>ou O2 por alto fluxo >6 L/min/máscara;<br/>UTI, tocilizumabe, considerar corticosteroide<br/>e oferecer suporte de órgão"])
  C4(["Grau 4: múltiplos vasopressores<br/>(excluindo vasopressina) ou pressão positiva;<br/>UTI avançada, tocilizumabe, corticosteroide<br/>e suporte circulatório/ventilatório conforme necessidade"])
  P2["Quando indicado, tocilizumabe IV:<br/>≥30 kg: 8 mg/kg; <30 kg: 12 mg/kg;<br/>infusão em 60 min; máximo 800 mg por infusão"]
  D3{"Melhora clínica após primeira dose?"}
  C5(["Sim: manter suporte e monitorização;<br/>reavaliar troponina/eco conforme alteração prévia"])
  C6(["Não: FDA permite até 3 doses adicionais,<br/>com intervalo mínimo de 8 h entre doses;<br/>escalar corticosteroide e investigação de choque refratário<br/>conforme protocolo institucional/especializado"])
  D4{"Há disfunção ventricular, arritmia,<br/>BAV, troponina elevada ou choque desproporcional?"}
  C7(["Sim: tratar como alto risco cardiovascular;<br/>telemetria, ecocardiograma, suporte hemodinâmico<br/>e excluir diagnósticos concomitantes, inclusive miocardite por ICI<br/>se houver exposição pertinente"])
  C8(["Não: seguir vigilância intensiva até resolução do CRS"])

  R0 --> D1
  D1 -->|"Não"| C1
  D1 -->|"Sim"| P1
  P1 --> D2
  D2 -->|"Grau 2"| C2
  D2 -->|"Grau 3"| C3
  D2 -->|"Grau 4"| C4
  C2 --> D2A
  D2A -->|"Sim"| P2
  D2A -->|"Não"| D4
  C3 --> P2
  C4 --> P2
  P2 --> D3
  D3 -->|"Sim"| C5
  D3 -->|"Não"| C6
  C5 --> D4
  C6 --> D4
  D4 -->|"Sim"| C7
  D4 -->|"Não"| C8

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7,C8 conduta;
```

## Pontos críticos

- A graduação ASTCT é determinada pelo **pior** entre hipotensão e hipoxemia; febre ≥38°C é requisito para o diagnóstico inicial de CRS.
- Tocilizumabe para CRS por CAR-T é administrado **por via intravenosa**. A rotulagem FDA recomenda 8 mg/kg em pacientes ≥30 kg e 12 mg/kg em pacientes <30 kg, com máximo de 800 mg por infusão.
- Se não houver melhora, podem ser administradas até **3 doses adicionais**, com intervalo mínimo de **8 horas**.
- O risco cardiovascular não é teórico: a coorte de Alvi et al. mostrou que eventos cardiovasculares se concentraram nos pacientes com CRS grau ≥2 e eram frequentemente precedidos por elevação de troponina.
- A classificação ASTCT descreve gravidade; ela não determina sozinha quando
  administrar tocilizumabe. No grau 2, a indicação e o limiar de escalada dependem
  do produto CAR-T, do protocolo institucional e da evolução clínica.
- CRS e sepse podem coexistir. Culturas, antimicrobianos quando indicados e busca
  de foco infeccioso não devem ser adiados porque a febre surgiu após CAR-T.
